from app.project_state_manager import ProjectStateItem, ProjectStateManager
from app.utils.logging_utilities import setup_logging, trace
from fastapi import HTTPException
from fastapi import APIRouter

logger = setup_logging()

router = APIRouter()

@router.get("/{project_id}/state", tags=["project"])
@trace(logger)
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


@router.post("/state", tags=["projects"])
@trace(logger)
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
@trace(logger)
async def update_project_state(project_id: str, project_state_item: ProjectStateItem):
    logger.debug(f"Params {project_state_item=}")
    if project_state_item.project_name != project_id:
        response_data= {'status':'FAILED',
                   'status_code':400, 
                   'message':f"{project_id} and {project_state_item.project_name} MUST be equal"}
    else:    
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
@trace(logger)
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

@router.get("/{project_id}/timestamp", tags=["project"])
@trace(logger)
async def get_chat_history_timestamp(project_id: str):
    logger.debug(f"Params {project_id=}")
    project_state_manager = ProjectStateManager.singleton()
    response_data = project_state_manager.get_chat_history_timestamp(project_id)
    logger.debug(f"{response_data=}")
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data
        