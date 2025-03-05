// src/App.js
import React, { useState, useEffect } from 'react';
import TopNav from './components/TopNav';
import LeftNav from './components/LeftNav';
import RightNav from './components/RightNav';
import DialogContainer from './components/DialogContainer';
import { ConfigProvider, useConfig } from './components/ConfigContext';
import { getChatInteractions } from "./api/chatAPI.mjs"
import { getActiveChat } from "./api/chatHistoryAPI.mjs"

function ChatContainer() {
  const [chatMessages, setChatMessages] = useState([]);
  const { persistentConfig, ephemeralConfig, updateConfig } = useConfig();

  // useEffect to refresh chatMessages when project_id changes
  useEffect(() => {
    if (persistentConfig.project_id) {
      const fetchChatMessages = async () => {
        try {
          const activeChat = await getActiveChat(persistentConfig.project_id);
          if (activeChat && Object.keys(activeChat).length > 0) {
            const chatItems = await getChatInteractions(persistentConfig.project_id, activeChat.chat_id);
            setChatMessages(chatItems);
          }
        } catch (error) {
          console.error('Error fetching active chat:', error);
          // Optionally show a user-friendly message or retry mechanism
        }
      };

      fetchChatMessages();
    }
  }, [persistentConfig.project_id, persistentConfig.chat_history_timestamp]);

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