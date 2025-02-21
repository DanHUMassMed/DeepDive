import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { createNewChat, getChatHistory } from '../api/chatAPI'; // Adjust the path if needed

// Set up the mock adapter to intercept axios requests
const mock = new MockAdapter(axios);

describe('Chat Service Tests', () => {

  afterEach(() => {
    mock.reset();  // Reset mock after each test
  });

  it('should create a new chat successfully', async () => {
    const mockData = { response: "Chat created successfully" };
    const project_id = 123;

    // Mock POST request
    mock.onPost('http://127.0.0.1:8000/create/chat-history-item/').reply(200, mockData);

    const response = await createNewChat(project_id);
    
    // Check if the response is what we expect
    expect(response).toEqual(mockData);
    expect(typeof response).toBe('object');
    expect(response.response).toBe("Chat created successfully");
  });

  it('should handle error when creating a new chat', async () => {
    const project_id = 123;

    // Mock POST request to return an error
    mock.onPost('http://127.0.0.1:8000/create/chat-history-item/').reply(500);

    await expect(createNewChat(project_id)).rejects.toThrow('Failed to create new chat');
  });

  it('should fetch chat history successfully', async () => {
    const mockData = { response: "Chat history" };
    const project_id = 123;

    // Mock GET request
    mock.onGet(`http://127.0.0.1:8000/get/chat-history/${project_id}`).reply(200, mockData);

    const response = await getChatHistory(project_id);
    
    // Check if the response is correct
    expect(response).toEqual(mockData);
    expect(response.response).toBe("Chat history");
  });

  it('should handle error when fetching chat history', async () => {
    const project_id = 123;

    // Mock GET request to return an error
    mock.onGet(`http://127.0.0.1:8000/get/chat-history/${project_id}`).reply(500);

    await expect(getChatHistory(project_id)).rejects.toThrow('Failed to fetch chat history');
  });

});