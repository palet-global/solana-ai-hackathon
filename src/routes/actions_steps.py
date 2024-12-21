from fastapi import Request
from src.restapi.response import success_data
from src.restapi.error_codes import ErrorCodes, raise_HTTPException
from src.database.query.read.actions_steps import select_actions_steps
from config import (
    LOGGER
)

async def get_actions_steps(request: Request, id_action: str):
    try:
        # Get the action
        actions_steps = await select_actions_steps(id_action=id_action)

        # Log the action request
        LOGGER.info(f"Fetched action steps for {id_action}")

        # Lets process the steps
        steps = []
        for step in actions_steps:
            step_data = {
                "id_step": step.human_readable_id,
	            "id_action": step.id_action,
                "id_user": step.id_user,
                "name": step.name,
                "description": step.description,
                "status": step.status,
                "changed_at": step.changed_at,
                "created_at": step.created_at
            }
            steps.append(step_data)

        # Return the data
        return success_data(steps)
        
    except Exception as e:
        LOGGER.error(f"Error fetching action steps for {id_action}: {str(e)}")
        raise_HTTPException(ErrorCodes.INVALID_REQUEST)