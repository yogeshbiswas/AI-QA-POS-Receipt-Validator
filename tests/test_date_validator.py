from src.extractors.pdf_extractor import extract_receipt_pdf
from src.parsers.receipt_parser import parse_receipt_lines
from src.validators.date_validator import validate_receipt_business_date


def test_receipt_business_date_matches_timestamp():
    receipt_pdf = extract_receipt_pdf(
        "sample_data/receipt_14289_debit_nonmember.pdf"
    )

    receipt_data = parse_receipt_lines(
        receipt_pdf.receipt_lines
    )

    errors = validate_receipt_business_date(
        receipt_data
    )

    assert errors == []


def test_receipt_business_date_mismatch_fails():
    receipt_pdf = extract_receipt_pdf(
        "sample_data/receipt_14289_debit_nonmember.pdf"
    )

    receipt_data = parse_receipt_lines(
        receipt_pdf.receipt_lines
    )

    # Simulate a defect on the physical receipt.
    receipt_data.transaction_timestamp = (
        "08/12/2026 2:01:56 PM"
    )

    errors = validate_receipt_business_date(
        receipt_data
    )

    assert errors != []    