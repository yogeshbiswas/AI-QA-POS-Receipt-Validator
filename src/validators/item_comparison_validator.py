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

        if item_key:
            grouped_pos_items[item_key].append(pos_item)

    # -------------------------------------------------
    # Aggregate receipt items by item code
    # -------------------------------------------------
    grouped_receipt_items = defaultdict(list)

    for receipt_item in receipt_data.items:
        if receipt_item.item_code:
            grouped_receipt_items[
                receipt_item.item_code
            ].append(receipt_item)

    # -------------------------------------------------
    # Compare each unique POS item against receipt
    # -------------------------------------------------
    for item_key, pos_items in grouped_pos_items.items():

        first_pos_item = pos_items[0]

        # Try POS item ID first, then POS identity
        receipt_items = grouped_receipt_items.get(
            first_pos_item.pos_item_id
        )

        if not receipt_items:
            receipt_items = grouped_receipt_items.get(
                first_pos_item.item_id
            )

        if not receipt_items:
            errors.append(
                f"POS item {first_pos_item.item_id} "
                f"({first_pos_item.description}) "
                f"is missing from receipt."
            )
            continue

        # -------------------------------------------------
        # Aggregate receipt quantity
        # -------------------------------------------------
        receipt_quantity = sum(
            item.quantity or 1
            for item in receipt_items
        )

        # -------------------------------------------------
        # Aggregate POS quantity
        # -------------------------------------------------
        pos_quantity = sum(
            item.quantity
            for item in pos_items
        )

        if receipt_quantity != pos_quantity:
            errors.append(
                f"Item quantity mismatch for "
                f"{first_pos_item.item_id}: "
                f"receipt={receipt_quantity}, "
                f"POS log={pos_quantity}."
            )

        # -------------------------------------------------
        # Description comparison
        # -------------------------------------------------
        receipt_descriptions = {
            item.description.strip()
            for item in receipt_items
            if item.description
        }

        if (
            receipt_descriptions
            and first_pos_item.description
            not in receipt_descriptions
        ):
            errors.append(
                f"Item description mismatch for "
                f"{first_pos_item.item_id}: "
                f"receipt={list(receipt_descriptions)}, "
                f"POS log='{first_pos_item.description}'."
            )

        # -------------------------------------------------
        # Aggregate POS extended amount
        # -------------------------------------------------
        pos_extended_total = sum(
            item.unit_price * item.quantity
            for item in pos_items
        )

        # -------------------------------------------------
        # Aggregate receipt amount
        # -------------------------------------------------
        receipt_total = sum(
            item.price
            for item in receipt_items
            if item.price is not None
        )

        # -------------------------------------------------
        # Return receipts print negative amounts,
        # while POS unit prices remain positive.
        # -------------------------------------------------
        if receipt_data.transaction_type == "RETURN":
            receipt_total = abs(receipt_total)
            pos_extended_total = abs(pos_extended_total)

        # -------------------------------------------------
        # Compare aggregated item amount
        # -------------------------------------------------
        if round(receipt_total, 2) != round(
            pos_extended_total,
            2,
        ):
            errors.append(
                f"Item price mismatch for "
                f"{first_pos_item.item_id}: "
                f"receipt={receipt_total:.2f}, "
                f"POS log={pos_extended_total:.2f}."
            )

    return errors