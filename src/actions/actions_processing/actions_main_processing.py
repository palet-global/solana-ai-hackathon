import asyncio
from config import LOGGER, CONCURRENCY_LIMIT
from src.utils.is_validators import is_empty
from src.database.sql.status import STATUS_PENDING
from src.database.cache.redis_key import REDIS_KEY_ACTIONS_MAIN_PROCESSING
from src.database.cache.query import redis_get, redis_set
from src.database.query.read.actions import select_all_actions
from src.database.query.write.update_actions import update_actions
from src.actions.actions_type import ACTION_PHONE_CALLS_SEARCH

async def actions_main_processing():
    # Lets indicate we started the action
    LOGGER.info("actions_main_processing: Run")

    # Let's get the latest ID marker with error handling
    try:
        marker_id = await redis_get(REDIS_KEY_ACTIONS_MAIN_PROCESSING)
        if is_empty(marker_id):
            marker_id = 0
        else:
            # Ensure it's an integer
            marker_id = int(marker_id)
    except Exception as e:
        LOGGER.error(f"actions_main_processing: Failed to get marker_id from Redis: {e}")
        # Exit the action job if we cannot get the marker_id
        return

    # Initialize variable to keep track of the new marker
    new_marker_id = marker_id

    # Lets print the user marker
    LOGGER.info(f"actions_main_processing: Current marker_id {marker_id}")

    # Lets get the list of all of actions
    actions = await select_all_actions(
        marker_id=marker_id, 
        status=STATUS_PENDING, 
        limit=2000
    )

    # If no actions, just return
    if not actions:
        LOGGER.info("actions_main_processing: No new actions found.")
        return
    
    # Semaphore to control concurrency
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    # Create a list of coroutines
    coroutines = [process_action(semaphore, action) for action in actions]

    # Run them concurrently and gather their results
    results = await asyncio.gather(*coroutines, return_exceptions=True)

    # Filter out any None results and exceptions
    valid_ids = [res for res in results if isinstance(res, int)]

    # Compute the new marker_id as the max ID processed
    if valid_ids:
        # Lets get the bigger marker id
        new_marker_id = max(valid_ids)

        # Save the new marker_id to Redis
        if new_marker_id > marker_id:
            await redis_set(REDIS_KEY_ACTIONS_MAIN_PROCESSING, new_marker_id)
            LOGGER.info(f"actions_main_processing: Updated marker_id to {new_marker_id}")
    else:
        LOGGER.info("actions_main_processing: No valid actions processed successfully.")
    
async def process_action(semaphore, action):
    async with semaphore:
        try:
            LOGGER.info(f"actions_main_processing: Process action {action.id_action}")
            
            # Before starting any action there is an action routers, that reasons and 
            # decides what action are we going to use to solve that query.
            await update_actions(
                human_readable_id=action.human_readable_id,
                type=ACTION_PHONE_CALLS_SEARCH
            )

            return action.id_action
        except Exception as e:
            LOGGER.error(f"actions_main_processing: Error processing action {action.id_action}: {e}")
            return None