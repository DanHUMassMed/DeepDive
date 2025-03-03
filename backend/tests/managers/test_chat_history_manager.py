import pytest
import json
import os
from datetime import datetime
from unittest.mock import patch, mock_open
from app.managers.chat_history_manager import ChatHistoryManager, ChatHistoryItem
from app.utils.logging_utilities import setup_logging
import copy
import inspect
import time

def get_current_method_name():
    return inspect.currentframe().f_code.co_name

logger = setup_logging(logger_nm="test")



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

def test_delete_chat_history_item(chat_history_manager):
    project_id='deep-dive'
    chat_id='c280103e-c807-48fb-986a-c302b43e1bea'
    results = chat_history_manager.delete_chat_history_item(project_id, chat_id)
    remaining_chats = chat_history_manager.get_chat_history_items('deep-dive')
    assert len(remaining_chats) == 1
    assert remaining_chats[0]['chat_id'] == '57132c50-ea95-4b4e-b9d4-548e4ed6ff11'
    # Note: Since we deleted an active Chat the next chap becomes the active chat
    assert remaining_chats[0]['active_chat'] is True


def test_get_active_chat(chat_history_manager):
    results = chat_history_manager.get_active_chat('deep-dive')
    logger.debug(f"{inspect.currentframe().f_code.co_name} results={results}")
    assert results['chat_id'] == 'c280103e-c807-48fb-986a-c302b43e1bea'
    assert results['active_chat'] is True

def test_set_active_chat(chat_history_manager):
    project_id='deep-dive' 
    chat_id='57132c50-ea95-4b4e-b9d4-548e4ed6ff11'
    chat_history_manager.set_active_chat(project_id, chat_id)
    chat_history = chat_history_manager.get_chat_history_items('deep-dive')
    logger.debug(f"{inspect.currentframe().f_code.co_name} results={chat_history}")
    assert chat_history[0]['active_chat'] is False
    assert chat_history[1]['active_chat'] is True
    
def test_update_chat_history_item_title(chat_history_manager):
    project_id='deep-dive'
    chat_id='57132c50-ea95-4b4e-b9d4-548e4ed6ff11'
    chat_title='Updated Chat Title'
    chat_history_item = ChatHistoryItem(project_id, chat_id, chat_title=chat_title)
    chat_history_manager.update_chat_history_item_title(chat_history_item)
    results = chat_history_manager.get_chat_history_items('deep-dive')
    results_json = json.dumps(results,indent=4)
    logger.debug(f"{inspect.currentframe().f_code.co_name} results={results_json}")
    assert results[1]['chat_title'] == 'Updated Chat Title'

def test_get_chat_history_items(chat_history_manager):
    result = chat_history_manager.get_chat_history_items('deep-dive')
    logger.debug(f"{inspect.currentframe().f_code.co_name} result={result}")
    assert len(result) == 2
    assert result[0]['chat_id'] == 'c280103e-c807-48fb-986a-c302b43e1bea'
    assert result[1]['chat_id'] == '57132c50-ea95-4b4e-b9d4-548e4ed6ff11'

def test_delete_chat_history_items(chat_history_manager):
    chat_history_manager.delete_chat_history_items('deep-dive')
    result = chat_history_manager.get_chat_history_items('deep-dive')
    assert len(result) == 0

def test_create_chat_history_item(chat_history_manager):
    new_chat_item = ChatHistoryItem(project_id='deep-dive')
    results = chat_history_manager.create_chat_history_item(new_chat_item)
    assert results['project_id'] == 'deep-dive'
    assert results['active_chat'] is True
    assert 'chat_id' in results
    assert 'chat_start_date' in results
    logger.debug(f"{inspect.currentframe().f_code.co_name} results={results}")
        

