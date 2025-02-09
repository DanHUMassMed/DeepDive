import { useState } from 'react';
import sendPrompt from '../api/chatAPI';

export const useChat = () => {
  const [messages, setMessages] = useState([]);

  const sendMessage = async (prompt) => {
    setMessages([...messages, { text: prompt, sender: 'user' }]);
    try {
      console.log('sendMessage:', prompt);
      const responseData = await sendPrompt(prompt);
      setMessages([...messages, { message: prompt, role: 'user' }, { message: responseData, role: 'ai' }]);
      
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return { messages, sendMessage };
};