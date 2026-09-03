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

        # Any separator made only of dashes/spaces
        if re.fullmatch(r"[- ]{10,}", stripped):
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

        # Item metadata line.
        # Examples:
        # 840243125319  StCiCo
        # 8211051       N
        # Future receipts may contain other item
        # classification/tax codes. We ignore the
        # entire metadata line rather than specific values.
        if re.fullmatch(
            r"\d{6,14}(?:\s+\S+)*",
            stripped,
        ):
            return True

        # Item-level return amount
        if re.fullmatch(
            r"Return Amount\s+\$-?[\d.]+",
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