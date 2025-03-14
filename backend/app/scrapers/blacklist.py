import json
from app.constants import BLACKLIST_FILENAME
from app.utils.logging_utilities import setup_logging
from app.utils.workspace_utilities import get_project_workspace
import importlib.util
import os

logger = setup_logging()

class Blacklist:
    def __init__(self):
        self.file_path = self._get_blacklist_json_path()
        self.urls = self._load_urls()

    def _load_urls(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading blacklist: {e}")
            return []

    def _get_blacklist_json_path(self):
        """Get the user defined path to blacklisted urls
        or return the defaults if it is not found in the project workspace
        """        
        prompt_json_path = f"{get_project_workspace()}/{BLACKLIST_FILENAME}"
        if os.path.isfile(prompt_json_path):
            return prompt_json_path
        else:
            package_nm = "app.resources"
            module_spec = importlib.util.find_spec(package_nm)

            if module_spec is not None and module_spec.submodule_search_locations:
                # Retrieve the first search location if available
                package_path = module_spec.submodule_search_locations[0]
                prompt_json_path = os.path.join(package_path, BLACKLIST_FILENAME)
                return prompt_json_path
            else:
                raise ImportError(f"Cannot find package {package_nm}.")  
            
    def save(self):
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.urls, file, indent=4)
        except IOError as e:
            print(f"Error saving blacklist: {e}")

    def add_url(self, url):
        if url not in self.urls:
            self.urls.append(url)
            self.save()
        else:
            print(f"URL '{url}' is already in the blacklist.")

    def remove_url(self, url):
        if url in self.urls:
            self.urls.remove(url)
            self.save()
        else:
            print(f"URL '{url}' not found in the blacklist.")


    def is_blacklisted(self, url):
        # Check if the provided URL is contained within any blacklisted URL
        for blacklisted_url in self.urls:
            if blacklisted_url in url:
                return True
        return False