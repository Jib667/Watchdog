import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Form, Button, Alert } from 'react-bootstrap';
import './Contact.css';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    state: '',
    message: '',
    representative: '',
    subscribe: false
  });

  const [submitStatus, setSubmitStatus] = useState(null);

  // Scroll to top of page when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // This would make an API call to the backend in a real implementation
    console.log('Form submitted:', formData);
    
    // Simulate API call with timeout
    setSubmitStatus('submitting');
    setTimeout(() => {
      setSubmitStatus('success');
      // Reset form after successful submission
      setFormData({
        name: '',
        email: '',
        state: '',
        message: '',
        representative: '',
        subscribe: false
      });
    }, 1500);
  };

  // This would be fetched from the API in a real implementation
  const states = [
    { code: 'AL', name: 'Alabama' },
    { code: 'AK', name: 'Alaska' },
    { code: 'AZ', name: 'Arizona' },
    // ... other states would be included
    { code: 'WY', name: 'Wyoming' },
  ];

  return (
    <div className="contact-page">
      <header className="page-header">
        <h1>Contact Your <span className="highlight">Representatives</span></h1>
        <p>Use this form to reach out to your elected officials</p>
      </header>

      {submitStatus === 'success' && (
        <div className="success-message">
          <h3>Message Sent!</h3>
          <p>Thank you for reaching out. Your message has been submitted successfully.</p>
        </div>
      )}

      {submitStatus !== 'success' && (
        <form className="contact-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Your Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="state">Your State</label>
            <select
              id="state"
              name="state"
              value={formData.state}
              onChange={handleChange}
              required
            >
              <option value="">Select Your State</option>
              {states.map((state) => (
                <option key={state.code} value={state.code}>
                  {state.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="representative">Select Representative or Senator</label>
            <select
              id="representative"
              name="representative"
              value={formData.representative}
              onChange={handleChange}
              required
              disabled={!formData.state}
            >
              <option value="">Select a Representative</option>
              {/* This would be populated based on the selected state */}
              <option value="rep1">Representative 1</option>
              <option value="rep2">Representative 2</option>
              <option value="sen1">Senator 1</option>
              <option value="sen2">Senator 2</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="message">Your Message</label>
            <textarea
              id="message"
              name="message"
              value={formData.message}
              onChange={handleChange}
              rows="6"
              required
            ></textarea>
          </div>

          <div className="form-group checkbox-group">
            <input
              type="checkbox"
              id="subscribe"
              name="subscribe"
              checked={formData.subscribe}
              onChange={handleChange}
            />
            <label htmlFor="subscribe">
              Sign up to receive updates about your representatives
            </label>
          </div>

          <button 
            type="submit" 
            className="submit-button" 
            disabled={submitStatus === 'submitting'}
          >
            {submitStatus === 'submitting' ? 'Sending...' : 'Send Message'}
          </button>
        </form>
      )}

      <section className="contact-info">
        <h2>Other Ways to Contact</h2>
        <p>
          In addition to this form, you can contact your representatives through:
        </p>
        <ul>
          <li>Phone: Call the U.S. Capitol Switchboard at (202) 224-3121</li>
          <li>Mail: Write a letter to their office</li>
          <li>Social Media: Many representatives maintain active profiles</li>
          <li>Local Offices: Visit their local district or state offices</li>
        </ul>
      </section>
    </div>
  );
};

export default Contact; 