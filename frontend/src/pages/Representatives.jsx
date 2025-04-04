import React, { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { useLocation } from 'react-router-dom'; // Import useLocation
import MemberCard from '../components/MemberCard'; // Import the MemberCard component
// Removed import for local data
// import { getRepresentativesByState } from '../data/representatives';
import 'leaflet/dist/leaflet.css';
import './Representatives.css';

const Representatives = () => {
  const [selectedState, setSelectedState] = useState(null);
  const [stateData, setStateData] = useState(null); // GeoJSON for states
  const [allRepresentatives, setAllRepresentatives] = useState([]); // Holds fetched data
  // Removed 'members' state as it's not strictly needed now
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

  // Fetch representatives data from backend API
  useEffect(() => {
    console.log(`Representatives useEffect triggered for path: ${location.pathname}`); // Log effect trigger
    
    const fetchRepsData = async () => {
      console.log("fetchRepsData started..."); // Log function start
      // Reset state on navigation
      setIsLoading(true);
      setError(null);
      setAllRepresentatives([]); 
      setSelectedState(null); 

      try {
        const response = await fetch('/api/congress/static/representatives');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("Fetched representatives data count:", data.length); // Log data success
        setAllRepresentatives(data);
      } catch (err) {
        console.error('Error fetching representatives data:', err);
        setError('Failed to load representatives data. Please try again later.');
        setAllRepresentatives([]);
      } finally {
        console.log("fetchRepsData finished, setting isLoading=false"); // Log finish
        setIsLoading(false);
      }
    };

    fetchRepsData();
  }, [location]);

  // Function to get representatives for a specific state from the fetched data
  const getRepresentativesByState = (stateName) => {
    if (!stateName || isLoading || error) return [];
    return allRepresentatives.filter(rep => rep.state.toLowerCase() === stateName.toLowerCase());
  };

  // Function to open the modal with selected member data
  // Modified to accept bioguideId and find the member in the state list
  const handleMemberClick = (bioguideId) => {
    const member = allRepresentatives.find(rep => rep.bioguide_id === bioguideId);
    if (member) {
      console.log('Member data in handleMemberClick:', member);
      setSelectedMember(member);
      setIsModalOpen(true);
    } else {
        console.error(`Representative with BioGuide ID ${bioguideId} not found.`);
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

    // Move console log here to only log the clicked state's properties
    console.log('Clicked State Feature Properties:', feature.properties);
  };

  // Style function for the GeoJSON layer
  const style = (feature) => {
    // Compare selectedState against the 'name' property for consistency
    const isSelected = feature?.properties?.name === selectedState;
    return {
      fillColor: isSelected ? '#D69E2E' : '#F6AD55', // Darker orange when selected
      weight: isSelected ? 2 : 1,
      opacity: 1,
      color: isSelected ? '#B7791F' : '#DD6B20',
      dashArray: '3',
      fillOpacity: isSelected ? 0.4 : 0.1
    };
  };

  // Create popup content
  const createPopupContent = (stateName) => {
    const stateMembers = getRepresentativesByState(stateName);

    if (error) return `Error: ${error}`;
    if (isLoading) return 'Loading representatives...'; 
    if (stateMembers.length === 0) {
      return `<div class="popup-content">No representatives found for ${stateName}.</div>`;
    }

    const representativesByDistrict = stateMembers.reduce((acc, rep) => {
      const district = rep.district || 'Unknown District';
      if (!acc[district]) {
        acc[district] = [];
      }
      acc[district].push(rep);
      return acc;
    }, {});

    // Assign the modified handleMemberClick to the window object
    window.handleRepClick = handleMemberClick; 

    let popupHtml = `<div class="popup-content"><h3 class="popup-state-title">${stateName} Representatives</h3>`;

    Object.entries(representativesByDistrict).forEach(([district, reps]) => {
      popupHtml += `<div class="popup-district-group"><h4>District ${district}</h4>`;
      reps.forEach(rep => {
        const bioguideId = rep.bioguide_id || ''; 
        const partyLower = (rep.party || '').toLowerCase();
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
                  onclick='window.handleRepClick("${bioguideId}")' 
               >
                  <span class="popup-member-name ${partyClass}">${rep.name}</span>
                  <span class="popup-member-party">(${rep.party ? rep.party.charAt(0) : 'U'})</span>
               </div>
             `;
        } else {
             console.warn("Representative missing bioguide_id:", rep.name);
        }
      });
      popupHtml += `</div>`;
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
              key={`reps-${allRepresentatives.length}`}
              data={stateData}
              style={style}
              onEachFeature={(feature, layer) => {
                // Use the correct property 'name'
                const stateName = feature.properties.name;
                // Remove console log from here
                // console.log('Clicked State Feature Properties:', feature.properties);
                
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

export default Representatives; 