import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL, ENDPOINTS, buildApiUrl } from '../config';

import './AdminPage.css';

const AdminPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [syncStatus, setSyncStatus] = useState(null);
  const [syncResults, setSyncResults] = useState({});
  const [apiConfig, setApiConfig] = useState({
    api_key: '',
    base_url: 'https://api.congress.gov/v3',
    is_active: true
  });
  const [isAdmin, setIsAdmin] = useState(false);
  
  // Check if user is admin
  useEffect(() => {
    // This would normally check auth status
    // For now, we're just allowing access
    setIsAdmin(true);
  }, []);
  
  // Fetch initial status
  useEffect(() => {
    if (isAdmin) {
      fetchSyncStatus();
      fetchApiConfig();
    }
  }, [isAdmin]);
  
  const fetchSyncStatus = async () => {
    try {
      setLoading(true);
      const response = await axios.get(buildApiUrl(ENDPOINTS.SYNC_STATUS));
      setSyncStatus(response.data);
    } catch (error) {
      console.error('Error fetching sync status:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchApiConfig = async () => {
    try {
      const response = await axios.get(buildApiUrl(ENDPOINTS.API_CONFIG));
      // We don't actually get the API key back for security reasons
      // but we get information about whether it's configured
      if (response.data.api_configs && response.data.api_configs.length > 0) {
        const config = response.data.api_configs[0];
        setApiConfig(prev => ({
          ...prev,
          is_active: config.is_active
        }));
      }
    } catch (error) {
      console.error('Error fetching API config:', error);
    }
  };
  
  const handleApiConfigChange = (e) => {
    const { name, value, type, checked } = e.target;
    setApiConfig(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const saveApiConfig = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await axios.post(
        buildApiUrl(ENDPOINTS.API_CONFIG),
        apiConfig
      );
      alert('API configuration saved successfully');
      fetchApiConfig();
      fetchSyncStatus();
    } catch (error) {
      console.error('Error saving API config:', error);
      alert('Error saving API configuration');
    } finally {
      setLoading(false);
    }
  };
  
  const runSync = async (endpoint, params = {}) => {
    try {
      setLoading(true);
      const response = await axios.post(buildApiUrl(endpoint), params);
      setSyncResults(prev => ({
        ...prev,
        [endpoint]: response.data
      }));
      // Refresh status after sync
      await fetchSyncStatus();
      alert('Synchronization completed');
    } catch (error) {
      console.error('Error running sync:', error);
      alert('Error running synchronization');
    } finally {
      setLoading(false);
    }
  };
  
  if (!isAdmin) {
    return (
      <div className="admin-page">
        <h1>Admin Access Required</h1>
        <p>You do not have permission to access this page.</p>
        <button onClick={() => navigate('/')}>Return to Home</button>
      </div>
    );
  }
  
  return (
    <div className="admin-page">
      <h1>Admin Dashboard</h1>
      
      <section className="admin-section">
        <h2>Congress API Configuration</h2>
        <form onSubmit={saveApiConfig} className="api-config-form">
          <div className="form-group">
            <label htmlFor="api_key">API Key:</label>
            <input
              type="password"
              id="api_key"
              name="api_key"
              value={apiConfig.api_key}
              onChange={handleApiConfigChange}
              required
              placeholder="Enter Congress API key"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="base_url">Base URL:</label>
            <input
              type="text"
              id="base_url"
              name="base_url"
              value={apiConfig.base_url}
              onChange={handleApiConfigChange}
              placeholder="https://api.congress.gov/v3"
            />
          </div>
          
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                name="is_active"
                checked={apiConfig.is_active}
                onChange={handleApiConfigChange}
              />
              Active
            </label>
          </div>
          
          <button type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Save Configuration'}
          </button>
        </form>
      </section>
      
      <section className="admin-section">
        <h2>Data Synchronization</h2>
        
        {syncStatus && (
          <div className="sync-status">
            <h3>Current Status</h3>
            <table>
              <thead>
                <tr>
                  <th>Dataset</th>
                  <th>Count</th>
                  <th>Last Updated</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Representatives</td>
                  <td>{syncStatus.record_counts.representatives}</td>
                  <td>{syncStatus.latest_updates.representatives || 'Never'}</td>
                </tr>
                <tr>
                  <td>Bills</td>
                  <td>{syncStatus.record_counts.bills}</td>
                  <td>{syncStatus.latest_updates.bills || 'Never'}</td>
                </tr>
                <tr>
                  <td>Votes</td>
                  <td>{syncStatus.record_counts.votes}</td>
                  <td>{syncStatus.latest_updates.votes || 'Never'}</td>
                </tr>
              </tbody>
            </table>
            
            <div className="api-status">
              API Status: 
              <span className={syncStatus.api_configured ? 'status-good' : 'status-bad'}>
                {syncStatus.api_configured ? 'Configured' : 'Not Configured'}
              </span>
            </div>
          </div>
        )}
        
        <div className="sync-actions">
          <h3>Synchronize Data</h3>
          <div className="button-group">
            <button 
              onClick={() => runSync(ENDPOINTS.SYNC_REPRESENTATIVES)}
              disabled={loading || !syncStatus?.api_configured}
            >
              Sync Representatives
            </button>
            
            <button 
              onClick={() => runSync(ENDPOINTS.SYNC_BILLS)}
              disabled={loading || !syncStatus?.api_configured}
            >
              Sync Bills
            </button>
            
            <button 
              onClick={() => runSync(ENDPOINTS.SYNC_VOTES)}
              disabled={loading || !syncStatus?.api_configured}
            >
              Sync Votes
            </button>
            
            <button 
              onClick={() => runSync(ENDPOINTS.SYNC_ALL)}
              disabled={loading || !syncStatus?.api_configured}
              className="primary-button"
            >
              Sync All Data
            </button>
          </div>
          
          <div className="force-sync">
            <button 
              onClick={() => runSync(ENDPOINTS.SYNC_ALL, { force: true })}
              disabled={loading || !syncStatus?.api_configured}
              className="warning-button"
            >
              Force Full Sync
            </button>
            <span className="helper-text">
              This will force synchronization regardless of last update time
            </span>
          </div>
        </div>
      </section>
      
      {Object.keys(syncResults).length > 0 && (
        <section className="admin-section">
          <h2>Sync Results</h2>
          <pre className="sync-results">
            {JSON.stringify(syncResults, null, 2)}
          </pre>
        </section>
      )}
    </div>
  );
};

export default AdminPage; 