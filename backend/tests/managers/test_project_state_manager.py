import pytest
import copy
from unittest.mock import patch
import os

from app.managers.project_state_manager import ProjectStateManager, ProjectStateItem
from app.utils.logging_utilities import setup_logging

logging = setup_logging('test')


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
    return copy.deepcopy(data)


@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ['DEEP_DIVE_WORKSPACE'] = './workspace/test'
    
@pytest.fixture
def project_state_manager():
    # Use a temporary file or mock file loading
    with patch('app.managers.project_state_manager.ProjectStateManager._load_project_state', return_value=mock_data()):
        with patch('app.managers.project_state_manager.ProjectStateManager._BaseManager__save_project_state', return_value=None):
                manager = ProjectStateManager.singleton()
    yield manager
    # Cleanup the singleton instance for other tests
    logging.debug(f"Reset singleton()")
    ProjectStateManager._instance = None

def test_get_project_state(project_state_manager):
    result = project_state_manager.get_project_state('deep-dive')
    # Note: project_id is not returned as it is the ket that is passed
    # Note: chat_history_timestamp is not returned as it is a chat feature
    assert result["project_name"] == "deep-dive"
    assert result["project_start_date"] == "2025-02-28 09:17:27 AM"
    assert result["project_llm_name"] == "deepseek-r1:32b"
    assert result["project_system_prompt"] == "Answer all questions to the best of your ability. Answer concisely but correctly. If you do not know the answer, just say 'I don\u2019t know.'"
    assert result["project_data_dir"] == "/User/home/amy"
    assert result["project_data_toggle"] == False

def test_delete_project_state(project_state_manager):
    result = project_state_manager.delete_project_state('deep-dive')
    assert result == {'status':'SUCCESS', 'status_code':200}

def test_create_project_state(project_state_manager):
    project_state_item = ProjectStateItem(project_name="project name test")
    result = project_state_manager.create_project_state(project_state_item)
    assert result['project_id'] == "project name test"
    assert result["project_name"] == "project name test"
    assert 'project_start_date' in result
    
        
def test_get_chat_history_timestamp(project_state_manager):
    result = project_state_manager.get_chat_history_timestamp('deep-dive')
    assert result["chat_history_timestamp"] == "2025-02-28 10:22:58.635"
   
    


