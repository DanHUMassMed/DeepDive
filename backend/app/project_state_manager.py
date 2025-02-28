from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from app.utils.logging_utilities import setup_logging, trace
from app.base_manager import BaseManager
from app import constants
import inspect
from dataclasses import asdict


logger = setup_logging()
    
@dataclass
class ProjectStateItem:
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_llm_name: Optional[str] = None
    project_system_prompt: Optional[str] = None
    project_data_dir: Optional[str] = None
    project_data_toggle: Optional[bool] = False


class ProjectStateManager(BaseManager):
    @trace(logger)
    def get_project_state(self, project_id):
        """Return a project state item for the given project_id."""
        return_fields=['project_name', 'project_start_date', 'project_llm_name', 'project_system_prompt', 'project_data_dir', 'project_data_toggle']
        ret_val = {'status':'FAILED', 'status_code':404, 'message':f"Project id [{project_id}] not found."}
        try:
            found = self._search('project_id', project_id, return_fields)
            logger.debug(f"{found=}")
            if 'project_name' in found:
                ret_val = found
        except Exception as err:
            class_name = self.__class__.__name__ if hasattr(self, '__class__') else 'UnknownClass'
            method_name = inspect.currentframe().f_code.co_name
            logger.error(f"Exception in {class_name}.{method_name} {err}")            
            ret_val = {'status':'FAILED', 'status_code':500, 'message':str(err)}
        return ret_val

        
    @trace(logger)
    def create_project_state(self, project_state_item: ProjectStateItem):
        """Create a new project state item to the list."""
        ret_val = {'status':'FAILED', 'status_code':500, 'message':'create_project_state failed to return a state'}
        # Ensure project_name is unique
        if self._search('project_id', project_state_item.project_name):
            return {'status':'FAILED', 'status_code':400, 
                    'message':f"Project Name [{project_state_item.project_name}] already exists. Project name must be unique."}
            
        try:
            project_state_to_create = {}
            project_state_to_create['project_id'] = project_state_item.project_name
            project_state_to_create['project_name'] = project_state_item.project_name
            project_state_to_create['project_start_date'] = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
            chat_history_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
            project_state_to_create['chat_history_timestamp'] = chat_history_timestamp

            # Set project_llm_name if it is provided use defaults if not provided
            if project_state_item.project_llm_name:
                project_state_to_create['project_llm_name'] = project_state_item.project_llm_name
            else:
                project_state_to_create['project_llm_name'] = constants.DEFAULT_LLM
                        
            # Set project_system_prompt if it is provided use defaults if not provided
            if project_state_item.project_system_prompt:
                project_state_to_create['project_system_prompt'] = project_state_item.project_system_prompt
            else:
                project_state_to_create['project_system_prompt'] = constants.DEFAULT_SYSTEM_PROMPT

            if project_state_item.project_data_dir:
                project_state_to_create['project_data_dir'] = project_state_item.project_data_dir

            project_state_to_create['project_data_toggle'] = project_state_item.project_data_toggle
            
            project_state_to_create['chat_history_items'] = []
            
            # Add the new project state item to the data
            self._insert(project_state_to_create)
            ret_val = project_state_to_create
        except Exception as err:
            class_name = self.__class__.__name__ if hasattr(self, '__class__') else 'UnknownClass'
            method_name = inspect.currentframe().f_code.co_name
            logger.error(f"Exception in {class_name}.{method_name} {err}")            
            ret_val = {'status':'FAILED', 'status_code':500, 'message':str(err)}
        
        return ret_val

    @trace(logger)
    def update_project_state(self, project_state_item: ProjectStateItem):
        """Update a project state item that is in the list."""
        ret_val = {'status':'FAILED', 'status_code':500, 'message':'update_project_state failed to return a state'}
        try:
            project_state_to_update = self._search('project_id', project_state_item.project_name)
            logger.debug(f"{project_state_to_update=}")
            # Ensure project_id is found
            if 'project_id' not in  project_state_to_update:
                return {'status':'FAILED', 'status_code':404, 
                    'message':f"project_name [{project_state_item.project_name}] not found to update_project_state. "}
            
            updated_fields = {}
            # Set project_llm_name if it is provided
            if project_state_item.project_llm_name:
                updated_fields['project_llm_name'] = project_state_item.project_llm_name
            
            # Set project_system_prompt if it is provided
            if project_state_item.project_system_prompt:
                updated_fields['project_system_prompt'] = project_state_item.project_system_prompt
            
            if project_state_item.project_data_dir:
                updated_fields['project_data_dir'] = project_state_item.project_data_dir

            updated_fields['project_data_toggle'] = project_state_item.project_data_toggle
        
            self._update('project_id', project_state_item.project_name, updated_fields)
            ret_val = asdict(project_state_item)
        except Exception as err:
            class_name = self.__class__.__name__ if hasattr(self, '__class__') else 'UnknownClass'
            method_name = inspect.currentframe().f_code.co_name
            logger.error(f"Exception in {class_name}.{method_name} {err}")            
            ret_val = {'status':'FAILED', 'status_code':500, 'message':str(err)}
        
        return ret_val

    @trace(logger)
    def delete_project_state(self, project_id):
        """Delete project state item for the given project_id."""
        ret_val = {'status':'SUCCESS', 'status_code':200}
        try:
            found = self._search('project_id', project_id,['project_id'])
            if 'project_id' in found:
                self._delete('project_id', project_id)
            else:
                ret_val = {'status':'FAILED', 'status_code':404, 'message':f"Project id [{project_id}] not found."}
        except Exception as err:
            class_name = self.__class__.__name__ if hasattr(self, '__class__') else 'UnknownClass'
            method_name = inspect.currentframe().f_code.co_name
            logger.error(f"Exception in {class_name}.{method_name} {err}")            
            ret_val = {'status':'FAILED', 'status_code':500, 'message':str(err)}
            
        return ret_val
               
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

        
