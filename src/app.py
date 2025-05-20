import asyncio
import uvicorn
from fastapi import FastAPI

from src.api.auth import auth_router
from src.api.chat import chat_router, websocket_router
from src.api.history import history_router
from src.api.user import user_router

from src import sync_persistent_and_memory_chat_storage

app = FastAPI()

app.include_router(user_router)
app.include_router(chat_router)
app.include_router(history_router)
app.include_router(auth_router)
app.include_router(websocket_router)

asyncio.run(sync_persistent_and_memory_chat_storage())

uvicorn.run(app, host="0.0.0.0")
