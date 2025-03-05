from app.managers.project_state_manager import ProjectStateItem, ProjectStateManager
from app.utils.logging_utilities import setup_logging, trace
from fastapi import HTTPException
from fastapi import APIRouter
from app.managers.chat_history_manager import ChatHistoryItem, ChatHistoryManager
from app.managers.chat_manager import ChatManager
import inspect

logger = setup_logging()

router = APIRouter()

@router.get("/{project_id}/items", tags=["chat-history"])
@trace(logger)
async def get_chat_history_items(project_id: str):
    """Return a list of chat history items for the given project_id."""
    logger.debug(f"params {project_id=}")
    chat_history_manager = ChatHistoryManager.singleton()
    response_data = chat_history_manager.get_chat_history_items(project_id)
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data

@router.delete("/{project_id}/items", tags=["chat-history"])
@trace(logger)
async def delete_chat_history_items(project_id: str):
    """Delete all chat history items for the given project_id."""
    logger.debug(f"params {project_id=}")
    chat_history_manager = ChatHistoryManager.singleton()
    response_data = chat_history_manager.delete_chat_history_items(project_id)
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data

@router.get("/{project_id}/active-chat", tags=["chat-history"])
@trace(logger)
async def get_active_chat(project_id: str):
    """Return the active chat history item for the given project_id."""
    logger.debug(f"get_active_chat Params {project_id=}")
    chat_history_manager = ChatHistoryManager.singleton()
    response_data = chat_history_manager.get_active_chat(project_id)
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data

@router.put("/{project_id}/active-chat/{chat_id}", tags=["chat-history"])
@trace(logger)
async def set_active_chat(project_id: str, chat_id: str):
    """ Set the provided chat as the active chat and ensure all other chats are set to inactive"""
    logger.debug(f"set_active_chat Params {project_id=} {chat_id=}")
    chat_history_manager = ChatHistoryManager.singleton()
    response_data = chat_history_manager.set_active_chat(project_id, chat_id)
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data

@router.post("/{project_id}/item", tags=["chat-history"])
@trace(logger)
def create_chat_history_item(project_id, chat_history_item: ChatHistoryItem):
    """Add a new chat history item to the list and set as the active_chat=True."""
    logger.debug(f"create_chat_history_item params {chat_history_item=}")
    if chat_history_item.project_id != project_id:
        response_data = {'status':'FAILED',
                   'status_code':400, 
                   'message':f"{project_id} and {chat_history_item.project_id} MUST be equal"}
    else:
        chat_history_manager = ChatHistoryManager.singleton()
        active_chat_response = chat_history_manager.get_active_chat(project_id)
        if 'chat_id' in active_chat_response:
            chat_id = active_chat_response['chat_id']
            chat_manager = ChatManager()
            chat_interactions_count = chat_manager.get_chat_interactions_count(chat_id)
            if chat_interactions_count == 0:
                chat_history_manager.delete_chat_history_item(project_id, chat_id)
        response_data = chat_history_manager.create_chat_history_item(chat_history_item)
        
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data

@router.put("/{project_id}/item/{chat_id}/title", tags=["chat-history"])
@trace(logger)
async def update_chat_history_item_title(project_id, chat_id,chat_history_item: ChatHistoryItem):
    """Update an existing chat history item title."""
    logger.debug(f"Params {chat_history_item=}")
    if chat_history_item.project_id != project_id or  chat_history_item.chat_id != chat_id:
        response_data = {'status':'FAILED',
                   'status_code':400, 
                   'message':f"{project_id} and {chat_history_item.project_id} MUST be equal and {chat_id} and {chat_history_item.chat_id} MUST be equal."}
    else:    
        chat_history_manager = ChatHistoryManager.singleton()
        response_data = chat_history_manager.update_chat_history_item_title(chat_history_item)
        
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data


@router.delete("/{project_id}/item/{chat_id}", tags=["chat-history"])
@trace(logger)
async def delete_chat_history_item(project_id, chat_id):
    """Delete a specific chat history item by chat_id and return status"""
    logger.debug(f"delete_chat_history_item {project_id=} {chat_id=}")
    chat_history_manager = ChatHistoryManager.singleton()
    response_data = chat_history_manager.delete_chat_history_item(project_id, chat_id)
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data


@router.get("/{project_id}/timestamp", tags=["chat-history"])
@trace(logger)
async def get_chat_history_timestamp(project_id: str):
    logger.debug(f"Params {project_id=}")
    chat_history_manager = ChatHistoryManager.singleton()
    response_data = chat_history_manager.get_chat_history_timestamp(project_id)
    logger.debug(f"{response_data=}")
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data
        


   