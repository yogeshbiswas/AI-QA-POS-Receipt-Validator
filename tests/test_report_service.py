from src.services.report_service import generate_validation_report
from src.services.validation_service import (
    validate_and_format_transaction,
)


def test_generate_validation_report():
    result = validate_and_format_transaction(
        xml_path="sample_data/transaction_14290_return_nonmember.xml",
        receipt_path="sample_data/receipt_14290_return_nonmember.pdf",
        voided_item_code=None,
    )

    pdf_bytes = generate_validation_report(result)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")