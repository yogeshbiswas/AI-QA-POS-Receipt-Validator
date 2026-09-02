from datetime import datetime

from src.models.receipt import ReceiptData


def validate_receipt_business_date(
    receipt_data: ReceiptData,
) -> list[str]:

    errors = []

    if not receipt_data.business_date:
        errors.append(
            "Receipt business date is missing."
        )
        return errors

    if not receipt_data.transaction_timestamp:
        errors.append(
            "Receipt transaction timestamp is missing."
        )
        return errors

    business_date = datetime.strptime(
        receipt_data.business_date,
        "%Y-%m-%d",
    ).date()

    timestamp_date = datetime.strptime(
        receipt_data.transaction_timestamp,
        "%m/%d/%Y %I:%M:%S %p",
    ).date()

    if business_date != timestamp_date:
        errors.append(
            "Receipt business date does not match "
            "transaction timestamp date."
        )

    return errors