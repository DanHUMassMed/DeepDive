import React, { useState, useRef, useEffect, useContext } from 'react';
import { useConfig } from './ConfigContext'; 
import { CiGlobe } from 'react-icons/ci';
import { IoBulbOutline, IoArrowUpCircle, IoStop } from 'react-icons/io5';

// ChatPrompt Component - Textarea for user input
const ChatPrompt = ({ textareaRef, handleSendPrompt, handleStopMessage }) => {
  const { ephemeralConfig, updateConfig } = useConfig();

  const handleOnChangePrompt = () => {
    const textarea = textareaRef.current;
    textarea.style.height = 'auto'; // Reset height to auto before resizing
    textarea.style.height = `${textarea.scrollHeight}px`; // Set height to scrollHeight
    updateConfig({ ephemeral: { isPromptTextEntered: (textarea.value.trim().length > 0) } });
  };

    // Toggle search button
    const toggleSearch = () => {
      updateConfig({ ephemeral: { isSearchEnabled: !ephemeralConfig.isSearchEnabled } });
    };
  
    // Toggle reason button
    const toggleReason = () => {
      updateConfig({ ephemeral: { isReasonEnabled: !ephemeralConfig.isReasonEnabled } });
    };
  
  return (
    <div className="flex flex-col w-full">
      <textarea
        ref={textareaRef}
        id="prompt-textarea"
        className="w-full p-2 border border-gray-300 rounded-md resize-none overflow-hidden"
        placeholder={ephemeralConfig.isProcessingPrompt ? 'Processing your request please wait ...' : 'Enter your prompt here...'}
        onKeyDown={handleSendPrompt} // Handle key down event
        onChange={handleOnChangePrompt}
      />

      <div className="flex items-center justify-between w-full mt-2">
        {/* Left-aligned buttons */}
        <div className="flex space-x-4">
          <button
            onClick={toggleSearch}
            className={`flex items-center space-x-2 ${ephemeralConfig.isSearchEnabled ? 'text-blue-500' : 'text-gray-500'}`}
          >
            <CiGlobe size={24} />
            <span>{ephemeralConfig.isSearchEnabled ? 'Search On' : 'Search'}</span>
          </button>
          <button
            onClick={toggleReason}
            className={`flex items-center space-x-2 ${ephemeralConfig.isReasonEnabled ? 'text-blue-500' : 'text-gray-500'}`}
          >
            <IoBulbOutline size={24} />
            <span>{ephemeralConfig.isReasonEnabled ? 'Reason On' : 'Reason'}</span>
          </button>
        </div>

        {/* Right-aligned button */}
        <ChatPromptButton handleStopMessage={handleStopMessage} />
      </div>
    </div>
  );
}

const ChatPromptButton = ({ handleStopMessage }) => {
  const { ephemeralConfig } = useConfig();
  return ( <button
        className="flex items-center space-x-2"
        disabled={!ephemeralConfig.isProcessingPrompt}
        onClick={handleStopMessage}
      >
        {ephemeralConfig.isProcessingPrompt ? (
              <IoStop 
              color='blue'
              size={24}
            />
            ) : (
              <IoArrowUpCircle 
              color={ephemeralConfig.isPromptTextEntered ? 'blue' : 'gray'}
              size={24}
            />
            )
        }
      </button>
    );
};

export default ChatPrompt;
