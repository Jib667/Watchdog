import { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import './Representatives.css';

const Representatives = () => {
  const [selectedDistrict, setSelectedDistrict] = useState(null);
  
  // Message received when a district is selected in the iframe
  const handleMessage = (event) => {
    // Check if the message is from GovTrack
    if (event.origin === 'https://www.govtrack.us') {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'districtSelected') {
          setSelectedDistrict({
            state: data.state,
            district: data.district
          });
          console.log('District selected:', data);
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
          title="Congressional Districts Map"
          width="100%" 
          height="100%" 
          frameBorder="0" 
          scrolling="no" 
          marginHeight="0" 
          marginWidth="0"
          src="https://www.govtrack.us/congress/members/embed/mapframe?&bounds=-145.242,44.506,-48.958,18.178"
        ></iframe>
      </div>
      
      {selectedDistrict && (
        <div className="selected-info">
          Selected: {selectedDistrict.state} - District {selectedDistrict.district}
        </div>
      )}
    </Container>
  );
};

export default Representatives; 