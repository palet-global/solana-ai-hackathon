import asyncio
from config import LOGGER, CONCURRENCY_LIMIT
from src.database.sql.status import (
    STATUS_PENDING
)
from src.actions.actions_type import ACTION_PHONE_CALLS_SEARCH
from src.database.query.read.actions import select_all_actions_atomically
from src.database.query.utils.actions_steps import mark_action_step_as_completed, mark_action_step_as_failed
from src.utils.is_validators import is_empty, is_not_empty
from src.database.query.utils.actions import (
    mark_action_as_completed,
    mark_action_as_failed,
    update_action_result
)
from src.actions.do_steps.steps_understanding_query import (
    new_step_understanding_query,
)
from src.actions.do_steps.steps_searching_locations_results import (
    new_step_searching_locations_results,
)
from src.actions.do_steps.steps_calling_locations import (
    new_step_calling_locations,
)
from src.actions.do_steps.steps_create_calls_report import (
    new_step_create_calls_report,
)

async def actions_phone_calls_search():
    # Lets indicate we started the action
    LOGGER.info("actions_phone_calls_search: Run")

    # Lets get the list of all of actions, pending
    actions = await select_all_actions_atomically(
        type=ACTION_PHONE_CALLS_SEARCH,
        status=STATUS_PENDING, 
        limit=2000
    )

    # If no actions, just return
    if not actions:
        LOGGER.info("actions_phone_calls_search: No new actions found.")
        return
    
    # Semaphore to control concurrency
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    # Create a list of coroutines
    coroutines = [process_action_phone_calls_search(semaphore, action) for action in actions]

    # Run them concurrently and gather their results
    results = await asyncio.gather(*coroutines, return_exceptions=True)

async def process_action_phone_calls_search(semaphore, action):
    async with semaphore:
        try:
            LOGGER.info(f"actions_phone_calls_search: Process action {action.id_action}")

            # Step 1 - Start: Understanding the query

            # Lets create a new step for understanding the query
            id_step = await new_step_understanding_query(
                id_action=action.human_readable_id,
                id_user=action.initiator_id_user
            )

            LOGGER.info(f"actions_phone_calls_search: Step 1 - Start: Understanding the query")

            # Step 2 - Start: Search the location result

            # Lets create a new step for seaching the location result
            id_step = await new_step_searching_locations_results(
                id_action=action.human_readable_id,
                id_user=action.initiator_id_user
            )

            LOGGER.info(f"actions_phone_calls_search: Step 2 - Start: Search the location result")
            
            # Step 3 - Start: Calling Locations

            # Lets create a new step for calling locations
            id_step = await new_step_calling_locations(
                id_action=action.human_readable_id,
                id_user=action.initiator_id_user
            )

            LOGGER.info(f"actions_phone_calls_search: Step 3 - Start: Calling Locations")

            # Step 4 - Start: User report
            id_step = await new_step_create_calls_report(
                id_action=action.human_readable_id,
                id_user=action.initiator_id_user
            )

            LOGGER.info(f"actions_phone_calls_search: Step 4 - Start: User report")

            # Lets return the action id
            return action.id_action
        except Exception as e:
            LOGGER.error(f"actions_phone_calls_search: Error processing action {action.id_action}: {e}")

            # Lets store the error for the action
            await update_action_result(
                id_action=action.human_readable_id,
                result="An error occurred. Please try again."
            )
            
            # Lets end the actions
            await mark_action_as_failed(id_action=action.human_readable_id)

            # Lets mark the step as failed
            if is_not_empty(id_step):
                await mark_action_step_as_failed(id_step=id_step)

            # Lets return 
            return None
        
async def _private_end_actions_phone_calls(id_action: str, id_step: str, error_message: str):
    try:
        # Lets store the result for the action
        await update_action_result(
            id_action=id_action,
            result=error_message
        )

        # Lets end the actions
        await mark_action_as_failed(id_action=id_action)

        # Lets mark the step as completed
        await mark_action_step_as_completed(id_step=id_step)
    except Exception as e:
        LOGGER.error(f"_private_end_actions_phone_calls: Error ending action {id_action}: {e}")