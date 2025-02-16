console.log('Current working directory:', process.cwd());
const path = require('path');
console.log('Current working directory!!:', path.resolve(__dirname));
// Require necessary modules
const axios = require('axios');
const sendPrompt = require('../api/chatAPI'); // Update with the correct path
const { expect } = require('chai');

// Mock axios to control its behavior during testing
const sinon = require('sinon');

// Describe the sendPrompt function tests
describe('sendPrompt', () => {
  
  let axiosPostStub;

  beforeEach(() => {
    // Stub axios.post before each test
    axiosPostStub = sinon.stub(axios, 'post');
  });

  afterEach(() => {
    // Restore the original axios.post after each test
    axiosPostStub.restore();
  });

  it('should return data when API call is successful', async () => {
    // Mock a successful response from the API
    const mockResponse = { data: { response: 'mocked response' } };
    axiosPostStub.resolves(mockResponse);

    const result = await sendPrompt('test prompt');
    
    // Expect that the result matches the mock data
    expect(result).to.deep.equal(mockResponse.data);
  });

  it('should throw an error when API call fails', async () => {
    // Mock a failed response from the API
    axiosPostStub.rejects(new Error('Failed to fetch response'));

    try {
      await sendPrompt('test prompt');
      throw new Error('Test failed because no error was thrown');
    } catch (error) {
      expect(error.message).to.equal('Failed to fetch response');
    }
  });
});