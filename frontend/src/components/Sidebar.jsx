import { NavLink, Link } from 'react-router-dom';
import './Sidebar.css';
import { useEffect } from 'react';

const Sidebar = ({ isOpen, onClose }) => {
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
              <h2>Watchdog</h2>
              <p>Congressional Monitoring</p>
            </div>
          </Link>
        </div>
        <nav className="sidebar-nav">
          <ul>
            <li>
              <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''} onClick={onClose}>
                Home
              </NavLink>
            </li>
            <li>
              <NavLink to="/representatives" className={({ isActive }) => isActive ? 'active' : ''} onClick={onClose}>
                House of Representatives
              </NavLink>
            </li>
            <li>
              <NavLink to="/senate" className={({ isActive }) => isActive ? 'active' : ''} onClick={onClose}>
                Senate
              </NavLink>
            </li>
            <li>
              <NavLink to="/contact" className={({ isActive }) => isActive ? 'active' : ''} onClick={onClose}>
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
          <p>© 2023 Watchdog</p>
        </div>
      </div>
    </>
  );
};

export default Sidebar; 