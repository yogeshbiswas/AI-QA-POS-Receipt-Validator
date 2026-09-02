import re

from src.models.receipt import ReceiptData


def validate_footer_presence(
    receipt_data: ReceiptData,
) -> list[str]:

    errors = []

    lines = [
        line.strip()
        for line in receipt_data.receipt_lines
        if line.strip()
    ]

    # Barcode only needs to be printed.
    has_barcode = any(
        line.lower().startswith("barcode")
        or line.lower().startswith("data:")
        or (
            line.isdigit()
            and len(line) >= 20
        )
        for line in lines
    )

    if not has_barcode:
        errors.append(
            "Receipt barcode is missing."
        )

    # Receipt transaction timestamp only needs to be printed.
    has_timestamp = any(
        re.fullmatch(
            r"\d{1,2}/\d{1,2}/\d{4}\s+"
            r"\d{1,2}:\d{2}:\d{2}\s+[AP]M",
            line,
        )
        for line in lines
    )

    if not has_timestamp:
        errors.append(
            "Receipt timestamp is missing."
        )

    

    return errors