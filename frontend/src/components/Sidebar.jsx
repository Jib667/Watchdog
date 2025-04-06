import { NavLink, Link } from 'react-router-dom';
import './Sidebar.css';
import { useEffect } from 'react';

const Sidebar = ({ isOpen, onClose, user }) => {
  // Add logging to debug sidebar state
  console.log("Sidebar render - isOpen:", isOpen);

  // Add an effect to handle body scroll when sidebar is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
    
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose}></div>}
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <button className="close-button" onClick={onClose}>×</button>
          <Link to="/" className="sidebar-logo-link" onClick={onClose}>
            <div className="sidebar-logo-text">
              <h2 className="orbitron-text">WATCHDOG</h2>
              <p className="centered-subtext">Congressional Oversight</p>
            </div>
          </Link>
        </div>
        
        {user && (
          <div className="sidebar-user-info">
            <div className="user-avatar">
              {user.username.charAt(0).toUpperCase()}
            </div>
            <div className="user-details">
              <p className="user-name">{user.full_name || user.username}</p>
              <p className="user-location">
                {user.state && user.district 
                  ? `${user.state}-${user.district}`
                  : user.state 
                    ? user.state 
                    : 'No location set'}
              </p>
            </div>
          </div>
        )}
        
        <nav className="sidebar-nav">
          <ul>
            <li>
              <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''} onClick={onClose}>
                Home
              </NavLink>
            </li>
            <li>
              <NavLink to="/representatives" className={({ isActive }) => isActive ? 'active' : ''} onClick={onClose}>
                House
              </NavLink>
            </li>
            <li>
              <NavLink to="/senate" className={({ isActive }) => `sidebar-link ${isActive ? "active-link" : ""}`} onClick={onClose}>
                Senate
              </NavLink>
            </li>
            <li>
              <NavLink to="/advanced-profile" className={({ isActive }) => `sidebar-link ${isActive ? "active-link" : ""}`} onClick={onClose}>
                Advanced Profile
              </NavLink>
            </li>
            <li>
              <NavLink to="/contact" className={({ isActive }) => `sidebar-link ${isActive ? "active-link" : ""}`} onClick={onClose}>
                Contact
              </NavLink>
            </li>
            <li>
              <NavLink to="/admin" className={({ isActive }) => isActive ? 'active' : ''} onClick={onClose}>
                Admin
              </NavLink>
            </li>
          </ul>
        </nav>
        <div className="sidebar-footer">
          <p>&copy; 2025 <a href="https://github.com/Jib667/Watchdog" target="_blank" rel="noopener noreferrer" style={{color: 'inherit', textDecoration: 'underline'}}>Watchdog</a></p>
        </div>
      </div>
    </>
  );
};

export default Sidebar; 