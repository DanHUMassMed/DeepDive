import test from 'ava';
import { getProjectState, createProjectState, updateProjectState, deleteProjectState, getChatHistoryTimestamp} from '../../api/projectAPI.mjs';

test('getProjectState Test', async t => {
    // Arrange
    const project_id = 'deep-dive-test1'; 

    try {
        // Act
        const response = await getProjectState(project_id);
        
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

test('createProjectState Test', async t => {
    // Arrange
    const projectStateItem = {project_name: 'deep-dive-test1',}; 

    try {
        // Act
        const response = await createProjectState(projectStateItem);
        
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

test('updateProjectState Test', async t => {
    // Arrange
    const projectStateItem = {project_name: 'deep-dive-test1',
        project_llm_name: 'llama3.2:1b',
        project_system_prompt: 'Answer all questions to the'
    }; 
    const project_id = 'deep-dive-test1'

    try {
        // Act
        const response = await updateProjectState(project_id, projectStateItem);
        
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

test('deleteProjectState Test', async t => {
    // Arrange
    const project_id = "deep-dive-test111"
    const projectStateItem = {project_name: 'deep-dive-test111',}; 
    try {
        // Act
        const response1 = await createProjectState(projectStateItem);
        const response = await deleteProjectState(project_id);
        
        // Assert
        t.truthy(response);
        // t.is(response.project_id, project_id); 
        // t.is(response.chat_llm_name, 'llama3.2:1b');
        
        console.log('Test Passed: Response:', response);
    } catch (error) {
        t.fail('API call failed: ' + error.message);
    }
});

test('getChatHistoryTimestamp Test', async t => {
    // Arrange
    const project_id = 'deep-dive-test'; 

    try {
        // Act
        const response = await getChatHistoryTimestamp(project_id);
        
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
