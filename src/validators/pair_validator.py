from src.models.validation import PairValidationResult


def validate_transaction_pair(
    receipt_store: str,
    receipt_register: str,
    receipt_transaction: str,
    receipt_date: str,
    pos_store: str,
    pos_register: str,
    pos_transaction: str,
    pos_date: str,
) -> PairValidationResult:

    is_match = receipt_transaction == pos_transaction

    if is_match:
        return PairValidationResult(
            is_match=True,
            message="Receipt and POS log belong to the same transaction.",
        )

    return PairValidationResult(
        is_match=False,
        message=(
            "Receipt and POS log do not appear to belong to the same transaction. "
            "Please upload the matching receipt and POS XML file."
        ),
    )