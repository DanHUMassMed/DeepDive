import React, { useState } from 'react';
import { IoIosSearch } from 'react-icons/io';

const LeftNav = ({ isOpen }) => {
  const chatHistory = [
    { id: 1, title: 'Chat 1', model: 'llama3.2', dateTime: '2025-02-09 12:00 PM' },
    { id: 2, title: 'Chat 2', model: 'gpt-4', dateTime: '2025-02-08 09:30 AM' },
    { id: 3, title: 'Chat 3', model: 'bert-base', dateTime: '2025-02-07 11:45 AM' },
    // Add more chat history items as needed
  ];

  return (
    <div
      className={`transition-all duration-300 ${isOpen ? 'w-64' : 'w-0'} bg-gray-200 h-full text-black overflow-hidden`}
      style={{
        zIndex: isOpen ? 10 : -1,  // Ensures it's above content when open
      }}
    >
      <SearchBar />
      <div className="p-2">
        {chatHistory.map((chat) => (
          <ChatHistoryItem key={chat.id} chat={chat} />
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

const ChatHistoryItem = ({ chat }) => {
  const { title, model, dateTime } = chat;

  const handleClick = () => {
    console.log(`Bringing back chat: ${title}`);
    // Implement logic to restore the chat here
  };

  return (
    <button
      onClick={handleClick}
      className="block w-full text-left p-2 rounded-lg hover:bg-gray-400 focus:outline-none"
    >
      <div className="font-semibold">{title}</div>
      <div className="text-sm text-gray-600">{model}</div>
      <div className="text-xs text-gray-500">{dateTime}</div>
    </button>
  );
};

export default LeftNav;