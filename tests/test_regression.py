from src.parsers.xml_parser import parse_pos_xml
from src.extractors.pdf_extractor import extract_receipt_pdf
from src.parsers.receipt_parser import parse_receipt_lines

from src.validators.receipt_financial_validator import validate_receipt_arithmetic
from src.validators.financial_comparison_validator import validate_financial_comparison
from src.validators.tender_comparison_validator import validate_tender_member_comparison
from src.validators.item_comparison_validator import validate_item_comparison
from src.validators.pair_validator import validate_transaction_pair
from src.validators.message_validator import validate_duplicate_receipt_lines


def test_14289_sale_regression():
    pos_data = parse_pos_xml(
        "sample_data/transaction_14289_debit_nonmember.xml"
    )

    receipt_pdf = extract_receipt_pdf(
        "sample_data/receipt_14289_debit_nonmember.pdf"
    )

    receipt_data = parse_receipt_lines(
        receipt_pdf.receipt_lines
    )

    assert validate_receipt_arithmetic(receipt_data) == []
    assert validate_financial_comparison(receipt_data, pos_data) == []
    assert validate_tender_member_comparison(receipt_data, pos_data) == []
    assert validate_item_comparison(receipt_data, pos_data) == []

    pair_result = validate_transaction_pair(
        receipt_store=receipt_data.store_number,
        receipt_register=receipt_data.register_number,
        receipt_transaction=receipt_data.transaction_number,
        receipt_date=receipt_data.business_date,
        pos_store=pos_data.store_number,
        pos_register=pos_data.register_number,
        pos_transaction=pos_data.transaction_number,
        pos_date=pos_data.business_date,
    )

    assert pair_result.is_match is True

def test_14290_return_regression():
    pos_data = parse_pos_xml(
        "sample_data/transaction_14290_return_nonmember.xml"
    )

    receipt_pdf = extract_receipt_pdf(
        "sample_data/receipt_14290_return_nonmember.pdf"
    )

    receipt_data = parse_receipt_lines(
        receipt_pdf.receipt_lines
    )

    # Core RETURN validations should pass
    assert validate_receipt_arithmetic(receipt_data) == []
    assert validate_financial_comparison(receipt_data, pos_data) == []
    assert validate_tender_member_comparison(receipt_data, pos_data) == []
    assert validate_item_comparison(receipt_data, pos_data) == []

    # Receipt/XML transaction numbers should match
    pair_result = validate_transaction_pair(
        receipt_store=receipt_data.store_number,
        receipt_register=receipt_data.register_number,
        receipt_transaction=receipt_data.transaction_number,
        receipt_date=receipt_data.business_date,
        pos_store=pos_data.store_number,
        pos_register=pos_data.register_number,
        pos_transaction=pos_data.transaction_number,
        pos_date=pos_data.business_date,
    )

    assert pair_result.is_match is True

    # 14290 intentionally contains the known duplicate defect
    duplicate_results = validate_duplicate_receipt_lines(pos_data.receipt_lines)

    duplicate_messages = [
        result.message
        for result in duplicate_results
    ]

    assert "Trainer's Name: John" in duplicate_messages
    assert "Training Start Date: 08/25/2026" in duplicate_messages
