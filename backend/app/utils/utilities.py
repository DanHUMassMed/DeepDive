import logging.config
import os
import subprocess
import sys

# logging_util.py
def setup_logging(logger_nm="app", config_path='logging_config.ini'):
    """Sets up logging configuration."""
    
    # If we are just given a file name for the config_path
    # Try to resolve to absolute path by searching the sys.path
    if os.path.dirname(config_path) == '':
        config_path = find_file_on_sys_path(config_path)
        
    if os.path.exists(config_path):
        logging.config.fileConfig(config_path)
    else:
        logging.basicConfig(level=logging.DEBUG)
        logging.warning(f"Logging configuration file '{config_path}' not found. Using default logging configuration.")
        logging.warning('\n'.join(sys.path))

    return logging.getLogger(logger_nm)

def find_file_on_sys_path(file_name):
    for directory in sys.path:
        # Join the directory path with the file name
        full_path = os.path.join(directory, file_name)
        # Check if the file exists
        if os.path.isfile(full_path):
            return full_path
    return file_name
        
def open_ollama():
    try:
        # Open Ollama (assuming it's a GUI app located in /Applications)
        subprocess.run(["open", "-a", "Ollama"], check=True)
        print("Ollama opened successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to open Ollama: {e}")

        