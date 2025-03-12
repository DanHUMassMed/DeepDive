"""This module provides a Prompts class for loading and managing prompts for LLM (Language Model) calls. 
The Prompts class implements a singleton pattern to ensure a single instance of prompts 
is loaded throughout the application."""

import json
import re
from app.exceptions import DeepDiveException
from app.constants import PROMPTS_FILENAME
from app.utils.logging_utilities import setup_logging
from app.utils.workspace_utilities import get_project_workspace
import importlib.util
import importlib
import os
from threading import Lock


logger = setup_logging()


class Prompts:
    """Loads prompts for LLM calls"""

    _instance = None
    _prompts = None
    _lock = Lock()

    def __new__(cls):
        # Ensure thread-safe instantiation
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Prompts, cls).__new__(cls)
                cls._prompts = cls._load_prompts()
            return cls._instance

    @classmethod
    def reset_instance(cls):
        cls._instance = None
        cls._prompts = None

    @classmethod
    def _load_prompts(cls):
        prompts_json = None
        prompts = {}
        try:
            prompts_json_path = cls._get_prompt_json_path()

            with open(prompts_json_path, "r", encoding="utf-8") as json_file:
                prompts_json = json.load(json_file)

            for prompt_key in prompts_json:
                prompt_raw = prompts_json[prompt_key]
                if isinstance(prompt_raw, str):
                    prompt_value = prompt_raw
                elif isinstance(prompt_raw, list) and all(
                    isinstance(x, str) for x in prompt_raw
                ):
                    prompt_value = "".join(prompt_raw)
                else:
                    logger.error(
                        "The prompt MUST be a list of Strings. All elements in the list are NOT Strings!"
                    )

                prompts[prompt_key] = prompt_value

        except Exception as e:
            logger.error("Error in Prompts._load_prompts %s", e)
            raise DeepDiveException("Error Prompts._load_prompts.") from e

        return prompts

    @classmethod
    def _get_prompt_json_path(self):
        """Get the user defined path to prompts.json
        or return the defaults if it is not found in the project workspace
        """
        
        prompt_json_path = f"{get_project_workspace()}/{PROMPTS_FILENAME}"
        if os.path.isfile(prompt_json_path):
            return prompt_json_path
        else:
            package_nm = "app.resources"
            module_spec = importlib.util.find_spec(package_nm)

            if module_spec is not None and module_spec.submodule_search_locations:
                # Retrieve the first search location if available
                package_path = module_spec.submodule_search_locations[0]
                prompt_json_path = os.path.join(package_path, PROMPTS_FILENAME)
                return prompt_json_path
            else:
                raise ImportError(f"Cannot find package {package_nm}.")  
    
    def print_params(self):
        """Helper function prints the available prompts and the required params for each
        """
        ret_val = ""
        for prompt_key, prompt_value in self._prompts.items():
            params = self._extract_variables(prompt_value)
            ret_val += f'prompt: "{prompt_key}" params({params})\n'
        return ret_val

    def get_prompt(self, prompt_nm, **kwargs):
        """Get the formatted prompt after applying the passed in key words if require
        """
        prompt = self._prompts.get(prompt_nm, None)

        if prompt and kwargs:
            try:
                prompt = prompt.format(**kwargs)
            except KeyError as e:
                variables = self._extract_variables(prompt)
                error_msg = f"ERROR: The PROMPT: [{prompt_nm}] expects the following VARIABLES: [{variables}]"
                logger.error(error_msg)
                raise DeepDiveException(error_msg) from e

        if prompt is None:
            error_msg = f"ERROR: Prompt [{prompt_nm}] is not found in the prompt json."
            logger.error(error_msg)
            raise DeepDiveException(error_msg)

        return prompt

    def _extract_variables(self, text):
        variable_list = re.findall(r"\{(.*?)\}", text)
        variables = ", ".join(variable_list)
        return variables
