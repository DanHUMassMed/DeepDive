// src/App.js
import React, { useState } from 'react';
import LeftNav from './components/LeftNav';
import RightNav from './components/RightNav';
import DialogContainer from './components/DialogContainer';
import TopNav from './components/TopNav';


function App() {
  const [isLeftNavOpen, setIsLeftNavOpen] = useState(true);
  const [isRightNavOpen, setIsRightNavOpen] = useState(false); // State for right nav

  const toggleLeftNav = () => {
    setIsLeftNavOpen((prevState) => !prevState);
  };

  const toggleRightNav = () => {
    setIsRightNavOpen((prevState) => !prevState); // Toggle the right nav state
  };


  return (
    <div className="flex h-screen flex-col">
      <TopNav isLeftSidebarOpen={isLeftNavOpen} 
            toggleLeftSidebar={toggleLeftNav} 
            isRightSidebarOpen={isRightNavOpen} 
            toggleRightSidebar={toggleRightNav} />
      <div className="flex flex-grow">
        <LeftNav isOpen={isLeftNavOpen} />
        <DialogContainer />
        <RightNav isOpen={isRightNavOpen} /> 
      </div>
    </div>
  );
}

export default App;