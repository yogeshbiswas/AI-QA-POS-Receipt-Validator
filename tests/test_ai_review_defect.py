from src.services.ai_qa_reviewer import generate_ai_qa_review


receipt_text = """
SUBTOTAL $16.61
SALE
TAX County 0.70% ON $17.26 $0.12
TAX City 2.00% ON $17.26 $0.35
TAX State 5.60% ON $17.26 $0.97
TAX TOTAL: $1.44
TOTAL $18.05
ROUNDING -$0.01
Cash $18.70
CHANGE DUE $0.00
"""


review = generate_ai_qa_review(receipt_text)

print("\nAI QA REVIEW - DEFECT RECEIPT")
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