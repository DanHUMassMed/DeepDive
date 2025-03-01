import test from 'ava';
import { getChatInteractions } from '../../api/chatAPI.mjs';

test('getChatInteractions Test', async t => {
    // Arrange
    const project_id = 'deep-dive'; 
    const chat_id = 'c280103e-c807-48fb-986a-c302b43e1bea'


    try {
        // Act
        const response = await getChatInteractions(project_id, chat_id);
        
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
