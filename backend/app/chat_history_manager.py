import logging
import uuid
from dataclasses import asdict, field
from datetime import datetime
from typing import List, Optional

from app import constants
from app.base_manager import BaseManager
from app.project_state_manager import ProjectStateManager
from app.utils.utilities import setup_logging, trace
from pydantic.dataclasses import dataclass

logger = setup_logging()


@dataclass
class ChatHistoryItem:
    project_id: str
    chat_id: Optional[str] = None
    chat_start_date: Optional[str] = None
    chat_title: Optional[str] = None
    chat_llm_name: Optional[str] = None
    active_chat: Optional[bool] = None
      

class ChatHistoryManager(BaseManager):
    @trace(logger)
    def get_chat_history(self, project_id):
        """Return a list of chat history items for the given project_id."""
        return_fields = ['chat_history_items']
        search_results = self._search('project_id', project_id, return_fields)
        return search_results.get('chat_history_items', None)

    @trace(logger)
    def delete_chat_history(self, project_id):
        """Delete all chat history items for the given project_id and save the updated list to disk."""
        update_fields= { 'chat_history_items':[] }
        self._update('project_id', project_id, update_fields)
        self._update_chat_history_timestamp(project_id)
    
    @trace(logger)
    def create_chat_history_item(self, chat_history_item: ChatHistoryItem):
        """Add a new chat history item to the list if the chat_id is unique and set active_chat=True."""

        # Ensure project_id is provided
        if not chat_history_item.project_id:
            raise Exception("project_id must be provided for chat history.")

        # Get the chat history for this project id
        chat_history_items = self.get_chat_history(chat_history_item.project_id)

        # We need a new chat_id 
        chat_history_item.chat_id = str(uuid.uuid4())

        # Add a start date for the chat
        chat_history_item.chat_start_date = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')

        # Set the chat_title if it is not provided or blank
        if not chat_history_item.chat_title:
            chat_history_item.chat_title = f"Chat on {chat_history_item.chat_start_date}"

        # Set chat_llm_name if it is not provided or blank
        project_state_manager = ProjectStateManager.singleton()
        project_state = project_state_manager.get_project_state(chat_history_item.project_id)
        chat_history_item.chat_llm_name = project_state['project_llm_name']
        

        # Set this as the active_chat
        chat_history_item.active_chat = True
        self._set_active_chat(chat_history_items, chat_history_item.chat_id)

        # Add the new chat history item to the data
        chat_history_items.insert(0, asdict(chat_history_item))
        
        # Save the updated chat_history_items
        self._update_chat_and_timestamp(chat_history_item.project_id, chat_history_items)

        return asdict(chat_history_item)

        
    @trace(logger)
    def update_chat_history_item_title(self, chat_history_item: ChatHistoryItem):
        """Update an existing chat history item if found, and save the updated list to disk."""
        logger.debug(f"ENTERING update_chat_history_item_title with={chat_history_item.chat_id} and title={chat_history_item.chat_title}")
        chat_history_items = self.get_chat_history(chat_history_item.project_id)

        for idx, existing_item in enumerate(chat_history_items):
            logger.debug(f"IN 1")
            if existing_item['chat_id'] == chat_history_item.chat_id:
                logger.debug(f"IN 2")
                existing_item['chat_title'] = chat_history_item.chat_title
                chat_history_items[idx] = existing_item
                
                # Save the updated chat_history_items
                self._update_chat_and_timestamp(chat_history_item.project_id, chat_history_items)
                return existing_item
            
        logger.debug(f"EXITING Exception: Chat ID {chat_history_item.chat_id} not found.")
        raise Exception(f"Chat ID {chat_history_item.chat_id} not found.")
              
    @trace(logger)
    def delete_chat_history_item(self, chat_history_item: ChatHistoryItem):
        """Delete a specific chat history item by chat_id and return status"""
        chat_history_items = self.get_chat_history(chat_history_item.project_id)
        for idx, existing_item in enumerate(chat_history_items):
                if existing_item['chat_id'] == chat_history_item.chat_id:
                    del chat_history_items[idx]
                    
                    # If the deleted chat was the active chat select a new active chat
                    # The new active chat is always the newest chat in the list
                    if existing_item['active_chat']:
                        if len(chat_history_items)>0:
                            self._set_active_chat(chat_history_items, chat_history_items[0]['chat_id'])
                    # Save the updated chat_history_items
                    self._update_chat_and_timestamp(chat_history_item.project_id, chat_history_items)
                    return {'status':'SUCCESS'}
        return {'status':'FAIL'}

    @trace(logger)
    def get_active_chat(self, project_id):
        """Return the active chat history item for the given project_id."""
        chat_history_items = self.get_chat_history(project_id)
        for item in chat_history_items:
            if item['active_chat']:
                return item
        return {}  # No active chat found

    @trace(logger)
    def set_active_chat(self, chat_history_item: ChatHistoryItem):
        logger.debug(f"FME")
        """Set the active chat for the user related to the given chat_id."""
        chat_history_items = self.get_chat_history(chat_history_item.project_id)
        logger.debug(f"{chat_history_items=}")
        for item in chat_history_items:
            logger.debug(f"{item}")
            if item['chat_id'] == chat_history_item.chat_id:
                item['active_chat'] = True
                self._set_active_chat(chat_history_items, chat_history_item.chat_id)
                # Save the updated chat_history_items
                self._update_chat_and_timestamp(chat_history_item.project_id, chat_history_items)
                return item
        raise Exception(f"Chat ID {chat_history_item.chat_id} not found.")

    @trace(logger)
    def _set_active_chat(self, chat_history_data, chat_id):
        """Set the provided chat_id's active_chat to True and all others for the same user to False."""
        for item in chat_history_data:
            if item['chat_id'] == chat_id:
                item['active_chat'] = True
            else:
                item['active_chat'] = False
                
        return chat_history_data
                    
    @trace(logger)
    def _update_chat_history_timestamp(self, project_id):
        """Update an existing project state item if found, and save the updated list to disk."""
        chat_history_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
        update_fields= { 'chat_history_timestamp':chat_history_timestamp }
        self._update('project_id', project_id, update_fields)
        
    @trace(logger)
    def _update_chat_and_timestamp(self, project_id, chat_history_items):
        # Save the updated chat_history_items
        update_fields= { 'chat_history_items':chat_history_items }
        self._update('project_id', project_id, update_fields)
        self._update_chat_history_timestamp(project_id)
        

