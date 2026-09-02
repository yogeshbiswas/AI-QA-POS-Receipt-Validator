from src.agent.graph import build_validation_graph
from src.extractors.pdf_extractor import extract_receipt_pdf
from src.parsers.receipt_parser import parse_receipt_lines
from src.parsers.xml_parser import parse_pos_xml
from src.services.result_formatter import format_validation_result
from pathlib import Path

from src.extractors.image_extractor import extract_receipt_image



def validate_transaction(
    xml_path: str,
    receipt_path: str,
    voided_item_code: str | None = None,
    tester_name: str | None = None,
    receipt_filename: str | None = None,
    xml_filename: str | None = None,
) -> dict:

    # Parse POS XML
    pos_data = parse_pos_xml(xml_path)

    # Extract and parse physical receipt
    receipt_suffix = Path(receipt_path).suffix.lower()

    if receipt_suffix == ".pdf":
        receipt_pdf = extract_receipt_pdf(receipt_path)
        receipt_lines = receipt_pdf.receipt_lines

    elif receipt_suffix in {".jpg", ".jpeg", ".png"}:
        receipt_lines = extract_receipt_image(receipt_path)

    else:
        raise ValueError(
            f"Unsupported receipt file type: {receipt_suffix}"
        )

    receipt_data = parse_receipt_lines(
        receipt_lines
    )

    

    # Run LangGraph validation workflow
    graph = build_validation_graph()

    result = graph.invoke(
        {
            "pos_data": pos_data,
            "receipt_data": receipt_data,
            "voided_item_code": voided_item_code,
        },
        config={
            "run_name": "QA Receipt Validation",
            "tags": ["qa-receipt-validator"],
            "metadata": {
                "receipt_file": receipt_filename or Path(receipt_path).name,
                "xml_file": xml_filename or Path(xml_path).name,
                "tester_name": tester_name or "Not Provided",
                "transaction_number": receipt_data.transaction_number,
                "transaction_type": receipt_data.transaction_type,
            },
        },
    )
    result["receipt_text"] = "\n".join(receipt_lines)

    return result


def validate_and_format_transaction(
    xml_path: str,
    receipt_path: str,
    voided_item_code: str | None = None,
    tester_name: str | None = None,
    receipt_filename: str | None = None,
    xml_filename: str | None = None,
) -> dict:

    raw_result = validate_transaction(
        xml_path=xml_path,
        receipt_path=receipt_path,
        voided_item_code=voided_item_code,
        tester_name=tester_name,
        receipt_filename=receipt_filename,
        xml_filename=xml_filename,
    )

    return format_validation_result(raw_result)