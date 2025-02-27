import asyncio
import inspect
import os


from app.chat_history_manager import ChatHistoryItem, ChatHistoryManager
from app.project_state_manager import ProjectStateItem, ProjectStateManager
from app.session_manager import SessionManager
from app.utils.logging_utilities import setup_logging, trace
from app.utils.ollama_utilities import get_available_ollama_models
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import debugpy
from app.routers import project_routers

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


# @app.get("/get/available-models")
# @trace(logger)
# async def available_models():
#     #logger.trace(f"ENTERING {__name__} {inspect.currentframe().f_code.co_name}")
#     model_names = get_available_ollama_models()
#     #logger.trace(f"EXITING  {__name__} {inspect.currentframe().f_code.co_name}")
#     return model_names
        
# @app.get("/get/chat-history/{project_id}")
# @trace(logger)
# def get_chat_history(project_id: str):
#     chat_history_manager = ChatHistoryManager.singleton()
#     chat_history = chat_history_manager.get_chat_history(project_id)
#     return chat_history

# @app.get("/get/active-chat/{project_id}")
# @trace(logger)
# def get_active_chat(project_id: str):
#     logger.debug(f"get_active_chat Params {project_id=}")
#     chat_history_manager = ChatHistoryManager.singleton()
#     active_chat = chat_history_manager.get_active_chat(project_id)
#     return active_chat

# @app.get("/get/chat-history-timestamp/{project_id}")
# @trace(logger)
# def get_chat_history_timestamp(project_id: str):
#     logger.debug(f"get_chat_history_timestamp Params  {project_id=}")
#     project_state_manager = ProjectStateManager.singleton()
#     chat_history_timestamp = project_state_manager.get_chat_history_timestamp(project_id)
#     return chat_history_timestamp

# @app.post("/create/chat-history-item")
# @trace(logger)
# def create_chat_history_item(chat_history_item: ChatHistoryItem):
#     logger.debug(f"create_chat_history_item params {chat_history_item=}")
#     active_session = session_manager.get_session(chat_history_item.project_id)
#     new_chat = active_session.create_new_chat(chat_history_item)
#     return new_chat

# @app.delete("/delete/chat-history-item")
# @trace(logger)
# async def delete_chat_history_item(chat_history_item: ChatHistoryItem):
#     logger.trace(f"ENTERING {__name__} {inspect.currentframe().f_code.co_name}")
#     chat_history_manager = ChatHistoryManager.singleton()
#     updated_history = chat_history_manager.delete_chat_history_item(chat_history_item)
#     if updated_history is None:
#         logger.debug("EXITING delete_chat_history: Item not found")
#         raise HTTPException(status_code=404, detail="Chat history item not found")
#     logger.trace(f"EXITING  {__name__} {inspect.currentframe().f_code.co_name}")
#     return updated_history

# @app.get("/get/chat-items/{project_id}/{chat_id}")
# def get_chat_items(project_id: str, chat_id: str):
#     logger.trace(f"ENTERING {__name__} {inspect.currentframe().f_code.co_name}")
#     logger.debug(f"params {project_id=} {chat_id=}")
#     active_session = session_manager.get_session(project_id)
#     chat_interactions = active_session.get_chat_interactions(chat_id)
#     chat_history_manager = ChatHistoryManager.singleton()
#     #TODO WHY IS THIS A SET OPERATION set_active_chat?
#     chat_history_manager.set_active_chat(ChatHistoryItem(project_id=project_id, chat_id=chat_id))
#     #update timestamp
#     logger.trace(f"EXITING  {__name__} {inspect.currentframe().f_code.co_name}")
#     return chat_interactions

# @app.post("/update/chat-history-item-title")
# async def update_chat_history_item_title(chat_history_item: ChatHistoryItem):
#     logger.trace(f"ENTERING {__name__} {inspect.currentframe().f_code.co_name}")
#     logger.debug(f"Params {chat_history_item=}")
#     chat_history_manager = ChatHistoryManager.singleton()
#     updated_history = chat_history_manager.update_chat_history_item_title(chat_history_item)
#     logger.debug(f"Variable {updated_history=}")
#     if updated_history is None:
#         raise HTTPException(status_code=404, detail="Chat history item not found")
#     logger.trace(f"EXITING  {__name__} {inspect.currentframe().f_code.co_name}")
#     return updated_history

