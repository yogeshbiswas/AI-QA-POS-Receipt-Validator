import base64
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "openai/gpt-oss-20b"


def extract_receipt_text_with_groq(
    image_path: str,
) -> str:
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Receipt image not found: {image_path}"
        )

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    image_bytes = path.read_bytes()
    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    suffix = path.suffix.lower()

    if suffix in {".jpg", ".jpeg"}:
        mime_type = "image/jpeg"
    elif suffix == ".png":
        mime_type = "image/png"
    else:
        raise ValueError(
            f"Unsupported image type: {suffix}"
        )

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Read this retail receipt exactly as printed. "
                            "Return only the receipt text, preserving the "
                            "original line order. Do not summarize, explain, "
                            "correct, infer, or add any text."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                f"data:{mime_type};base64,"
                                f"{encoded_image}"
                            )
                        },
                    },
                ],
            }
        ],
        temperature=0,
        max_completion_tokens=900,
        reasoning_format="hidden",
    )

    return response.choices[0].message.content or ""