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
    def __init__(self, project_id, system_prompt=None):    
        self._db_path = f"{get_parent_directory()}/resources/checkpoints.db"
        self._model = init_chat_model("deepseek-r1:32b", model_provider="ollama")
        self.project_id = project_id                  
        self.chat_history_manager = ChatHistoryManager.singleton()
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = "Answer all questions to the best of your ability. Answer concisely but correctly. If you do not know the answer, just say 'I don’t know.'"
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
        print(f"IN create_new_chat {self.project_id}")
        active_chat = self.chat_history_manager.get_active_chat(self.project_id)
        print(f"active_chat == {active_chat}")
        if active_chat is not None:
            number_of_messages_in_current_chat = self.get_chat_interactions_count(active_chat['chat_id'])
            if number_of_messages_in_current_chat == 0:
                self.chat_history_manager.delete_chat_history_item(active_chat['chat_id'])
        new_chat = self.chat_history_manager.create_chat_history_item(chat_history_item)

        # new_chat =     {
        #     "project_id": "deep-dive",
        #     "chat_id": "8b353d98-8705-48e8-ab9b-a4f4863f707f",
        #     "chat_start_date": "2025-02-21 07:56:55 AM",
        #     "chat_title": "Chat on FME",
        #     "chat_llm_name": "deep.seekr1:32b",
        #     "active_chat": True
        # }

        return new_chat
    

    def get_chat_interactions_count(self, chat_id):
        print("IN get_chat_interactions_count")
        interactions_count = 0
        with SqliteSaver.from_conn_string(self._db_path) as checkpointer:            
            config = {"configurable": {"thread_id": chat_id}}
            print("before compiled_graph")
            compiled_graph = self.graph.compile(checkpointer=checkpointer)
            print("after compiled_graph")
            state_history = compiled_graph.get_state_history(config) 
            print("after state_history")
            last_interaction = next(state_history, None)
            print("after last_interaction")
            if last_interaction:
                values = last_interaction.values  
                if 'messages' in values:
                    interactions_count = len(values['messages'])
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
