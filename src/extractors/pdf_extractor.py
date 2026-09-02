import pymupdf

from src.models.receipt import ReceiptData


def extract_receipt_pdf(file_path: str) -> ReceiptData:
    document = pymupdf.open(file_path)

    receipt_lines = []

    for page in document:
        text = page.get_text()

        for line in text.splitlines():
            line = line.strip()

            if line:
                receipt_lines.append(line)

    return ReceiptData(
        receipt_lines=receipt_lines
    )