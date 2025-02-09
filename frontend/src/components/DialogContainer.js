import React, { useState, useRef, useEffect } from 'react';
import { CiGlobe } from 'react-icons/ci';
import { IoBulbOutline, IoArrowUpCircle } from 'react-icons/io5';
import { useChat } from '../hooks/useChat';


// DialogContainer Component - Main container for the chat UI
const DialogContainer = () => {
  const textareaRef = useRef(null);
  const { messages, sendMessage } = useChat();

  const handleSendMessage = async (prompt) => {
    console.log('handleSendMessage:', prompt);
    if (prompt.trim()) {
      await sendMessage(prompt); // returns messages
    }
  };


  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent form submission
      const userInput = textareaRef.current.value;

      console.log('Sending message:', userInput);
      handleSendMessage(userInput);

      textareaRef.current.value = ''; // Clear the textarea
    }
  };

  return (
    <div className="w-full h-full p-4 flex flex-col justify-end">
      <ChatWindow messages={messages} />
      <ChatPrompt textareaRef={textareaRef} handleKeyDown={handleKeyDown} />
    </div>
  );
};

// ChatWindow Component - Holds all chat interactions (User & AI dialogs)
const ChatWindow = ({ messages }) => {
  return (
    <div className="flex-grow overflow-auto p-2">
      {messages.map((interaction, index) => (
        <ChatInteraction key={index} interaction={interaction} />
      ))}
    </div>
  );
};

// ChatInteraction Component - A single conversation exchange
const ChatInteraction = ({ interaction }) => {
  return (
    <div className={`flex w-full ${interaction.role === 'user' ? 'justify-start' : 'justify-end'} mb-4`}>
      {interaction.role === 'user' ? (
        <UserDialog message={interaction.message} />
      ) : (
        <AIDialog message={interaction.message} />
      )}
    </div>
  );
};

// UserDialog Component - User's message with avatar and text
const UserDialog = ({ message }) => {
  return (
    <div className="flex items-center w-full max-w-full space-x-2 bg-blue-100 p-3 rounded-lg">
      <img
        src="/images/avatar-1.png"
        alt="User Avatar"
        className="rounded-full w-10 h-10"
      />
      <div className="text-sm">{message}</div>
    </div>
  );
};

// AIDialog Component - AI's response with avatar and text
const AIDialog = ({ message }) => {
  return (
    <div className="flex items-center w-full max-w-full space-x-2 bg-gray-100 p-3 rounded-lg">
      <img
        src="/images/ai-avatar.png"
        alt="AI Avatar"
        className="rounded-full w-10 h-10"
      />
      <div className="text-sm">{message}</div>
    </div>
  );
};

// ChatPrompt Component - Textarea for user input
function ChatPrompt({ textareaRef, handleKeyDown }) {
  const [isTextEntered, setIsTextEntered] = useState(false);

  const handleInput = () => {
    const textarea = textareaRef.current;
    textarea.style.height = 'auto'; // Reset height to auto before resizing
    textarea.style.height = `${textarea.scrollHeight}px`; // Set height to scrollHeight
    setIsTextEntered(textarea.value.trim().length > 0);

  };

  useEffect(() => {
    const textarea = textareaRef.current;
    textarea.addEventListener('input', handleInput);

    // Clean up event listener
    return () => {
      textarea.removeEventListener('input', handleInput);
    };
  }, []);

  return (
    <div className="flex flex-col w-full">
      <textarea
        ref={textareaRef}
        id="chat-textarea"
        className="w-full p-2 border border-gray-300 rounded-md resize-none overflow-hidden"
        placeholder="Enter your prompt here..."
        onKeyDown={handleKeyDown} // Handle key down event
      />

      <div className="flex items-center justify-between w-full mt-2"> 
        {/* Left-side buttons */}
        <div className="flex space-x-4">
          <button className="flex items-center space-x-2">
            <CiGlobe size={24}/>
            <span>Search</span>
          </button>
          <button className="flex items-center space-x-2">
            <IoBulbOutline size={24}/>
            <span>Reason</span>
          </button>
        </div>

        {/* Right-side button */}
        <button
          className="flex items-center space-x-2"
          disabled={!isTextEntered}
        >
          <IoArrowUpCircle 
            color={isTextEntered ? 'blue' : 'gray'} // Set color based on isTextEntered
            size={24}
          />
        </button>
      </div>
    </div>
  );
}

export default DialogContainer;