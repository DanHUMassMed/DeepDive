from app.utils.logging_utilities import setup_logging, trace
from fastapi import APIRouter
import inspect
import traceback
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import inspect
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, FastAPI, BackgroundTasks
from fastapi import HTTPException
from typing import Dict
import asyncio
from app.managers.chat_manager import ChatManager
from app.managers.chat_history_manager import ChatHistoryManager
from app.managers.project_state_manager import ProjectStateManager


    
logger = setup_logging()

router = APIRouter()

# Dictionary to store active connections and cancel tokens
active_connections: Dict[str, WebSocket] = {}
cancellation_tokens: Dict[str, asyncio.Event] = {}


@router.websocket("/ws/{connection_id}")
async def websocket_chat(websocket: WebSocket, connection_id: str):
    await websocket.accept()
    active_connections[connection_id] = websocket
    cancel_event = asyncio.Event()
    cancellation_tokens[connection_id] = cancel_event
    try:
        project_state_manager = ProjectStateManager.singleton()
        project_state = project_state_manager.get_project_state(connection_id)
        llm_name = project_state['project_llm_name']
        system_prompt = project_state['project_system_prompt']
        chat_manager = ChatManager(llm_name=llm_name,system_prompt=system_prompt)
        
        chat_history_manager = ChatHistoryManager.singleton()
        active_chat = chat_history_manager.get_active_chat(connection_id)
        chat_id = active_chat['chat_id']
        
    except Exception as err:
        logger.error("Exception occurred in %s: %s", __name__, err)
        logger.debug("Full traceback: %s", traceback.format_exc())
        raise
    try:
        while True:
            data = await websocket.receive_text()
            prompt = data.strip()

            if cancel_event.is_set():
                await websocket.send_text("Connection has been canceled.")
                await websocket.close(code=1000)
                return
            
            
            await chat_manager.stream_llm_responses(websocket, prompt, chat_id)
            
            # Once the streaming is complete, close the connection
            #await websocket.send_text("[DONE]")
            await websocket.close(code=1000)
            return

    except WebSocketDisconnect:
        print(f"Connection {connection_id} closed.")
    finally:
        # Clean up on disconnection
        active_connections.pop(connection_id, None)
        cancellation_tokens.pop(connection_id, None)

# Route to cancel an active WebSocket connection
@router.post("/cancel/{connection_id}", tags=["chat"])
async def cancel_connection(connection_id: str):
    if connection_id in active_connections:
        websocket = active_connections[connection_id]
        await websocket.close(code=1000)
        return {"status": "SUCCESS", "message": f"Connection {connection_id} canceled."}
    return {"status": "FAILED", "message": "No active connection found."}


@router.get("/{project_id}/interactions/{chat_id}", tags=["chat"])
@trace(logger)
async def get_chat_interactions(project_id: str,chat_id: str):
    logger.debug(f"Params {project_id=}")
    project_state_manager = ProjectStateManager.singleton()
    project_state = project_state_manager.get_project_state(project_id)
    llm_name = project_state['project_llm_name']
    system_prompt = project_state['project_system_prompt']
    chat_manager = ChatManager(llm_name=llm_name, system_prompt=system_prompt)
    response_data = chat_manager.get_chat_interactions(chat_id)
    logger.debug(f"{response_data=}")
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data
   
   
@router.get("/{project_id}/interactions_count/{chat_id}", tags=["chat"])
@trace(logger)
async def get_chat_interaction_count(project_id: str,chat_id: str):
    logger.debug(f"Params {project_id=}")
    project_state_manager = ProjectStateManager.singleton()
    project_state = project_state_manager.get_project_state(project_id)
    llm_name = project_state['project_llm_name']
    system_prompt = project_state['project_system_prompt']
    chat_manager = ChatManager(llm_name=llm_name, system_prompt=system_prompt)
    response_data = chat_manager.get_chat_interactions_count(chat_id)
    logger.debug(f"{response_data=}")
    if isinstance(response_data, int):
        return response_data  
    else:
        if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
            raise HTTPException(
                status_code=response_data['status_code'],
                detail=response_data
            )
        return response_data        