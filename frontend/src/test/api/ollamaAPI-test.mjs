import test from 'ava';
import { getAvailableModels } from '../../api/ollamaAPI.mjs';

test('getAvailableModels Test', async t => {
    // Arrange

    try {
        // Act
        const response = await getAvailableModels();
        
        // Assert
        t.truthy(response); 
        // t.is(Array.isArray(response), true); 
        // t.is(response.length, 1);
        
        // const chatItem = response[0]; 
        // t.is(chatItem.project_id, project_id); 
        // t.is(chatItem.chat_llm_name, 'llama3.2:1b');

        console.log('Test Passed: Response:', response);
    } catch (error) {
        t.fail('API call failed: ' + error.message);
    }
});
