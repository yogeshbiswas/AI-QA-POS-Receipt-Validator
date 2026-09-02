from src.services.validation_service import (
    validate_transaction,
    validate_and_format_transaction,
)


def test_validation_service_14289_passes():
    result = validate_transaction(
        xml_path="sample_data/transaction_14289_debit_nonmember.xml",
        receipt_path="sample_data/receipt_14289_debit_nonmember.pdf",
        voided_item_code=None,
    )

    assert result["pair_is_match"] is True
    assert result["final_status"] == "PASS"

    assert result["receipt_arithmetic_errors"] == []
    assert result["financial_comparison_errors"] == []
    assert result["tender_member_errors"] == []
    assert result["item_comparison_errors"] == []
    assert result["member_errors"] == []
    assert result["void_errors"] == []
    assert result["footer_errors"] == []
    assert result["physical_duplicate_results"] == []


def test_validation_service_14290_fails_for_duplicates():
    result = validate_transaction(
        xml_path="sample_data/transaction_14290_return_nonmember.xml",
        receipt_path="sample_data/receipt_14290_return_nonmember.pdf",
        voided_item_code=None,
    )

    # Receipt and XML are the correct transaction pair.
    assert result["pair_is_match"] is True

    # Core comparisons should still be clean.
    assert result["receipt_arithmetic_errors"] == []
    assert result["financial_comparison_errors"] == []
    assert result["tender_member_errors"] == []
    assert result["item_comparison_errors"] == []
    assert result["member_errors"] == []
    assert result["void_errors"] == []
    assert result["footer_errors"] == []

    # Physical receipt contains the known duplicate defect.
    assert len(result["physical_duplicate_results"]) == 2

    # Therefore the overall QA result must fail.
    assert result["final_status"] == "FAIL"


def test_validate_and_format_transaction():
    result = validate_and_format_transaction(
        xml_path="sample_data/transaction_14289_debit_nonmember.xml",
        receipt_path="sample_data/receipt_14289_debit_nonmember.pdf",
        voided_item_code=None,
    )

    assert result["overall_status"] == "PASS"
    assert result["transaction"]["transaction_number"] == "14289"
    assert result["transaction"]["transaction_type"] == "SALE"
    assert result["finding_count"] == 0
    assert result["findings"] == []
