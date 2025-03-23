import { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import './Senate.css';

const Senate = () => {
  const [selectedState, setSelectedState] = useState(null);
  
  // Message received when a state is selected in the iframe
  const handleMessage = (event) => {
    // Check if the message is from GovTrack
    if (event.origin === 'https://www.govtrack.us') {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'stateSelected') {
          setSelectedState(data.state);
          console.log('State selected:', data);
        }
      } catch (e) {
        console.error('Error parsing message from iframe:', e);
      }
    }
  };

  // Add event listener for messages from the iframe
  useEffect(() => {
    window.addEventListener('message', handleMessage);
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, []);

  return (
    <Container fluid className="px-3">
      <div className="map-container map-fullsize">
        <iframe 
          title="Senate Map"
          width="100%" 
          height="100%" 
          frameBorder="0" 
          scrolling="no" 
          marginHeight="0" 
          marginWidth="0"
          src="https://www.govtrack.us/congress/members/embed/mapframe?&bounds=-145.242,44.506,-48.958,18.178&chamber=senate"
        ></iframe>
      </div>
      
      {selectedState && (
        <div className="selected-info">
          Selected: {selectedState}
        </div>
      )}
    </Container>
  );
};

export default Senate; 