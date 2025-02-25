// src/App.js
import React, { useState, useEffect, createContext } from 'react';
import TopNav from './components/TopNav';
import LeftNav from './components/LeftNav';
import RightNav from './components/RightNav';
import DialogContainer from './components/DialogContainer';
import { ConfigProvider, useConfig } from './components/ConfigContext';


function App() {
  const [chatMessages, setChatMessages] = useState([]);  

  return (
    <div className="flex h-screen flex-col">
      <ConfigProvider>
      <TopNav />
      <div className="flex flex-grow">
        <LeftNav setChatMessages={setChatMessages}/>
        <DialogContainer chatMessages={chatMessages} setChatMessages={setChatMessages}/>
        <RightNav /> 
      </div>
      </ConfigProvider>
    </div>
  );
}

export default App;