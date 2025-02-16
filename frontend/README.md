import React, { useState, useRef, useEffect } from 'react';

useState:   Allows you to add state to functional components.
useEffect:  Handles side effects (e.g., data fetching, subscriptions, and updating the DOM).
useContext: Allows you to access the value of a context inside functional components.
useReducer: Provides a way to manage complex state logic (similar to Redux, but without an external library).
useRef:     Provides a way to persist values across renders without causing re-renders.



== GlobalState:
ChatsHistory = [{title:title, model_nm:model_nm, start_time:time, chat:Chat}]
Chat = [{user:message, ai:message}]

== ConfigurationState:
api_root_url     = 'http://127.0.0.1:8000'
availableModels  = []
selectedModelNm  = ""
maxNumberOfChats = 10


== Methods:
Initialize()
   getAvailableModelNames() [API CALL]
   getAPIRootUrl()          [Config file]


SelectModel()

NewChat() {
   addToChatHistory()
   initializeChat()
}

DeleteChats()

Chat() {
   submitChat
}
