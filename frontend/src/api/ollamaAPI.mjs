import { apiRequest } from "./apiRequestUtil.mjs";

  
export const getAvailableModels = () => {
    return apiRequest('get', `/ollama/available-models`);
};

