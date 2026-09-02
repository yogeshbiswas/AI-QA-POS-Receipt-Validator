from src.models.receipt import ReceiptData


def validate_receipt_arithmetic(receipt_data: ReceiptData) -> list[str]:
    errors = []

    if receipt_data.tax_total is not None:
        calculated_tax_total = round(
            sum(tax.amount for tax in receipt_data.taxes),
            2,
        )

        if calculated_tax_total != round(receipt_data.tax_total, 2):
            errors.append(
                f"Receipt tax total mismatch: "
                f"calculated {calculated_tax_total:.2f}, "
                f"printed {receipt_data.tax_total:.2f}."
            )

    if (
        receipt_data.subtotal is not None
        and receipt_data.tax_total is not None
        and receipt_data.total is not None
    ):
        calculated_total = round(
            receipt_data.subtotal + receipt_data.tax_total,
            2,
        )

        if calculated_total != round(receipt_data.total, 2):
            errors.append(
                f"Receipt total mismatch: "
                f"calculated {calculated_total:.2f}, "
                f"printed {receipt_data.total:.2f}."
            )

    return errors