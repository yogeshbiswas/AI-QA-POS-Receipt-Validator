def format_validation_result(result: dict) -> dict:
    pos_data = result["pos_data"]
    receipt_data = result["receipt_data"]

    tender_member_errors = result.get(
        "tender_member_errors",
        [],
    )

    member_status_errors = [
        error
        for error in tender_member_errors
        if error.startswith("Member status mismatch:")
    ]

    tender_errors = [
        error
        for error in tender_member_errors
        if not error.startswith("Member status mismatch:")
    ]


    validation_summary = [
        {
            "validation": (
                "Receipt Arithmetic "
                "(Subtotal + Tax Total = Total)"
            ),
            "status": (
                "FAIL"
                if result.get("receipt_arithmetic_errors")
                else "PASS"
            ),
        },
        {
            "validation": (
                "Receipt vs POS Amounts "
                "(Subtotal, Tax Total, Total)"
            ),
            "status": (
                "FAIL"
                if result.get("financial_comparison_errors")
                else "PASS"
            ),
        },
        {
            "validation": (
                "Receipt vs POS Tender Details "
                "(Payment Type, Last 4, Authorization, "
                "Network, Approval)"
            ),
            "status": (
                "FAIL"
                if tender_errors
                else "PASS"
            ),
        },
        {
            "validation": "Receipt vs POS Member Status",
            "status": (
                "FAIL"
                if member_status_errors
                else "PASS"
            ),
        },
        {
            "validation": (
                "Member Required Data in POSLog "
                "(First Name, Last Name, Email, Phone)"
            ),
            "status": (
                "N/A"
                if pos_data.customer.member_status == "NON_MEMBER"
                else (
                    "FAIL"
                    if result.get("member_errors")
                    else "PASS"
                )
            ),
        },
        
        {
            "validation": (
                "Receipt vs POS Sale/Return Items "
                "(Item Code, Description, Price, Item Count)"
            ),
            "status": (
                "FAIL"
                if result.get("item_comparison_errors")
                else "PASS"
            ),
        },
        {
            "validation": (
                "Receipt Business Date vs "
                "Transaction Timestamp Date"
            ),
            "status": (
                "FAIL"
                if result.get("date_errors")
                else "PASS"
            ),
        },
        {
            "validation": (
                "Physical Receipt Footer "
                "(Barcode Present, Transaction Timestamp Present)"
            ),
            "status": (
                "FAIL"
                if result.get("footer_errors")
                else "PASS"
            ),
        },
        {
            "validation": "Unexpected Duplicate Receipt Content",
            "status": (
                "FAIL"
                if result.get("physical_duplicate_results")
                else "PASS"
            ),
        },
    ]



    findings = []

    # Pair validation
    if result.get("pair_is_match") is False:
        findings.append(
            {
                "category": "Transaction Pair",
                "status": "FAIL",
                "message": (
                    "Receipt and POS log transaction numbers do not match."
                ),
            }
        )

    # Standard error groups
    error_groups = [
        ("Receipt Arithmetic", "receipt_arithmetic_errors"),
        ("Financial Comparison", "financial_comparison_errors"),
        ("Tender / Member Comparison", "tender_member_errors"),
        ("Item Comparison", "item_comparison_errors"),
        ("Member Validation", "member_errors"),
        ("Voided Item Validation", "void_errors"),
        ("Footer Validation", "footer_errors"),
    ]

    for category, key in error_groups:
        for error in result.get(key, []):
            findings.append(
                {
                    "category": category,
                    "status": "FAIL",
                    "message": str(error),
                }
            )

    # Unexpected Duplicate Receipt Content findings
    for duplicate in result.get(
        "physical_duplicate_results",
        [],
    ):
        findings.append(
            {
                "category": "Unexpected Duplicate Receipt Content",
                "status": duplicate.status,
                "message": duplicate.message,
            }
        )

    return {
        "overall_status": result["final_status"],
        "transaction": {
            "store_number": receipt_data.store_number,
            "register_number": receipt_data.register_number,
            "transaction_number": receipt_data.transaction_number,
            "business_date": receipt_data.business_date,
            "transaction_type": receipt_data.transaction_type,
            "tender_type": receipt_data.tender_type,
            "member_status": receipt_data.member_status,
        },
        "finding_count": len(findings),
        "findings": findings,
        "validation_summary": validation_summary,
        "receipt_text": result.get("receipt_text", ""),
    }