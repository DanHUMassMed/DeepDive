import React, { useState, useEffect, useRef, useContext } from 'react';
import { MdOutlineDriveFileRenameOutline } from "react-icons/md";
import { FiShare } from "react-icons/fi";
import { RiDeleteBinLine } from "react-icons/ri";
import { Tooltip } from 'react-tooltip';
import { renameChat, getChatHistoryTimestamp, deleteChatHistoryItem } from "../api/chatAPI.mjs"
import ConfigContext from './ConfigContext';


const ChatHistoryItem = ({ chat }) => {
  const { config, setConfig  } = useContext(ConfigContext);
  const { chat_id, chat_title, chat_llm_name, chat_start_date, active_chat } = chat;
  const [showMenu, setShowMenu] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState(null); // Holds the type of modal (rename, share, delete)
  const [newName, setNewName] = useState(chat_title); // For the new name input in Rename
  const [confirmation, setConfirmation] = useState(false); // For delete confirmation
  const [shareLink, setShareLink] = useState(''); // For Share Link (will be implemented later)
  const menuRef = useRef(null);

  const handleClick = () => {
    console.log(`Bringing back chat: ${chat_title}`);
    // Implement logic to restore the chat here
  };

  const handleEllipsisClick = (e) => {
    e.stopPropagation(); // Prevents triggering the button click event
    setShowMenu((prevShowMenu) => !prevShowMenu); // Toggle the menu visibility
  };

  // Close the menu if clicked outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setShowMenu(false); // Hide the menu if clicked outside
      }
    };

    // Add event listener when the menu is visible
    if (showMenu) {
      document.addEventListener('click', handleClickOutside);
    }

    // Clean up the event listener when the component unmounts or when the menu is closed
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [showMenu]);

  // Open Modal based on action
  const handleMenuClick = (action) => {
    setModalType(action);
    setShowModal(true);
    setShowMenu(false); // Close the menu
  };

  // Handle actions for the modal
  const handleModalClose = () => {
    setShowModal(false);
    setConfirmation(false);
    setNewName(chat_title)
  };

  const handleRename = () => {
    console.log(`Renaming chat to: ${newName}`);
    renameChat(chat_id, newName)
      .then((chatItem) => {
        // Handle the updated chat item here
        console.log('Updated chat item:', chatItem);
        return getChatHistoryTimestamp(config.project_id); // Return the promise from getChatHistoryTimestamp
      })
      .then((chatHistoryTimestamp) => {
        // Handle the result of getChatHistoryTimestamp
        setConfig((prevConfig) => ({
          ...prevConfig,
          chat_history_timestamp: chatHistoryTimestamp,
        }));
        handleModalClose();
      })
      .catch((error) => {
        // Handle any errors that occurred during the rename operation
        console.error('Error renaming chat:', error);
        // Optionally, handle the error (e.g., show a notification to the user)
      });
  };

  const handleDelete = () => {
    console.log(`Deleting chat: ${chat_title}`);
    deleteChatHistoryItem(chat_id)
    .then((returnStatus) => {
      // Handle the updated chat item here
      //TODO manage returnStatus {'status':'FAIL'}
      return getChatHistoryTimestamp(config.project_id); // Return the promise from getChatHistoryTimestamp
    })
    .then((chatHistoryTimestamp) => {
      // Handle the result of getChatHistoryTimestamp
      setConfig((prevConfig) => ({
        ...prevConfig,
        chat_history_timestamp: chatHistoryTimestamp,
      }));
      handleModalClose();
    })
    .catch((error) => {
      // Handle any errors that occurred during the rename operation
      console.error('Error renaming chat:', error);
      // Optionally, handle the error (e.g., show a notification to the user)
    });

    handleModalClose();
  };

  const handleShare = () => {
    console.log(`Sharing chat with link: ${shareLink}`);
    // Handle share logic here
    handleModalClose();
  };

  return (
    <div className="relative group">
      {/* Main Chat Button */}
      <button
        onClick={handleClick}
        className={`block w-full text-left p-2 rounded-lg hover:bg-gray-400 focus:outline-none
          ${active_chat ? 'border border-blue-500 rounded-full' : ''}`} // Conditional blue oval
      >
        <div className="font-semibold">{chat_title}</div>
        <div className="text-sm text-gray-600">{chat_llm_name}</div>
        <div className="text-xs text-gray-500">{chat_start_date}</div>
      </button>

      {/* Ellipsis Button (Visible on Hover) */}
      <div
        className="absolute top-2 right-2 p-1 text-gray-500 cursor-pointer opacity-0 group-hover:opacity-100"
        onClick={handleEllipsisClick}  // Click to toggle the menu
      >
        <span data-tooltip-id="optionsTooltip">...</span>
        <Tooltip
        id="optionsTooltip"
        place="top"
        type="dark"
        effect="solid"
      >
        Options
      </Tooltip>
        {showMenu && (
          <div
          ref={menuRef} // Attach the ref to the menu
          className="fixed bg-white shadow-lg rounded-lg w-32"
          style={{ 
            zIndex: 1000,  // Ensure this menu is above other elements
          }}
        >
          <ul className="py-1">
            <li
              className="px-4 py-2 hover:bg-gray-100 cursor-pointer flex items-center"
              onClick={() => handleMenuClick('rename')}
            >
              <MdOutlineDriveFileRenameOutline className="mr-2" /> Rename
            </li>
            <li
              className="px-4 py-2 hover:bg-gray-100 cursor-pointer flex items-center"
              onClick={() => handleMenuClick('share')}
            >
              <FiShare className="mr-2" /> Share
            </li>
            <li
              className="px-4 py-2 hover:bg-gray-100 cursor-pointer flex items-center text-red-500"
              onClick={() => handleMenuClick('delete')}
            >
              <RiDeleteBinLine className="mr-2" /> Delete
            </li>
          </ul>
        </div>
        )}
      </div>

      {/* Modal for Rename, Share, Delete */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-gray-500 bg-opacity-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full relative">
            <button
              onClick={handleModalClose}
              className="absolute top-2 right-2 text-gray-500"
            >
              X
            </button>
            <h2 className="font-semibold text-xl mb-4">{modalType.charAt(0).toUpperCase() + modalType.slice(1)}</h2>
            {modalType === 'rename' && (
              <>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="border p-2 mb-4 w-full"
                  placeholder="Enter new name"
                />
                <div className="flex justify-between">
                  <button onClick={handleRename} className="bg-blue-500 text-white p-2 rounded-lg w-full">
                    Rename
                  </button>
                  <button onClick={handleModalClose} className="bg-gray-500 text-white p-2 rounded-lg w-full">
                    Cancel
                  </button>
                </div>
              </>
            )}
            {modalType === 'delete' && (
              <>
                <p className="text-gray-600 mb-4">Are you sure you want to delete the chat "{chat_title}"?</p>
                <div className="flex justify-between">
                  <button
                    onClick={handleDelete} className="bg-red-500 text-white p-2 rounded-lg w-full">
                    Yes
                  </button>
                  <button
                    onClick={handleModalClose} className="bg-gray-500 text-white p-2 rounded-lg  w-full">
                    Cancel
                  </button>
                </div>
              </>
            )}
            {modalType === 'share' && (
              <>
                <input
                  type="text"
                  value={shareLink}
                  onChange={(e) => setShareLink(e.target.value)}
                  className="border p-2 mb-4 w-full"
                  placeholder="Shareable link"
                />
                <div className="flex justify-between">
                  <button onClick={handleShare} className="bg-green-500 text-white p-2 rounded-lg w-full">
                    Share
                  </button>
                  <button onClick={handleModalClose} className="bg-gray-500 text-white p-2 rounded-lg w-full">
                    Cancel
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHistoryItem;