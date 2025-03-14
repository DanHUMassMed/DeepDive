import requests
from fastapi import HTTPException
import subprocess
import platform
import inspect
import os
import psutil
from app import constants
from app.utils.logging_utilities import setup_logging, trace

logger = setup_logging()

@trace(logger)
def get_available_ollama_models():
    function_name = inspect.currentframe().f_code.co_name
    module_name = inspect.getmodule(inspect.currentframe()).__name__

    url = constants.OLLAMA_URL
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
    """Check if Ollama is installed, and if not running, open it."""
    if is_program_installed("Ollama"):
        if is_program_running("Ollama"):
            print("Ollama is already running.")
        else:
            try:
                subprocess.run(["open", "-a", "Ollama"], check=True)
                print("Ollama opened successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to open Ollama: {e}")
    else:
        print("Ollama is not installed.")
        
def is_program_installed(program_name):
    """Check if the program exists in the /Applications folder."""
    app_path = f"/Applications/{program_name}.app"
    return os.path.exists(app_path)

def is_program_running(program_name):
    """Check if a program is running based on the program name."""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if program_name.lower() in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                logger.error(f"Error accessing process {proc.info['pid']}: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking processes: {e}", exc_info=True)
        return False

