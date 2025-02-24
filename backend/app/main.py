import asyncio
import os

import requests
from app.session_manager import SessionManager
from app.chat_history_manager import ChatHistoryItem, ChatHistoryManager
from app.project_state_manager import ProjectStateManager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.utils.utilities import open_ollama, setup_logging

logger = setup_logging()

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
    print(f"websocket_endpoint project_id={project_id}")
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
        
# API endpoint to get the chat history
@app.get("/get/chat-history/{project_context}")
def get_chat_history(project_context: str):
    print(f"calling get_chat_history {project_context}")
    chat_history_manager = ChatHistoryManager.singleton()
    return chat_history_manager.get_chat_history(project_context)

# API endpoint to get the active chat
@app.get("/get/active-chat/{project_context}")
def get_active_chat(project_context: str):
    print(f"calling get_active_chat {project_context}")
    chat_history_manager = ChatHistoryManager.singleton()
    active_chat = chat_history_manager.get_active_chat(project_context)
    logger.debug(f"active_chat {active_chat}")
    return active_chat

@app.get("/get/chat-history-timestamp/{project_context}")
def get_chat_history_timestamp(project_context: str):
    logger.debug(f"get_chat_history_timestamp with={project_context}")
    project_state_manager = ProjectStateManager.singleton()
    chat_history_timestamp = project_state_manager.update_chat_history_timestamp(project_context)
    logger.debug(f"chat_history_timestamp {chat_history_timestamp}")
    return chat_history_timestamp

@app.delete("/delete/chat-history-item/{chat_id}")
async def delete_chat_history_item(chat_id: str):
    logger.debug(f"ENTERING delete_chat_history with={chat_id}")
    chat_history_manager = ChatHistoryManager.singleton()
    updated_history = chat_history_manager.delete_chat_history_item(chat_id)
    if updated_history is None:
        logger.debug(f"EXITING delete_chat_history: Item not found")
        raise HTTPException(status_code=404, detail="Chat history item not found")
    logger.debug(f"EXITING delete_chat_history")
    return updated_history

@app.post("/create/chat-history-item")
def create_chat_history_item(chat_history_item: ChatHistoryItem):
    print(f"calling get_session {chat_history_item.project_id}")
    active_session = session_manager.get_session(chat_history_item.project_id)
    print(f"calling create_new_chat {chat_history_item}")
    new_chat = active_session.create_new_chat(chat_history_item)
    return new_chat

class ChatTitleUpdate(BaseModel):
    name: str  # This is the field sent in the request body

@app.put("/update/chat-history-item-title/{chat_id}")
async def update_chat_history_item_title(chat_id: str, chat_title: ChatTitleUpdate):
    logger.debug(f"ENTERING update_chat_history_item_title with={chat_id} and title={chat_title.name}")
    chat_history_manager = ChatHistoryManager.singleton()
    logger.debug(f"IN update_chat_history_item_title")
    updated_history = chat_history_manager.update_chat_history_item_title(chat_id, chat_title.name)
    logger.debug(f"IN update_chat_history_item_title with={updated_history}")
    if updated_history is None:
        logger.debug(f"EXITING update_chat_history_item_title: Item not found")
        raise HTTPException(status_code=404, detail="Chat history item not found")
    logger.debug(f"EXITING update_chat_history_item_title")
    return updated_history
