import { apiRequest } from "./apiRequestUtil.mjs";

  
export const getProjectState = (project_id) => {
    return apiRequest('get', `/projects/${project_id}/state`);
};

export const createProjectState = (projectStateItem) => {
    return apiRequest('post', `/projects/state`, projectStateItem );
};

export const updateProjectState = (project_id, projectStateItem) => {
    return apiRequest('put', `/projects/${project_id}/state`, projectStateItem );
};

export const deleteProjectState = (project_id) => {
    return apiRequest('delete', `/projects/${project_id}/state`);
};

export const getChatHistoryTimestamp = (project_id) => {
    return apiRequest('get', `/projects/${project_id}/timestamp`);
};

