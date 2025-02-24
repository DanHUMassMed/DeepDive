import asyncio
import os
from app.chat_history_manager import ChatHistoryItem, ChatHistoryManager
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import START, MessagesState, StateGraph
from app.utils.utilities import setup_logging
import logging
from app import constants

setup_logging()
logger = logging.getLogger(__name__)
print(f"logger {__name__}")

def get_parent_directory():
    directory = os.path.dirname(__file__)
    parent_directory = os.path.dirname(directory)
    return parent_directory

class SessionManager:
    def __init__(self):
        self.active_sessions: dict = {}
    
    def create_session(self, project_id: str):
        """Create a session and store the LLM instance"""
        user_session = UserSession(project_id)
        self.active_sessions[project_id] = user_session
    
    def get_session(self, project_id: str):
        """Get the session for a user create it if it does not exist"""
        if project_id not in self.active_sessions:
            self.create_session(project_id)
            print("Creating session")
        else:
            print("Session already established")
            
        return self.active_sessions[project_id]
    
    
class UserSession:
    def __init__(self, project_id):
        logger.debug(f"ENTERING UserSession.__init__ with project_id={project_id} and system_prompt={system_prompt}")    
        self._db_path = f"{get_parent_directory()}/resources/checkpoints.db"
        self._model = init_chat_model("llama3.2:1b", model_provider="ollama")
        self.project_id = project_id                  
        self.chat_history_manager = ChatHistoryManager.singleton()
        active_chat = self.chat_history_manager.get_active_chat(self.project_id)
        logger.debug(f"IN active_chat={active_chat}")    
        if active_chat is None:
            logger.debug(f"IN before create_chat_history_item")  
            chat_item = ChatHistoryItem(project_id=self.project_id)
            self.chat_history_manager.create_chat_history_item(chat_item)
            logger.debug(f"IN after create_chat_history_item")   
        
        #active_chat = self.chat_history_manager.get_active_chat(self.project_id)
        #logger.debug(f"IN active_chat={active_chat}")   
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = constants.DEFAULT_SYSTEM_PROMPT
        self.graph = self._create_graph()
        
        
    def _create_graph(self):    
        #TODO THIS DOES NOT LOOK RIGHT    
        trimmer = trim_messages(
            max_tokens=6_500_000,
            strategy="last",
            token_counter=self._model,
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
            response = self._model.invoke(prompt)
            return {"messages": [response]}

        graph.add_edge(START, "model")
        graph.add_node("model", call_model)

        return graph


    def create_new_chat(self, chat_history_item: ChatHistoryItem):
        logger.debug(f"ENTERING create_new_chat with={self.project_id}")
        active_chat = self.chat_history_manager.get_active_chat(self.project_id)
        logger.debug(f"active_chat == {active_chat}")
        if active_chat:
            number_of_messages_in_current_chat = self.get_chat_interactions_count(active_chat['chat_id'])
            if number_of_messages_in_current_chat == 0:
                # If we have not had any interaction on the active chat just remove it
                self.chat_history_manager.delete_chat_history_item(active_chat['chat_id'])
        
        new_chat = self.chat_history_manager.create_chat_history_item(chat_history_item)
        logger.debug(f"EXITING create_new_chat with={new_chat}")
        return new_chat
    

    def get_chat_interactions_count(self, chat_id):
        logger.debug(f"ENTERING get_chat_interactions_count with={chat_id}")
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
        logger.debug(f"EXITING get_chat_interactions_count with={interactions_count}")
        return interactions_count
            

    async def stream_llm(self, websocket: WebSocket, prompt: str):
        input_messages = [HumanMessage(prompt)]
        active_chat = self.chat_history_manager.get_active_chat(self.project_id)
        print(f"self.project_id={self.project_id} active_chat={active_chat}")
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
            print("Streaming task was canceled.")
        finally:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text("[DONE]")
