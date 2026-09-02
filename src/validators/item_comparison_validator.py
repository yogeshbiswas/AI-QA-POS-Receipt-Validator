from src.models.pos import POSData
from src.models.receipt import ReceiptData

from collections import defaultdict

from src.models.pos import POSData
from src.models.receipt import ReceiptData


def validate_item_comparison(
    receipt_data: ReceiptData,
    pos_data: POSData,
) -> list[str]:

    errors = []

    active_pos_items = [
        item
        for item in pos_data.items
        if not item.is_voided
    ]

    # -------------------------------------------------
    # Compare printed transaction item count
    # -------------------------------------------------
    if receipt_data.transaction_item_count is not None:
        total_pos_quantity = sum(
            item.quantity
            for item in active_pos_items
        )

        if receipt_data.transaction_item_count != int(total_pos_quantity):
            errors.append(
                f"Sale item count mismatch: "
                f"receipt={receipt_data.transaction_item_count}, "
                f"POS log={int(total_pos_quantity)}."
            )

    # -------------------------------------------------
    # Aggregate POS items by item identity
    # -------------------------------------------------
    grouped_pos_items = defaultdict(list)

    for pos_item in active_pos_items:
        item_key = pos_item.pos_item_id or pos_item.item_id
        grouped_pos_items[item_key].append(pos_item)

    # -------------------------------------------------
    # Compare each unique POS item against receipt
    # -------------------------------------------------
    for item_key, pos_items in grouped_pos_items.items():

        first_pos_item = pos_items[0]

        matching_receipt_item = next(
            (
                receipt_item
                for receipt_item in receipt_data.items
                if receipt_item.item_code
                in (
                    first_pos_item.item_id,
                    first_pos_item.pos_item_id,
                )
            ),
            None,
        )

        if matching_receipt_item is None:
            errors.append(
                f"POS item {first_pos_item.item_id} "
                f"({first_pos_item.description}) "
                f"is missing from receipt."
            )
            continue

        # -------------------------------------------------
        # Description comparison
        # -------------------------------------------------
        if (
            matching_receipt_item.description
            != first_pos_item.description
        ):
            errors.append(
                f"Item description mismatch for "
                f"{first_pos_item.item_id}: "
                f"receipt='{matching_receipt_item.description}', "
                f"POS log='{first_pos_item.description}'."
            )

        # -------------------------------------------------
        # Aggregate POS extended amount
        # -------------------------------------------------
        pos_extended_total = sum(
            item.unit_price * item.quantity
            for item in pos_items
        )

        receipt_price = matching_receipt_item.price

        if receipt_price is not None:

            # Return receipts print negative amounts,
            # while POS unit prices remain positive.
            if receipt_data.transaction_type == "RETURN":
                receipt_price = abs(receipt_price)
                pos_extended_total = abs(pos_extended_total)

            if round(receipt_price, 2) != round(
                pos_extended_total,
                2,
            ):
                errors.append(
                    f"Item price mismatch for "
                    f"{first_pos_item.item_id}: "
                    f"receipt={matching_receipt_item.price:.2f}, "
                    f"POS log={pos_extended_total:.2f}."
                )

    return errors