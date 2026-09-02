from collections import Counter
from src.models.validation import ValidationResult
from collections import Counter
import re


def validate_duplicate_receipt_lines(
    receipt_lines: list[str],
) -> list[ValidationResult]:

    ignored_lines = {
        "SALE",
        "RETURN",
        "------------",
        "--------------------------------------",
        "--------------------------------------------",
        "---------- End Receipt ----------",
    }
    def is_ignored_line(line: str) -> bool:
        stripped = line.strip()

        if stripped in ignored_lines:
            return True

        if re.fullmatch(
            r"\d{1,2}/\s*\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M",
            stripped,
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