import json
import os
import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
import logging
from app.utils.utilities import setup_logging

logger = setup_logging()
    
    
class BaseManager:
    _instance = None
    _file_name = "resources/project_state.json"
    project_state_data = None  # Class variable

    def __init__(self):
        if BaseManager._instance is not None:
            raise Exception("This class is a singleton! Use singleton() to get the instance.")
        if BaseManager.project_state_data is None:
            BaseManager.project_state_data = self._load_project_state()

    @classmethod
    def singleton(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_parent_directory(self):
        directory = os.path.dirname(__file__)
        parent_directory = os.path.dirname(directory)
        return parent_directory

    def _load_project_state(self):
        """Load project state from the JSON file or return an empty dictionary if the file doesn't exist."""
        chat_history_json = f"{self._get_parent_directory()}/{self._file_name}"
        if os.path.exists(chat_history_json):
            with open(chat_history_json, 'r', encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    logger.error(f"Error loading JSON from file: {chat_history_json}")
                    return []
        return []

    def _save_project_state(self):
        """Save the current project state data to the JSON file. Ensure the directory exists."""
        chat_history_json = f"{self._get_parent_directory()}/{self._file_name}"
        directory = os.path.dirname(chat_history_json)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(chat_history_json, 'w', encoding="utf-8") as file:
            json.dump(self.project_state_data, file, indent=4)
            
    def _search(self, key, value, return_fields=None):
        """Search for a dictionary in project_state_data where key matches value."""
        # Find the first matching item
        item = next((item for item in self.project_state_data if item.get(key) == value), None)
        
        if item is None:
            return None  # No matching item found
        
        if return_fields is None:
            return item  # Return all fields if return_fields is None
        
        # Return only the specified fields
        return {field: item.get(field) for field in return_fields if field in item}

    def _delete(self, key, value):
        """Delete the first dictionary in project_state_data where key matches value."""
        self.project_state_data = [
            item for item in self.project_state_data if item.get(key) != value
        ]
        self._save_project_state()
        
    def _update(self, key, value, updated_fields):
        """Update the first dictionary in project_state_data where key matches value."""
        for item in self.project_state_data:
            if item.get(key) == value:
                item.update(updated_fields)
                self._save_project_state()
                return item
        
        raise KeyError(f"Item with {key} = {value} not found.")