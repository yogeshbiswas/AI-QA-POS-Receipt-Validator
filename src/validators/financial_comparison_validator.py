from src.models.pos import POSData
from src.models.receipt import ReceiptData


def validate_financial_comparison(
    receipt_data: ReceiptData,
    pos_data: POSData,
) -> list[str]:
    errors = []

    if receipt_data.subtotal != pos_data.subtotal:
        errors.append(
            f"Subtotal mismatch: "
            f"receipt={receipt_data.subtotal}, "
            f"POS log={pos_data.subtotal}."
        )

    if receipt_data.tax_total != pos_data.tax_total:
        errors.append(
            f"Tax total mismatch: "
            f"receipt={receipt_data.tax_total}, "
            f"POS log={pos_data.tax_total}."
        )

    if receipt_data.total != pos_data.total:
        errors.append(
            f"Total mismatch: "
            f"receipt={receipt_data.total}, "
            f"POS log={pos_data.total}."
        )

    return errors