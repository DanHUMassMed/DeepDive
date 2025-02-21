import { useEffect, useRef, useContext } from 'react';
import ConfigContext from '../components/ConfigContext';

const useChatEffect = (messageToSend, setChatMessage) => {
  const { config, setConfig  } = useContext(ConfigContext);

  const websocketRef = useRef(null);

  const setIsProcessing = (isProcessing) => {
    setConfig((prevConfig) => ({...prevConfig, isProcessingPrompt: isProcessing}));
  }

  const closeWebSocket = () => {
    if (websocketRef.current) {
      if (websocketRef.current.readyState === WebSocket.CONNECTING) {
        // Wait until the WebSocket is open, then close it
        websocketRef.current.onopen = () => {
          console.log("WebSocket opened, now closing it");
          websocketRef.current.close();
        };
      } else if (websocketRef.current.readyState === WebSocket.OPEN) {
        // If already open, close the WebSocket directly
        console.log("WebSocket is open, closing it now");
        websocketRef.current.close();
      }
    }
    setIsProcessing(false);
  };

  useEffect(() => {
    if (messageToSend.trim()) {
      // Initialize WebSocket connection
      websocketRef.current = new WebSocket("ws://localhost:8000/ws/sendMessage?project_id=DeepDive");

      websocketRef.current.onopen = () => {
        setIsProcessing(true);
        console.log("websocketRef.current.send(messageToSend);")
        websocketRef.current.send(messageToSend);
      };

      websocketRef.current.onclose = () => {
        console.log('WebSocket connection closed');
        setIsProcessing(false);
      };

      websocketRef.current.onerror = (error) => {
        console.error('WebSocket error!!!:', error);
      };

      websocketRef.current.onmessage = (event) => {
        let message = event.data;

        if (message.includes('[DONE]')) {
          message = message.replace('[DONE]', '\n');
          setIsProcessing(false);
        }

        setChatMessage((prev) => {
          const prevChatMessage = [...prev];
          const lastMessage = prevChatMessage[prevChatMessage.length - 1];
          if (lastMessage && lastMessage.type === 'ai') {
            lastMessage.content += message;
          } else {
            prevChatMessage.push({ type: 'ai', content: message });
          }
          return prevChatMessage;
        });
      };
    }

    // Cleanup on component unmount
    return () => {
      closeWebSocket();
      

    };
  }, [messageToSend, setChatMessage]);

  return { closeWebSocket };
};

export default useChatEffect;