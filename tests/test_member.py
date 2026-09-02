from src.parsers.xml_parser import parse_pos_xml
from src.validators.member_validator import validate_member_data


def test_member_validator_valid_member():
    pos_data = parse_pos_xml(
        "sample_data/Sale_voidItems_member_T-21704.xml"
    )

    errors = validate_member_data(pos_data)

    assert errors == []


def test_member_validator_missing_required_data():
    pos_data = parse_pos_xml(
        "sample_data/Sale_voidItems_member_T-21704.xml"
    )

    # Simulate a defect: member email is missing
    pos_data.customer.email = None

    errors = validate_member_data(pos_data)

    assert errors != []    