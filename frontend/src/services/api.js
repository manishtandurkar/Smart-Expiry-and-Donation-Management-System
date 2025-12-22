/**
 * API Service Layer
 * Handles all HTTP requests to the backend API
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Donors API
// ============================================================================

export const donorsAPI = {
  getAll: () => api.get('/api/donors'),
  getById: (id) => api.get(`/api/donors/${id}`),
  create: (data) => api.post('/api/donors', data),
  update: (id, data) => api.put(`/api/donors/${id}`, data),
  delete: (id, adminPassword) => api.delete(`/api/donors/${id}`, { headers: { 'X-Admin-Password': adminPassword } }),
};

// ============================================================================
// Items API
// ============================================================================

export const itemsAPI = {
  getAll: (params) => api.get('/api/items', { params }),
  getById: (id) => api.get(`/api/items/${id}`),
  create: (data) => api.post('/api/items', data),
  update: (id, data) => api.put(`/api/items/${id}`, data),
  getExpiring: (days = 30) => api.get('/api/items/expiring', { params: { days } }),
  getExpired: () => api.get('/api/items/expired'),
  predictCategory: (name) => api.post('/api/items/predict-category', null, { 
    params: { name } 
  }),
};

// ============================================================================
// Receivers API
// ============================================================================

export const receiversAPI = {
  getAll: () => api.get('/api/receivers'),
  getById: (id) => api.get(`/api/receivers/${id}`),
  create: (data) => api.post('/api/receivers', data),
  delete: (id, adminPassword) => api.delete(`/api/receivers/${id}`, { headers: { 'X-Admin-Password': adminPassword } }),
};

// ============================================================================
// Donations API
// ============================================================================

export const donationsAPI = {
  getAll: (params) => api.get('/api/donations', { params }),
  create: (data) => api.post('/api/donations', data),
};

// ============================================================================
// Alerts API
// ============================================================================

export const alertsAPI = {
  getAll: (params) => api.get('/api/alerts', { params }),
  getMongo: (params) => api.get('/api/alerts/mongo', { params }),
  triggerCheck: (days) => api.post('/api/alerts/check', null, { params: { days } }),
  acknowledge: (id) => api.put(`/api/alerts/${id}/acknowledge`),
};

// ============================================================================
// Statistics API
// ============================================================================

export const statsAPI = {
  getDashboard: () => api.get('/api/stats'),
};

// ============================================================================
// Admin API
// ============================================================================
export const adminAPI = {
  login: (username, password) => api.post('/api/admin/login', { username, password }),
};

export default api;
