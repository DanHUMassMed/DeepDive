import { apiRequest } from "./apiRequestUtil.mjs";

  
export const getChatHistoryItems = (project_id) => {
    return apiRequest('get', `/chat-history/${project_id}/items`);
};

export const deleteChatHistoryItems = (project_id) => {
    return apiRequest('delete', `/chat-history/${project_id}/items`);
};

export const getActiveChat = (project_id) => {
    return apiRequest('get', `/chat-history/${project_id}/active-chat`);
};

export const setActiveChat = (project_id, chat_id) => {
    return apiRequest('put', `/chat-history/${project_id}/active-chat/${chat_id}`);
};

export const createChatHistoryItem = (chatHistoryItem) => {
    return apiRequest('post', `/chat-history/${chatHistoryItem.project_id}/item`, chatHistoryItem );
  };

export const updateChatHistoryTitle = (chatHistoryItem) => {
    return apiRequest('put', `/chat-history/${chatHistoryItem.project_id}/item/${chatHistoryItem.chat_id}/title`, chatHistoryItem);
};

export const deleteChatHistoryItem = (project_id, chat_id) => {
    return apiRequest('delete', `/chat-history/${project_id}/item/${chat_id}`);
};
