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
from fastapi import APIRouter

logger = setup_logging()

router = APIRouter()

@router.get("/{project_id}/state", tags=["project"])
def get_project_state(project_id: str):
    logger.debug(f"params {project_id=}")
    project_state_manager = ProjectStateManager.singleton()
    response_data = project_state_manager.get_project_state(project_id)
    logger.debug(f"{response_data=}")
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data


@router.post("/state", tags=["project"])
def create_project_state(project_state_item: ProjectStateItem):
    logger.debug(f"params {project_state_item=}")
    project_state_manager = ProjectStateManager.singleton()
    response_data = project_state_manager.create_project_state(project_state_item)
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data
 
@router.put("/{project_id}/state", tags=["project"])
async def update_project_state(project_state_item: ProjectStateItem):
    logger.debug(f"Params {project_state_item=}")
    project_state_manager = ProjectStateManager.singleton()
    response_data = project_state_manager.update_project_state(project_state_item)
    logger.debug(f"{response_data=}")
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data

@router.delete("/{project_id}/state", tags=["project"])
async def delete_project_state(project_id: str):
    logger.debug(f"Params {project_id=}")
    project_state_manager = ProjectStateManager.singleton()
    response_data = project_state_manager.delete_project_state(project_id)
    logger.debug(f"{response_data=}")
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data

        