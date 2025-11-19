import axios from 'axios';

const API_URL = 'http://localhost:8000';
const STORAGE_KEY = 'wfir_workflows';

// Local Storage Helpers
const getStoredWorkflows = (): any[] => {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? JSON.parse(stored) : [];
};

const saveStoredWorkflows = (workflows: any[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(workflows));
};

// API Functions

export const getWorkflows = async () => {
  return getStoredWorkflows();
};

export const getWorkflow = async (id: string) => {
  const workflows = getStoredWorkflows();
  const workflow = workflows.find((w: any) => w.id === id);
  if (!workflow) throw new Error('Workflow not found');
  return workflow;
};

export const createWorkflow = async (workflow: any) => {
  const workflows = getStoredWorkflows();
  const newWorkflow = { ...workflow, id: crypto.randomUUID() };
  workflows.push(newWorkflow);
  saveStoredWorkflows(workflows);
  return newWorkflow;
};

export const updateWorkflow = async (id: string, workflow: any) => {
  const workflows = getStoredWorkflows();
  const index = workflows.findIndex((w: any) => w.id === id);
  if (index === -1) throw new Error('Workflow not found');
  workflows[index] = { ...workflow, id };
  saveStoredWorkflows(workflows);
  return workflows[index];
};

export const runWorkflow = async (_id: string, _inputs: any) => {
  throw new Error("Server-side execution is not supported. Please compile and run locally.");
};

export const transpileWorkflow = async (id: string, target: string = 'langgraph') => {
  const workflow = await getWorkflow(id);
  const response = await axios.post(`${API_URL}/compile`, {
    workflow,
    target
  });
  return response.data;
};

export const validateWorkflow = async (id: string) => {
  const workflow = await getWorkflow(id);
  const response = await axios.post(`${API_URL}/validate`, workflow);
  return response.data;
};

export const getNodeTypes = async () => {
  const response = await axios.get(`${API_URL}/node-types`);
  return response.data;
};
