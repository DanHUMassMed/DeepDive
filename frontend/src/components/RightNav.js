import React, { useState, useContext } from 'react';
import ConfigContext from './ConfigContext';
import SelectLLM from './SelectLLM';
import SystemPrompt from './SystemPrompt';


const RightNav = ({ isOpen }) => {
  const { config, setConfig  } = useContext(ConfigContext);
  return (
    <div className={`transition-all duration-300 ${config.isRightNavOpen ? 'w-7/12' : 'w-0'} bg-gray-200 h-full text-black`}>
      <SelectLLM/>
      <SystemPrompt/>
    </div>
  );
};

export default RightNav;
