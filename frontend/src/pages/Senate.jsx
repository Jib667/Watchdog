import React, { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
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
    const fetchSenatorsData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/congress/static/senators');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setAllSenators(data);
      } catch (err) {
        console.error('Error fetching senators data:', err);
        setError('Failed to load senators data. Please try again later.');
        setAllSenators([]); // Ensure it's an array even on error
      } finally {
        setIsLoading(false);
      }
    };

    fetchSenatorsData();
  }, []); // Runs once on component mount

  // Function to get senators for a specific state from the fetched data
  const getSenatorsByState = (stateName) => {
    if (!stateName || isLoading || error) return [];
    return allSenators.filter(sen => sen.state.toLowerCase() === stateName.toLowerCase());
  };

  // Function to open the modal with selected member data
  const handleMemberClick = (memberData) => {
    setSelectedMember(memberData);
    setIsModalOpen(true);
  };

  // Handle state selection (now just updates selected state for styling)
  const handleStateClick = (event) => {
    const feature = event.layer.feature; // Access feature from layer
    if (!feature || !feature.properties) return;
    const stateName = feature.properties.NAME;
    setSelectedState(stateName);
    // No longer need to setMembers here
  };

  // Style function for the GeoJSON layer
  const style = (feature) => {
    const state = feature.properties.postal;
    const isSelected = state === selectedState;
    return {
      fillColor: isSelected ? '#6B46C1' : '#9F7AEA',
      weight: isSelected ? 2 : 1,
      opacity: 1,
      color: isSelected ? '#553C9A' : '#805AD5',
      dashArray: '3',
      fillOpacity: isSelected ? 0.4 : 0.1
    };
  };

  // Create popup content
  const createPopupContent = (stateName) => {
    const stateMembers = getSenatorsByState(stateName);

    // Check for errors first
    if (error) return `Error: ${error}`;
    
    // If still loading, show loading message
    if (isLoading) return 'Loading senators...';
    
    // If loading is done and there are no members, show message
    if (stateMembers.length === 0) {
      return `<div class="popup-content">No senators found for ${stateName}.</div>`;
    }

    // Make handleMemberClick globally accessible (or use event delegation)
    // TEMPORARY HACK: Attach to window. This is not ideal for larger apps.
    window.handleSenClick = handleMemberClick;

    let popupHtml = `<div class="popup-content"><h3>${stateName} Senators</h3>`;
    stateMembers.forEach(sen => {
      const senJsonString = JSON.stringify(sen).replace(/'/g, "\\'").replace(/"/g, '\'');
      popupHtml += `
        <div 
           class="popup-member-item"
           onclick='window.handleSenClick(${senJsonString})'
        >
           <span class="popup-member-name">${sen.name}</span>
           <span class="popup-member-party">(${sen.party ? sen.party.charAt(0) : 'U'})</span>
        </div>
      `;
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
              data={stateData}
              style={style}
              onEachFeature={(feature, layer) => {
                const stateName = feature.properties.NAME;
                // Bind popup content dynamically
                layer.bindPopup(() => createPopupContent(stateName), {
                    minWidth: 250,
                    maxHeight: 300
                });

                layer.on({
                  click: handleStateClick,
                  mouseover: (e) => {
                    const layer = e.target;
                    layer.setStyle({
                      fillOpacity: 0.6,
                      weight: 2
                    });
                  },
                  mouseout: (e) => {
                    const layer = e.target;
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