// createNewChat.test.js
import test from 'ava';
import { createNewChat, getChatHistory, getActiveChat, getChatHistoryTimestamp,
    deleteChatHistoryItem, renameChat
 } from '../api/chatAPI.mjs';  // Adjust the path to your module

test('createNewChat should successfully create a new chat', async t => {
    // Arrange
    const project_id = 'deep-dive'; // Replace this with a valid project_id as needed

    try {
        // Act
        const response = await createNewChat(project_id);
        
        // Assert
        t.truthy(response); // Check that the response is not null or undefined
        t.is(typeof response, 'object'); // Ensure that the response is an object
        t.is(response.project_id, project_id); // Check if the project_id in the response matches

        console.log('Test Passed: Response:', response);
    } catch (error) {
        t.fail('API call failed: ' + error.message);
    }
});

// Test for valid project_id response
test('getChatHistory returns correct data', async (t) => {
    const project_id = 'deep-dive'; // Replace with an actual project ID
    const expectedResponse = [
        {
            "project_id": "deep-dive",
            "chat_id": "45946b1b-d8b0-4ee3-9733-ae07c5e4b906",
            "chat_start_date": "2025-02-24 04:40:28 PM",
            "chat_title": "Chat on 2025-02-24 04:40:28 PM",
            "chat_llm_name": "llama3.2:1b",
            "active_chat": true
        }
    ];
    
    // Perform the actual test by hitting the server
    try {
      const response = await getChatHistory(project_id);
      
      // Assertions
      t.truthy(response); // Check that response is truthy
      t.deepEqual(response.response, expectedResponse.response); // Check response structure
    } catch (error) {
      t.fail('Failed to fetch chat history');
    }
  });
  
  // Test for invalid project_id response
  test('getChatHistory throws error for invalid project_id', async (t) => {
    const project_id = 'invalid_project_id'; // Replace with an invalid project ID
    
    try {
      await getChatHistory(project_id);
      t.fail('Expected an error, but no error was thrown');
    } catch (error) {
      t.is(error.message, 'Failed to fetch chat history');
    }
});

// Test for valid project_id response
test('getActiveChat returns correct data', async (t) => {
    const project_id = 'deep-dive'; // Replace with an actual project ID
    const expectedResponse =
        {
            "project_id": "deep-dive",
            "chat_id": "45946b1b-d8b0-4ee3-9733-ae07c5e4b906",
            "chat_start_date": "2025-02-24 04:40:28 PM",
            "chat_title": "Chat on 2025-02-24 04:40:28 PM",
            "chat_llm_name": "llama3.2:1b",
            "active_chat": true
        };
    
    // Perform the actual test by hitting the server
    try {
      const response = await getActiveChat(project_id);
      
      // Assertions
      t.truthy(response); // Check that response is truthy
      t.deepEqual(response.response, expectedResponse.response); // Check response structure
    } catch (error) {
      t.fail('Failed to fetch chat history');
    }
  });

  test('getChatHistoryTimestamp includes chat_history_timestamp in the response', async (t) => {
    const project_id = 'deep-dive'; // Replace with an actual project ID
    
    try {
        const response = await getChatHistoryTimestamp(project_id);
        
        // Assertions
        t.truthy(response); // Ensure response is truthy (i.e., not null or undefined)
        console.log('Response:', response);

        // Check if the response includes a chat_history_timestamp field
        t.true(response.hasOwnProperty('chat_history_timestamp'), 'chat_history_timestamp is missing');
    } catch (error) {
        t.fail(`Failed to fetch chat history: ${error.message}`); // Enhanced error message
    }
});  

test('renameChat includes chat_title in the response', async (t) => {
    const projectId = 'deep-dive';
    const chatId = '451245f5-a524-4ab8-9a50-43466011e9ed';
    const chatName = 'My New Name'

    
    try {
        const response = await renameChat(projectId,chatId,chatName);
        
        // Assertions
        t.truthy(response); // Ensure response is truthy (i.e., not null or undefined)
        console.log('Response:', response);

        // Check if the response includes a chat_history_timestamp field
        t.true(response.hasOwnProperty('chat_title'), 'chat_title is missing');
    } catch (error) {
        t.fail(`Failed to rename title: ${error.message}`); // Enhanced error message
    }
});

test('deleteChatHistoryItem includes chat_title in the response', async (t) => {
    const projectId = 'deep-dive';
    const chatId = '451245f5-a524-4ab8-9a50-43466011e9ed';

    
    try {
        const response = await deleteChatHistoryItem(projectId,chatId);
        
        // Assertions
        t.truthy(response); // Ensure response is truthy (i.e., not null or undefined)
        console.log('Response:', response);

        // Check if the response includes a chat_history_timestamp field
        t.true(response.hasOwnProperty('project_id'), 'project_id is missing');
    } catch (error) {
        t.fail(`Failed to delete chat: ${error.message}`); // Enhanced error message
    }
});