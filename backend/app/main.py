import os
from app.utils.logging_utilities import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import debugpy
from app.routers import project_router, ollama_router, chat_history_router, chat_router

ACTIVATE_DEBUG = os.getenv("ACTIVATE_DEBUG", "FALSE")
if ACTIVATE_DEBUG=="TRUE":
    debugpy.listen(("0.0.0.0", 58979))
    print("Waiting for debugger to attach...")

logger = setup_logging()

# localhost:8000
# Swagger http://127.0.0.1:8000/docs#/
app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Allows React app on localhost
        "http://127.0.0.1:3000",  # Allows React app using 127.0.0.1
    ],  # Allows React app to make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(project_router.router, prefix="/projects")
app.include_router(ollama_router.router, prefix="/ollama")
app.include_router(chat_history_router.router, prefix="/chat-history")
app.include_router(chat_router.router, prefix="/chat")
