from src.services.result_formatter import format_validation_result
from src.services.validation_service import validate_transaction


def test_result_formatter_14290():
    raw_result = validate_transaction(
        xml_path="sample_data/transaction_14290_return_nonmember.xml",
        receipt_path="sample_data/receipt_14290_return_nonmember.pdf",
        voided_item_code=None,
    )

    formatted = format_validation_result(raw_result)

    assert formatted["overall_status"] == "FAIL"

    assert formatted["transaction"]["transaction_number"] == "14290"
    assert formatted["transaction"]["transaction_type"] == "RETURN"
    assert formatted["transaction"]["tender_type"] == "Cash"

    assert formatted["finding_count"] == 2

    messages = [
        finding["message"]
        for finding in formatted["findings"]
    ]

    assert "Trainer's Name: John" in messages
    assert "Training Start Date: 08/25/2026" in messages