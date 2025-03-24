import React, { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { fetchRepresentativesByState } from '../utils/api';
import MemberCard from '../components/MemberCard';
import 'leaflet/dist/leaflet.css';
import './Representatives.css';

const Representatives = () => {
  const [selectedState, setSelectedState] = useState(null);
  const [representatives, setRepresentatives] = useState(null);
  const [selectedMember, setSelectedMember] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stateData, setStateData] = useState(null);

  // Fetch state data
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

  // Handle state selection
  const handleStateClick = async (event) => {
    const { properties } = event.layer;
    if (!properties) return;

    const state = properties.postal;
    console.log('State clicked:', state);
    setSelectedState(state);
    setSelectedMember(null);
    setError(null);
    setLoading(true);

    try {
      const repsData = await fetchRepresentativesByState(state);
      console.log('Received representatives data:', repsData);
      setRepresentatives(repsData);
    } catch (err) {
      console.error('Error fetching member data:', err);
      setError('Failed to load member information. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Style function for the GeoJSON layer
  const style = (feature) => {
    const state = feature.properties.postal;
    const isSelected = state === selectedState;
    return {
      fillColor: isSelected ? '#D69E2E' : '#F6AD55', // Yellow/brown colors
      weight: isSelected ? 2 : 1,
      opacity: 1,
      color: isSelected ? '#B7791F' : '#DD6B20',
      dashArray: '3',
      fillOpacity: isSelected ? 0.4 : 0.1
    };
  };

  const onEachFeature = (feature, layer) => {
    layer.on({
      mouseover: (e) => {
        const layer = e.target;
        layer.setStyle({
          fillOpacity: 0.3,
          weight: 3
        });
      },
      mouseout: (e) => {
        const layer = e.target;
        layer.setStyle(style(feature));
      },
      click: handleStateClick
    });

    // Add state abbreviation label
    const state = feature.properties.postal;
    
    // Create a div element for the label
    const label = document.createElement('div');
    label.className = 'state-label';
    label.textContent = state;
    
    // Add the label to the map
    layer.bindTooltip(label, {
      permanent: true,
      direction: 'center',
      className: 'state-label-tooltip',
      offset: [0, 0]
    });
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
              onEachFeature={onEachFeature}
            />
          )}
        </MapContainer>
      </div>

      {selectedState && (
        <div className="member-card-container">
          {loading ? (
            <div className="text-center p-4">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="mt-2">Loading member information...</p>
            </div>
          ) : error ? (
            <div className="alert alert-danger">{error}</div>
          ) : representatives ? (
            <div className="representatives-list">
              <h3 className="text-center mb-3">Representatives from {selectedState}</h3>
              <div className="d-flex flex-wrap justify-content-center gap-3">
                {representatives.map((rep) => (
                  <div 
                    key={rep.id} 
                    className={`representative-option ${selectedMember?.id === rep.id ? 'selected' : ''}`}
                    onClick={() => setSelectedMember(rep)}
                  >
                    <h4>District {rep.district}</h4>
                    <h5>{rep.name}</h5>
                    <p className="mb-0">{rep.party}</p>
                  </div>
                ))}
              </div>
              {selectedMember && (
                <div className="mt-4">
                  <MemberCard 
                    member={selectedMember}
                    onClose={() => setSelectedMember(null)}
                  />
                </div>
              )}
            </div>
          ) : null}
        </div>
      )}
    </Container>
  );
};

export default Representatives; 