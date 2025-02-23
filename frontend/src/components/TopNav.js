import React, { useState, useContext, useEffect } from 'react';
import ConfigContext from './ConfigContext';

import { VscLayoutSidebarLeft, VscLayoutSidebarLeftOff, VscLayoutSidebarRight, VscLayoutSidebarRightOff } from 'react-icons/vsc';
import { HiOutlinePencilSquare } from "react-icons/hi2";
import { createNewChat, getChatHistoryTimestamp } from "../api/chatAPI"


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

    console.log('toggleRightNav',config.isRightNavOpen);
  };

  const onNewChat = async (e) => {
    const newChat = await createNewChat(config.project_id)
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