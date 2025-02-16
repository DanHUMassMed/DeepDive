import React, { useState, useRef, useEffect } from 'react';
import { CiGlobe } from 'react-icons/ci';
import { IoBulbOutline, IoArrowUpCircle } from 'react-icons/io5';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { dark } from "react-syntax-highlighter/dist/esm/styles/prism";
import useChatEffect from '../hooks/useChatEffect';


// DialogContainer Component - Main container for the chat UI
const DialogContainer = () => {
  const textareaRef = useRef(null);
  const [chatHistory, setChatHistory] = useState([]);  
  const [messageToSend, setMessageToSend] = useState('');
  const [isProcessing, setIsProcessing] = useState(false); 

  // Use the custom hook
  const { closeWebSocket } = useChatEffect(messageToSend, setChatHistory, setIsProcessing);
  

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent form submission
      const userMessage = textareaRef.current.value;
      if (!userMessage.trim() || isProcessing) return;

      // Add the user's message to the chat history
      setChatHistory((prev) => [...prev, { type: 'user', content: userMessage }]);

      // Send the user's message to the server
      setMessageToSend(userMessage);
      textareaRef.current.value = '';  
    }
  };


  const handleStopMessage = (e) => {
    e.preventDefault();
    if (isProcessing) {
      try {
        // Call the FastAPI cancel endpoint when [STOP] message is detected
        const response = axios.post('http://localhost:8000/cancel-stream');
        console.log('Cancel stream response:', response.data);
        closeWebSocket();
      } catch (error) {
        console.error('Error cancelling the stream:', error);
      }
    }
  };

  return (
    <div className="w-full h-full p-4 flex flex-col justify-end">
      <ChatWindow chatHistory={chatHistory} />
      <ChatPrompt textareaRef={textareaRef} handleKeyDown={handleKeyDown} />
    </div>
  );
};

// ChatWindow Component - Holds all chat interactions (User & AI dialogs)
const ChatWindow = ({ chatHistory }) => {
  const chatWindowRef = useRef(null);

  useEffect(() => {
    // Scroll to the bottom when messages change
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [chatHistory]); // Run the effect every time messages change

  return (
    <div
      ref={chatWindowRef} 
      className="flex-grow overflow-y-auto p-2 max-h-[calc(100vh-150px)]"
    >
      {chatHistory.map((interaction, index) => (
        <ChatInteraction key={index} interaction={interaction} />
      ))}
    </div>
  );
};

// ChatInteraction Component - A single conversation exchange
const ChatInteraction = ({ interaction }) => {
  return (
    <div className={`flex w-full ${interaction.type === 'user' ? 'justify-start' : 'justify-end'} mb-4`}>
      {interaction.type === 'user' ? (
        <UserDialog interaction={interaction} />
      ) : (
        <AIDialog interaction={interaction} />
      )}
    </div>
  );
};

// UserDialog Component - User's message with avatar and text
const UserDialog = ({ interaction }) => {
  return (
    <div className="flex items-center w-full max-w-full space-x-2 bg-blue-100 p-3 rounded-lg">
      <img
        src="/images/avatar-1.png"
        alt="User Avatar"
        className="rounded-full w-10 h-10"
      />
      <div className="text-sm">
        <ReactMarkdown>{interaction.content}</ReactMarkdown>
      </div>
    </div>
  );
};

// AIDialog Component - AI's response with avatar and text
const AIDialog = ({ interaction }) => {
  return (
    <div className="flex items-center w-full max-w-full space-x-2 bg-gray-100 p-3 rounded-lg">
      <img
        src="/images/ai-avatar.png"
        alt="AI Avatar"
        className="rounded-full w-10 h-10"
      />
      <div className="text-sm">
        <ReactMarkdown components={{
          code({ className, children, ...rest }) {
            const match = /language-(\w+)/.exec(className || "");
            return match ? (
              <SyntaxHighlighter
                PreTag="div"
                language={match[1]}
                style={dark}
                {...rest}
              >
                {children}
              </SyntaxHighlighter>
            ) : (
              <code {...rest} className={className}>
                {children}
              </code>
            );
          },
        }}>{interaction.content}</ReactMarkdown>
      </div>
    </div>
  );
};

// ChatPrompt Component - Textarea for user input
function ChatPrompt({ textareaRef, handleKeyDown }) {

  const [isTextEntered, setIsTextEntered] = useState(false);

  const handlePromptInput = () => {
    const textarea = textareaRef.current;
    textarea.style.height = 'auto'; // Reset height to auto before resizing
    textarea.style.height = `${textarea.scrollHeight}px`; // Set height to scrollHeight
    setIsTextEntered(textarea.value.trim().length > 0);

  };

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
        {/* Left-aligned buttons */}
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

        {/* Right-aligned button */}
        <button
          className="flex items-center space-x-2"
          disabled={!isTextEntered}
        >
          <IoArrowUpCircle 
            color={isTextEntered ? 'blue' : 'gray'}
            size={24}
          />
        </button>
      </div>
    </div>
  );
}

export default DialogContainer;