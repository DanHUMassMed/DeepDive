import subprocess
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from langchain_ollama import ChatOllama
from pydantic import BaseModel

import requests
import asyncio
from app.app_session import SessionManager
from app.chat_history_manager import ChatHistoryManager, ChatHistoryItem

# localhost:8000
app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows React app to make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Instantiate session manager
session_manager = SessionManager()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.active_tasks: dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = None

    def disconnect(self, websocket: WebSocket):
        # Cancel the task if still running
        task = self.active_tasks.get(websocket)
        if task and not task.done():
            task.cancel()

        # Remove the websocket from active connections and tasks
        self.active_connections.pop(websocket, None)
        self.active_tasks.pop(websocket, None)

    async def receive_message(self, websocket: WebSocket):
        return await websocket.receive_text()

    async def send_message(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

# TODO: Move connection_manager into the session
# This is working for now as we only have one session
connection_manager = ConnectionManager()


@app.websocket("/ws/sendMessage")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    print(f"websocket_endpoint {project_id}")
    await connection_manager.connect(websocket)

    active_session = session_manager.get_session(project_id)
        
    try:
        # Await message from the client
        prompt = await websocket.receive_text()
        print(f"prompt: {prompt}")

        # Launch the streaming task in the background
        task = asyncio.create_task(active_session.stream_llm(websocket, prompt))

        # Store the task in the manager
        connection_manager.active_tasks[websocket] = task

        # Await the task's completion
        await task

    except WebSocketDisconnect:
        print("disconnect websocket")
        connection_manager.disconnect(websocket)
    except Exception as e:
        print(f"Error: {e}")
        connection_manager.disconnect(websocket)
        await websocket.close()


@app.post("/cancel-stream")
async def cancel_stream():
    # Iterate through active tasks and cancel them
    for websocket, task in connection_manager.active_tasks.items():
        if task and not task.done():
            print(f"Cancelling task for {websocket.client.host}")
            task.cancel()

    return {"status": "Task canceled"}


# API endpoint to get the response from the model
@app.get("/get/available-models")
async def available_models():
    url = "http://localhost:11434/api/tags"
    response = requests.get(url)
    if response.status_code == 200:
        models_data = response.json()
        model_names = [model['name'] for model in models_data.get('models', [])]
        return model_names
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch models")


def open_ollama():
    try:
        # Open Ollama (assuming it's a GUI app located in /Applications)
        subprocess.run(["open", "-a", "Ollama"], check=True)
        print("Ollama opened successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to open Ollama: {e}")
        
# API endpoint to get the response from the model
@app.get("/get/chat-history/{project_context}")
def get_chat_history(project_context: str):
    print(f"get_chat_history {project_context}")
    chat_history_manager = ChatHistoryManager.get_chat_history_manager()
    return chat_history_manager.get_chat_history(project_context)


# API endpoint to create a new chat history item
@app.post("/create/chat-history-item")
def create_chat_history_item(chat_history_item: ChatHistoryItem):
    chat_history_manager = ChatHistoryManager.get_chat_history_manager()
    # Use chat_history_item.project_id to access the 'project_id' field
    return chat_history_manager.create_chat_history_item(chat_history_item)