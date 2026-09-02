from typing import TypedDict

from src.models.pos import POSData
from src.models.receipt import ReceiptData


class ValidationState(TypedDict, total=False):
    pos_data: POSData
    receipt_data: ReceiptData

    voided_item_code: str | None

    pair_is_match: bool

    receipt_arithmetic_errors: list[str]
    financial_comparison_errors: list[str]
    tender_member_errors: list[str]
    item_comparison_errors: list[str]
    footer_errors: list[str]
    date_errors: list[str]
    

    pos_duplicate_results: list
    physical_duplicate_results: list

    member_errors: list[str]
    void_errors: list[str]

    final_status: str
    summary: str