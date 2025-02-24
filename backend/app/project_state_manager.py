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

logger = setup_logging()
    

class ProjectStateManager(BaseManager):
    
    def get_project_state(self, project_id):
        """Return a project state item for the given project_id."""
        return_fields=['project_name','project_start_date','chat_history_timestamp']
        return self._search('project_id', project_id, return_fields)

    def delete_project_state(self, project_id):
        """Delete project state item for the given project_id and save the updated list to disk."""
        self._delete('project_id', project_id)
    
    def create_project_state(self, project_name):
        """Add a new project state item to the list."""
        project_state_item = {}
        
        # Ensure project_name is unique; 
        if self._search('project_id', project_name):
            return {'Error':f"Project Name {project_name} already exists. Project name must be unique."}

        project_state_item['project_id'] = project_name 
        project_state_item['project_name'] = project_name
        project_state_item['project_start_date']=datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
        chat_history_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
        project_state_item['chat_history_timestamp'] = chat_history_timestamp
        project_state_item['chat_history_items'] = []
        
        # Add the new project state item to the data
        self.project_state_data.insert(0, project_state_item)

        # Save the updated chat history data to disk
        self._save_project_state()
        
        return project_state_item
                            

    def get_chat_history_timestamp(self, project_id):
        """Get an existing project state item if found, and return chat_history_timestamp"""
        return_fields = ['chat_history_timestamp']
        return self._search('project_id', project_id, return_fields)
        
