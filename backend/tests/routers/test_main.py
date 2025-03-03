import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.managers.chat_history_manager import ChatHistoryManager, ChatHistoryItem
import copy
import os
from app.main import app
from app.utils.logging_utilities import setup_logging, trace

logger = setup_logging("test")

client = TestClient(app)

@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ['DEEP_DIVE_WORKSPACE'] = './workspace/test'


def mock_data():
    data = [
        {   "project_id": "first-project",
            "project_name": "first-project",
            "project_start_date": "2025-01-01 09:17:27 AM",
            "chat_history_timestamp": "2025-01-01 10:22:58.635",
            "project_llm_name": "deepseek-r1:32b",
            "project_system_prompt": "Answer all questions to the best of your ability.'",
            "project_data_dir": "/User/home/dan",
            "project_data_toggle": False,
            "chat_history_items": []
        },
        {
            "project_id": "deep-dive",
            "project_name": "deep-dive",
            "project_start_date": "2025-02-28 09:17:27 AM",
            "chat_history_timestamp": "2025-02-28 10:22:58.635",
            "project_llm_name": "deepseek-r1:32b",
            "project_system_prompt": "Answer all questions to the best of your ability. Answer concisely but correctly. If you do not know the answer, just say 'I don\u2019t know.'",
            "project_data_dir": "/User/home/amy",
            "project_data_toggle": False,
            "chat_history_items": [
                {
                    "project_id": "deep-dive",
                    "chat_id": "c280103e-c807-48fb-986a-c302b43e1bea",
                    "chat_start_date": "2025-02-28 10:19:58 AM",
                    "chat_title": "Chat on 2025-02-28 10:19:58 AM",
                    "chat_llm_name": "deepseek-r1:32b",
                    "active_chat": True
                },
                {
                    "project_id": "deep-dive",
                    "chat_id": "57132c50-ea95-4b4e-b9d4-548e4ed6ff11",
                    "chat_start_date": "2025-02-28 10:10:31 AM",
                    "chat_title": "Chat on 2025-02-28 10:10:31 AM",
                    "chat_llm_name": "deepseek-r1:32b",
                    "active_chat": False
                }
            ]
        }
    ]
    logger.debug("mock_data loading")
    return copy.deepcopy(data)

@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ['DEEP_DIVE_WORKSPACE'] = './workspace/test'


@pytest.fixture
def chat_history_manager():
    # Use a temporary file or mock file loading
    with patch('app.managers.chat_history_manager.ChatHistoryManager._load_project_state', return_value=mock_data()):
        with patch('app.managers.chat_history_manager.ChatHistoryManager._BaseManager__save_project_state', return_value=None):
            manager = ChatHistoryManager.singleton()
    yield manager
    # Cleanup the singleton instance for other tests 
    ChatHistoryManager._instance = None


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


