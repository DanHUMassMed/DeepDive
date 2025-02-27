import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app,get_chat_history   # Assuming your file is named 'main.py'
from app.utils.logging_utilities import setup_logging, trace

logger = setup_logging("test")

client = TestClient(app)

def test_create_chat_history_item():
    chat_history_item = {
        "project_id": "deep-dive",
    }
    
    # Pass the data as a JSON payload to the POST request
    response = client.post("/create/chat-history-item", json=chat_history_item)
    

    # Assert that the status code is 200 (OK)
    assert response.status_code == 200

    # Assert the structure of the returned response
    #assert response.json() == [ 'deepseek-r1:1.5b', 'deepseek-r1:32b', 'llama3.2:1b', 'llama3.3:latest', 'nomic-embed-text:latest', 'qwen2.5:32b' ]
    logger.debug(response.json())

    

# Test case for GET /available-models/ endpoint
def test_available_models():
    # Send a test request to the /available-models/ endpoint
    response = client.get("/get/available-models/")

    # Assert that the status code is 200 (OK)
    assert response.status_code == 200

    # Assert the structure of the returned response
    assert response.json() == [ 'deepseek-r1:1.5b', 'deepseek-r1:32b', 'llama3.2:1b', 'llama3.3:latest', 'nomic-embed-text:latest', 'qwen2.5:32b' ]
    logger.debug(response.json())


