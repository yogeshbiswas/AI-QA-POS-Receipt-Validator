from src.models.pos import POSData


def validate_pos_arithmetic(pos_data: POSData) -> bool:
    calculated_total = pos_data.subtotal + pos_data.tax_total

    return round(calculated_total, 2) == round(pos_data.total, 2)