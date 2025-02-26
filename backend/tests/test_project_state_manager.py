import pytest
import json
import copy
import os
from datetime import datetime
from unittest.mock import patch, mock_open

from app.project_state_manager import ProjectStateManager, ProjectStateItem
import logging

# Configure the logger
logging.basicConfig(
    filename='debug.log',        # Log file name
    filemode='a',              # Append mode; use 'w' to overwrite
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.DEBUG       # Set the logging level
)


def mock_data():
    data = [
        {
            "project_id": "my-second-project",
            "project_name": "my-second-project",
            "project_start_date": "2025-02-24 10:13:31 AM",
            "chat_history_timestamp": "2025-02-24 10:13:31.090",
            "project_llm_name": "llama3.2:1b",
            "project_system_prompt": "Answer all questions to the best of your ability. ",
            "chat_history_items": []
        },
        {
            "project_id": "my-first-project",
            "project_name": "my-first-project",
            "project_start_date": "2025-02-24 10:13:05 AM",
            "chat_history_timestamp": "2025-02-24 10:13:05.474",
            "project_llm_name": "my_llm",
            "project_system_prompt": "Do only good",
            "chat_history_items": []
        },
        {
            "project_id": "deep-dive",
            "project_name": "deep-dive",
            "project_start_date": "2025-02-24 10:13:05 AM",
            "chat_history_timestamp": "2025-02-24 10:13:05.472",
            "project_llm_name": "my_better_llm",
            "project_system_prompt": "Answer all questions to the best of your ability. ",
            "chat_history_items": []
        }
    ]
    return copy.deepcopy(data)

@pytest.fixture
def project_state_manager():
    # Use a temporary file or mock file loading
    with patch('app.project_state_manager.ProjectStateManager._file_name', None):
        with patch('app.project_state_manager.ProjectStateManager._load_project_state', return_value=mock_data()):
            with patch('app.project_state_manager.ProjectStateManager._BaseManager__save_project_state', return_value=None):
                manager = ProjectStateManager.singleton()
    yield manager
    # Cleanup the singleton instance for other tests
    logging.debug(f"Reset singleton()")
    ProjectStateManager._instance = None

def test_get_project_state(project_state_manager):
    result = project_state_manager.get_project_state('deep-dive')
    assert result['project_name'] == 'deep-dive'

def test_delete_project_state(project_state_manager):
    project_state_manager.delete_project_state('deep-dive')
    assert project_state_manager.get_project_state('deep-dive') == None

def test_create_project_state(project_state_manager):
    project_state_item = ProjectStateItem(project_name="project name test")
    result = project_state_manager.create_project_state(project_state_item)
    assert 'project_id' in result
    assert 'project_start_date' in result
    logging.debug(f"results {result}")
        

def test_get_chat_history_timestamp(project_state_manager):
    chat_history_timestamp = project_state_manager.get_chat_history_timestamp('deep-dive')
    assert 'chat_history_timestamp' in chat_history_timestamp
    logging.debug(f"results {chat_history_timestamp}")
    


