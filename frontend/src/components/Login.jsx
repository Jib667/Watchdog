import React, { useState } from 'react';
import './Login.css';

const Login = ({ onClose }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    rememberMe: false
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loginError, setLoginError] = useState('');

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
    
    // Clear login error when user changes inputs
    if (loginError) {
      setLoginError('');
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formErrors = validateForm();
    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors);
      return;
    }
    
    setIsSubmitting(true);
    console.log('Login attempt with username:', formData.username);
    
    try {
      // Create form data for OAuth2 password flow
      const formBody = new URLSearchParams();
      formBody.append('username', formData.username);
      formBody.append('password', formData.password);
      
      // Make actual API call to backend using the proxy
      const response = await fetch('/api/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formBody,
        credentials: 'include'
      });
      
      console.log('Login response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Login error response:', errorData);
        throw new Error(errorData.detail || 'Login failed');
      }
      
      const data = await response.json();
      console.log('Login successful, received token');
      
      // Store token in localStorage
      localStorage.setItem('accessToken', data.access_token);
      localStorage.setItem('tokenType', data.token_type);
      
      // Close modal on success
      onClose();
    } catch (error) {
      console.error('Login error:', error);
      setLoginError(error.message || 'Invalid username or password. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <div className="login-title">Log In to <span className="orbitron-text">WATCHDOG</span></div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="login-content">
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-header">
              <div className="watchdog-title">
                <h2 className="orbitron-text">WATCHDOG</h2>
              </div>
              <p>Welcome back to the citizen oversight community</p>
            </div>
            
            {loginError && (
              <div className="login-error-message">
                {loginError}
              </div>
            )}
            
            <div className="form-group left-aligned-labels">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className={errors.username ? 'error' : ''}
              />
              {errors.username && <div className="error-message">{errors.username}</div>}
            </div>
            
            <div className="form-group left-aligned-labels">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={errors.password ? 'error' : ''}
              />
              {errors.password && <div className="error-message">{errors.password}</div>}
            </div>
            
            <div className="form-options">
              <div className="form-group checkbox-group">
                <input
                  type="checkbox"
                  id="rememberMe"
                  name="rememberMe"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                />
                <label htmlFor="rememberMe">Remember me</label>
              </div>
              <a href="#forgot-password" className="forgot-password">Forgot password?</a>
            </div>
            
            <div className="form-actions centered">
              <button type="button" className="action-button cancel-button" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="action-button modal-submit-button" disabled={isSubmitting}>
                {isSubmitting ? 'Logging in...' : 'Log In'}
              </button>
            </div>
            
            <div className="form-footer">
              <p className="account-message">
                Don't have an account? <a href="#signup" onClick={(e) => { e.preventDefault(); onClose(); }}>Sign up</a> to join the community.
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login; 