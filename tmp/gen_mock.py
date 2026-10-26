import json
from pathlib import Path
from datetime import date

def _build_mock_record(name, tool, idx=1):
    if "purchaseorder" in name and "item" not in name and "scheduleline" not in name:
        return {"PurchaseOrder": f"450000000{idx}", "Supplier": f"VENDOR-100{idx}", "CompanyCode": "1000", "DocumentCurrency": "USD", "PurchasingOrganization": "1000", "PurchaseOrderDate": "/Date(1740000000000)/", "NetAmount": f"{75000 * idx}.00"}
    elif "purchaseorderitem" in name:
        return {"PurchaseOrder": f"450000000{idx}", "PurchaseOrderItem": f"0001{idx}", "Material": f"MAT-{idx:04d}", "OrderQuantity": f"{100 * idx}", "NetPriceAmount": f"{500 * idx}.00", "DocumentCurrency": "USD", "CommodityCode": "7208.10.30"}
    elif "scheduleline" in name:
        return {"PurchaseOrder": f"450000000{idx}", "PurchaseOrderItem": f"0001{idx}", "ScheduleLine": f"{idx:04d}", "ScheduleLineDeliveryDate": "/Date(1745000000000)/", "ScheduleLineOrderQuantity": f"{50 * idx}"}
    elif "purchasereqn" in name and "item" not in name:
        return {"PurchaseRequisition": f"100000000{idx}", "PurchaseRequisitionType": "NB", "PurchasingOrganization": "1000", "CompanyCode": "1000"}
    elif "purchasereqnitem" in name:
        return {"PurchaseRequisition": f"100000000{idx}", "PurchaseRequisitionItem": f"0001{idx}", "Material": f"MAT-{idx:04d}", "ReqnItemQty": f"{100 * idx}", "PurchaseRequisitionPrice": f"{500 * idx}.00", "Currency": "USD", "Plant": "1000", "DeliveryDate": "/Date(1746000000000)/"}
    elif "supplieractivity" in name or "suplracty" in name:
        return {"SupplierActivityUUID": f"guid-{idx:04d}-abcd", "SupplierActivityType": "CALL", "Supplier": f"VENDOR-100{idx}", "ActivityStatus": "OPEN", "ActivityStartDate": "/Date(1740000000000)/"}
    elif "suplractysupplier" in name:
        return {"SupplierActivityUUID": f"guid-{idx:04d}-abcd", "Supplier": f"VENDOR-100{idx}", "SupplierName": f"Global Supply Co {idx}"}
    elif "risk" in name and "exposure" in name:
        return {"supplierId": f"VENDOR-100{idx}", "riskScore": 45 + idx * 15, "riskCategory": "FINANCIAL", "trend": "DETERIORATING" if idx > 1 else "STABLE"}
    elif "engagement" in name:
        return {"engagementId": f"ENG-{idx:04d}", "supplierId": f"VENDOR-100{idx}", "status": "IN_PROGRESS", "title": "Supply Continuity Review", "ownerName": "Jane Smith"}
    elif "cost" in name and "breakdown" in name:
        return {"orderId": f"450000000{idx}", "unitPrice": f"{400 * idx}.00", "dutyAmount": f"{100 * idx}.00", "freightCharges": f"{50 * idx}.00", "totalLandedCost": f"{550 * idx}.00", "currency": "USD"}
    elif "pric" in name:
        return {"materialId": f"MAT-{idx:04d}", "sellingPrice": f"{800 * idx}.00", "currency": "USD", "validFrom": "/Date(1740000000000)/"}
    elif "reporting" in name:
        return {"reportId": f"RPT-{idx:04d}", "supplierId": f"VENDOR-100{idx}", "totalSpend": f"{150000 * idx}.00", "currency": "USD", "period": "2026-Q1"}
    return {"id": f"mock-id-{idx}", "status": "active"}

translation_files = sorted(Path("assets").glob("*/mcp-translation/translation.json"))
servers = {}
total_tools = 0

for tf in translation_files:
    data = json.loads(tf.read_text())
    server_info = data.get("serverInfo", {})
    server_name = server_info.get("name", tf.parent.parent.name)
    server_desc = server_info.get("description", "")
    slug_clean = tf.parent.parent.name.replace("-mcp-server", "")
    tools_dict = {}
    for tool in data.get("tools", []):
        name = tool["name"]
        description = tool.get("description", "")
        input_props = {}
        for param in tool.get("parameters", []):
            if param.get("deactivate"): continue
            pname = param.get("newParameterName") or param.get("name", "")
            if not pname: continue
            input_props[pname] = {"type": "string", "description": param.get("description", "")}
        input_schema = {"type": "object", "properties": input_props, "required": []}
        is_list = name.startswith("list_")
        is_count = name.startswith("count_")
        is_meta = "metadata" in name or "batch" in name
        if is_meta:
            mock_response = {"$metadata": "OData service metadata"}
        elif is_count:
            mock_response = 5
        elif is_list:
            mock_response = {"results": [_build_mock_record(name, tool), _build_mock_record(name, tool, idx=2)]}
        else:
            mock_response = _build_mock_record(name, tool)
        tools_dict[name] = {"description": description, "input_schema": input_schema, "mock_response": mock_response}
        total_tools += 1
    servers[slug_clean] = {"mcp_server_name": server_name, "description": server_desc or f"MCP server for {slug_clean}", "tools": tools_dict}

output = {
    "servers": servers,
    "metadata": {
        "version": "1.0.0",
        "created_for_agent": "trade-disruption-intelligence-agent",
        "mock_mode": True,
        "deterministic": True,
        "total_servers": len(servers),
        "total_tools": total_tools,
        "generated_from": ["translation.json"],
        "generation_date": str(date.today()),
    }
}

Path("assets/trade-disruption-intelligence-agent/mcp-mock.json").write_text(json.dumps(output, indent=2))
print(f"mcp-mock.json written: {len(servers)} servers, {total_tools} tools")
