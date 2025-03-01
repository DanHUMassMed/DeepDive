import { apiRequest } from "./apiRequestUtil.mjs";

  
export const getChatInteractions = (project_id, chat_id) => {
    return apiRequest('get', `/chat/${project_id}/interactions/${chat_id}`);
};

export const cancelActiveChat = (project_id) => {
    return apiRequest('post', `/chat/cancel/${project_id}`);
};
