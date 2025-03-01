import axios from 'axios';

const BASE_URL = 'http://localhost:8000';


export const apiRequest = async (method, endpoint, data = null) => {
  try {
    let response;
    const url = `${BASE_URL}${endpoint}`;
    if (method === 'get') {
      response = await axios.get(url);
    } else if (method === 'post') {
      response = await axios.post(url, data);
    } else if (method === 'put') {
      response = await axios.put(url, data);
    } else if (method === 'delete') {
      response = await axios.delete(url, { data });
    } else {
      throw new Error('Unsupported HTTP method');
    }

    console.log(JSON.stringify(response.data, null, 4));
    return response.data;

  } catch (error) {
    if (error.response) {
      console.error(`HTTP error occurred: ${error.response.status} ${error.response.statusText}`);
      try {
        console.error('Response content:', JSON.stringify(error.response.data, null, 4));
      } catch {
        console.error('Response content:', error.response.data);
      }
    } else {
      console.error('Other error occurred:', error.message);
    }
    throw error;
  }
};

