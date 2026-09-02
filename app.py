import streamlit as st
import tempfile
from pathlib import Path
from src.services.ai_qa_reviewer import generate_ai_qa_review

from src.services.validation_service import (
    validate_and_format_transaction,
)
from src.services.report_service import generate_validation_report

st.set_page_config(
    page_title="QA Receipt Validator",
    page_icon="🤖",
    layout="wide",
)

# ---------------------------------------------------------
# UI Styling
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1250px;
        }

        .app-header {
            padding: 1.6rem 1.8rem;
            border: 1px solid #d9e2f2;
            border-radius: 16px;
            background: linear-gradient(
                135deg,
                #f8fbff 0%,
                #eef5ff 100%
            );
            margin-bottom: 1.5rem;
        }

        .app-title {
            font-size: 2.25rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .app-subtitle {
            font-size: 1rem;
            color: #556070;
            margin-bottom: 0;
        }

        .ai-badge {
            display: inline-block;
            padding: 0.3rem 0.7rem;
            margin-bottom: 0.8rem;
            border-radius: 999px;
            background: #e8f1ff;
            font-size: 0.8rem;
            font-weight: 600;
        }

        div[data-testid="stFileUploader"] {
            border: 1px solid #dce3ec;
            border-radius: 12px;
            padding: 0.6rem;
        }

        div.stButton > button {
            border-radius: 9px;
            font-weight: 600;
            min-height: 44px;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }
        .ai-check-card {
            border: 1px solid #dfe7f2;
            border-radius: 12px;
            padding: 1rem;
            background: #f8fbff;
            min-height: 150px;
        }

        .ai-check-title {
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }

        .ai-check-status-good {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            background: #e6f6ec;
            color: #137333;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }

        .ai-check-status-issue {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            background: #fde8e7;
            color: #b3261e;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }
        .ai-check-status-review {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            background: #fff4d6;
            color: #8a5a00;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }
        .ai-check-status-neutral {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            background: #e8eef7;
            color: #475467;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }

        .ai-check-message {
            font-size: 0.9rem;
            line-height: 1.5;
            color: #344054;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <div class="ai-badge">AI-ASSISTED QA VALIDATION</div>
        <div class="app-title">QA Receipt Validator</div>
        <p class="app-subtitle">
            Validate physical receipts against POS transaction logs using
            AI-assisted receipt extraction and automated QA validation.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Transaction Inputs")

col_receipt, col_xml = st.columns(2)

with col_receipt:
    receipt_file = st.file_uploader(
        "Receipt PDF or Photo",
        type=["pdf", "jpg", "jpeg", "png"],
        help="Upload the physical or PDF receipt to validate.",
    )

with col_xml:
    xml_file = st.file_uploader(
        "POS Transaction XML",
        type=["xml"],
        help="Upload the matching POS transaction log.",
    )

st.markdown("#### Test Execution Details")

tester_col, environment_col, build_col = st.columns(3)

with tester_col:
    tester_name = st.text_input(
        "Tester Name (optional)",
        placeholder="Enter tester name",
    )

with environment_col:
    test_environment = st.text_input(
        "Test Environment (optional)",
        placeholder="Regression, SIT, UAT",
    )

with build_col:
    build_version = st.text_input(
        "Build / Version (optional)",
        #placeholder="e.g. 26.8.114",
    )


voided_item_code = st.text_input(
    "Voided Item Code (optional)",
    placeholder="Enter item code only when validating a void transaction",
)

st.divider()

validate_button = st.button(
    "Run AI-Assisted Validation",
    type="primary",
)


if validate_button:
    if receipt_file is None:
        st.error("Please upload a receipt PDF or photo.")

    elif xml_file is None:
        st.error("Please upload a POS transaction XML file.")

    else:
        try:
            with st.spinner("Validating transaction..."):

                receipt_suffix = Path(receipt_file.name).suffix
                xml_suffix = Path(xml_file.name).suffix

                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)

                    receipt_path = temp_path / (
                        f"receipt{receipt_suffix}"
                    )

                    xml_path = temp_path / (
                        f"transaction{xml_suffix}"
                    )

                    receipt_path.write_bytes(
                        receipt_file.getvalue()
                    )

                    xml_path.write_bytes(
                        xml_file.getvalue()
                    )

                    result = validate_and_format_transaction(
                        xml_path=str(xml_path),
                        receipt_path=str(receipt_path),
                        voided_item_code=(
                            voided_item_code.strip()
                            if voided_item_code.strip()
                            else None
                        ),
                        tester_name=tester_name.strip() if tester_name.strip() else None,
                        receipt_filename=receipt_file.name,
                        xml_filename=xml_file.name,
                    )
                    with st.spinner("Running independent AI receipt review..."):
                        try:
                            ai_qa_review = generate_ai_qa_review(
                                result.get("receipt_text", "")
                            )
                        except Exception:
                            ai_qa_review = {
                                "overall_ai_review": "REVIEW_NOT_AVAILABLE",
                                "summary": (
                                    "AI receipt review is currently unavailable."
                                ),
                                "tender_discrepancy": {
                                    "status": "NOT_VERIFIABLE",
                                    "message": (
                                        "Tender discrepancy review was not available."
                                    ),
                                },
                                "calculation_review": {
                                    "status": "NOT_VERIFIABLE",
                                    "message": (
                                        "Calculation review was not available."
                                    ),
                                },
                                "additional_observations": [],
                            }

                    result["ai_qa_review"] = ai_qa_review

            st.divider()

            status = result["overall_status"]

            if status == "PASS":
                st.success("Overall Result: PASS")
            else:
                st.error(f"Overall Result: {status}")

            transaction = result["transaction"]

            st.subheader("Transaction Summary")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Store",
                    transaction["store_number"],
                )
                st.metric(
                    "Transaction",
                    transaction["transaction_number"],
                )

            with col2:
                st.metric(
                    "Register",
                    transaction["register_number"],
                )
                st.metric(
                    "Type",
                    transaction["transaction_type"],
                )

            with col3:
                st.metric(
                    "Tender",
                    transaction["tender_type"] or "N/A",
                )
                st.metric(
                    "Member",
                    transaction["member_status"] or "N/A",
                )

            st.write(
                f"**Business Date:** "
                f"{transaction['business_date']}"
            )

            st.subheader("Validation Summary")

            validation_summary = result.get("validation_summary", [])

            for validation in validation_summary:
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.write(validation["validation"])

                with col2:
                    status = validation["status"]

                    if status == "PASS":
                        st.success("PASS")
                    elif status == "FAIL":
                        st.error("FAIL")
                    else:
                        st.info(status)

            #===================================================================================================
            st.subheader("✦ AI Receipt Review")

            st.caption(
                "Independent AI review of the physical receipt. "
                "AI findings are included in the overall QA result."
            )

            ai_review = result.get("ai_qa_review", {})

            ai_status = ai_review.get(
                "overall_ai_review",
                "REVIEW_NOT_AVAILABLE",
            )

            if ai_status == "NO_ISSUE_DETECTED":
                st.markdown(
                    "**Overall AI Assessment:** 🟢 NO ISSUE DETECTED"
                )
            elif ai_status == "ISSUE_DETECTED":
                st.markdown(
                    "**Overall AI Assessment:** 🔴 ISSUE DETECTED"
                )
            else:
                st.markdown(
                    "**Overall AI Assessment:** 🟠 NOT VERIFIABLE"
    )

            summary = ai_review.get("summary")

            if summary:
                st.write(summary)

            st.markdown("##### Independent AI Checks")

            tender_review = ai_review.get(
                "tender_discrepancy",
                {},
            )

            calculation_review = ai_review.get(
                "calculation_review",
                {},
            )
            # -------------------------------------------------
            # Merge AI findings into overall QA result
            # -------------------------------------------------
            if ai_status == "ISSUE_DETECTED":
                result["findings"].append(
                    {
                        "category": "AI Receipt Review",
                        "status": "FAIL",
                        "message": tender_review.get(
                            "message",
                            ai_review.get(
                                "summary",
                                "AI detected an issue on the physical receipt.",
                            ),
                        ),
                    }
                )

                result["finding_count"] = len(result["findings"])
                result["overall_status"] = "FAIL"

            ai_checks = [
                (
                    "Tender Discrepancy Check",
                    tender_review.get(
                        "status",
                        "NOT_VERIFIABLE",
                    ),
                    tender_review.get(
                        "message",
                        "",
                    ),
                ),
                (
                    "Calculation Review",
                    calculation_review.get(
                        "status",
                        "NOT_VERIFIABLE",
                    ),
                    calculation_review.get(
                        "message",
                        "",
                    ),
                ),
            ]

            col1, col2 = st.columns(2)

            for index, (check_name, check_status, message) in enumerate(ai_checks):

                target_col = col1 if index == 0 else col2

                if check_status == "NO_ISSUE_DETECTED":
                    status_class = "ai-check-status-good"
                elif check_status == "ISSUE_DETECTED":
                    status_class = "ai-check-status-issue"
                elif check_status == "REVIEW_RECOMMENDED":
                    status_class = "ai-check-status-review"
                else:
                    status_class = "ai-check-status-neutral"

                with target_col:
                    st.markdown(
                        f"""
                        <div class="ai-check-card">
                            <div class="ai-check-title">{check_name}</div>
                            <div class="{status_class}">
                                {check_status.replace("_", " ")}
                            </div>
                            <div class="ai-check-message">
                                {message}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )     

            additional_observations = ai_review.get(
                "additional_observations",
                [],
            )

            if additional_observations:
                st.markdown("##### Additional AI Observations")

                for observation in additional_observations:
                    observation_status = observation.get(
                        "status",
                        "REVIEW_RECOMMENDED",
                    )

                    message = (
                        f"**{observation.get('category', 'Observation')}** — "
                        f"{observation.get('message', '')}"
                    )

                    if observation_status == "ISSUE_DETECTED":
                        st.error(message)
                    else:
                        st.warning(message)

                # Merge additional AI observations into QA findings
                for observation in additional_observations:
                    observation_status = observation.get(
                        "status",
                        "REVIEW_RECOMMENDED",
                    )

                    if observation_status == "ISSUE_DETECTED":
                        result["findings"].append(
                            {
                                "category": "AI Receipt Review",
                                "status": "FAIL",
                                "message": (
                                    f"{observation.get('category', 'AI Observation')}: "
                                    f"{observation.get('message', '')}"
                                ),
                            }
                        )

                        result["overall_status"] = "FAIL"

                    elif observation_status == "REVIEW_RECOMMENDED":
                        result["findings"].append(
                            {
                                "category": "AI Receipt Review",
                                "status": "WARNING",
                                "message": (
                                    f"{observation.get('category', 'AI Observation')}: "
                                    f"{observation.get('message', '')}"
                                ),
                            }
                        )

                        if result["overall_status"] == "PASS":
                            result["overall_status"] = "WARNING"

                result["finding_count"] = len(result["findings"])        

            #=========================================================================================                 

            st.subheader("QA Findings")

            if result["finding_count"] == 0:
                st.success(
                    "No validation defects were found."
                )

            else:
                st.write(
                    f"{result['finding_count']} finding(s) detected."
                )

                for finding in result["findings"]:
                    st.error(
                        f"**{finding['category']}** — "
                        f"{finding['message']}"
                    )

            report_metadata = {
                "tester_name": tester_name.strip() or None,
                "test_environment": test_environment.strip() or None,
                "build_version": build_version.strip() or None,
            }        
            pdf_report = generate_validation_report(result,metadata=report_metadata,)

            transaction_number = (
                result["transaction"]["transaction_number"]
                or "unknown"
            )

            st.download_button(
                label="Download PDF Report",
                data=pdf_report,
                file_name=f"qa_receipt_validation_{transaction_number}.pdf",
                mime="application/pdf",
            )        

        except Exception as exc:
            st.error(
                f"Validation could not be completed: {exc}"
            )