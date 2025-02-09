import axios from 'axios';

const sendPrompt = async (prompt) => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/chat/', {
      prompt: prompt
    }, {
      headers: {
        'Content-Type': 'application/json',
      }
    });

    return response.data;
  } catch (error) {
    console.error('Error sending prompt:', error);
    throw new Error('Failed to fetch response');
  }
};

export default sendPrompt;