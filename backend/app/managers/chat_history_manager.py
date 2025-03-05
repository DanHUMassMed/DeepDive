import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Optional

from app.managers.base_manager import BaseManager
from app.managers.project_state_manager import ProjectStateManager
from app.utils.logging_utilities import setup_logging, trace
from pydantic.dataclasses import dataclass
import inspect

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
    """ The ChatHistoryManager manages the state for all Chat and History interactions"""
    
    @trace(logger)
    def get_chat_history_items(self, project_id):
        """Return a list of chat history items for the given project_id.
        Return an empty list if there are no items."""
        ret_val = {'status':'FAILED', 'status_code':404, 'message':f"Project id [{project_id}] not found."}
        try:
            found = self._search('project_id', project_id, ['chat_history_items'])
            found_chat_history_items = found.get('chat_history_items', [])
            return found_chat_history_items
        except Exception as err:
            class_name = self.__class__.__name__ if hasattr(self, '__class__') else 'UnknownClass'
            method_name = inspect.currentframe().f_code.co_name
            logger.error(f"Exception in {class_name}.{method_name} {err}")            
            ret_val = {'status':'FAILED', 'status_code':500, 'message':str(err)}
        return ret_val

    
    @trace(logger)
    def delete_chat_history_items(self, project_id):
        """Delete all chat history items for the given project_id."""
        try:
            found = self._search('project_id', project_id, ['chat_history_items'])
            if 'chat_history_items' in found:
                update_fields= { 'chat_history_items':[] }
                self._update('project_id', project_id, update_fields)
                self._update_chat_history_timestamp(project_id)
                ret_val = {'status':'SUCCESS', 'status_code':200}
            else:
                ret_val = {'status':'FAILED', 'status_code':404, 'message':f"Project id [{project_id}] not found."}
        except Exception as err:
            class_name = self.__class__.__name__ if hasattr(self, '__class__') else 'UnknownClass'
            method_name = inspect.currentframe().f_code.co_name
            logger.error(f"Exception in {class_name}.{method_name} {err}")            
            ret_val = {'status':'FAILED', 'status_code':500, 'message':str(err)}
        return ret_val

    @trace(logger)
    def get_active_chat(self, project_id):
        """Return the active chat history item for the given project_id."""
        chat_history_items_found = self.get_chat_history_items(project_id)
        if chat_history_items_found == []:
            return {'status': 'SUCCESS', 'status_code': 200, 
                    'message':'The list is empty so no active chat found'}
        elif isinstance(chat_history_items_found,list):
            for item in chat_history_items_found:
                if item['active_chat']: # Find the active chat
                    return item
            return {'status':'FAILED', 'status_code':404, 
                   'message':f"No Active chat found for Project id [{project_id}]."}
        # We should not get here but if we do lets FAIL
        return {'status':'FAILED', 'status_code':500, 'message':'Failed to find active chat.'}


    @trace(logger)
    def set_active_chat(self, project_id, chat_id):
        """ Set the provided chat as the active chat and ensure all other chats are set to inactive"""
        ret_val = {'status':'FAILED',
                   'status_code':404, 
                   'message':f"No Chat found with id [{chat_id}]. Active chat not set"}
        chat_history_items_found = self.get_chat_history_items(project_id)
        if isinstance(chat_history_items_found, list):
            for item in chat_history_items_found:
                if item['chat_id'] == chat_id:
                    item['active_chat'] = True
                    self._set_active_chat(chat_history_items_found, chat_id)
                    self._update_chat_and_timestamp(project_id, chat_history_items_found)
                    return item
            return ret_val
        else:
            return chat_history_items_found


    @trace(logger)
    def create_chat_history_item(self, chat_history_item: ChatHistoryItem):
        """Add a new chat history item to the list and set as the active_chat=True."""

        # Ensure project_id is provided
        if not chat_history_item.project_id:
            return {'status':'FAILED',
                   'status_code':400, 
                   'message':f"A Project ID is required in the ChatHistoryItem but none was provided."}

        # Get the chat history for this project id
        chat_history_items_found = self.get_chat_history_items(chat_history_item.project_id)
        if isinstance(chat_history_items_found, dict):
            # If it is a dictionary it is an error message
            return chat_history_items_found
        
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
        self._set_active_chat(chat_history_items_found, chat_history_item.chat_id)

        # Add the new chat history item to the data
        chat_history_items_found.insert(0, asdict(chat_history_item))
        
        # Save the updated chat_history_items
        self._update_chat_and_timestamp(chat_history_item.project_id, chat_history_items_found)

        return asdict(chat_history_item)

        
    @trace(logger)
    def update_chat_history_item_title(self, chat_history_item: ChatHistoryItem):
        """Update an existing chat history item title."""
        ret_val_success = {'status':'SUCCESS', 'status_code':200}
        ret_val_error =  {'status':'FAILED', 'status_code':400, 'message':f"The Chat ID was not found [{chat_history_item.chat_id}]."}
        chat_history_items_found = self.get_chat_history_items(chat_history_item.project_id)
        if isinstance(chat_history_items_found, dict):
            # If it is a dictionary it is an error message
            return chat_history_items_found
        
        for idx, existing_item in enumerate(chat_history_items_found):
            if existing_item['chat_id'] == chat_history_item.chat_id:
                existing_item['chat_title'] = chat_history_item.chat_title
                chat_history_items_found[idx] = existing_item
                
                # Save the updated chat_history_items
                self._update_chat_and_timestamp(chat_history_item.project_id, chat_history_items_found)
                return ret_val_success
            
        return ret_val_error
              
    @trace(logger)
    def delete_chat_history_item(self, project_id, chat_id):
        """Delete a specific chat history item by chat_id and return status"""
        ret_val_success = {'status':'SUCCESS', 'status_code':200}
        ret_val_error =  {'status':'FAILED', 'status_code':400, 'message':f"The Chat ID was not found [{chat_id}]."}
        chat_history_items_response = self.get_chat_history_items(project_id)
        if isinstance(chat_history_items_response, dict) and 'status' in chat_history_items_response:
            if chat_history_items_response['status'] == 'FAILED':
                return chat_history_items_response

        for idx, existing_item in enumerate(chat_history_items_response):
                if existing_item['chat_id'] == chat_id:
                    del chat_history_items_response[idx]
                    # If the deleted chat was the active chat select a new active chat
                    # The new active chat is always the newest chat in the list
                    if existing_item['active_chat']:
                        if len(chat_history_items_response)>0:
                            self._set_active_chat(chat_history_items_response, chat_history_items_response[0]['chat_id'])
                    # Save the updated chat_history_items
                    self._update_chat_and_timestamp(project_id, chat_history_items_response)
                    return ret_val_success
                
        return ret_val_error

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
        update_fields= { 'chat_history_timestamp': chat_history_timestamp }
        return self._update('project_id', project_id, update_fields)
        
    @trace(logger)
    def _update_chat_and_timestamp(self, project_id, chat_history_items):
        # Save the updated chat_history_items
        update_fields= { 'chat_history_items':chat_history_items }
        self._update('project_id', project_id, update_fields)
        self._update_chat_history_timestamp(project_id)
        
        

    @trace(logger)
    def get_chat_history_timestamp(self, project_id):
        """Get an existing project state item if found, and return chat_history_timestamp."""
        ret_val = {'status':'FAILED', 'status_code':400, 'message':f"get_chat_history_timestamp failed to return a timestamp for [{project_id}]"}
        try:
            return_fields = ['chat_history_timestamp']
            chat_history_timestamp = self._search('project_id', project_id, return_fields)
            if len(chat_history_timestamp)==1:
                return chat_history_timestamp
        except Exception as err:
            class_name = self.__class__.__name__ if hasattr(self, '__class__') else 'UnknownClass'
            method_name = inspect.currentframe().f_code.co_name
            logger.error(f"Exception in {class_name}.{method_name} {err}")            
            ret_val = {'status':'FAILED', 'status_code':500, 'message':str(err)}
        
        return ret_val