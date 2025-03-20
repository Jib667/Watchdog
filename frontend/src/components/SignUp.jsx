import React, { useState } from 'react';
import './SignUp.css';

const SignUp = ({ onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    state: '',
    district: '',
    subscribeToCivicUpdates: true
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  
  const states = [
    { code: 'AL', name: 'Alabama' },
    { code: 'AK', name: 'Alaska' },
    { code: 'AZ', name: 'Arizona' },
    { code: 'AR', name: 'Arkansas' },
    { code: 'CA', name: 'California' },
    { code: 'CO', name: 'Colorado' },
    { code: 'CT', name: 'Connecticut' },
    { code: 'DE', name: 'Delaware' },
    { code: 'FL', name: 'Florida' },
    { code: 'GA', name: 'Georgia' },
    { code: 'HI', name: 'Hawaii' },
    { code: 'ID', name: 'Idaho' },
    { code: 'IL', name: 'Illinois' },
    { code: 'IN', name: 'Indiana' },
    { code: 'IA', name: 'Iowa' },
    { code: 'KS', name: 'Kansas' },
    { code: 'KY', name: 'Kentucky' },
    { code: 'LA', name: 'Louisiana' },
    { code: 'ME', name: 'Maine' },
    { code: 'MD', name: 'Maryland' },
    { code: 'MA', name: 'Massachusetts' },
    { code: 'MI', name: 'Michigan' },
    { code: 'MN', name: 'Minnesota' },
    { code: 'MS', name: 'Mississippi' },
    { code: 'MO', name: 'Missouri' },
    { code: 'MT', name: 'Montana' },
    { code: 'NE', name: 'Nebraska' },
    { code: 'NV', name: 'Nevada' },
    { code: 'NH', name: 'New Hampshire' },
    { code: 'NJ', name: 'New Jersey' },
    { code: 'NM', name: 'New Mexico' },
    { code: 'NY', name: 'New York' },
    { code: 'NC', name: 'North Carolina' },
    { code: 'ND', name: 'North Dakota' },
    { code: 'OH', name: 'Ohio' },
    { code: 'OK', name: 'Oklahoma' },
    { code: 'OR', name: 'Oregon' },
    { code: 'PA', name: 'Pennsylvania' },
    { code: 'RI', name: 'Rhode Island' },
    { code: 'SC', name: 'South Carolina' },
    { code: 'SD', name: 'South Dakota' },
    { code: 'TN', name: 'Tennessee' },
    { code: 'TX', name: 'Texas' },
    { code: 'UT', name: 'Utah' },
    { code: 'VT', name: 'Vermont' },
    { code: 'VA', name: 'Virginia' },
    { code: 'WA', name: 'Washington' },
    { code: 'WV', name: 'West Virginia' },
    { code: 'WI', name: 'Wisconsin' },
    { code: 'WY', name: 'Wyoming' }
  ];

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
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    if (!formData.state) {
      newErrors.state = 'Please select your state';
    }
    
    if (formData.state && !formData.district) {
      newErrors.district = 'Please enter your district';
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
    
    // Prepare data for API request
    const userData = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
      full_name: formData.name,
      state: formData.state,
      district: formData.district
    };
    
    console.log('Submitting user data:', userData);
    
    try {
      // Make actual API call to backend
      // Ensure we're using the relative URL to use the proxy
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
        // Include credentials if using cookies for authentication
        credentials: 'include'
      });
      
      console.log('Response status:', response.status);
      const responseData = await response.json();
      console.log('Response data:', responseData);
      
      if (!response.ok) {
        throw new Error(responseData.detail || 'Registration failed');
      }
      
      // Show success message on successful registration
      setSubmitSuccess(true);
      console.log('Registration successful!');
      
      // Close modal after showing success message
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({
        submit: error.message || 'Registration failed. Please try again.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <div className="login-title">Join <span className="orbitron-text">WATCHDOG</span></div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        {submitSuccess ? (
          <div className="success-message">
            <div className="success-icon">✓</div>
            <h3>Account Created!</h3>
            <p>Welcome to the citizen oversight community.</p>
          </div>
        ) : (
          <div className="signup-content">
            <form onSubmit={handleSubmit} className="signup-form">
              <div className="form-header">
                <div className="watchdog-title">
                  <h2 className="orbitron-text">WATCHDOG</h2>
                </div>
                <p>Join our community of citizens working to bring transparency to government.</p>
              </div>
              
              {errors.submit && (
                <div className="login-error-message">
                  <strong>Registration Error:</strong> {errors.submit}
                </div>
              )}
              
              <div className="form-group left-aligned-labels">
                <label htmlFor="name">Full Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={errors.name ? 'error' : ''}
                />
                {errors.name && <div className="error-message">{errors.name}</div>}
              </div>
              
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
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={errors.email ? 'error' : ''}
                />
                {errors.email && <div className="error-message">{errors.email}</div>}
              </div>
              
              <div className="form-row">
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
                
                <div className="form-group left-aligned-labels">
                  <label htmlFor="confirmPassword">Confirm Password</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className={errors.confirmPassword ? 'error' : ''}
                  />
                  {errors.confirmPassword && <div className="error-message">{errors.confirmPassword}</div>}
                </div>
              </div>
              
              <div className="form-group left-aligned-labels">
                <label htmlFor="state">State</label>
                <select
                  id="state"
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  className={errors.state ? 'error' : ''}
                >
                  <option value="">Select your state</option>
                  {states.map(state => (
                    <option key={state.code} value={state.code}>{state.name}</option>
                  ))}
                </select>
                {errors.state && <div className="error-message">{errors.state}</div>}
              </div>
              
              <div className="form-group left-aligned-labels">
                <label htmlFor="district">Congressional District</label>
                <input
                  type="text"
                  id="district"
                  name="district"
                  placeholder="e.g. 1 or At-Large"
                  value={formData.district}
                  onChange={handleChange}
                  className={errors.district ? 'error' : ''}
                />
                {errors.district && <div className="error-message">{errors.district}</div>}
                <div className="input-help-text">
                  Enter your district number (e.g. 1, 2, 3) or "At-Large" if your state has only one representative. 
                  <a href="https://www.house.gov/representatives/find-your-representative" target="_blank" rel="noopener noreferrer">
                    Find your district
                  </a>
                </div>
              </div>
              
              <div className="form-group checkbox-group">
                <input
                  type="checkbox"
                  id="subscribeToCivicUpdates"
                  name="subscribeToCivicUpdates"
                  checked={formData.subscribeToCivicUpdates}
                  onChange={handleChange}
                />
                <label htmlFor="subscribeToCivicUpdates">
                  Keep me updated on important civic oversight issues and platform updates
                </label>
              </div>
              
              <div className="form-actions centered">
                <button type="button" className="action-button cancel-button" onClick={onClose}>
                  Cancel
                </button>
                <button type="submit" className="action-button modal-submit-button" disabled={isSubmitting}>
                  {isSubmitting ? 'Creating Account...' : 'Create Account'}
                </button>
              </div>
              
              <div className="form-footer">
                <p>By signing up, you agree to our <a href="#terms">Terms of Service</a> and <a href="#privacy">Privacy Policy</a>.</p>
                <p className="account-message">Already have an account? <a href="#login" onClick={(e) => { e.preventDefault(); onClose(); }}>Log in</a></p>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default SignUp; 