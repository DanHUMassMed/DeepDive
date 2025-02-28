import requests
from fastapi import HTTPException
import subprocess
import platform
import inspect

from app.utils.logging_utilities import setup_logging, trace

logger = setup_logging()

@trace(logger)
def get_available_ollama_models():
    function_name = inspect.currentframe().f_code.co_name
    module_name = inspect.getmodule(inspect.currentframe()).__name__

    url = "http://localhost:11434/api/tags"
    try:
        logger.debug("get_available_ollama_models start")
        response = requests.get(url, timeout=5)    
        logger.debug("get_available_ollama_models after get")
        if response.status_code == 200:
            models_data = response.json()
            ret_val = sorted([model['name'] for model in models_data.get('models', [])])
        else:
            try:
                error_message = response.json()  # Try to parse error response as JSON
                error_detail = error_message.get('message', 'No detailed error message provided')
            except ValueError:  # If response isn't JSON
                error_detail = response.text  # Use plain text response if JSON parsing fails
                
            logger.error(f"Error in {module_name}.{function_name} - {error_detail}")
            ret_val = {'status':'FAILED', 'status_code':response.status_code, 'message':error_detail} 
    except Exception as err:
        #TODO add retry as this is the most common error ollama is not started
        open_ollama()
        ret_val = ret_val = {'status':'FAILED', 'status_code':500, 'message':str(err)}

    return ret_val



def open_ollama():
    """
    Opens the Ollama application using a subprocess on macOS and handles errors if it fails to open.
    """
    if platform.system() == "Darwin":  # Darwin indicates macOS
        try:
            # Open Ollama (assuming it's a GUI app located in /Applications)
            subprocess.run(["open", "-a", "Ollama"], check=True)
            logger.info("Ollama opened successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to open Ollama: {e}")
    else:
        logger.error("'open_ollama' function can only run on macOS.")
