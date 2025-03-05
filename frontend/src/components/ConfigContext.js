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
const defaultPersistentConfig = {
  theme: 'dark',
  project_id: 'deep-dive',
  isLeftNavOpen: true,
  isRightNavOpen: false,
  chat_history_timestamp: '',
};

const defaultEphemeralConfig = {
  isPromptTextEntered: false,
  isProcessingPrompt: false,
};

// ConfigProvider component
export const ConfigProvider = ({ children }) => {
  // Separate state for persistent and ephemeral attributes
  const [persistentConfig, setPersistentConfig] = useState(defaultPersistentConfig);
  const [ephemeralConfig, setEphemeralConfig] = useState(defaultEphemeralConfig);

  // Load persistent config from localStorage or use default
  useEffect(() => {
    const storedPersistentConfig = localStorage.getItem('appConfig');
    if (storedPersistentConfig) {
      setPersistentConfig(JSON.parse(storedPersistentConfig));
    }
  }, []);

  // Save only persistent config to localStorage
  useEffect(() => {
    localStorage.setItem('appConfig', JSON.stringify(persistentConfig));
  }, [persistentConfig]);

  // Function to update both persistent and ephemeral config
  const updateConfig = (newConfig) => {
    console.log("newConfig ", newConfig)
    if (newConfig.hasOwnProperty('persistent')) {
      setPersistentConfig((prev) => ({ ...prev, ...newConfig.persistent }));
    }
    if (newConfig.hasOwnProperty('ephemeral')) {
      setEphemeralConfig((prev) => ({ ...prev, ...newConfig.ephemeral }));
    }
  };

  return (
    <ConfigContext.Provider value={{ persistentConfig, ephemeralConfig, updateConfig }}>
      {children}
    </ConfigContext.Provider>
  );
};

export default ConfigContext;