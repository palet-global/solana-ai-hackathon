from version import palet_api_version
from datetime import datetime, timezone
from src.restapi.response import success_data

async def get_healthcheck():
    json_data = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": palet_api_version
    }
    return success_data(json_data)