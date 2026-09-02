from pydantic import BaseModel


class ReceiptItem(BaseModel):
    description: str
    item_code: str | None = None
    quantity: float | None = None
    price: float | None = None


class ReceiptTax(BaseModel):
    tax_type: str
    rate: float | None = None
    taxable_amount: float | None = None
    amount: float

class ReceiptData(BaseModel):
    store_number: str | None = None
    register_number: str | None = None
    transaction_number: str | None = None
    business_date: str | None = None
    transaction_type: str | None = None
    transaction_timestamp: str | None = None

    items: list[ReceiptItem] = []
    transaction_item_count: int | None = None
    taxes: list[ReceiptTax] = []

    subtotal: float | None = None
    tax_total: float | None = None
    total: float | None = None

    member_status: str | None = None
    member_id: str | None = None
    tier: str | None = None

    receipt_lines: list[str] = []

    barcode: str | None = None
    tender_type: str | None = None
    last4: str | None = None
    authorization_code: str | None = None
    network_name: str | None = None
    approval_status: str | None = None
    
    
    