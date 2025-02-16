import React, { useState, useContext } from 'react';
import ConfigContext from './ConfigContext';

const RightNav = ({ isOpen }) => {
  const { config, setConfig  } = useContext(ConfigContext);
  return (
    <div className={`transition-all duration-300 ${config.isRightNavOpen ? 'w-64' : 'w-0'} bg-gray-200 h-full text-black`}></div>
  );
};

export default RightNav;
