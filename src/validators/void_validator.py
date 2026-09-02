from src.models.pos import POSData


from src.models.pos import POSData


def validate_voided_item(
    pos_data: POSData,
    expected_item_code: str | None,
) -> list[str]:
    errors = []

    if not expected_item_code:
        return errors

    matching_voided_items = [
        item
        for item in pos_data.items
        if item.is_voided
        and expected_item_code in (item.item_id, item.pos_item_id)
    ]

    if not matching_voided_items:
        errors.append(
            f"Expected voided item {expected_item_code} "
            "was not found as voided in POS log."
        )

    return errors