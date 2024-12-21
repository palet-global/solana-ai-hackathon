from typing import Any
from fastapi.responses import HTMLResponse

# Return json success response to the client
def success_true():
    return {"success": True}

# Return json success response to the client with false
def success_false():
    return {"success": False}

# Return json success response to the client with an Id
def success_true_with_id(id: str):
    return {"success": True, "id": id}

# Return json data response to the client
def success_data(data: Any):
    return {"data": data}

# Return XML data response to the client
def success_xml(data: Any):
    return HTMLResponse(content=data, media_type="application/xml")