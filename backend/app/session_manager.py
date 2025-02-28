import asyncio
import inspect
import os

from app import constants
from app.chat_history_manager import ChatHistoryItem, ChatHistoryManager
from app.project_state_manager import ProjectStateManager
from app.utils.logging_utilities import setup_logging, trace
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import START, MessagesState, StateGraph

logger = setup_logging()

def get_parent_directory():
    directory = os.path.dirname(__file__)
    parent_directory = os.path.dirname(directory)
    return parent_directory

class SessionManager:
    def __init__(self):
        self.active_sessions: dict = {}
        
    @trace(logger)
    def create_session(self, project_id: str):
        """Create a session and store the LLM instance"""
        user_session = UserSession(project_id)
        self.active_sessions[project_id] = user_session
    
    @trace(logger)
    def get_session(self, project_id: str):
        """Get the session for a user create it if it does not exist"""
        logger.debug(f"params {project_id=}")
        logger.debug(f"var {self.active_sessions=}")
        if project_id not in self.active_sessions:
            self.create_session(project_id)
            logger.debug(f"{inspect.currentframe().f_code.co_name} Creating session.")
        else:
            logger.debug(f"{inspect.currentframe().f_code.co_name} Session already created.")
            
        return self.active_sessions[project_id]
    
    
