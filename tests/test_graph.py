from src.agent.graph import build_validation_graph

from src.parsers.xml_parser import parse_pos_xml
from src.extractors.pdf_extractor import extract_receipt_pdf
from src.parsers.receipt_parser import parse_receipt_lines


def load_test_data(xml_path: str, pdf_path: str):
    pos_data = parse_pos_xml(xml_path)

    receipt_pdf = extract_receipt_pdf(pdf_path)
    receipt_data = parse_receipt_lines(
        receipt_pdf.receipt_lines
    )

    return pos_data, receipt_data


def test_graph_14289_sale_passes():
    pos_data, receipt_data = load_test_data(
        "sample_data/transaction_14289_debit_nonmember.xml",
        "sample_data/receipt_14289_debit_nonmember.pdf",
    )

    graph = build_validation_graph()

    result = graph.invoke(
        {
            "pos_data": pos_data,
            "receipt_data": receipt_data,
            "voided_item_code": None,
        }
    )

    assert result["pair_is_match"] is True
    assert result["final_status"] == "PASS"

    assert result["receipt_arithmetic_errors"] == []
    assert result["financial_comparison_errors"] == []
    assert result["tender_member_errors"] == []
    assert result["item_comparison_errors"] == []
    assert result["physical_duplicate_results"] == []


def test_graph_14290_return_fails_for_duplicates():
    pos_data, receipt_data = load_test_data(
        "sample_data/transaction_14290_return_nonmember.xml",
        "sample_data/receipt_14290_return_nonmember.pdf",
    )

    graph = build_validation_graph()

    result = graph.invoke(
        {
            "pos_data": pos_data,
            "receipt_data": receipt_data,
            "voided_item_code": None,
        }
    )

    assert result["pair_is_match"] is True

    assert result["receipt_arithmetic_errors"] == []
    assert result["financial_comparison_errors"] == []
    assert result["tender_member_errors"] == []
    assert result["item_comparison_errors"] == []

    assert len(result["physical_duplicate_results"]) == 2
    assert result["final_status"] == "FAIL"


def test_graph_mismatched_transaction_stops():
    pos_data = parse_pos_xml(
        "sample_data/transaction_14290_return_nonmember.xml"
    )

    receipt_pdf = extract_receipt_pdf(
        "sample_data/receipt_14289_debit_nonmember.pdf"
    )

    receipt_data = parse_receipt_lines(
        receipt_pdf.receipt_lines
    )

    graph = build_validation_graph()

    result = graph.invoke(
        {
            "pos_data": pos_data,
            "receipt_data": receipt_data,
            "voided_item_code": None,
        }
    )

    assert result["pair_is_match"] is False
    assert result["final_status"] == "FAIL"

    # Core validation node should have been skipped.
    assert "receipt_arithmetic_errors" not in result
    assert "financial_comparison_errors" not in result
    assert "tender_member_errors" not in result
    assert "item_comparison_errors" not in result

def test_graph_no_void_code_skips_void_validation():
    pos_data, receipt_data = load_test_data(
        "sample_data/transaction_14289_debit_nonmember.xml",
        "sample_data/receipt_14289_debit_nonmember.pdf",
    )

    graph = build_validation_graph()

    result = graph.invoke(
        {
            "pos_data": pos_data,
            "receipt_data": receipt_data,
            "voided_item_code": None,
        }
    )

    assert result["void_errors"] == []
    assert result["final_status"] == "PASS"


from src.agent.nodes import final_decision_node


def test_final_decision_fails_for_void_error():
    state = {
        "pair_is_match": True,
        "receipt_arithmetic_errors": [],
        "financial_comparison_errors": [],
        "tender_member_errors": [],
        "item_comparison_errors": [],
        "physical_duplicate_results": [],
        "member_errors": [],
        "void_errors": [
            "Provided item code was not voided."
        ],
    }

    result = final_decision_node(state)

    assert result["final_status"] == "FAIL"

def test_final_decision_fails_for_footer_error():
    state = {
        "pair_is_match": True,
        "receipt_arithmetic_errors": [],
        "financial_comparison_errors": [],
        "tender_member_errors": [],
        "item_comparison_errors": [],
        "physical_duplicate_results": [],
        "member_errors": [],
        "void_errors": [],
        "footer_errors": [
            "Receipt barcode is missing."
        ],
    }

    result = final_decision_node(state)

    assert result["final_status"] == "FAIL"

def test_final_decision_fails_for_date_error():
    state = {
        "pair_is_match": True,
        "receipt_arithmetic_errors": [],
        "financial_comparison_errors": [],
        "tender_member_errors": [],
        "item_comparison_errors": [],
        "physical_duplicate_results": [],
        "member_errors": [],
        "void_errors": [],
        "footer_errors": [],
        "date_errors": [
            "Receipt business date does not match transaction timestamp date."
        ],
    }

    result = final_decision_node(state)

    assert result["final_status"] == "FAIL"    