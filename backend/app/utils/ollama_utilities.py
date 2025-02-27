import requests
from fastapi import HTTPException
import subprocess
import platform

from app.utils.logging_utilities import setup_logging, trace

logger = setup_logging()


@trace(logger)
def get_available_ollama_models():
    url = "http://localhost:11434/api/tags"
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        models_data = response.json()
        model_names = sorted([model['name'] for model in models_data.get('models', [])])
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch models")
    return model_names

def open_ollama():
    """
    Opens the Ollama application using a subprocess on macOS and handles errors if it fails to open.
    """
    if platform.system() == "Darwin":  # Darwin indicates macOS
        try:
            # Open Ollama (assuming it's a GUI app located in /Applications)
            subprocess.run(["open", "-a", "Ollama"], check=True)
            print("Ollama opened successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to open Ollama: {e}")
    else:
        logger.error("'open_ollama' function can only run on macOS.")
