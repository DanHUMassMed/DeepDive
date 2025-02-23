import pytest
import json
import os
from datetime import datetime
from unittest.mock import patch, mock_open

from app.project_state_manager import ProjectStateManager, ProjectState
import logging

# Configure the logger
logging.basicConfig(
    filename='debug.log',        # Log file name
    filemode='a',              # Append mode; use 'w' to overwrite
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.DEBUG       # Set the logging level
)


def mock_data():
    return [
        {
            'project_id': 'projectid1',
            'project_name': 'project1',
            'project_start_date': '2023-01-01 12:00 PM',
            'chat_history_timestamp': '000000'
        },
        {
            'project_id': 'projectid2',
            'project_name': 'project2',
            'project_start_date': '2023-01-02 02:00 PM',
            'chat_history_timestamp': '111111'
        }
    ]

@pytest.fixture
def project_state_manager():
    # Use a temporary file or mock file loading
    with patch('app.project_state_manager.ProjectStateManager._file_name', "resources/test_project_state.json"):
        with patch('app.project_state_manager.ProjectStateManager._load_project_state', return_value=mock_data()):
            manager = ProjectStateManager.singleton()
    yield manager
    # Cleanup the singleton instance for other tests
    ProjectStateManager._instance = None

def test_get_project_state(project_state_manager):
    result = project_state_manager.get_project_state('projectid1')
    assert result['project_name'] == 'project1'

def test_delete_project_state(project_state_manager):
    project_state_manager.delete_project_state('projectid1')
    assert project_state_manager.get_project_state('projectid1') == None

def test_create_project_state(project_state_manager):
    new_project_state = ProjectState()
    result = project_state_manager.create_project_state(new_project_state)
    assert 'project_id' in result
    assert 'project_start_date' in result
    logging.debug(f"results {result}")
        
def test_update_project_state_name(project_state_manager):
    project_state_manager.update_project_state_name('projectid1', 'Updated Project Name')
    result = project_state_manager.get_project_state('projectid1') 
    logging.debug(f"results {result}")
    assert result['project_name'] == 'Updated Project Name'

def test_update_chat_history_timestamp(project_state_manager):
    chat_history_timestamp = project_state_manager.update_chat_history_timestamp('projectid1')
    result = project_state_manager.get_project_state('projectid1') 
    logging.debug(f"results {result}")
    assert result['chat_history_timestamp'] == chat_history_timestamp


