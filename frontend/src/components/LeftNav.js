import React, { useRef, useState, useContext, useEffect } from 'react';
import { useConfig } from './ConfigContext'; 
import ChatHistoryItem from './ChatHistoryItem';
import { IoIosSearch } from 'react-icons/io';
import { getChatHistoryItems } from "../api/chatHistoryAPI.mjs"

const LeftNav = ( { setChatMessages } ) => {
  const { persistentConfig, ephemeralConfig, updateConfig } = useConfig();
  const [chatHistory, setChatHistory] = useState([]);

  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        const chatHistoryServer = await getChatHistoryItems(persistentConfig.project_id);
        setChatHistory(chatHistoryServer);
        // alert(chatHistoryServer.length);
        //alert("Left Nav");
        // alert(JSON.stringify(chatHistoryServer, null, 2));
      } catch (error) {
        console.error('Error fetching chat history:', error);
      }
    };

    if (persistentConfig.project_id) {
      fetchChatHistory();
    }
  }, [persistentConfig.chat_history_timestamp])

  return (
    <div
      className={`transition-all duration-300 ${persistentConfig.isLeftNavOpen ? 'w-64' : 'w-0'} bg-gray-200 h-full text-black overflow-hidden`}
      style={{
        zIndex: persistentConfig.isLeftNavOpen ? 10 : -1,  // Ensures it's above content when open
      }}
    >
      <SearchBar />
      <div className="p-2 max-h-[calc(100vh-64px)] overflow-y-auto">
        {chatHistory.map((chat) => (
          <ChatHistoryItem   key={chat.chat_id}  setChatMessages={setChatMessages} chat={chat} />
        ))}
      </div>
    </div>
  );
};

function SearchBar({ searchText, onSearchTextChange }) {
  return (
    <div className="p-1">
      <form className="flex items-center p-1 rounded-lg shadow-md">
        <IoIosSearch size={24}/>
        <input
          id="search"
          type="text"
          value={searchText}
          placeholder="  Search"
          onChange={(e) => onSearchTextChange(e.target.value)}
          className="flex-grow p-.3 rounded-lg focus:outline-none"
        />
      </form>
    </div>
  );
}




export default LeftNav;