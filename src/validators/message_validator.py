from collections import Counter
import re

from src.models.validation import ValidationResult


def validate_duplicate_receipt_lines(
    receipt_lines: list[str],
) -> list[ValidationResult]:

    ignored_lines = {
        "SALE",
        "RETURN",
        "---------- End Receipt ----------",
    }

    def is_ignored_line(line: str) -> bool:
        stripped = line.strip()

        # Known non-content lines
        if stripped in ignored_lines:
            return True

        # Formatting separators:
        # ------
        # ******
        # ______
        if re.fullmatch(r"[-_* =]{10,}", stripped):
            return True

        # Full timestamp
        if re.fullmatch(
            r"\d{1,2}/\s*\d{1,2}/\d{4}\s+"
            r"\d{1,2}:\d{2}:\d{2}\s+[AP]M",
            stripped,
        ):
            return True

        # Short date such as 8/11/26
        if re.fullmatch(
            r"\d{1,2}/\d{1,2}/\d{2}",
            stripped,
        ):
            return True

        # Item metadata / UPC / classification code
        # Example:
        # 840243125319 StCiCo
        # 8211051 N
        if re.fullmatch(
            r"\d{6,14}(?:\s+\S+)*",
            stripped,
        ):
            return True

        # Quantity lines
        # QTY: 2
        if re.fullmatch(
            r"QTY:\s*\d+(?:\s+.*)?",
            stripped,
            re.IGNORECASE,
        ):
            return True

        # Prescription / item reference metadata
        # Rx Number: 2154
        if re.fullmatch(
            r"Rx Number:\s*\S+",
            stripped,
            re.IGNORECASE,
        ):
            return True

        # Item-level return amount
        if re.fullmatch(
            r"Return Amount\s+\$-?[\d.]+",
            stripped,
            re.IGNORECASE,
        ):
            return True

        # Item-level promotion / redemption text
        if re.match(
            r"^Points Redemption\s+\$?[\d.]+",
            stripped,
            re.IGNORECASE,
        ):
            return True

        return False

    meaningful_lines = [
        line.strip()
        for line in receipt_lines
        if line.strip()
        and not is_ignored_line(line)
    ]

    line_counts = Counter(meaningful_lines)

    results = []

    for line, count in line_counts.items():
        if count > 1:
            results.append(
                ValidationResult(
                    rule_name="Duplicate Receipt Content",
                    status="FAIL",
                    message=line,
                    expected="1 occurrence",
                    actual=f"{count} occurrences",
                )
            )

    return results