from fastapi import Request
from pydantic import BaseModel
from src.restapi.response import success_true_with_id, success_data
from src.database.query.write.insert_actions import insert_actions
from src.restapi.error_codes import ErrorCodes, raise_HTTPException
from src.database.query.write.insert_threads_groups import insert_threads_groups
from src.database.query.read.actions import select_actions
from src.database.sql.status import (
    STATUS_ACTION,
    STATUS_PENDING
)
from config import (
    LOGGER,
    PALET_DEMO_USER_ID
)

class ItemActions(BaseModel):
    query: str

async def get_actions(request: Request, id_action: str):
    try:
        # Get the action
        action = await select_actions(id_action=id_action)
        action = action[0]

        # Log the action request
        LOGGER.info(f"Fetched action {id_action}")

        # Lets extract the results
        results = action.results
        if isinstance(results, dict):
            if "value" in results:
                results = action.results["value"]
        
        # Return the data
        return success_data(
            {
                "id_action": action.human_readable_id,
	            "id_user": action.initiator_id_user,
                "type": action.type,
                "query": action.query,
                "results": results,
                "status": action.status,
                "changed_at": action.changed_at,
                "created_at": action.created_at
            }
        )
        
    except Exception as e:
        LOGGER.error(f"Error fetching action {id_action}: {str(e)}")
        raise_HTTPException(ErrorCodes.INVALID_REQUEST)
    
async def post_actions(request: Request, item: ItemActions):
    try:
        # Lets create a thread group for this action
        id_threads_group = await insert_threads_groups(
            id_user=PALET_DEMO_USER_ID,
            status=STATUS_ACTION
        )

        # Lets insert the action
        id = await insert_actions(
            id_threads_group=id_threads_group,
            initiator_id_user=PALET_DEMO_USER_ID,
            query=item.query,
            status=STATUS_PENDING
        )

        # Lets return the id
        return success_true_with_id(id)
    except Exception as e:
        # Log the error and raise an HTTPExeption
        LOGGER.error(f"Exception: {e}")
        raise_HTTPException(ErrorCodes.REQUEST_ERROR)