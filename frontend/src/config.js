// Configuration for the frontend application

// API URL - uses the environment variable with a fallback
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// Create standard API request headers
export const getHeaders = () => {
  return {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
};

// API endpoints
export const ENDPOINTS = {
  // User endpoints
  USERS: '/api/users',
  USER_BY_ID: '/api/users/:id',
  USER_LOGIN: '/api/users/login',
  USER_REGISTER: '/api/users/register',
  
  // Representatives endpoints
  REPRESENTATIVES: '/api/representatives',
  REPRESENTATIVE_BY_ID: '/api/representatives/:id',
  HOUSE_REPRESENTATIVES: '/api/representatives/house',
  SENATE_REPRESENTATIVES: '/api/representatives/senate',
  
  // Bills endpoints
  BILLS: '/api/bills',
  BILL_BY_ID: '/api/bills/:id',
  RECENT_BILLS: '/api/bills/recent',
  
  // Votes endpoints
  VOTES: '/api/votes',
  VOTE_BY_ID: '/api/votes/:id',
  RECENT_VOTES: '/api/votes/recent',
  REPRESENTATIVE_VOTES: '/api/representatives/:id/votes',
  
  // Sync endpoints
  SYNC_STATUS: '/api/sync/status',
  SYNC_REPRESENTATIVES: '/api/sync/representatives',
  SYNC_BILLS: '/api/sync/bills',
  SYNC_VOTES: '/api/sync/votes',
  SYNC_ALL: '/api/sync/all',
  
  // Config endpoints
  API_CONFIG: '/api/config/api'
};

// Helper function to build a complete API URL
export const buildApiUrl = (endpoint, params = {}) => {
  const url = new URL(`${API_BASE_URL}${endpoint}`);
  
  // Add query parameters
  Object.keys(params).forEach(key => {
    url.searchParams.append(key, params[key]);
  });
  
  return url.toString();
};

// Function to replace path parameters in endpoints
// Example: replacePathParams('/api/sync/representatives/:repId/votes', { repId: 123 })
// Returns: '/api/sync/representatives/123/votes'
export const replacePathParams = (endpoint, params = {}) => {
  let result = endpoint;
  
  Object.keys(params).forEach(key => {
    result = result.replace(`:${key}`, params[key]);
  });
  
  return result;
}; 