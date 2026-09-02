from pydantic import BaseModel



class POSItem(BaseModel):
    description: str
    item_id: str
    quantity :float
    unit_price: float
    special_fields: dict[str, list[str]] = {}
    is_voided: bool = False
    pos_item_id: str | None = None

class POSTender(BaseModel):
    tender_type: str
    amount: float
    tender_description: str | None = None
    sub_tender_type: str | None = None
    last4: str | None = None
    authorization_code: str | None = None
    network_name: str | None = None
    approval_status: str | None = None


class POSCustomer(BaseModel):
    member_status: str
    member_id: str | None = None
    tier: str | None = None    
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None

class POSData(BaseModel):
        
        store_number: str
        register_number: str
        transaction_number: str
        business_date: str
        transaction_type: str
        items: list[POSItem]
        subtotal: float
        tax_total: float
        total: float
        tender: POSTender
        customer : POSCustomer
        receipt_lines: list[str] = []
        