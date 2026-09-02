from src.parsers.xml_parser import parse_pos_xml
from src.validators.void_validator import validate_voided_item


def test_void_validator_xml_only():
    pos_data = parse_pos_xml(
        "sample_data/Sale_voidItems_member_T-21704.xml"
    )

    errors = validate_voided_item(
        pos_data,
        "400514786214",
    )

    assert errors == []


def test_void_validator_rejects_non_voided_item():
    pos_data = parse_pos_xml(
        "sample_data/Sale_voidItems_member_T-21704.xml"
    )

    errors = validate_voided_item(
        pos_data,
        "400403463943",
    )

    assert errors != []    