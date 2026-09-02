from pathlib import Path

from src.providers.groq_vision import extract_receipt_text_with_groq


def extract_receipt_image(file_path: str) -> list[str]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Receipt image not found: {file_path}"
        )

    if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise ValueError(
            "Unsupported receipt image type."
        )

    receipt_text = extract_receipt_text_with_groq(
        file_path
    )

    receipt_lines = [
        line.rstrip()
        for line in receipt_text.splitlines()
        if line.strip()
    ]

    return receipt_lines