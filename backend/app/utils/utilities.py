import logging.config
import os
import subprocess

# logging_util.py
def setup_logging(config_path='logging_config.ini'):
    """Sets up logging configuration."""
    if os.path.exists(config_path):
        logging.config.fileConfig(config_path)
    else:
        logging.basicConfig(level=logging.DEBUG)
        logging.warning(f"Logging configuration file '{config_path}' not found. Using default logging configuration.")
        
    return logging.getLogger("app")

        
def open_ollama():
    try:
        # Open Ollama (assuming it's a GUI app located in /Applications)
        subprocess.run(["open", "-a", "Ollama"], check=True)
        print("Ollama opened successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to open Ollama: {e}")

        