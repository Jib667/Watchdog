// API utility functions to interact with backend and external APIs

// Fetch data from our backend API
export const fetchFromAPI = async (endpoint, options = {}) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
  const url = `${baseUrl}${endpoint}`;
  
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};

// Fetch representative information by state and district
export const fetchRepresentative = async (state, district) => {
  try {
    console.log('Fetching representative for state:', state, 'district:', district);
    const endpoint = `/api/representatives/member?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`;
    const response = await fetchFromAPI(endpoint);
    console.log('API response:', response);
    return response;
  } catch (error) {
    console.error('Error fetching representative data:', error);
    throw error;
  }
};

// Fetch senators by state
export const fetchSenatorsByState = async (state) => {
  try {
    const endpoint = `/api/representatives/senate`;
    const response = await fetchFromAPI(endpoint);
    return response.representatives.filter(rep => rep.state === state);
  } catch (error) {
    console.error('Error fetching senator data:', error);
    throw error;
  }
};

// Fetch representatives by state
export const fetchRepresentativesByState = async (state) => {
  try {
    const endpoint = `/api/representatives/house`;
    const response = await fetchFromAPI(endpoint);
    return response.representatives.filter(rep => rep.state === state);
  } catch (error) {
    console.error('Error fetching representative data:', error);
    throw error;
  }
};

// Fetch a member's sponsored legislation
export const fetchMemberSponsored = async (memberId) => {
  try {
    const endpoint = `/api/members/${memberId}/sponsored`;
    return await fetchFromAPI(endpoint);
  } catch (error) {
    console.error('Error fetching member sponsored legislation:', error);
    throw error;
  }
};

// Fetch a member's cosponsored legislation
export const fetchMemberCosponsored = async (memberId) => {
  try {
    const endpoint = `/api/members/${memberId}/cosponsored`;
    return await fetchFromAPI(endpoint);
  } catch (error) {
    console.error('Error fetching member cosponsored legislation:', error);
    throw error;
  }
};

export const fetchMembersByState = async (state) => {
  try {
    const response = await fetch(`${API_BASE_URL}/members?state=${state}`);
    if (!response.ok) {
      throw new Error('Failed to fetch members');
    }
    const data = await response.json();
    return data.members;
  } catch (error) {
    console.error('Error fetching members:', error);
    throw error;
  }
};

export const fetchSenators = async (state) => {
  try {
    // Make request to our backend endpoint that will proxy to Congress API
    const endpoint = `/api/representatives/senators?state=${state}`;
    return await fetchFromAPI(endpoint);
  } catch (error) {
    console.error('Error fetching senator data:', error);
    throw error;
  }
}; 