import re
from src.models.receipt import ReceiptData, ReceiptTax, ReceiptItem
from datetime import datetime



def parse_receipt_lines(receipt_lines: list[str]) -> ReceiptData:
    store_number = None
    register_number = None
    transaction_number = None
    business_date = None
    transaction_type = None
    taxes = []
    tax_total = None
    subtotal = None
    total = None
    member_status = None
    tender_type = None
    last4 = None
    authorization_code = None
    network_name = None
    approval_status = None
    items = []
    transaction_item_count = None
    transaction_timestamp = None
    

    for i, line in enumerate(receipt_lines):    
        if "BUS.DATE-" in line:
            match = re.search(
                r"S-(\d+)\s+R-(\d+)\s+BUS\.DATE-(\d{2}/\d{2}/\d{4})",
                line,
            )

            if match:
                store_number = match.group(1)
                register_number = match.group(2)
                business_date = match.group(3)       

        timestamp_match = re.fullmatch(
            r"\s*(\d{1,2}/\d{1,2}/\d{4}\s+"
            r"\d{1,2}:\d{2}:\d{2}\s+[AP]M)\s*",
            line,
        )

        if timestamp_match:
            transaction_timestamp = timestamp_match.group(1)             

        if line.startswith("T-"):
            match = re.search(r"T-(\d+)", line)

            if match:
                transaction_number = match.group(1)

        if line.strip() in ("SALE", "RETURN"):
            transaction_type = line.strip()

        tax_match = re.search(
            r"TAX\s+([A-Za-z]+)\s+([\d.]+)%\s+ON\s+\$?([\d.]+)\s+\$?([\d.]+)",
            line,
        )

        if tax_match:
            taxes.append(
                ReceiptTax(
                    tax_type=tax_match.group(1),
                    rate=float(tax_match.group(2)),
                    taxable_amount=float(tax_match.group(3)),
                    amount=float(tax_match.group(4)),
                )
            )    
        if line.startswith("SUBTOTAL"):
            match = re.search(r"(-?)\$([\d.]+)", line)

            if match:
                subtotal = float(match.group(2))

                if match.group(1) == "-":
                    subtotal = -subtotal    


        if line.startswith("TAX TOTAL"):
            match = re.search(r"\$(-?[\d.]+)", line)

            if match:
                tax_total = float(match.group(1))        

        if line.startswith("TOTAL"):
            match = re.search(r"(-?)\$([\d.]+)", line)

            if match:
                total = float(match.group(2))

                if match.group(1) == "-":
                    total = -total             

        if line.strip() == "NON-MEMBER":
            member_status = "NON_MEMBER"

        elif line.strip() == "MEMBER":
            member_status = "MEMBER"

        elif line.strip().startswith("Member ID:"):
            member_status = "MEMBER"      
           
        if line.strip().startswith("Cash"):
            tender_type = "Cash"

        elif line.strip() == "Debit":
            tender_type = "Debit"

        elif line.strip() in (
            "VISA",
            "MASTERCARD",
            "AMEX",
            "DISCOVER",
        ):
            tender_type = line.strip()   
              

        if line.startswith("ACCOUNT#"):
            match = re.search(r"(\d{4})\s+\$?[\d.]+$", line)

            if match:
                last4 = match.group(1)    
        if line.startswith("AUTH#"):
            authorization_code = line.split(":", 1)[1].strip()   
        if line.startswith("NETWORKNAME:"):
            network_name = line.split(":", 1)[1].strip()  
        if line.strip() == "Approved":
            approval_status = "Approved"   
        item_match = re.search(
            r"^(.*?)\s+(-?)\$([\d.]+)$",
            line
        )

        if item_match:
            description = item_match.group(1).strip()
            price = float(item_match.group(3))

            if item_match.group(2) == "-":
                price = -price

            excluded_prefixes = (
                "SUBTOTAL",
                "TOTAL",
                "TAX ",
                "TAX TOTAL",
                "Return Amount",
                "ACCOUNT#",
                "CHANGE DUE",
                "Expected change",
                "Total USD",
            )

            if not description.startswith(excluded_prefixes):
                item_code = None

                if i + 1 < len(receipt_lines):
                    next_line = receipt_lines[i + 1].strip()

                    code_match = re.match(r"^(\d{6,14})", next_line)

                    if code_match:
                        item_code = code_match.group(1)

                if item_code:
                    items.append(
                        ReceiptItem(
                            description=description,
                            item_code=item_code,
                            price=price,
                        )
                    )       

        item_count_match = re.search(
            r"(\d+)\s+(?:Sale|Return) item\(s\)",
            line,
        )

        if item_count_match:
            transaction_item_count = int(item_count_match.group(1))                

    if business_date:
        business_date = datetime.strptime(
            business_date,
            "%m/%d/%Y").strftime("%Y-%m-%d")           

    return ReceiptData(
        store_number=store_number,
        register_number=register_number,
        transaction_number=transaction_number,
        business_date=business_date,
        transaction_type=transaction_type,
        receipt_lines=receipt_lines,
        taxes=taxes,
        subtotal=subtotal,
        tax_total=tax_total,
        total=total,
        member_status=member_status,
        tender_type=tender_type,
        last4=last4,
        authorization_code=authorization_code,
        network_name=network_name,
        approval_status=approval_status,
        items=items,
        transaction_item_count=transaction_item_count,
        transaction_timestamp=transaction_timestamp,
    )