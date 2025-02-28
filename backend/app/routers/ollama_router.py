from app.project_state_manager import ProjectStateItem, ProjectStateManager
from app.utils.logging_utilities import setup_logging, trace
from fastapi import HTTPException
from fastapi import APIRouter
from app.utils.ollama_utilities import get_available_ollama_models

logger = setup_logging()

router = APIRouter()

@router.get("/available-models", tags=["ollama"])
@trace(logger)
async def available_models():
    response_data = get_available_ollama_models()
    logger.debug(f"{response_data=}")
    if 'status_code' in response_data and 400 <= response_data['status_code'] <= 599:
        raise HTTPException(
            status_code=response_data['status_code'],
            detail=response_data
        )
    return response_data

