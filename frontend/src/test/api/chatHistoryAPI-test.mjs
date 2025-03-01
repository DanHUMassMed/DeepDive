// createNewChat.test.js
import test from 'ava';
import { getChatHistoryItems, deleteChatHistoryItems, getActiveChat, setActiveChat, createChatHistoryItem, updateChatHistoryTitle, deleteChatHistoryItem
 } from '../../api/chatHistoryAPI.mjs';  // Adjust the path to your module

test('getChatHistoryItems Test', async t => {
    // Arrange
    const project_id = 'deep-dive-test'; 

    try {
        // Act
        const response = await getChatHistoryItems(project_id);
        
        // Assert
        t.truthy(response); 
        t.is(Array.isArray(response), true); 
        t.is(response.length, 1);
        
        const chatItem = response[0]; 
        t.is(chatItem.project_id, project_id); 
        t.is(chatItem.chat_llm_name, 'llama3.2:1b');

        console.log('Test Passed: Response:', response);
    } catch (error) {
        t.fail('API call failed: ' + error.message);
    }
});

test('getActiveChat Test', async t => {
    // Arrange
    const project_id = 'deep-dive-test'; 

    try {
        // Act
        const response = await getActiveChat(project_id);
        
        // Assert
        t.truthy(response);
        t.is(response.project_id, project_id); 
        t.is(response.chat_llm_name, 'llama3.2:1b');
        
        console.log('Test Passed: Response:', response);
    } catch (error) {
        t.fail('API call failed: ' + error.message);
    }
});


test('createChatHistoryItem Test', async t => {
    // Arrange
    const chatHistoryItem = {
        project_id: "deep-dive-test",
    };

    try {
        // Act
        const response = await createChatHistoryItem(chatHistoryItem);
        
        // Assert
        t.truthy(response);
        // t.is(response.project_id, project_id);
        // t.is(response.chat_llm_name, 'llama3.2:1b');
        
        console.log('Test Passed: Response:', response);
    } catch (error) {
        t.fail('API call failed: ' + error.message);
    }
});

test('setActiveChat Test', async t => {
    // Arrange
    const project_id = 'deep-dive-test'; 
    const chat_id = '90357994-c39f-4d43-84ce-1148787bfe5c'

    try {
        // Act
        const response = await setActiveChat(project_id, chat_id);
        
        // Assert
        t.truthy(response);
        // t.is(response.project_id, project_id); 
        // t.is(response.chat_llm_name, 'llama3.2:1b');
        
        console.log('Test Passed: Response:', response);
    } catch (error) {
        t.fail('API call failed: ' + error.message);
    }
});

test('updateChatHistoryTitle Test', async t => {
    // Arrange
    const chatHistoryItem = {
        project_id: "deep-dive-test",
        chat_id: '90357994-c39f-4d43-84ce-1148787bfe5c',
        chat_title: "New Title"
    };

    try {
        // Act
        const response = await updateChatHistoryTitle(chatHistoryItem);
        
        // Assert
        t.truthy(response);
        // t.is(response.project_id, project_id); 
        // t.is(response.chat_llm_name, 'llama3.2:1b');
        
        console.log('Test Passed: Response:', response);
    } catch (error) {
        t.fail('API call failed: ' + error.message);
    }
});

test('deleteChatHistoryItem Test', async t => {
    // Arrange
    const chatHistoryItem = {
        project_id: "deep-dive-test",
    };

    try {
        // Act
        const expectAGoodChatHistoryItem = await createChatHistoryItem(chatHistoryItem);
        console.log('expectAGoodChatHistoryItem:', expectAGoodChatHistoryItem);
        const project_id = expectAGoodChatHistoryItem.project_id
        const chat_id = expectAGoodChatHistoryItem.chat_id
        const response = await deleteChatHistoryItem(project_id, chat_id);
        
        // Assert
        t.truthy(expectAGoodChatHistoryItem);
        t.truthy(response);
        // t.is(response.project_id, project_id); 
        // t.is(response.chat_llm_name, 'llama3.2:1b');
        
        console.log('Test Passed: Response:', response);
    } catch (error) {
        t.fail('API call failed: ' + error.message);
    }
});

test('deleteChatHistoryItems Test', async t => {
    // Arrange
    const project_id = "my-first-project"

    try {
        // Act
        const response = await deleteChatHistoryItems(project_id);
        
        // Assert
        t.truthy(response);
        // t.is(response.project_id, project_id); 
        // t.is(response.chat_llm_name, 'llama3.2:1b');
        
        console.log('Test Passed: Response:', response);
    } catch (error) {
        t.fail('API call failed: ' + error.message);
    }
});
