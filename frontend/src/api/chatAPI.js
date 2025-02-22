import axios from 'axios';

export const createNewChat = async (project_id) => {
  try {
    const response = await axios.post(
        'http://localhost:8000/create/chat-item', 
        { project_id: project_id }, // This is the data being sent in the POST request
        { headers: { 'Content-Type': 'application/json' }} // This is the headers object
    );
    
    console.log('Type of response.data:', typeof response.data);
    console.log('sendPrompt Response:', response.data['response']?.toString()); // Safe access to `response`
    
    return response.data;
    
  } catch (error) {
    console.error('Error creating new chat:', error);
    throw new Error('Failed to create new chat');
  }
};

export const getChatHistory = async (project_id) => {
  try {
    const response = await axios.get(
        `http://127.0.0.1:8000/get/chat-history/${project_id}`,  
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    // Log the entire response to check the structure
    console.log('Response data:', response.data);

    // Check if 'response' key exists before accessing it
    if (response.data && response.data['response']) {
      console.log('sendPrompt Response:', response.data['response'].toString());
    }

    return response.data;
    
  } catch (error) {
    console.error('Error fetching chat history:', error);
    throw new Error('Failed to fetch chat history');
  }
};

export const getActiveChat = async (project_id) => {
  try {
    const response = await axios.get(
        `http://127.0.0.1:8000/get/active-chat/${project_id}`,  
        { headers: { 'Content-Type': 'application/json' } }
    );

    return response.data;
    
  } catch (error) {
    console.error('Error fetching chat history:', error);
    throw new Error('Failed to fetch chat history');
  }
};

