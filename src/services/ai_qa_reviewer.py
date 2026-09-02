import json
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


MODEL = os.getenv(
    "AI_QA_REVIEW_MODEL",
    "qwen/qwen3.6-27b",
)


def generate_ai_qa_review(
    receipt_text: str,
) -> dict[str, Any]:
    """
    Perform an independent AI QA review of the physical receipt.

    The AI reviews ONLY the receipt content.
    It does not receive POS XML and does not determine
    the application's authoritative PASS/FAIL result.
    """

    if not receipt_text or not receipt_text.strip():
        return {
            "overall_ai_review": "REVIEW_NOT_AVAILABLE",
            "summary": (
                "AI receipt review could not be performed because "
                "receipt content was not available."
            ),
            "tender_discrepancy": {
                "status": "NOT_VERIFIABLE",
                "message": (
                    "Tender information could not be reviewed."
                ),
            },
            "calculation_review": {
                "status": "NOT_VERIFIABLE",
                "message": (
                    "Receipt calculations could not be reviewed."
                ),
            },
            "additional_observations": [],
        }

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    client = Groq(api_key=api_key)

    user_prompt = f"""
You are an AI QA reviewer for retail receipts.

Review ONLY the physical receipt text below.

You have NO POS XML and must NOT compare this receipt
with any POS transaction data.

Perform an independent QA review of the receipt.

Look broadly for issues, including:

1. Tender and payment consistency
   - cash/card/tender amount
   - total
   - rounding
   - change due
   - relationships between printed payment values

2. Receipt calculations
   - item amounts
   - quantities
   - discounts
   - subtotal
   - individual taxes
   - tax total
   - total
   - rounding

3. Other receipt anomalies

Only report an additional observation when the receipt itself
provides clear evidence of an inconsistency, contradiction,
or potentially incorrect value.

Do NOT flag something merely because it looks unusual.

Treat normal retail receipt behavior as valid unless the receipt
itself demonstrates a contradiction.

Examples of things that should NOT be flagged by themselves:

- multiple timestamps appearing on the receipt
- normal receipt footer information
- normal item-level promotional or discount lines
- return-related text when the receipt structure supports it
- different tax bases when the receipt provides a plausible reason
- rounding lines without clear evidence that the resulting amount
  is incorrect
- item counts that cannot be conclusively reconciled from the
  printed receipt structure

For an additional observation to be reported:

- ISSUE_DETECTED requires strong evidence of an internal receipt
  inconsistency.
- REVIEW_RECOMMENDED requires a clearly unusual condition that
  cannot be confirmed as an error but is specific enough to merit
  human QA review.
- Do not create observations simply to make the review more
  comprehensive.

Independently verify calculations whenever enough information
is present.

For money-related checks, show the actual printed values used
in the calculation.

Do not assume the receipt is correct, but do not assume that
an unusual-looking field is incorrect either.

Do not invent information.

If something cannot be verified from the receipt, use
NOT_VERIFIABLE instead of guessing.

Overall review rule:

Set overall_ai_review to ISSUE_DETECTED only when at least one
primary AI review check or additional observation has strong
evidence of an actual receipt-level inconsistency.

Do not set overall_ai_review to ISSUE_DETECTED solely because
something is unusual or ambiguous.

Important:
Your review is an independent AI observation layer.
Do not change or override any deterministic application result.

Return ONLY a valid JSON object.
Do not return Markdown.
Do not return <think> tags.
Do not return explanations outside the JSON object.

Use exactly this structure:

{{
  "overall_ai_review": "NO_ISSUE_DETECTED" or "ISSUE_DETECTED",
  "summary": "Short professional QA summary.",
  "tender_discrepancy": {{
    "status": "NO_ISSUE_DETECTED" or "ISSUE_DETECTED" or "NOT_VERIFIABLE",
    "message": "Clear explanation of the tender review."
  }},
  "calculation_review": {{
    "status": "NO_ISSUE_DETECTED" or "ISSUE_DETECTED" or "NOT_VERIFIABLE",
    "message": "Clear explanation of the calculation review."
  }},
  "additional_observations": [
    {{
      "category": "Short category name",
      "status": "ISSUE_DETECTED" or "REVIEW_RECOMMENDED",
      "message": "Clear QA observation."
    }}
  ]
}}
Write all summary and message fields as clean professional plain text.

Use normal spaces between words and sentences.

Do not use Markdown, mathematical notation, LaTeX, special formatting,
or concatenated words inside JSON string values.

Express calculations in simple readable text, for example:
"Subtotal $104.49 plus tax $1.12 equals total $105.61."

Keep the response concise.

PHYSICAL RECEIPT:

---------------- RECEIPT START ----------------

{receipt_text}

----------------- RECEIPT END -----------------
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        temperature=0,
        max_completion_tokens=4000,
        response_format={
            "type": "json_object",
        },
        reasoning_format="hidden",
        reasoning_effort="default",
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "AI QA Reviewer returned an empty response."
        )

    return _parse_ai_review(content)


def _parse_ai_review(
    content: str,
) -> dict[str, Any]:
    """
    Parse the AI response as JSON and return the review.
    """

    cleaned = content.strip()

    try:
        review = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "AI QA Reviewer did not return valid JSON."
        ) from exc

    if not isinstance(review, dict):
        raise RuntimeError(
            "AI QA Reviewer returned an invalid response structure."
        )

    return review