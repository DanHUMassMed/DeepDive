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
class ProjectState:
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    chat_history_timestamp: Optional[str] = ''  
    project_start_date: Optional[str] = None
    

class ProjectStateManager:
    _instance = None
    _file_name = "resources/project_state.json"
    
    def __init__(self):
        if ProjectStateManager._instance is not None:
            raise Exception("This class is a singleton! Use sigleton() to get the instance.")
        self.project_state_data = self._load_project_state()

    @classmethod
    def singleton(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_project_state(self):
        """Load project state from the JSON file or return an empty list if the file doesn't exist."""
        if os.path.exists(self._file_name):
            with open(self._file_name, 'r', encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def _save_project_state(self):
        """Save the current project state data to the JSON file. Ensure the directory exists."""
        # Get the directory from the file name
        directory = os.path.dirname(self._file_name)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write the data to the file
        with open(self._file_name, 'w', encoding="utf-8") as file:
            json.dump(self.project_state_data, file, indent=4)

    def get_project_state(self, project_id):
        """Return a project state item for the given project_id."""
        for item in self.project_state_data:
            if item['project_id'] == project_id:
                return item
            else:
                return None

    def delete_project_state(self, project_id):
        """Delete project state item for the given project_id and save the updated list to disk."""
        self.project_state_data = [item for item in self.project_state_data if item['project_id'] != project_id]
        self._save_project_state()

    
    def create_project_state(self, project_state: ProjectState):
        """Add a new project state item to the list."""

        # Ensure project_id is unique; if not provided, generate one
        if not project_state.project_id:
            project_state.project_id = str(uuid.uuid4())
        else:
            for item in self.project_state_data:
                if item.project_id == project_state.project_id:
                    raise Exception(f"Project Id {project_state.project_id} already exists. Project Id must be unique.")

        # Ensure project_id is provided
        if not project_state.project_id:
            raise Exception("project_id must be provided for project state.")

        # Set the current date and time if not provided
        if not project_state.project_start_date:
            project_state.project_start_date = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')

        # Set the project_name if not provided or blank
        if not project_state.project_name:
            project_state.project_name = f"Project on {project_state.project_start_date}"
       
        # Add the new project state item to the data
        self.project_state_data.insert(0, asdict(project_state))

        # Save the updated chat history data to disk
        self._save_project_state()
        
        return asdict(project_state)
        
        
    def update_project_state_name(self, project_id, project_name):
        """Update an existing project state item if found, and save the updated list to disk."""
        for idx, existing_item in enumerate(self.project_state_data):
            if existing_item['project_id'] == project_id:
                existing_item['project_name'] = project_name
                self.project_state_data[idx] = existing_item
                self._save_project_state()
                return
            else:
                raise Exception(f"Project Id {project_id} not found.")
            
    def update_project_state_chat_history_timestamp(self, project_id):
        """Update an existing project state item if found, and save the updated list to disk."""
        # Get the current timestamp with milliseconds
        chat_history_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
        
        for idx, existing_item in enumerate(self.project_state_data):
            if existing_item['project_id'] == project_id:
                existing_item['chat_history_timestamp'] = chat_history_timestamp
                self.project_state_data[idx] = existing_item
                self._save_project_state()
                return chat_history_timestamp
        else:
            raise Exception(f"Project Id {project_id} not found.")
        