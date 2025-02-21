from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import asyncio
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import sqlite3
from app.chat_history_manager import ChatHistoryManager


class SessionManager:
    def __init__(self):
        # A dictionary to store active sessions keyed by client tokens
        # Currently we expect only one active session DeepDive
        self.active_sessions: dict = {}
    
    def create_session(self, project_id: str):
        """Create a session and store the LLM instance"""
        user_session = UserSession(project_id)
        self.active_sessions[project_id] = user_session
    
    def get_session(self, project_id: str):
        """Get the session for a user"""
        if project_id not in self.active_sessions:
            self.create_session(project_id)
            print("Creating session")
        else:
            print("Session already established")
            
        return self.active_sessions[project_id]
    
    
class UserSession:
    def __init__(self, project_id, system_prompt=None):    
        self.db_path = 'checkpoints.db'
        self.model = init_chat_model("deepseek-r1:32b", model_provider="ollama")
        self.project_id = project_id
        self.chatHistoryManager = ChatHistoryManager.get_chat_history_manager()
        self.graph = self.create_graph(system_prompt)
        
        
    def create_graph(self, system_prompt=None):        
        trimmer = trim_messages(
            max_tokens=6_500_000,
            strategy="last",
            token_counter=self.model,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )

        if not system_prompt:
            system_prompt = "Answer all questions to the best of your ability. Answer concisely but correctly. If you do not know the answer, just say 'I don’t know.'"
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        graph = StateGraph(state_schema=MessagesState)

        def call_model(state: MessagesState):
            trimmed_messages = trimmer.invoke(state["messages"])
            prompt = prompt_template.invoke({"messages": trimmed_messages})
            response = self.model.invoke(prompt)
            return {"messages": [response]}

        graph.add_edge(START, "model")
        graph.add_node("model", call_model)

        return graph


    async def stream_llm(self, websocket: WebSocket, prompt: str):
        input_messages = [HumanMessage(prompt)]
        chat_id = self.chatHistoryManager.get_active_chat(self.project_id)
        config = {"configurable": {"thread_id": chat_id}}

        try:
            async with AsyncSqliteSaver.from_conn_string(self.db_path) as saver:
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
