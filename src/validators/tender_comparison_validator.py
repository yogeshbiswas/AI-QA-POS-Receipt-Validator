from src.models.pos import POSData
from src.models.receipt import ReceiptData


def validate_tender_member_comparison(
    receipt_data: ReceiptData,
    pos_data: POSData,
) -> list[str]:
    errors = []

    if receipt_data.member_status != pos_data.customer.member_status:
        errors.append(
            f"Member status mismatch: "
            f"receipt={receipt_data.member_status}, "
            f"POS log={pos_data.customer.member_status}."
        )

    pos_tender_type = (
        pos_data.tender.tender_description
        or pos_data.tender.tender_type
    )

    if receipt_data.tender_type != pos_tender_type:
        errors.append(
            f"Tender type mismatch: "
            f"receipt={receipt_data.tender_type}, "
            f"POS log={pos_tender_type}."
        )

    if receipt_data.tender_type in ("Debit", "Credit"):
        if not receipt_data.last4:
            errors.append("Card last 4 is missing from receipt.")
        elif receipt_data.last4 != pos_data.tender.last4:
            errors.append(
                f"Card last4 mismatch: "
                f"receipt={receipt_data.last4}, "
                f"POS log={pos_data.tender.last4}."
            )

        if not receipt_data.authorization_code:
            errors.append("Authorization code is missing from receipt.")
        elif receipt_data.authorization_code != pos_data.tender.authorization_code:
            errors.append(
                f"Authorization code mismatch: "
                f"receipt={receipt_data.authorization_code}, "
                f"POS log={pos_data.tender.authorization_code}."
            )

        if not receipt_data.network_name:
            errors.append("Card network is missing from receipt.")
        elif receipt_data.network_name != pos_data.tender.network_name:
            errors.append(
                f"Network mismatch: "
                f"receipt={receipt_data.network_name}, "
                f"POS log={pos_data.tender.network_name}."
            )

        if not receipt_data.approval_status:
            errors.append("Approval status is missing from receipt.")
        elif receipt_data.approval_status != pos_data.tender.approval_status:
            errors.append(
                f"Approval status mismatch: "
                f"receipt={receipt_data.approval_status}, "
                f"POS log={pos_data.tender.approval_status}."
            )

    return errors