from src.models.pos import POSData


def validate_member_data(pos_data: POSData) -> list[str]:
    errors = []

    if (
        pos_data.transaction_type == "SALE"
        and pos_data.customer.member_status == "MEMBER"
    ):
        if not pos_data.customer.first_name:
            errors.append("Member first name is missing from POS log.")

        if not pos_data.customer.last_name:
            errors.append("Member last name is missing from POS log.")

        if not pos_data.customer.email:
            errors.append("Member email is missing from POS log.")

        if not pos_data.customer.phone:
            errors.append("Member phone is missing from POS log.")

    return errors