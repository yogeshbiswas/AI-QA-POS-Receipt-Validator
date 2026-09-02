import xml.etree.ElementTree as ET

from src.models.pos import POSData, POSItem , POSTender, POSCustomer




def parse_pos_xml(file_path: str) -> POSData:
    tree = ET.parse(file_path)
    root = tree.getroot()

    namespaces = {
    "ns": "http://www.nrf-arts.org/IXRetail/namespace/",
    "ncr": "http://www.ncr.com/rsd/tlog/markup/poslog",
}

    transaction = root.find("ns:Transaction", namespaces)

    store_number = transaction.findtext("ns:RetailStoreID", namespaces=namespaces)

    register_number = transaction.findtext(
        "ns:WorkstationID",
        namespaces=namespaces
        )

    transaction_number = transaction.findtext(
        "ns:SequenceNumber",
        namespaces=namespaces
        )

    business_date = transaction.findtext(
    "ns:BusinessDayDate",
    namespaces=namespaces
    )
    transaction_type_id = transaction.findtext(
        ".//ncr:TransactionTypeId",
        namespaces=namespaces
    )

    if transaction_type_id == "1":
        transaction_type = "SALE"
    elif transaction_type_id == "2":
        transaction_type = "RETURN"
    else:
        transaction_type = "UNKNOWN"

    items = []

    for line_item in transaction.findall(".//ns:LineItem", namespaces):
        item_element = line_item.find("ns:Sale", namespaces)
        if item_element is None:
            item_element = line_item.find("ns:Return", namespaces)
        if item_element is None:
            continue

        description = item_element.findtext(
            "ns:Description",
            namespaces=namespaces
            )

        item_id = item_element.findtext(
                "ns:ItemID",
                namespaces=namespaces
            )
        pos_item_id = item_element.findtext(
            "ns:POSIdentity/ns:POSItemID",
            namespaces=namespaces
        )

        quantity = item_element.findtext(
                "ns:Quantity",
                namespaces=namespaces
            )

        unit_price = item_element.findtext(
                "ns:ActualSalesUnitPrice",
                namespaces=namespaces
            )

        special_fields = {}

        trainer_name = item_element.findtext(
            ".//ncr:Item[@name='TrainerFirstName']",
            namespaces=namespaces
            )

        training_start_date = item_element.findtext(
            ".//ncr:Item[@name='TrainingStartDate']",
            namespaces=namespaces
            )

        if trainer_name:
            special_fields["TrainerFirstName"] = [trainer_name]

        if training_start_date:
            special_fields["TrainingStartDate"] = [training_start_date]

        is_voided = line_item.get("VoidFlag") == "true"    

        item = POSItem(
            description=description,
            item_id=item_id,
            pos_item_id=pos_item_id,
            quantity=float(quantity),
            unit_price=float(unit_price),
            special_fields=special_fields,
            is_voided=is_voided,
        )

        items.append(item)

    subtotal = transaction.find(
    ".//ns:Total[@TotalType='TransactionNetAmount']",
    namespaces
    )

    tax_total = transaction.find(
        ".//ns:Total[@TotalType='TransactionTaxAmount']",
        namespaces
        )

    total = transaction.find(
        ".//ns:Total[@TotalType='TransactionGrossAmount']",
        namespaces
        )      
    subtotal_value = float(subtotal.text)
    tax_total_value = float(tax_total.text)
    total_value = float(total.text)  

    tender_element = transaction.find(
        ".//ns:Tender",
        namespaces
    )

    tender_type = tender_element.get("TenderType")
    sub_tender_type = tender_element.get("SubTenderType")

    tender_description = tender_element.get(
        f"{{{namespaces['ncr']}}}TenderDescription"
    )

    authorization_code = tender_element.findtext(
        ".//ns:AuthorizationCode",
        namespaces=namespaces
    )

    approval_status = tender_element.findtext(
        ".//ns:AuthorizationDescription",
        namespaces=namespaces
    )

    primary_account_number = tender_element.findtext(
        ".//ns:PrimaryAccountNumber",
        namespaces=namespaces
    )

    last4 = primary_account_number[-4:] if primary_account_number else None

    # extracting network details
    authorizer_data = tender_element.findtext(
        ".//ncr:AuthorizerData",
        namespaces=namespaces
    )

    network_name = None

    if authorizer_data:
        marker = "<networkname>"
        end_marker = "</networkname>"

        start = authorizer_data.find(marker)
        end = authorizer_data.find(end_marker)

        if start != -1 and end != -1:
            start += len(marker)
            network_name = authorizer_data[start:end]
    #-------------------------------

    
            
    tender_amount = tender_element.findtext(
        "ns:Amount",
        namespaces=namespaces
    )
    
    tender = POSTender(
        tender_type=tender_type,
        amount=float(tender_amount),
        tender_description=tender_description,
        sub_tender_type=sub_tender_type,
        last4=last4,
        authorization_code=authorization_code,
        network_name=network_name,
        approval_status=approval_status,
    )

    customer_element = transaction.find(
            ".//ns:Customer",
            namespaces
            )
    
    member_status = "UNKNOWN"
    member_id = None
    tier = None
    first_name = None
    last_name = None
    email = None
    phone = None

    if customer_element is not None:
        non_member = customer_element.get(
            f"{{{namespaces['ncr']}}}NonMember"
        )

        if non_member == "true":
            member_status = "NON_MEMBER"
        elif non_member == "false":
            member_status = "MEMBER"

        member_id = customer_element.findtext(
            "ns:CustomerID",
            namespaces=namespaces
        )
        first_name = customer_element.findtext(
            "ncr:FirstName",
            namespaces=namespaces
        )

        last_name = customer_element.findtext(
            "ncr:LastName",
            namespaces=namespaces
        )

        email = customer_element.findtext(
            "ns:eMail",
            namespaces=namespaces
        )

        phone = customer_element.findtext(
            "ns:TelephoneNumber",
            namespaces=namespaces
        )

    tier_element = transaction.find(
        ".//ncr:Item[@name='TIER_LEVEL']",
        namespaces
    )

    if tier_element is not None:
        tier = tier_element.text

    customer = POSCustomer(
        member_status=member_status,
        member_id=member_id,
        tier=tier,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        )

    receipt_lines = []

    for receipt_line in transaction.findall(
        ".//ns:ReceiptLine",
        namespaces
    ):
        if receipt_line.text:
            line_text = receipt_line.text.strip()

            if line_text:
                receipt_lines.append(line_text)

            
    pos_data = POSData(
        store_number=store_number,
        register_number=register_number,
        transaction_number=transaction_number,
        business_date=business_date,
        transaction_type=transaction_type,
        items=items,
        subtotal=subtotal_value,
        tax_total=tax_total_value,
        total=total_value,
        tender=tender,
        customer=customer,
        receipt_lines=receipt_lines,
    )

    return pos_data