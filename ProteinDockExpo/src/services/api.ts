// Render Production URL
const API_URL = 'https://proteindock.onrender.com/api';

export const api = {
  // Auth
  register: async (data: any) => {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  login: async (data: any) => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  // Proteins
  fetchProtein: async (pdbId: string, token: string) => {
    const response = await fetch(`${API_URL}/proteins/fetch/${pdbId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.json();
  },

  uploadProtein: async (data: any, token: string) => {
    const response = await fetch(`${API_URL}/proteins`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  getGridSuggestion: async (proteinId: string, token: string) => {
    const response = await fetch(`${API_URL}/proteins/grid-suggestion/${proteinId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.json();
  },

  searchProteins: async (query: string, token: string) => {
    const response = await fetch(`${API_URL}/proteins/search?query=${query}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  // Ligands
  createLigand: async (data: any, token: string) => {
    const response = await fetch(`${API_URL}/ligands`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  getLigands: async (token: string) => {
    const response = await fetch(`${API_URL}/ligands`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  // Docking
  submitDocking: async (data: any, token: string) => {
    const response = await fetch(`${API_URL}/docking/submit`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  getJob: async (jobId: string, token: string) => {
    const response = await fetch(`${API_URL}/docking/job/${jobId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  getJobs: async (token: string) => {
    const response = await fetch(`${API_URL}/docking/jobs`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },
};
