import React, { useState, useRef, useEffect, useContext } from 'react';
import { useConfig } from './ConfigContext'; 
import ChatPrompt from './ChatPrompt';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkHtml from 'remark-html';
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { dark, vs, prism } from "react-syntax-highlighter/dist/esm/styles/prism";
import rehypeRaw from 'rehype-raw';

import useChatEffect from '../hooks/useChatEffect';
import { cancelActiveChat } from '../api/chatAPI.mjs';


// DialogContainer Component - Main container for the chat UI
const DialogContainer = ({ chatMessages, setChatMessages }) => {
  const { persistentConfig, ephemeralConfig, updateConfig } = useConfig();

  const textareaRef = useRef(null);
  const [messageToSend, setMessageToSend] = useState('');
  const [forceRenderKey, setForceRenderKey] = useState(0);
  
  // Use the custom hook
  const { closeWebSocket } = useChatEffect(messageToSend, setChatMessages, forceRenderKey);

  useEffect(() => {
    // Scroll to the bottom when messages change
    if (ephemeralConfig.isProcessingPrompt) {
      updateConfig({ ephemeral: { isProcessingPrompt: false } });
    }
  }, []); // Run the effect every time messages change


  const handleSendPrompt = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent form submission
      const userMessage = textareaRef.current.value;
      if (!userMessage.trim() || ephemeralConfig.isProcessingPrompt) return;

      // Add the user's message to the chat history
      setChatMessages((prev) => [...prev, { type: 'user', content: userMessage }]);

      // Send the user's message to the server
      updateConfig({ ephemeral: { isPromptTextEntered: false } });
      setMessageToSend(userMessage);
      // This make sure if we send the same message twice we still rerender
      setForceRenderKey(prevKey => prevKey + 1);
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
    <div className="flex w-full h-full p-4 flex-col justify-end">
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
        {interaction.content}
      </div>
    </div>
  );
};

// AIDialog Component - AI's response with avatar and text
const AIDialog = ({ interaction }) => {

  const components = {
    code({ className, children, ...rest }) {
      const match = /language-(\w+)/.exec(className || '');
      return match ? (
        <SyntaxHighlighter
          PreTag="div"
          language={match[1]}
          style={vs}
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
  console.log(`[*********************[${interaction.content}]***********************]`);

  return (
    <div className="flex items-center w-full max-w-full space-x-2 bg-gray-100 p-3 rounded-lg">
      <img
        src="/images/ai-avatar.png"
        alt="AI Avatar"
        className="rounded-full w-10 h-10"
      />
      <div className="text-sm">
        <ReactMarkdown 
            remarkPlugins={[remarkGfm, remarkHtml]} 
            rehypePlugins={[rehypeRaw]} 
            components={components}
        >
          {interaction.content}
        </ReactMarkdown>      
      </div>
    </div>
  );
};

export default DialogContainer;