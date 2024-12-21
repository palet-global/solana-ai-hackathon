import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.actions.actions_processing.actions_main_processing import actions_main_processing
from src.actions.do_actions.actions_phone_calls_search import actions_phone_calls_search

async def start_actions_jobs():
    # Lets initiate the scheduler
    scheduler = AsyncIOScheduler()

    # Schedule jobs with staggered start times

    # Job Group for Processing

    # Lets process the actions and assign a type
    scheduler.add_job(
        actions_main_processing,
        'interval',
        seconds=10,
        next_run_time=datetime.now()
    )

    # Job Group for Actions

    # Lets process the actions for phone_calls_search
    scheduler.add_job(
        actions_phone_calls_search,
        'interval',
        seconds=10,
        next_run_time=datetime.now() + timedelta(seconds=5)
    )

    # Lets start the scheduler
    scheduler.start()
    
    # Keep the program running
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass