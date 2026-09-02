from src.agent.state import ValidationState
from src.validators.pair_validator import validate_transaction_pair
from src.validators.receipt_financial_validator import (
    validate_receipt_arithmetic,
)
from src.validators.financial_comparison_validator import (
    validate_financial_comparison,
)
from src.validators.tender_comparison_validator import (
    validate_tender_member_comparison,
)
from src.validators.item_comparison_validator import (
    validate_item_comparison,
)
from src.validators.message_validator import (
    validate_duplicate_receipt_lines,
)
from src.validators.member_validator import validate_member_data
from src.validators.void_validator import validate_voided_item
from src.validators.footer_validator import validate_footer_presence
from src.validators.date_validator import validate_receipt_business_date


def validate_pair_node(state: ValidationState) -> ValidationState:
    pos_data = state["pos_data"]
    receipt_data = state["receipt_data"]

    pair_result = validate_transaction_pair(
        receipt_store=receipt_data.store_number,
        receipt_register=receipt_data.register_number,
        receipt_transaction=receipt_data.transaction_number,
        receipt_date=receipt_data.business_date,
        pos_store=pos_data.store_number,
        pos_register=pos_data.register_number,
        pos_transaction=pos_data.transaction_number,
        pos_date=pos_data.business_date,
    )

    return {
        **state,
        "pair_is_match": pair_result.is_match,
    }


def run_core_validations_node(
    state: ValidationState,
) -> ValidationState:
    pos_data = state["pos_data"]
    receipt_data = state["receipt_data"]
    date_errors = validate_receipt_business_date(receipt_data)
    member_errors = validate_member_data(pos_data)

    void_errors = []

    voided_item_code = state.get("voided_item_code")

    if voided_item_code:
        void_errors = validate_voided_item(
            pos_data,
            voided_item_code,
        )

    receipt_arithmetic_errors = validate_receipt_arithmetic(
        receipt_data
    )

    financial_comparison_errors = validate_financial_comparison(
        receipt_data,
        pos_data,
    )

    tender_member_errors = validate_tender_member_comparison(
        receipt_data,
        pos_data,
    )

    item_comparison_errors = validate_item_comparison(
        receipt_data,
        pos_data,
    )

    physical_duplicate_results = validate_duplicate_receipt_lines(
        receipt_data.receipt_lines
    )
    footer_errors = validate_footer_presence(receipt_data)

    return {
        **state,
        "receipt_arithmetic_errors": receipt_arithmetic_errors,
        "financial_comparison_errors": financial_comparison_errors,
        "tender_member_errors": tender_member_errors,
        "item_comparison_errors": item_comparison_errors,
        "physical_duplicate_results": physical_duplicate_results,
        "member_errors": member_errors,\
        "void_errors": void_errors,
        "footer_errors": footer_errors,
        "date_errors": date_errors,
    }


def final_decision_node(
    state: ValidationState,
) -> ValidationState:

    has_errors = any(
        [
            state.get("pair_is_match") is False,
            state.get("receipt_arithmetic_errors"),
            state.get("financial_comparison_errors"),
            state.get("tender_member_errors"),
            state.get("item_comparison_errors"),
            state.get("physical_duplicate_results"),
            state.get("member_errors"),
            state.get("void_errors"),
            state.get("footer_errors"),
            state.get("date_errors"),
        ]
    )

    final_status = "FAIL" if has_errors else "PASS"

    return {
        **state,
        "final_status": final_status,
    }

def pair_route(state: ValidationState) -> str:
    if state.get("pair_is_match"):
        return "continue"

    return "stop"