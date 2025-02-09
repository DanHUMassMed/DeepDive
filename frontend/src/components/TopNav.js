import React, { useState } from 'react';
import { VscLayoutSidebarLeft, VscLayoutSidebarLeftOff, VscLayoutSidebarRight, VscLayoutSidebarRightOff } from 'react-icons/vsc';
import { HiOutlinePencilSquare } from "react-icons/hi2";
import { FaCheck } from 'react-icons/fa';
import { IoChevronDownOutline } from "react-icons/io5";

const SelectModel = () => {
  const [selectedModel, setSelectedModel] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const models = [
    { label: "Select a Model", value: "", disabled: true },
    { label: "deepseek-r1:32b", value: "deepseek-r1:32b" },
    { label: "llama-3.2:30b", value: "llama-3.2:30b" },
  ];

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleSelect = (model) => {
    if (model.disabled) return; // Prevent selecting the disabled option
    setSelectedModel(model.label);
    setIsDropdownOpen(false);
  };

  return (
    <div className="relative">
      <button
        className="px-4 py-1 bg-gray-200 rounded-md text-black flex items-center"
        onClick={toggleDropdown}
      >
        <span>{selectedModel || "Select a Model"}</span>
        <IoChevronDownOutline size={18} className="ml-2" />
      </button>

      {isDropdownOpen && (
        <ul className="absolute z-10 mt-2 w-52 bg-white border border-gray-300 rounded-md shadow-lg">
          {models.map((model) => (
            <li
              key={model.value}
              onClick={() => handleSelect(model)}
              className={`px-6 py-2 cursor-pointer hover:bg-gray-100 ${
                model.disabled ? "text-gray-400 cursor-not-allowed" : ""
              }`}
            >
              <div className="flex items-center">
                {selectedModel === model.label && (
                  <FaCheck className="mr-2 text-green-500" />
                )}
                {model.label}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

const TopNav = ({ isLeftSidebarOpen, toggleLeftSidebar, isRightSidebarOpen, toggleRightSidebar, onNewChat }) => {
  return (
    <div className="flex justify-between items-center h-10 px-4 bg-gray-300 text-black">
      {/* New Chat button on the left */}
      <button onClick={onNewChat} className="focus:outline-none px-2">
        <HiOutlinePencilSquare size={24} color="black" />
      </button>
      
      {/* Select Model dropdown moved to the left */}
      <div className="flex-grow pl-[180px]">
        <SelectModel />
      </div>

      {/* Sidebar buttons on the right */}
      <div className="flex space-x-2">
        <button onClick={toggleLeftSidebar} className="focus:outline-none px-1">
          {isLeftSidebarOpen ? (
            <VscLayoutSidebarLeftOff size={24} color="black" />
          ) : (
            <VscLayoutSidebarLeft size={24} color="black" />
          )}
        </button>
        <button onClick={toggleRightSidebar} className="focus:outline-none px-1">
          {isRightSidebarOpen ? (
            <VscLayoutSidebarRightOff size={24} color="black" />
          ) : (
            <VscLayoutSidebarRight size={24} color="black" />
          )}
        </button>
      </div>
    </div>
  );
};

export default TopNav;