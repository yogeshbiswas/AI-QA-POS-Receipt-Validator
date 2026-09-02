from src.services.ai_qa_reviewer import generate_ai_qa_review
from src.extractors.pdf_extractor import extract_receipt_pdf



receipt_pdf = extract_receipt_pdf(
    "sample_data/receipt_14289_debit_nonmember.pdf"
)

receipt_text = "\n".join(
    receipt_pdf.receipt_lines
)

review = generate_ai_qa_review(receipt_text)

print("\nAI QA REVIEW")
print("=" * 60)

print("Overall:", review["overall_ai_review"])

print("\nSummary:")
print(review["summary"])

print("\nTender Discrepancy:")
print(review["tender_discrepancy"]["status"])
print(review["tender_discrepancy"]["message"])

print("\nCalculation Review:")
print(review["calculation_review"]["status"])
print(review["calculation_review"]["message"])

print("\nAdditional Observations:")

for observation in review["additional_observations"]:
    print(
        f"- {observation['category']}: "
        f"{observation['status']} - "
        f"{observation['message']}"
    )