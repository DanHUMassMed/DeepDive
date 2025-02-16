import subprocess
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from langchain.llms import Ollama
from pydantic import BaseModel
import requests
import asyncio

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows React app to make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Define the Pydantic model for the request body
class PromptRequest(BaseModel):
    prompt: str

# Initialize the Ollama LLM
llm = Ollama(model="deepseek-r1:32b")  # Replace with the actual model name if needed

# Function to send a prompt to the model
def sendPrompt(prompt: str) -> str:
    return llm(prompt)


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

manager = ConnectionManager()


@app.websocket("/ws/sendMessage/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        # Await message from the client
        prompt = await websocket.receive_text()
        print(f"prompt: {prompt}")

        # Launch the streaming task in the background
        task = asyncio.create_task(stream_llm(websocket, prompt))

        # Store the task in the manager
        manager.active_tasks[websocket] = task

        # Await the task's completion
        await task

    except WebSocketDisconnect:
        print("disconnect websocket")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error: {e}")
        manager.disconnect(websocket)
        await websocket.close()

# Stream data from LLM in chunks
async def stream_llm(websocket: WebSocket, prompt: str):
    try:
        async for chunk in llm.astream(prompt):
            await websocket.send_text(chunk)
            #await asyncio.sleep(0.1)  # Simulating delay for stream chunks
    except asyncio.CancelledError:
        print("Streaming task was canceled.")
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text("[DONE]")

@app.post("/cancel-stream")
async def cancel_stream():
    # Iterate through active tasks and cancel them
    for websocket, task in manager.active_tasks.items():
        if task and not task.done():
            print(f"Cancelling task for {websocket.client.host}")
            task.cancel()

    return {"status": "Task canceled"}


# API endpoint to get the response from the model
@app.get("/available-models/")
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
        
        