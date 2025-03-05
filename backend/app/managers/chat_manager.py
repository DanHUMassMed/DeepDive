import asyncio
import inspect
import os

from app import constants
from app.managers.chat_history_manager import ChatHistoryItem, ChatHistoryManager
from app.managers.project_state_manager import ProjectStateManager
from app.utils.logging_utilities import setup_logging, trace
from app.utils.workspace_utilities import get_project_workspace
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import START, MessagesState, StateGraph

logger = setup_logging()

class ChatManager:
    @trace(logger)
    def __init__(self, llm_name = constants.DEFAULT_LLM, system_prompt = constants.DEFAULT_SYSTEM_PROMPT):
        self._db_path = f"{get_project_workspace()}/checkpoints.db"
        self._llm_name = llm_name
        self._system_prompt = system_prompt
    
    @property
    def llm_name(self):
        return self._llm_name

    @llm_name.setter
    def llm_name(self, value):
        if isinstance(value, str) and value:
            self._llm_name = value
        else:
            raise ValueError("llm_name must be a non-empty string")

    @property
    def system_prompt(self):
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value):
        if isinstance(value, str) and value:
            self._system_prompt = value
        else:
            raise ValueError("system_prompt must be a non-empty string")
    
    @trace(logger)
    def _create_prompt_and_reply_graph(self):
        model = init_chat_model(self.llm_name, model_provider="ollama")

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
                ("system", self.system_prompt),
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
    def get_chat_interactions_count(self, chat_id):
        #TODO There should be an easier and quicker way to get the interaction count
        interactions = self.get_chat_interactions(chat_id)
        return len(interactions) // 2
    
    @trace(logger)           
    def get_chat_interactions(self, chat_id):
        interactions=[]
        with SqliteSaver.from_conn_string(self._db_path) as checkpointer:            
            config = {"configurable": {"thread_id": chat_id}}
            prompt_and_reply_graph = self._create_prompt_and_reply_graph()
            compiled_graph = prompt_and_reply_graph.compile(checkpointer=checkpointer)
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


    async def stream_llm_responses(self, websocket: WebSocket, prompt: str, chat_id: str):
        input_messages = [HumanMessage(prompt)]
        config = {"configurable": {"thread_id": chat_id}}
        try:
            async with AsyncSqliteSaver.from_conn_string(self._db_path) as saver:
                prompt_and_reply_graph = self._create_prompt_and_reply_graph()
                compiled_graph = prompt_and_reply_graph.compile(checkpointer=saver)        
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
