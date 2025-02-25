import json
import os
import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
import logging
from app.utils.utilities import open_ollama, setup_logging
from app.base_manager import BaseManager
from app import constants

logger = setup_logging()
    
@dataclass
class ProjectStateItem:
    project_name: str
    project_llm_name: Optional[str] = None
    project_system_prompt: Optional[str] = None



class ProjectStateManager(BaseManager):
    
    def get_project_state(self, project_id):
        """Return a project state item for the given project_id."""
        return_fields=['project_name', 'project_start_date', 'project_llm_name', 'project_system_prompt']
        return self._search('project_id', project_id, return_fields)

    def delete_project_state(self, project_id):
        """Delete project state item for the given project_id and save the updated list to disk."""
        self._delete('project_id', project_id)
    
    def create_project_state(self, project_state_item: ProjectStateItem):
        """Add a new project state item to the list."""
        
        # Ensure project_name is unique; 
        if self._search('project_id', project_state_item.project_name):
            return {'Error':f"Project Name {project_state_item.project_name} already exists. Project name must be unique."}

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

        project_state_to_create['chat_history_items'] = []
        
        # Add the new project state item to the data
        self.project_state_data.insert(0, project_state_to_create)

        # Save the updated chat history data to disk
        self._save_project_state()
        
        return project_state_to_create

    def update_project_state(self, project_state_item: ProjectStateItem):
        """Add a new project state item to the list."""
        project_state_to_update = self._search('project_id', project_state_item.project_name)
        # Ensure project_id is found
        if not project_state_to_update:
            raise Exception(f"project_name not found to update_project_state. {project_state_item.project_name} ")
        
        updated_fields = {}
        # Set project_llm_name if it is provided
        if project_state_item.project_llm_name:
            updated_fields['project_llm_name'] = project_state_item.project_llm_name
           
        # Set project_system_prompt if it is provided
        if project_state_item.project_system_prompt:
            updated_fields['project_system_prompt'] = project_state_item.project_system_prompt
            
        self._update('project_id', project_state_item.project_name, updated_fields)
        return {'status':'SUCCESS'}
               

    def get_chat_history_timestamp(self, project_id):
        """Get an existing project state item if found, and return chat_history_timestamp"""
        return_fields = ['chat_history_timestamp']
        return self._search('project_id', project_id, return_fields)
        
