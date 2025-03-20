import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import capitolImage from './assets/capitol.png' // Import the capitol image

// Components
import Sidebar from './components/Sidebar'
import SignUp from './components/SignUp'
import Login from './components/Login'

// Pages
import Home from './pages/Home'
import Representatives from './pages/Representatives'
import Senate from './pages/Senate'
import Contact from './pages/Contact'
import HomePage from './pages/HomePage'
import RepresentativesPage from './pages/RepresentativesPage'
import SenatePage from './pages/SenatePage'
import ContactPage from './pages/ContactPage'
import AdminPage from './pages/AdminPage'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showSignUp, setShowSignUp] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  
  // Add debugging for sidebar state
  useEffect(() => {
    console.log("Sidebar state changed:", sidebarOpen);
  }, [sidebarOpen]);
  
  // Handle scroll events to update header appearance
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    
    // Clean up the event listener on component unmount
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);
  
  const handleLoginClick = () => {
    setShowLogin(true);
  };
  
  const handleSignUpClick = () => {
    setShowSignUp(true);
  };
  
  const closeLogin = () => {
    setShowLogin(false);
  };
  
  const closeSignUp = () => {
    setShowSignUp(false);
  };

  const toggleSidebar = () => {
    console.log("Toggle sidebar clicked. Current state:", sidebarOpen);
    setSidebarOpen(prevState => !prevState);
  };

  return (
    <Router>
      <div className="app">
        <Sidebar 
          isOpen={sidebarOpen} 
          onClose={() => setSidebarOpen(false)} 
        />
        <div className="sparkle"></div>
        <div className="sparkle"></div>
        <div className="sparkle"></div>
        <div className="sparkle"></div>
        <div className="sparkle"></div>
        <div className="sparkle"></div>
        <div className="sparkle"></div>
        <div className="sparkle"></div>
        <div className="decorative-circle decorative-circle-1"></div>
        <div className="decorative-circle decorative-circle-2"></div>
        <div className="decorative-circle decorative-circle-3"></div>
        <div className="decorative-circle decorative-circle-4"></div>
        <header className={`app-header ${isScrolled ? 'scrolled' : ''}`}>
          <div className="header-left">
            <button 
              className="menu-button" 
              onClick={toggleSidebar}
              aria-label="Toggle sidebar menu"
            >
              <span className="menu-icon"></span>
            </button>
            <Link to="/" className="logo-link">
              <img src={capitolImage} alt="Capitol" className="capitol-logo" />
              <div className="logo-text">
                <h1 className="app-title">Watchdog</h1>
                <p className="app-subtitle">Congressional Oversight</p>
              </div>
            </Link>
          </div>
          <div className="nav-buttons">
            <button className="login-button" onClick={handleLoginClick}>Login</button>
            <button className="signup-button" onClick={handleSignUpClick}>Sign Up</button>
          </div>
        </header>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/home" element={<Home />} />
            <Route path="/representatives" element={<RepresentativesPage />} />
            <Route path="/senate" element={<SenatePage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </main>

        <footer className="footer">
          <div className="footer-content">
            <div className="footer-section">
              <div className="logo-container">
                <Link to="/" className="logo-link">
                  <span className="logo-text">Watchdog</span>
                </Link>
              </div>
              <p className="footer-description">Making congressional monitoring accessible and transparent for all citizens.</p>
            </div>
            <div className="footer-section">
              <h4>Pages</h4>
              <ul>
                <li><Link to="/" className="footer-text">Home</Link></li>
                <li><Link to="/representatives" className="footer-text">Representatives</Link></li>
                <li><Link to="/senate" className="footer-text">Senate</Link></li>
                <li><Link to="/contact" className="footer-text">Contact</Link></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Features</h4>
              <ul>
                <li><span className="footer-text">Voting Records</span></li>
                <li><span className="footer-text">Platforms</span></li>
                <li><span className="footer-text">Contradiction Tracking</span></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Connect</h4>
              <div className="social-links">
                <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="social-link">GitHub</a>
                <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-link">Twitter</a>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2023 Watchdog. All rights reserved. Open source software for citizen oversight.</p>
          </div>
        </footer>
        
        {showLogin && <Login onClose={closeLogin} />}
        {showSignUp && <SignUp onClose={closeSignUp} />}
      </div>
    </Router>
  )
}

export default App
