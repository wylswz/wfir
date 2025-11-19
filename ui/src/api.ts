import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const getWorkflows = async () => {
  const response = await axios.get(`${API_URL}/workflows`);
  return response.data;
};

export const getWorkflow = async (id: string) => {
  const response = await axios.get(`${API_URL}/workflows/${id}`);
  return response.data;
};

export const createWorkflow = async (workflow: any) => {
  const response = await axios.post(`${API_URL}/workflows`, workflow);
  return response.data;
};

export const updateWorkflow = async (id: string, workflow: any) => {
  const response = await axios.put(`${API_URL}/workflows/${id}`, workflow);
  return response.data;
};

export const runWorkflow = async (id: string, inputs: any) => {
  const response = await axios.post(`${API_URL}/workflows/${id}/run`, { inputs });
  return response.data;
};

export const transpileWorkflow = async (id: string, target: string = 'langgraph') => {
  const response = await axios.post(`${API_URL}/workflows/${id}/transpile?target=${target}`);
  return response.data;
};

export const getNodeTypes = async () => {
  const response = await axios.get(`${API_URL}/node-types`);
  return response.data;
};
