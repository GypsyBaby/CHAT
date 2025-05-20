import asyncio
import logging
import uvicorn
from fastapi import FastAPI, Request, HTTPException

from src.api.auth import auth_router
from src.api.chat import chat_router, websocket_router
from src.api.history import history_router
from src.api.user import user_router

from src import sync_persistent_and_memory_chat_storage

logger = logging.getLogger(__name__)

app = FastAPI()

@app.middleware
async def base_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except BaseException as exc:
        logger.exception("An unexpected error occurred")
        raise HTTPException(status_code=500, detail="Call Sergey Dmitriev, smth went wrong")


app.include_router(user_router)
app.include_router(chat_router)
app.include_router(history_router)
app.include_router(auth_router)
app.include_router(websocket_router)

asyncio.run(sync_persistent_and_memory_chat_storage())

uvicorn.run(app, host="0.0.0.0")
