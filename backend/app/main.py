import asyncio
import inspect
import os


from app.chat_history_manager import ChatHistoryItem, ChatHistoryManager
from app.project_state_manager import ProjectStateItem, ProjectStateManager
from app.session_manager import SessionManager
from app.utils.logging_utilities import setup_logging, trace
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import debugpy
from app.routers import project_routers, ollama_routers, chat_history_routers

ACTIVATE_DEBUG = os.getenv("ACTIVATE_DEBUG", False)
if ACTIVATE_DEBUG:
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

app.include_router(project_routers.router, prefix="/projects")
app.include_router(ollama_routers.router, prefix="/ollama")
app.include_router(chat_history_routers.router, prefix="/chat-history")


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


# @app.websocket("/ws/sendMessage")
# async def websocket_endpoint(websocket: WebSocket, project_id: str):
#     logger.trace(f"ENTERING {__name__} {inspect.currentframe().f_code.co_name}")
#     logger.debug(f"websocket_endpoint project_id={project_id}")
    
#     await connection_manager.connect(websocket)
#     active_session = session_manager.get_session(project_id)
        
#     try:
#         # Await message from the client
#         prompt = await websocket.receive_text()
#         logger.debug(f"prompt: {prompt}")

#         # Launch the streaming task in the background
#         task = asyncio.create_task(active_session.stream_llm(websocket, prompt))

#         # Store the task in the manager
#         connection_manager.active_tasks[websocket] = task

#         # Await the task's completion
#         await task

#     except WebSocketDisconnect:
#         logger.debug("disconnect websocket")
#         connection_manager.disconnect(websocket)
#     except Exception as e:
#         logger.debug(f"Error: {e}")
#         connection_manager.disconnect(websocket)
#         await websocket.close()
#     logger.trace(f"EXITING  {__name__} {inspect.currentframe().f_code.co_name}")


# @app.post("/cancel-stream")
# async def cancel_stream():
#     logger.trace(f"ENTERING {__name__} {inspect.currentframe().f_code.co_name}")
#     # Iterate through active tasks and cancel them
#     for websocket, task in connection_manager.active_tasks.items():
#         if task and not task.done():
#             logger.debug(f"Cancelling task for {websocket.client.host}")
#             task.cancel()

#     logger.trace(f"EXITING  {__name__} {inspect.currentframe().f_code.co_name}")
#     return {"status": "Task canceled"}


        


