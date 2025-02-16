import os
import subprocess

def is_program_installed(program_name):
    """Check if the program exists in the /Applications folder."""
    app_path = f"/Applications/{program_name}.app"
    return os.path.exists(app_path)

def is_program_running(program_name):
    """Check if a program is running based on the program name."""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            if program_name.lower() in proc.info['name'].lower():
                return True
    except ImportError:
        print("psutil module not installed. Can't check running processes.")
    return False

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

# Check if Ollama is installed and open it if necessary
open_ollama()

if __name__ == "__main__":
    print("This script is intended to be imported and not run directly.")
    