import axios from 'axios';

export const createNewChat = async (project_id) => {
  try {
    const response = await axios.post(
        'http://localhost:8000/create/chat-history-item', 
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

export const getChatHistoryTimestamp = async (project_id) => {
  try {
    const response = await axios.get(
        `http://127.0.0.1:8000/get/chat-history-timestamp/${project_id}`,  
        { headers: { 'Content-Type': 'application/json' } }
    );

    // Check if chat_history_timestamp exists in the response
    if (response.data && response.data.chat_history_timestamp) {
      return response.data.chat_history_timestamp;
    } else {
      throw new Error('chat_history_timestamp not found in response');
    }
    
  } catch (error) {
    console.error('Error fetching chat history:', error);
    throw new Error('Failed to fetch chat history');
  }
};

export const cancelActiveChat = async (closeWebSocket) => {
  try {
          // Call the FastAPI cancel endpoint when [STOP] message is detected
          const response = axios.post('http://localhost:8000/cancel-stream');
          if(response.data){
            console.log('Cancel stream response:', response.data);
          }else{
            console.log('Cancel stream but got not response');
          }
          closeWebSocket();
        } catch (error) {
          console.error('Error cancelling the stream:', error);
        }
};

export const deleteChatHistoryItem = async (projectId, chatId) => {
  try {
    const response = await axios.delete(
      `http://localhost:8000/delete/chat-history-item`, 
      {
        headers: { 'Content-Type': 'application/json' },
        data: { project_id: projectId, chat_id: chatId } // Send data in the body
      }
    );
    console.log('Type of response.data:', typeof response.data);
    return response.data;
  } catch (error) {
    console.error('Error deleting chat history item:', error);
    throw new Error('Failed to delete chat history item');
  }
};


export const renameChat = async (projectId, chatId, chatName) => {
  try {
    const response = await axios.post(
      `http://localhost:8000/update/chat-history-item-title`,
      { project_id: projectId,
        chat_id: chatId,
        chat_title: chatName }, // Send 'name' in the request body
      { headers: { 'Content-Type': 'application/json' } }
    );
    console.log('Updated item:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error renaming field:', error);
    throw new Error('Failed to rename field');
  }
};

export const getChatItems = async (project_id,chat_id) => {
  try {
    const response = await axios.get(
        `http://127.0.0.1:8000/get/chat-items/${project_id}/${chat_id}`,  
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