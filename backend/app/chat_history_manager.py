import json
import os
import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Optional
import logging

from pydantic.dataclasses import dataclass
# Configure the logger
logging.basicConfig(
    filename='debug.log',        # Log file name
    filemode='a',              # Append mode; use 'w' to overwrite
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.DEBUG       # Set the logging level
)

@dataclass
class ChatHistoryItem:
    project_id: str
    chat_id: Optional[str] = None
    chat_start_date: Optional[str] = None  
    chat_title: Optional[str] = None
    chat_llm_name: Optional[str] = None
    active_chat: Optional[bool] = None
    

class ChatHistoryManager:
    _instance = None
    _file_name = "resources/chat_history.json"
    
    def __init__(self):
        if ChatHistoryManager._instance is not None:
            raise Exception("This class is a singleton! Use get_chat_history_manager() to get the instance.")
        self.chat_history_data = self._load_chat_history()

    @classmethod
    def singleton(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_chat_history(self):
        """Load chat history from the JSON file or return an empty list if the file doesn't exist."""
        if os.path.exists(self._file_name):
            with open(self._file_name, 'r') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def _save_chat_history(self):
        """Save the current chat history data to the JSON file. Ensure the directory exists."""
        # Get the directory from the file name
        directory = os.path.dirname(self._file_name)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write the data to the file
        with open(self._file_name, 'w') as file:
            json.dump(self.chat_history_data, file, indent=4)

    def get_chat_history(self, project_id):
        """Return a list of chat history items for the given project_id."""
        return [item for item in self.chat_history_data if item['project_id'] == project_id]

    def delete_chat_history(self, project_id):
        """Delete all chat history items for the given project_id and save the updated list to disk."""
        self.chat_history_data = [item for item in self.chat_history_data if item['project_id'] != project_id]
        self._save_chat_history()

    
    def create_chat_history_item(self, chat_history_item: ChatHistoryItem):
        """Add a new chat history item to the list if the chat_id is unique and set active_chat=True."""

        # Ensure chat_id is unique; if not provided, generate one
        if not chat_history_item.chat_id:
            chat_history_item.chat_id = str(uuid.uuid4())
        else:
            for item in self.chat_history_data:
                if item.chat_id == chat_history_item.chat_id:
                    raise Exception(f"Chat ID {chat_history_item.chat_id} already exists. Chat ID must be unique.")

        # Ensure project_id is provided
        if not chat_history_item.project_id:
            raise Exception("project_id must be provided for chat history.")

        # Set the current date and time if not provided
        if not chat_history_item.chat_start_date:
            #chat_history_item.chat_start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            chat_history_item.chat_start_date = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')

        # Set the chat_title if not provided or blank
        if not chat_history_item.chat_title:
            chat_history_item.chat_title = f"Chat on {chat_history_item.chat_start_date}"

        # Set chat_llm_name if not provided or blank
        if not chat_history_item.chat_llm_name:
            chat_history_item.chat_llm_name = 'deep.seekr1:32b'

        # Set the new chat's active_chat to True
        chat_history_item.active_chat = True

        # Set active_chat for other items of the same user to False
        self._set_active_chat_for_user(chat_history_item.project_id, chat_history_item.chat_id)

        # Add the new chat history item to the data
        self.chat_history_data.insert(0, asdict(chat_history_item))

        # Save the updated chat history data to disk
        self._save_chat_history()
        
        return asdict(chat_history_item)
        
        
    def update_chat_history_item_title(self, chat_id, chat_title):
        """Update an existing chat history item if found, and save the updated list to disk."""
        for idx, existing_item in enumerate(self.chat_history_data):
            if existing_item['chat_id'] == chat_id:
                existing_item['chat_title'] = chat_title
                self.chat_history_data[idx] = existing_item
                self._save_chat_history()
                return
            else:
                raise Exception(f"Chat ID {chat_id} not found.")
        
    
    def update_chat_history_item_model_name(self, chat_id, chat_llm_name):
        """Update an existing chat history item if found, and save the updated list to disk."""
        for idx, existing_item in enumerate(self.chat_history_data):
            if existing_item['chat_id'] == chat_id:
                existing_item['chat_llm_name'] = chat_llm_name
                self.chat_history_data[idx] = existing_item
                self._save_chat_history()
                return
            else:
                raise Exception(f"Chat ID {chat_id} not found.")
        
        

    def delete_chat_history_item(self, chat_id):
        """Delete a specific chat history item by chat_id and return the remaining items for the user."""
        for idx, existing_item in enumerate(self.chat_history_data):
            if existing_item['chat_id'] == chat_id:
                project_id = existing_item['project_id']
                del self.chat_history_data[idx]
                self._save_chat_history()
                return self.get_chat_history(project_id)
        return []  # Item not found

    def get_active_chat(self, project_id):
        """Return the active chat history item for the given project_id."""
        for item in self.chat_history_data:
            if item['project_id'] == project_id and item['active_chat']:
                return item
        return None  # No active chat found

    def set_active_chat(self, chat_id):
        """Set the active chat for the user related to the given chat_id."""
        for item in self.chat_history_data:
            if item['chat_id'] == chat_id:
                project_id = item['project_id']
                self._set_active_chat_for_user(project_id, chat_id)
                self._save_chat_history()
                return
        raise Exception(f"Chat ID {chat_id} not found.")

    def _set_active_chat_for_user(self, project_id, chat_id):
        """Set the provided chat_id's active_chat to True and all others for the same user to False."""
        for item in self.chat_history_data:
            if item['project_id'] == project_id:
                if item['chat_id'] == chat_id:
                    item['active_chat'] = True
                else:
                    item['active_chat'] = False