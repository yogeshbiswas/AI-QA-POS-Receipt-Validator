from src.extractors.pdf_extractor import extract_receipt_pdf
from src.parsers.receipt_parser import parse_receipt_lines
from src.validators.footer_validator import validate_footer_presence


def test_footer_presence_14289():
    receipt_pdf = extract_receipt_pdf(
        "sample_data/receipt_14289_debit_nonmember.pdf"
    )

    receipt_data = parse_receipt_lines(
        receipt_pdf.receipt_lines
    )

    errors = validate_footer_presence(receipt_data)

    assert errors == []

def test_footer_missing_barcode_fails():
    receipt_pdf = extract_receipt_pdf(
        "sample_data/receipt_14289_debit_nonmember.pdf"
    )

    receipt_data = parse_receipt_lines(
        receipt_pdf.receipt_lines
    )

    # Simulate a receipt where the barcode was not printed.
    receipt_data.receipt_lines = [
        line
        for line in receipt_data.receipt_lines
        if not line.strip().lower().startswith("barcode")
        and not line.strip().lower().startswith("data:")
    ]

    errors = validate_footer_presence(receipt_data)

    assert "Receipt barcode is missing." in errors    