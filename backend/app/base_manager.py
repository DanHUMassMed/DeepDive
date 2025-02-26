import json
import os
from app.utils.utilities import setup_logging
import threading

logger = setup_logging()
    
    
class BaseManager:
    """
    Singleton class to manage and load project state from a file.
    """
    _instance = None
    _file_name = "resources/project_state.json"
    _lock = threading.Lock()  # Lock for synchronization
 

    def __init__(self):
        if BaseManager._instance is not None:
            raise Exception("This class is a singleton! Use singleton() to get the instance.")
        
        if self._file_name is not None: # Added for testing
            self._file_name = f"{self._get_parent_directory()}/{self._file_name}"
            directory = os.path.dirname(self._file_name)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
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

    def _get_parent_directory(self):
        directory = os.path.dirname(__file__)
        parent_directory = os.path.dirname(directory)
        return parent_directory

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
        item = next((item for item in self.project_state_data if item.get(key) == value), None)
        
        if item is None:
            return None  # No matching item found
        
        if return_fields is None:
            return item  # Return all fields if return_fields is None
        
        # Return only the specified fields
        return {field: item.get(field) for field in return_fields if field in item}

    def get_project_state(self):
        return self.project_state_data

    def _insert(self, new_data):
        # Use lock to ensure thread-safe updates to project_state_data
        with BaseManager._lock:
            self.project_state_data.insert(0, new_data)
            self.__save_project_state()

    def _update(self, key, value, updated_fields):
        """Update the first dictionary in project_state_data where key matches value."""
        with BaseManager._lock:
            for item in self.project_state_data:
                if item.get(key) == value:
                    item.update(updated_fields)
                    self.__save_project_state()
                    return item
        
        raise KeyError(f"Item with {key} = {value} not found.")
    
    def _delete(self, key, value):
        """Delete the first dictionary in project_state_data where key matches value."""
        with BaseManager._lock:
            self.project_state_data = [
                item for item in self.project_state_data if item.get(key) != value
            ]
            self.__save_project_state()
        
