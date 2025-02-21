import React, { createContext, useContext, useState, useEffect } from 'react';

// Create the ConfigContext
const ConfigContext = createContext();

// Custom hook to use the ConfigContext
export const useConfig = () => {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
};

// Default configuration values
const defaultConfig = {
  apiUrl: 'http://127.0.0.1:8000/',
  theme: 'dark',
  project_id: 'deep-dive',
  active_chat_id:'',
  isLeftNavOpen: true,
  isRightNavOpen: false,
  isPromptTextEntered: false,
  isProcessingPrompt: false,
};

// ConfigProvider component
export const ConfigProvider = ({ children }) => {
  const [config, setConfig] = useState(defaultConfig);

  // Load config from localStorage or use default config
  useEffect(() => {
    const storedConfig = localStorage.getItem('appConfig');
    if (storedConfig) {
      setConfig(JSON.parse(storedConfig));
    }
  }, []);

  // Save config to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('appConfig', JSON.stringify(config));
  }, [config]);

  return (
    <ConfigContext.Provider value={{ config, setConfig }}>
      {children}
    </ConfigContext.Provider>
  );
};

export default ConfigContext;