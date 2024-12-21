from config import base_route
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from src.database.cache.instance import redis_client
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import routes to use in FastAPI
from src.routes.actions import ItemActions, post_actions, get_actions
from src.routes.actions_steps import get_actions_steps
from src.routes.healthcheck import get_healthcheck

# FastAPI Lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code (before yield)
    # (If you need to initialize anything before the app starts, you can do it here)

    yield

    # Shutdown code (after yield)
    await redis_client.aclose()

# Create the FastAPI app
app = FastAPI(lifespan=lifespan)

# Add CORS Middleware for the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a manual Exception to replace "detail" with "error"
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"message": exc.detail}},
    )

# Route Group: General

# Route: Get Health checks
@app.get(f"{base_route}/healthcheck")
async def route_get_healthcheck():
    return await get_healthcheck()

# Route Group: Actions

# Route: Get an action
@app.get(f"{base_route}/actions/{{id_action}}")
async def route_get_actions(request: Request, id_action: str):
    return await get_actions(request, id_action)

# Route: Make an action
@app.post(f"{base_route}/actions")
async def route_post_actions(request: Request, item: ItemActions):
    return await post_actions(request, item)

# Route Group: Actions Steps

# Route: Get an action step
@app.get(f"{base_route}/actions_steps/{{id_action}}")
async def route_get_actions_steps(request: Request, id_action: str):
    return await get_actions_steps(request, id_action)