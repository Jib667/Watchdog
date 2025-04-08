import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import './App.css'
import capitolImage from './assets/capitol.png' 
import donkeyGif from './assets/donkey.gif' 
import elephantGif from './assets/elephant.gif' 

import Sidebar from './components/Sidebar'
import SignUp from './components/SignUp'
import Login from './components/Login'

import Home from './pages/Home'
import Representatives from './pages/Representatives'
import Senate from './pages/Senate'
import Contact from './pages/Contact'
import AdminPage from './pages/AdminPage'
import AdvancedProfile from './pages/AdvancedProfile'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showSignUp, setShowSignUp] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const location = useLocation();
  
 
  useEffect(() => {
    console.log("Sidebar state changed:", sidebarOpen);
  }, [sidebarOpen]);
  
  useEffect(() => {
    const checkUserAuth = async () => {
      setIsLoading(true);
      const token = localStorage.getItem('accessToken');
      
      if (token) {
        try {
          const response = await fetch('/api/users/me', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (response.ok) {
            const userData = await response.json();
            console.log('User data fetched:', userData);
            setUser(userData);
          } else {
          
            console.log('Invalid token, clearing authentication');
            localStorage.removeItem('accessToken');
            localStorage.removeItem('tokenType');
            setUser(null);
          }
        } catch (error) {
          console.error('Error fetching user data:', error);
          setUser(null);
        }
      }
      
      setIsLoading(false);
    };
    
    checkUserAuth();
  }, []);
  
  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('tokenType');
    setUser(null);
  };
  
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    
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
    const token = localStorage.getItem('accessToken');
    if (token) {
      fetch('/api/users/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(response => {
        if (response.ok) return response.json();
        throw new Error('Failed to fetch user data');
      })
      .then(userData => {
        setUser(userData);
      })
      .catch(error => {
        console.error('Error fetching user data after login:', error);
      });
    }
  };
  
  const closeSignUp = () => {
    setShowSignUp(false);
  };

  const toggleSidebar = () => {
    console.log("Toggling sidebar");
    setSidebarOpen(prevState => !prevState);
  };

  // Determine if we should show the mascots based on current location
  const showMascots = location.pathname === '/' || location.pathname === '/home';
  
  // Determine the title to show in the center based on current location
  let centerTitle = '';
  if (location.pathname === '/representatives') {
    centerTitle = 'The House';
  } else if (location.pathname === '/senate') {
    centerTitle = 'The Senate';
  }

  return (
    <div className="app">
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)} 
        user={user}
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
        
        <div className="header-center">
          {showMascots ? (
            <div className="mascot-container">
              <img src={donkeyGif} alt="Democratic mascot" className="mascot donkey" />
              <img src={elephantGif} alt="Republican mascot" className="mascot elephant" />
            </div>
          ) : centerTitle ? (
            <h2 className="page-title">{centerTitle}</h2>
          ) : null}
        </div>
        
        <div className="nav-buttons">
          {isLoading ? (
            <div className="loading-auth">Loading...</div>
          ) : user ? (
            <div className="user-auth">
              <span className="user-welcome">Welcome, {user.username}</span>
              <button className="logout-button" onClick={handleLogout}>Logout</button>
            </div>
          ) : (
            <>
              <button className="login-button" onClick={handleLoginClick}>Login</button>
              <button className="signup-button" onClick={handleSignUpClick}>Sign Up</button>
            </>
          )}
        </div>
      </header>
      
      <main className="main-content">
        <Routes>
          {/* Remove keys - they didn't solve the loading issue */}
          <Route path="/" element={<Home onSignUpClick={handleSignUpClick} />} />
          <Route path="/home" element={<Home onSignUpClick={handleSignUpClick} />} />
          <Route path="/representatives" element={<Representatives />} />
          <Route path="/senate" element={<Senate />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/advanced-profile" element={<AdvancedProfile />} />
          <Route path="/advanced-profile/:memberId" element={<AdvancedProfile />} />
        </Routes>
      </main>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <div className="logo-container">
              <Link to="/" className="logo-link">
                <span className="logo-text orbitron-text" style={{textAlign: 'left', display: 'block'}}>WATCHDOG</span>
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
              <a href="https://github.com/Jib667/Watchdog" target="_blank" rel="noopener noreferrer" className="social-link">GitHub</a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-link">Twitter</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 Watchdog. All rights reserved. <a href="https://github.com/Jib667/Watchdog" target="_blank" rel="noopener noreferrer" style={{color: 'inherit', textDecoration: 'underline'}}>Open source software</a> for citizen oversight.</p>
        </div>
      </footer>
      
      {showLogin && <Login onClose={closeLogin} />}
      {showSignUp && <SignUp onClose={closeSignUp} />}
    </div>
  )
}

export default App