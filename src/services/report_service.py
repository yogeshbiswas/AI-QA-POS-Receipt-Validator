from datetime import datetime
from io import BytesIO
from reportlab.platypus import HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_validation_report(
    result: dict,
    metadata: dict | None = None,
) -> bytes:
    buffer = BytesIO()
    metadata = metadata or {}

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="QA Receipt Validation Report",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=16,
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = styles["BodyText"]

    def draw_ai_watermark(canvas, doc):
        canvas.saveState()

        canvas.setFont(
            "Helvetica-Bold",
            45,
        )

        canvas.setFillColor(
            colors.HexColor("#F6F8FB")
        )

        canvas.translate(
            letter[0] * 0.58,
            letter[1] * 0.30,
            
        )

        canvas.rotate(0)

        canvas.drawCentredString(
            0,
            -20,
            "AI Receipt Review",
        )

        canvas.restoreState()

    story = []

    # -------------------------------------------------
    # Report title
    # -------------------------------------------------
    story.append(
        Paragraph(
            "QA Receipt Validation Report",
            title_style,
        )
    )

    validation_timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    story.append(
        Paragraph(
            f"Validation Timestamp: {validation_timestamp}",
            normal_style,
        )
    )

    story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # Optional test execution details
    # ---------------------------------------------------------
    execution_rows = []

    if metadata.get("tester_name"):
        execution_rows.append(
            ["Tester Name", metadata["tester_name"]]
        )

    if metadata.get("test_environment"):
        execution_rows.append(
            ["Test Environment", metadata["test_environment"]]
        )

    if metadata.get("build_version"):
        execution_rows.append(
            ["Build / Version", metadata["build_version"]]
        )

    if execution_rows :
        story.append(
            Paragraph(
                "Test Execution Details",
                section_style,
            )
        )

        execution_table = Table(
            execution_rows,
            colWidths=[
                2.0 * inch,
                4.5 * inch,
            ],
            
        )

        execution_table.setStyle(
            TableStyle(
                [
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(execution_table)
        story.append(Spacer(1, 16))

    # -------------------------------------------------
    # Overall status
    # -------------------------------------------------
    overall_status = result["overall_status"]

    if overall_status == "PASS":
        status_color = colors.green
    elif overall_status == "FAIL":
        status_color = colors.red
    else:
        status_color = colors.orange

    status_table = Table(
        [
            [
                "Overall QA Result",
                overall_status,
            ]
        ],
        colWidths=[
            2.4 * inch,
            2.4 * inch,
        ],
    )

    status_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    colors.lightgrey,
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, 0),
                    status_color,
                ),
                (
                    "TEXTCOLOR",
                    (1, 0),
                    (1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, -1),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    story.append(status_table)

    story.append(Spacer(1, 16))

    # -------------------------------------------------
    # Transaction summary
    # -------------------------------------------------
    story.append(
        Paragraph(
            "Transaction Summary",
            section_style,
        )
    )

    transaction = result["transaction"]

    transaction_rows = [
        ["Store", transaction.get("store_number") or "N/A"],
        ["Register", transaction.get("register_number") or "N/A"],
        [
            "Transaction",
            transaction.get("transaction_number") or "N/A",
        ],
        [
            "Business Date",
            transaction.get("business_date") or "N/A",
        ],
        [
            "Transaction Type",
            transaction.get("transaction_type") or "N/A",
        ],
        [
            "Tender",
            transaction.get("tender_type") or "N/A",
        ],
        [
            "Member Status",
            transaction.get("member_status") or "N/A",
        ],
    ]

    transaction_table = Table(
        transaction_rows,
        colWidths=[
            2.0 * inch,
            4.5 * inch,
        ],
        
    )

    transaction_table.setStyle(
        TableStyle(
            [
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(transaction_table)

    story.append(PageBreak())

    # -------------------------------------------------
    # Validation summary
    # -------------------------------------------------
    story.append(
        Paragraph(
            "Validation Summary",
            section_style,
        )
    )

    validation_rows = [
        ["Validation", "Status"]
    ]

    for validation in result.get("validation_summary", []):
        validation_rows.append(
            [
                Paragraph(
                    str(validation.get("validation", "")),
                    normal_style,
                ),
                validation.get("status", ""),
            ]
        )

    validation_table = Table(
        validation_rows,
        colWidths=[
            5.3 * inch,
            1.2 * inch,
        ],
        repeatRows=1,
    )

    validation_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E9ECEF"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (1, 1),
                    (1, -1),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    # Color-code PASS / FAIL / N/A
    for row_index, validation in enumerate(
        result.get("validation_summary", []),
        start=1,
    ):
        status = validation.get("status", "")

        if status == "PASS":
            background_color = colors.HexColor("#DFF2E3")
            text_color = colors.HexColor("#137333")
        elif status == "FAIL":
            background_color = colors.HexColor("#FDE2E2")
            text_color = colors.HexColor("#B3261E")
        else:
            background_color = colors.HexColor("#E8F0FE")
            text_color = colors.HexColor("#315C9B")

        validation_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (1, row_index),
                        (1, row_index),
                        background_color,
                    ),
                    (
                        "TEXTCOLOR",
                        (1, row_index),
                        (1, row_index),
                        text_color,
                    ),
                ]
            )
        )

    story.append(validation_table)
    story.append(Spacer(1, 16))

    # -------------------------------------------------
    # AI receipt review
    # -------------------------------------------------
    story.append(
        Paragraph(
            "AI Receipt Review",
            section_style,
        )
    )

    story.append(
        Paragraph(
            "Independent AI review of the physical receipt. AI findings are included in the overall QA result.",
            normal_style,
        )
    )

    ai_review = result.get("ai_qa_review", {})

    ai_status = ai_review.get(
        "overall_ai_review",
        "NOT_VERIFIABLE",
    )

    story.append(
        Paragraph(
            f"<b>Overall AI Assessment:</b> "
            f"{ai_status.replace('_', ' ')}",
            normal_style,
        )
    )

    story.append(Spacer(1, 8))

    
    tender_review = ai_review.get(
        "tender_discrepancy",
        {},
    )

    calculation_review = ai_review.get(
        "calculation_review",
        {},
    )

    #--------------------------------------------------------------------

    def get_ai_status_style(status):
        if status == "NO_ISSUE_DETECTED":
            return (
                colors.HexColor("#E6F6EC"),
                colors.HexColor("#137333"),
            )

        if status == "ISSUE_DETECTED":
            return (
                colors.HexColor("#FDE8E7"),
                colors.HexColor("#B3261E"),
            )

        if status == "REVIEW_RECOMMENDED":
            return (
                colors.HexColor("#FFF4D6"),
                colors.HexColor("#8A5A00"),
            )

        return (
            colors.HexColor("#E8EEF7"),
            colors.HexColor("#475467"),
        )


    def build_ai_card(title, review):
        status = review.get(
            "status",
            "NOT_VERIFIABLE",
        )

        message = review.get(
            "message",
            "No additional details available.",
        )

        background_color, text_color = get_ai_status_style(
            status
        )

        status_text = status.replace(
            "_",
            " ",
        )
        #----------------------------------------
        card = Table(
        [
            [
                Paragraph(
                    f'<font size="11"><b>{title}</b></font>',
                    normal_style,
                )
            ],
            [
                Paragraph(
                    f'<font color="{text_color.hexval()}" size="9">'
                    f"<b>{status_text}</b>"
                    f"</font>",
                    normal_style,
                )
            ],
            [
                Paragraph(
                    f'<font size="9">{message}</font>',
                    normal_style,
                )
            ],
        ],
        colWidths=[3.05 * inch],
        rowHeights=[
            0.35 * inch,
            0.32 * inch,
            0.95 * inch,
        ],
    )
        #-----------------------------------------------------

     

        card.setStyle(
            TableStyle(
                [                    
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#F8FBFF"),
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.HexColor("#C9D8EA"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                        ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (0, 1),
                        background_color,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        12,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        12,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                ]
            )
        )

        return card


    tender_card = build_ai_card(
        "Tender Discrepancy Check",
        tender_review,
    )

    calculation_card = build_ai_card(
        "Calculation Review",
        calculation_review,
    )

    ai_cards = Table(
        [
            [
                tender_card,
                "",
                calculation_card,
            ]
        ],
        colWidths=[
            3.05 * inch,
            0.40 * inch,
            3.05 * inch,
        ],
        
    )

    ai_cards.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    

    story.append(ai_cards)
    story.append(Spacer(1, 10))

# -------------------------------------------------
# QA findings
# -------------------------------------------------


    # -------------------------------------------------
    # QA findings
    # -------------------------------------------------
    story.append(
        Paragraph(
            "QA Findings",
            section_style,
        )
    )

    findings = result.get("findings", [])

    if not findings:
        story.append(
            Paragraph(
                "No validation defects were found.",
                normal_style,
            )
        )

    else:
        finding_rows = [
            [
                "Status",
                "Category",
                "Finding",
            ]
        ]

        for finding in findings:
            finding_rows.append(
                [
                    finding.get("status", ""),
                    Paragraph(
                        str(
                            finding.get(
                                "category",
                                "",
                            )
                        ),
                        normal_style,
                    ),
                    Paragraph(
                        str(
                            finding.get(
                                "message",
                                "",
                            )
                        ),
                        normal_style,
                    ),
                ]
            )

        findings_table = Table(
            finding_rows,
            colWidths=[
                0.75 * inch,
                1.9 * inch,
                3.85 * inch,
            ],
            repeatRows=1,
        )

        findings_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#E9ECEF"),
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "ALIGN",
                        (0, 1),
                        (0, -1),
                        "CENTER",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(findings_table)

    story.append(Spacer(1, 16))

    # -------------------------------------------------
    # Report footer note
    # -------------------------------------------------
    story.append(
        HRFlowable(
            width="100%",
            thickness=0.6,
            color=colors.HexColor("#D9E2EC"),
            spaceBefore=0,
            spaceAfter=8,
        )
    )   
    footer_style = ParagraphStyle(
            "FooterStyle",
            parent=normal_style,
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#D5DDE7"),
        )

    story.append(
            Paragraph(
                "<b>AI-Assisted QA Receipt Validator</b>",
                footer_style,
            )
        )

    story.append(
            Paragraph(
                "<i>Created by Yogesh Biswas</i>",
                footer_style,
            )
        )

    story.append(Spacer(1, 4))
        

    document.build(
        story,
        onLaterPages=draw_ai_watermark,
    )

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes