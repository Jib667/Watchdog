import React, { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { useLocation } from 'react-router-dom'; // Import useLocation
import MemberCard from '../components/MemberCard'; // Import the MemberCard component
// Removed import for local data
// import { getSenatorsByState } from '../data/senators';
import 'leaflet/dist/leaflet.css';
import './Senate.css';

const Senate = () => {
  const [selectedState, setSelectedState] = useState(null);
  const [stateData, setStateData] = useState(null); // GeoJSON for states
  const [allSenators, setAllSenators] = useState([]); // Holds fetched data
  // Removed 'members' state
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // State for the modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState(null);

  const location = useLocation(); // Get location object

  // Fetch state GeoJSON data
  useEffect(() => {
    const fetchStateData = async () => {
      try {
        const response = await fetch('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json');
        const data = await response.json();
        setStateData(data);
      } catch (err) {
        console.error('Error fetching state data:', err);
        setError('Failed to load map data. Please try again later.');
      }
    };

    fetchStateData();
  }, []);

  // Fetch senators data from backend API
  useEffect(() => {
    console.log(`Senate useEffect triggered for path: ${location.pathname}`); // Log effect trigger
    
    const fetchSenatorsData = async () => {
      console.log("fetchSenatorsData started..."); // Log function start
      // Reset state on navigation
      setIsLoading(true);
      setError(null);
      setAllSenators([]); 
      setSelectedState(null); 
      
      try {
        const response = await fetch('/api/congress/static/senators');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Fetched senators data count:", data.length); // Log data success
        setAllSenators(data);
      } catch (err) {
        console.error('Error fetching senators data:', err);
        setError('Failed to load senators data. Please try again later.');
        setAllSenators([]);
      } finally {
        console.log("fetchSenatorsData finished, setting isLoading=false"); // Log finish
        setIsLoading(false);
      }
    };

    fetchSenatorsData();
  }, [location]);

  // Function to get senators for a specific state from the fetched data
  const getSenatorsByState = (stateName) => {
    if (!stateName || isLoading || error) return [];
    return allSenators.filter(sen => sen.state.toLowerCase() === stateName.toLowerCase());
  };

  // Function to open the modal with selected member data
  // Modified to accept bioguideId and find the member in the state list
  const handleMemberClick = (bioguideId) => {
    const member = allSenators.find(sen => sen.bioguide_id === bioguideId);
    if (member) {
        console.log('Member data in handleMemberClick:', member);
        setSelectedMember(member);
        setIsModalOpen(true);
    } else {
        console.error(`Senator with BioGuide ID ${bioguideId} not found.`);
        // Optionally show an error to the user
    }
  };

  // Handle state selection
  const handleStateClick = (event) => {
    const feature = event.target.feature; 
    if (!feature || !feature.properties) return;
    // Use the correct property 'name'
    const stateName = feature.properties.name; 
    setSelectedState(stateName);

    // Add console log here to only log the clicked state's properties
    console.log('Clicked State Feature Properties:', feature.properties);
  };

  // Style function for the GeoJSON layer
  const style = (feature) => {
    // Compare selectedState against the 'name' property for consistency
    const isSelected = feature?.properties?.name === selectedState;
    // Use different colors for Senate page
    return {
      fillColor: isSelected ? '#553C9A' : '#805AD5', // Darker purple when selected
      weight: isSelected ? 2 : 1,
      opacity: 1,
      color: isSelected ? '#44337A' : '#6B46C1',
      dashArray: '3',
      fillOpacity: isSelected ? 0.4 : 0.1
    };
  };

  // Create popup content
  const createPopupContent = (stateName) => {
    const stateMembers = getSenatorsByState(stateName);

    if (error) return `Error: ${error}`;
    if (isLoading) return 'Loading senators...';
    if (stateMembers.length === 0) {
      return `<div class="popup-content">No senators found for ${stateName}.</div>`;
    }

    // Assign the modified handleMemberClick to the window object
    window.handleSenClick = handleMemberClick;

    let popupHtml = `<div class="popup-content"><h3 class="popup-state-title">${stateName} Senators</h3>`;
    stateMembers.forEach(sen => {
      const bioguideId = sen.bioguide_id || ''; 
      const partyLower = (sen.party || '').toLowerCase();
      let partyClass = '';
      if (partyLower.includes('democrat')) {
        partyClass = 'party-democrat';
      } else if (partyLower.includes('republican')) {
        partyClass = 'party-republican';
      } else if (partyLower.includes('independent')) {
        partyClass = 'party-independent';
      }

      if (bioguideId) { 
           popupHtml += `
             <div 
                class="popup-member-item"
                onclick='window.handleSenClick("${bioguideId}")'
             >
                <span class="popup-member-name ${partyClass}">${sen.name}</span>
                <span class="popup-member-party">(${sen.party ? sen.party.charAt(0) : 'U'})</span>
             </div>
           `;
       } else {
             console.warn("Senator missing bioguide_id:", sen.name);
       }
    });
    popupHtml += `</div>`;
    return popupHtml;
  };

  return (
    <Container fluid className="px-3">
      <div className="map-container">
        <MapContainer
          center={[39.8283, -98.5795]}
          zoom={4}
          style={{ height: '100%', width: '100%' }}
          zoomAnimation={true}
          zoomAnimationDuration={500}
          markerZoomAnimation={true}
          markerZoomAnimationDuration={500}
          animate={true}
          easeLinearity={0.25}
          maxZoom={18}
          minZoom={3}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            updateWhenIdle={true}
            updateWhenZooming={false}
          />
          {stateData && (
            <GeoJSON
              key={`sen-${allSenators.length}`}
              data={stateData}
              style={style}
              onEachFeature={(feature, layer) => {
                // Use the correct property 'name'
                const stateName = feature.properties.name;
                
                // Bind popup content dynamically
                layer.bindPopup(() => createPopupContent(stateName), {
                    minWidth: 250,
                    maxHeight: 300
                });

                layer.on({
                  click: handleStateClick, // This now logs the properties too
                  mouseover: (e) => {
                    const layer = e.target;
                    // Use the style function to ensure consistency on hover
                     layer.setStyle({
                      fillOpacity: 0.6,
                      weight: 2
                    });
                  },
                  mouseout: (e) => {
                    const layer = e.target;
                    // Re-apply the dynamic style based on selection state
                    layer.setStyle(style(feature)); 
                  }
                });
              }}
            />
          )}
        </MapContainer>
      </div>

      {/* Render the MemberCard modal conditionally */}
      {isModalOpen && selectedMember && (
        <MemberCard 
          member={selectedMember} 
          onClose={() => setIsModalOpen(false)} 
        />
      )}
    </Container>
  );
};

export default Senate; 