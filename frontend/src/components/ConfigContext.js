import React, { createContext, useContext, useState } from 'react';

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

// ConfigProvider component
export const ConfigProvider = ({ children }) => {
  const [config, setConfig] = useState({
    apiUrl: 'http://127.0.0.1:8000/',
    theme: 'dark',
    isLeftNavOpen: true,
    isRightNavOpen: false,
    isPromptTextEntered: false,
    isProcessingPrompt: false
  });

  return (
    <ConfigContext.Provider value={{ config, setConfig }}>
      {children}
    </ConfigContext.Provider>
  );
};

export default ConfigContext;