// src/App.js
import React, { useState, useEffect, createContext } from 'react';
import TopNav from './components/TopNav';
import LeftNav from './components/LeftNav';
import RightNav from './components/RightNav';
import DialogContainer from './components/DialogContainer';
import { ConfigProvider, useConfig } from './components/ConfigContext';


function App() {

  return (
    <div className="flex h-screen flex-col">
      <ConfigProvider>
      <TopNav />
      <div className="flex flex-grow">
        <LeftNav/>
        <DialogContainer />
        <RightNav /> 
      </div>
      </ConfigProvider>
    </div>
  );
}

export default App;