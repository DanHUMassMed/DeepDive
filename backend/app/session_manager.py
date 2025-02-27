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
            logger.debug(f"NOT IN")
            self.create_session(project_id)
            logger.debug(f"NOT IN after")
            logger.debug(f"{inspect.currentframe().f_code.co_name} Creating session.")
        else:
            logger.debug(f"{inspect.currentframe().f_code.co_name} Session already created.")
            
        return self.active_sessions[project_id]
    
    
class UserSession:
    @trace(logger)
    def __init__(self, project_id):
        self._db_path = f"{get_parent_directory()}/resources/checkpoints.db"
        self.project_id = project_id
        
        # If the chat history list is empty give us a new chat
        chat_history_manager = ChatHistoryManager.singleton()
        active_chat = chat_history_manager.get_active_chat(self.project_id)
        if active_chat and len(active_chat)==0:
            logger.debug(f"IN before create_chat_history_item")  
            chat_item = ChatHistoryItem(project_id=self.project_id)
            chat_history_manager.create_chat_history_item(chat_item)
            logger.debug(f"IN after create_chat_history_item")   
        
        self.system_prompt = constants.DEFAULT_SYSTEM_PROMPT
        #TODO FIX THIS
        self.graph = self._create_graph()
        
    @trace(logger)
    def _create_graph(self):
        project_state_manager = ProjectStateManager.singleton()
        project_state = project_state_manager.get_project_state(self.project_id)
        model = init_chat_model(project_state['project_llm_name'], model_provider="ollama")

        #TODO THIS DOES NOT LOOK RIGHT    
        trimmer = trim_messages(
            max_tokens=6_500_000,
            strategy="last",
            token_counter=model,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.system_prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        graph = StateGraph(state_schema=MessagesState)

        def call_model(state: MessagesState):
            trimmed_messages = trimmer.invoke(state["messages"])
            prompt = prompt_template.invoke({"messages": trimmed_messages})
            response = model.invoke(prompt)
            return {"messages": [response]}

        graph.add_edge(START, "model")
        graph.add_node("model", call_model)

        return graph

    @trace(logger)
    def create_new_chat(self, chat_history_item: ChatHistoryItem):
        logger.debug(f"params {chat_history_item.project_id=}")
        chat_history_manager = ChatHistoryManager.singleton()
        active_chat = chat_history_manager.get_active_chat(chat_history_item.project_id)
        logger.debug(f"active_chat == {active_chat}")
        if active_chat and len(active_chat) > 0:
            number_of_messages_in_current_chat = self.get_chat_interactions_count(active_chat['chat_id'])
            logger.debug(f"IN1 {number_of_messages_in_current_chat=}")   

            if number_of_messages_in_current_chat == 0:
                # If we have not had any interaction on the active chat just remove it
                logger.debug("FM1")
                chat_history_manager.delete_chat_history_item(ChatHistoryItem(**active_chat))
                logger.debug("FM2")
        
        new_chat = chat_history_manager.create_chat_history_item(chat_history_item)
        logger.debug(f" with={new_chat}")
        return new_chat
    
    @trace(logger)
    def get_chat_interactions_count(self, chat_id):
        interactions_count = 0
        with SqliteSaver.from_conn_string(self._db_path) as checkpointer:            
            config = {"configurable": {"thread_id": chat_id}}
            compiled_graph = self.graph.compile(checkpointer=checkpointer)
            state_history = compiled_graph.get_state_history(config) 
            last_interaction = next(state_history, None)
            if last_interaction:
                values = last_interaction.values  
                if 'messages' in values:
                    interactions_count = len(values['messages'])
        return interactions_count
    
    @trace(logger)           
    def get_chat_interactions(self, chat_id):
        interactions=[]
        with SqliteSaver.from_conn_string(self._db_path) as checkpointer:            
            config = {"configurable": {"thread_id": chat_id}}
            compiled_graph = self.graph.compile(checkpointer=checkpointer)
            state_history = compiled_graph.get_state_history(config) 
            last_interaction = next(state_history, None)
            if last_interaction:
                values = last_interaction.values  
                if 'messages' in values:
                    for message in values['messages']:
                        interaction_type = 'user' if isinstance(message,HumanMessage) else 'ai'
                        interaction = {'type':interaction_type, 'content':message.content}
                        interactions.append(interaction)
        return interactions


    async def stream_llm(self, websocket: WebSocket, prompt: str):
        input_messages = [HumanMessage(prompt)]
        chat_history_manager = ChatHistoryManager.singleton()
        active_chat = chat_history_manager.get_active_chat(self.project_id)
        logger.debug(f"self.project_id={self.project_id} active_chat={active_chat}")
        config = {"configurable": {"thread_id": active_chat['chat_id']}}

        try:
            async with AsyncSqliteSaver.from_conn_string(self._db_path) as saver:
                compiled_graph = self.graph.compile(checkpointer=saver)        
                async for chunk, metadata in compiled_graph.astream(
                    {"messages": input_messages},
                    config,
                    stream_mode="messages",
                ):
                    if isinstance(chunk, AIMessage): 
                        await websocket.send_text(chunk.content)
                        
        except asyncio.CancelledError:
            logger.warning("Streaming task was canceled.")
        finally:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text("[DONE]")
