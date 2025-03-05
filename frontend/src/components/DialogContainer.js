import React, { useState, useRef, useEffect, useContext } from 'react';
import { useConfig } from './ConfigContext'; 

import Think from './Think';
import { CiGlobe } from 'react-icons/ci';
import { IoBulbOutline, IoArrowUpCircle, IoStop } from 'react-icons/io5';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkHtml from 'remark-html';
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { dark, vs, prism } from "react-syntax-highlighter/dist/esm/styles/prism";
import useChatEffect from '../hooks/useChatEffect';
import { cancelActiveChat } from '../api/chatAPI.mjs';
import rehypeRaw from 'rehype-raw';


// DialogContainer Component - Main container for the chat UI
const DialogContainer = ({ chatMessages, setChatMessages }) => {
  const { persistentConfig, ephemeralConfig, updateConfig } = useConfig();


  const textareaRef = useRef(null);
  const [messageToSend, setMessageToSend] = useState('');
  
  // Use the custom hook
  const { closeWebSocket } = useChatEffect(messageToSend, setChatMessages);
  useEffect(() => {
    // Scroll to the bottom when messages change
    if (ephemeralConfig.isProcessingPrompt) {
      updateConfig({ ephemeral: { isProcessingPrompt: false } });
    }
  }, []); // Run the effect every time messages change



  const handleSendPrompt = (e) => {
    //TODO: If you send the exact prompt twice the second prompt will not trigger an update
    // and this will not call the chat server
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent form submission
      const userMessage = textareaRef.current.value;
      if (!userMessage.trim() || ephemeralConfig.isProcessingPrompt) return;

      // Add the user's message to the chat history
      setChatMessages((prev) => [...prev, { type: 'user', content: userMessage }]);

      // Send the user's message to the server
      updateConfig({ ephemeral: { isPromptTextEntered: false } });
      setMessageToSend(userMessage);
      textareaRef.current.value = '';
    }
  };


  const handleStopMessage = (e) => {
    e.preventDefault();
    if (ephemeralConfig.isProcessingPrompt) {
      cancelActiveChat(persistentConfig.project_id)
      updateConfig({ ephemeral: { isPromptTextEntered: false } });
    }
  };

  return (
    <div className="w-full h-full p-4 flex flex-col justify-end">
      <ChatWindow chatMessages={chatMessages} />
      <ChatPrompt textareaRef={textareaRef} 
                  handleSendPrompt={handleSendPrompt} 
                  handleStopMessage={handleStopMessage} />
    </div>
  );
};

// ChatWindow Component - Holds all chat interactions (User & AI dialogs)
const ChatWindow = ({ chatMessages }) => {
  const chatWindowRef = useRef(null);

  useEffect(() => {
    // Scroll to the bottom when messages change
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [chatMessages]); // Run the effect every time messages change

  return (
    <div
      ref={chatWindowRef} 
      className="flex-grow overflow-y-auto p-2 max-h-[calc(100vh-150px)]"
    >
      {chatMessages.map((interaction, index) => (
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
  const [isOpen, setIsOpen] = useState(true);

  const onClick = () => {
    alert('Button clicked!!!');
  };

  // PART OF TIME SINK OF HIDE AND SHOW THINK
  // useEffect(() => {
  //   const button = document.getElementById('stupid_trick')   
  //   button.addEventListener('click', onClick);

  //   return () => {
  //     button.removeEventListener('click', handleClick);
  //   };
  // }, []); 


  const toggleSection = () => setIsOpen(!isOpen);

  // // Preprocess function to replace <think> and </think>
  // const preprocessMarkdown = (markdown) => {
  //   return markdown
  //     .replace(/<think>/g, "<div> <button id='stupid_trick' style=' background-color: #007bff; color: #fff; border: none; padding: 10px; cursor: pointer; width: 100%; text-align: left; ' >Reveal Thinking Process</button> <div id='toggleContent' style=' margin-top: 10px; padding: 10px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 5px; white-space: pre-wrap; display: none; '> <p>")   
  //     .replace(/<\/think>/g, "</p> </div> </div><script>");  
  // };
  // const postprocess = preprocessMarkdown(interaction.content);

  const components = {
    // Custom rendering for <think> tags

    code({ className, children, ...rest }) {
      const match = /language-(\w+)/.exec(className || '');
      return match ? (
        <SyntaxHighlighter
          PreTag="div"
          language={match[1]}
          style={prism}
          {...rest}
        >
          {children}
        </SyntaxHighlighter>
      ) : (
        <code {...rest} className={className}>
          {children}
        </code>
      );
    },think({ children, ...rest }) {
      return  <div {...rest}>{children}</div>
     }
 
  };


  // Log the content before rendering
  //console.log(`[*********************[${interaction.content}]***********************]`);

  return (
    <div className="flex items-center w-full max-w-full space-x-2 bg-gray-100 p-3 rounded-lg">
      <img
        src="/images/ai-avatar.png"
        alt="AI Avatar"
        className="rounded-full w-10 h-10"
      />
      <div className="text-sm">
        <ReactMarkdown remarkPlugins={[remarkGfm, remarkHtml]} rehypePlugins={[rehypeRaw]} components={components}
>{interaction.content}</ReactMarkdown>
      </div>
    </div>
  );
};

// ChatPrompt Component - Textarea for user input
function ChatPrompt({ textareaRef, handleSendPrompt, handleStopMessage }) {
  const { ephemeralConfig, updateConfig } = useConfig();
  const [isSearchEnabled, setIsSearchEnabled] = useState(false);
  const [isReasonEnabled, setIsReasonEnabled] = useState(false);


  const handleOnChangePrompt = () => {
    const textarea = textareaRef.current;
    textarea.style.height = 'auto'; // Reset height to auto before resizing
    textarea.style.height = `${textarea.scrollHeight}px`; // Set height to scrollHeight
    updateConfig({ ephemeral: { isPromptTextEntered: (textarea.value.trim().length > 0) } });
  };

    // Toggle search button
    const toggleSearch = () => {
      setIsSearchEnabled(!isSearchEnabled);
    };
  
    // Toggle reason button
    const toggleReason = () => {
      setIsReasonEnabled(!isReasonEnabled);
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
            className={`flex items-center space-x-2 ${isSearchEnabled ? 'text-blue-500' : 'text-gray-500'}`}
          >
            <CiGlobe size={24} />
            <span>{isSearchEnabled ? 'Search On' : 'Search'}</span>
          </button>
          <button
            onClick={toggleReason}
            className={`flex items-center space-x-2 ${isReasonEnabled ? 'text-blue-500' : 'text-gray-500'}`}
          >
            <IoBulbOutline size={24} />
            <span>{isReasonEnabled ? 'Reason On' : 'Reason'}</span>
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

export default DialogContainer;