import React, { useState, useContext, useEffect } from 'react';
import ConfigContext from './ConfigContext';

import { VscLayoutSidebarLeft, VscLayoutSidebarLeftOff, VscLayoutSidebarRight, VscLayoutSidebarRightOff } from 'react-icons/vsc';
import { HiOutlinePencilSquare } from "react-icons/hi2";
import { createChatHistoryItem } from "../api/chatHistoryAPI.mjs"
import { getChatHistoryTimestamp } from "../api/projectAPI.mjs"


const TopNav = () => {
  const { config, setConfig  } = useContext(ConfigContext);

  const toggleLeftNav = () => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      isLeftNavOpen: !prevConfig.isLeftNavOpen,
    }));
  };

  const toggleRightNav = () => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      isRightNavOpen: !prevConfig.isRightNavOpen,
    }));

  };

  const onNewChat = async (e) => {
    const newChat = await createChatHistoryItem({project_id:config.project_id})
    const chatHistoryTimestamp = await getChatHistoryTimestamp(config.project_id)
    setConfig((prevConfig) => ({
      ...prevConfig,
      chat_history_timestamp: chatHistoryTimestamp,
    }));
  };
  
  // useEffect(() => {
  //   alert(JSON.stringify(config, null, 2));
  // }, [config]); // This will run every time `config` is updated


  return (
    <div className="flex justify-between items-center h-10 px-4 bg-gray-300 text-black">
      {/* New Chat button on the left */}
      <button onClick={onNewChat} className="focus:outline-none px-2">
        <HiOutlinePencilSquare size={24} color="black" />
      </button>
      
      {/* Centered fields */}
      <div className="flex space-x-2 justify-center items-center">
      <label className="font-semibold mr-2">Project:</label>
        <input
          type="text"
          value={`Deep-Dive`}
          readOnly
          className="bg-gray-100 border border-gray-300 text-center p-1 rounded"
          style={{ width: '200px' }}
        />
        <label className="font-semibold mr-2">Started on:</label>
        <input
          type="text"
          value={`2025-02-24 10:13:05 AM`}
          readOnly
          className="bg-gray-100 border border-gray-300 text-center p-1 rounded"
          style={{ width: '300px' }}
        />
      </div>

      {/* Sidebar buttons on the right */}
      <div className="flex space-x-2">
        <button onClick={toggleLeftNav} className="focus:outline-none px-1">
          {config.isLeftNavOpen ? (
            <VscLayoutSidebarLeft size={24} color="black" />
          ) : (
            <VscLayoutSidebarLeftOff size={24} color="black" />
          )}
        </button>
        <button onClick={toggleRightNav} className="focus:outline-none px-1">
          {config.isRightNavOpen ? (
            <VscLayoutSidebarRight size={24} color="black" />
          ) : (
            <VscLayoutSidebarRightOff size={24} color="black" />
          )}
        </button>
      </div>
    </div>
  );
};

export default TopNav;