// src/App.js
import React, { useState, useEffect } from 'react';
import TopNav from './components/TopNav';
import LeftNav from './components/LeftNav';
import RightNav from './components/RightNav';
import DialogContainer from './components/DialogContainer';
import { ConfigProvider, useConfig } from './components/ConfigContext';
import { getActiveChat, getChatItems } from "./api/chatAPI.mjs"

function ChatContainer() {
  const [chatMessages, setChatMessages] = useState([]);
  const { config } = useConfig();

  // useEffect to refresh chatMessages when project_id changes
  useEffect(() => {
    if (config.project_id) {
      const fetchChatMessages = async () => {
        try {
          const activeChat = await getActiveChat(config.project_id);
          if (activeChat && Object.keys(activeChat).length > 0) {
            const chatItems = await getChatItems(config.project_id, activeChat.chat_id);
            setChatMessages(chatItems);
          }
        } catch (error) {
          console.error('Error fetching active chat:', error);
          // Optionally show a user-friendly message or retry mechanism
        }
      };

      fetchChatMessages();
    }
  }, [config.project_id]); // Effect depends on config.project_id

  return (
    <div className="flex h-screen flex-col">
      <TopNav />
      <div className="flex flex-grow">
        <LeftNav setChatMessages={setChatMessages} />
        <DialogContainer chatMessages={chatMessages} setChatMessages={setChatMessages} />
        <RightNav />
      </div>
    </div>
  );
}

function App() {
  return (
    <ConfigProvider>
      <ChatContainer />
    </ConfigProvider>
  );
}

export default App;