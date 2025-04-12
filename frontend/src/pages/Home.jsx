import './Home.css';
import { useContext, useEffect, useState, useRef } from 'react';
import capitolBackground from '../assets/capitol_background.webp';
import MemberCard from '../components/MemberCard';

const Home = ({ onSignUpClick }) => {
  // Updated rotating words - using 'organize', 'converse', 'advocate', 'assemble'
  const [rotatingWord, setRotatingWord] = useState('organize');
  const [isChanging, setIsChanging] = useState(false);
  // Updated list without 'petition'
  const rotatingWords = ['assemble', 'advocate', 'converse', 'organize'];
  const currentIndex = useRef(0);
  
  useEffect(() => {
    const intervalId = setInterval(() => {
      setIsChanging(true);
      setTimeout(() => {
        currentIndex.current = (currentIndex.current + 1) % rotatingWords.length;
        setRotatingWord(rotatingWords[currentIndex.current]);
        
        // Give the animation time to show the new word
        setTimeout(() => {
          setIsChanging(false);
        }, 100);
      }, 300); // Delay word change to coincide with animation
    }, 3000); // Change word every 3 seconds
    
    return () => clearInterval(intervalId);
  }, []);
  
  // Function to create the hero text with appropriate styling
  const renderHeroText = () => {
    return (
      <h1 className={isChanging ? 'text-changing' : ''}>
        Monitor your <span className="highlight">representatives</span> and{' '}
        <span className="rotating-word">{rotatingWord}</span> with fellow citizens
      </h1>
    );
  };
  
  // Scroll to top of page when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  
  return (
    <div className="home-page">
      <div className="capitol-background-container">
        <img src={capitolBackground} alt="Capitol Building" className="capitol-background" />
      </div>
      
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-text">
            {renderHeroText()}
            <p className="hero-description">
              Free, open-source software providing transparency and accountability in government
            </p>
            <button onClick={onSignUpClick} className="get-started-button">Sign Up</button>
          </div>
        </div>
      </section>

      <section id="features" className="features-section">
        <h2>Citizen Oversight Tools</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>Platform Transparency</h3>
            <p>Easily access and review the platforms of representatives and senators to understand their positions and promises made to constituents.</p>
          </div>
          <div className="feature-card">
            <h3>Voting Records</h3>
            <p>Track how your elected officials vote on important issues that matter to you and your community, with full history and context.</p>
          </div>
          <div className="feature-card">
            <h3>Contradiction Alerts</h3>
            <p>See when officials' actions don't align with their campaign promises or public statements, keeping them accountable to voters.</p>
          </div>
        </div>
      </section>

      <section className="about-section">
        <h2>About Watchdog</h2>
        <p>
          Watchdog is a non-partisan, open-source platform dedicated to increasing transparency in government. 
          As citizens, we deserve easy access to information about our elected officials. 
          Our goal is to provide accurate, up-to-date data about representatives and senators 
          to help voters make informed decisions and hold officials accountable to their constituents. With 
          Watchdog, you can organize with other constituents in your district, petition your representatives 
          to take action, and talk with other citizens about the issues that matter.
        </p>
        <div className="open-source-note">
          <h3>Open Source</h3>
          <p>
            Watchdog is developed and maintained by citizens for citizens. As an open-source project, 
            the code is freely available for anyone to inspect, modify, and improve. We believe in 
            transparency not just in government, but in the tools we use to monitor it.
          </p>
          <div className="contribute-links">
            <a href="https://github.com/Jib667/Watchdog" target="_blank" rel="noopener noreferrer" className="contribute-link">View Source</a>
            <a href="https://github.com/Jib667/Watchdog/issues" target="_blank" rel="noopener noreferrer" className="contribute-link">Contribute</a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home; 