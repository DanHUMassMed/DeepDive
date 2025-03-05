import json
import os
import threading
from app.utils.workspace_utilities import get_project_workspace

from app.utils.logging_utilities import setup_logging

logger = setup_logging()
    
    
class BaseManager:
    """
    Singleton class to manage and load project state json from a file.
    """
    _instance = None
    _file_name = "project_state.json"
    _lock = threading.Lock()  # Lock for synchronization
 

    def __init__(self):
        if BaseManager._instance is not None:
            raise Exception("This class is a singleton! Use singleton() to get the instance.")
        
        self._file_name = f"{get_project_workspace()}/{self._file_name}"
            
        with BaseManager._lock:
            self.project_state_data = self._load_project_state()

            
    @classmethod
    def singleton(cls):
        """
        Returns the single instance of the class it is called on (including subclasses).
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_project_state(self):
        """Load project state from the JSON file or return an empty dictionary if the file doesn't exist."""
        if os.path.exists(self._file_name):
            with open(self._file_name, 'r', encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    logger.error(f"Error loading JSON from file: {self._file_name}")
                    return []
        return []

    def __save_project_state(self):
        """Save the current project state data to the JSON file. Ensure the directory exists."""
        # Note: This method is only called when we already have a lock on project_state_data
        with open(self._file_name, 'w', encoding="utf-8") as file:
            json.dump(self.project_state_data, file, indent=4)
            
    def _search(self, key, value, return_fields=None):
        """Search for a dictionary in project_state_data where key matches value."""
        # Find the first matching item
        # logger.debug(f"_search {key} {value} {return_fields}")
        # logger.debug(json.dumps(self.project_state_data, indent=4))
        item = next((item for item in self.project_state_data if item.get(key) == value), None)
        
        if item is None:
            return {}  # No matching item found
        
        if return_fields is None:
            return item  # Return all fields if return_fields is None
        
        # Return only the specified fields
        return {field: item.get(field) for field in return_fields if field in item}

    def _insert(self, new_data):
        """Insert a new project state item"""
        # Use lock to ensure thread-safe updates to project_state_data
        with BaseManager._lock:
            self.project_state_data.insert(0, new_data)
            self.__save_project_state()

    def _update(self, key, value, updated_fields):
        """Update the first dictionary in project_state_data where key matches value."""
        with BaseManager._lock:
            for i, item in enumerate(self.project_state_data):
                if item.get(key) == value:
                    # Update the dictionary in place
                    self.project_state_data[i].update(updated_fields)
                    self.__save_project_state()
                    logger.debug("Successfully updated the project state data.")
                    return self.project_state_data[i]
            logger.debug("No matching item found to update.")
            return None
            raise KeyError(f"Item with {key} = {value} not found.")
    
    def _delete(self, key, value):
        """Delete the first dictionary in project_state_data where key matches value."""
        with BaseManager._lock:
            self.project_state_data = [
                item for item in self.project_state_data if item.get(key) != value
            ]
            self.__save_project_state()
        
