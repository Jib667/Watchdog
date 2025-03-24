import React, { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { fetchSenatorsByState } from '../utils/api';
import MemberCard from '../components/MemberCard';
import 'leaflet/dist/leaflet.css';
import './Senate.css';

const Senate = () => {
  const [selectedState, setSelectedState] = useState(null);
  const [senators, setSenators] = useState(null);
  const [selectedSenator, setSelectedSenator] = useState(null);
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

    const state = properties.STATE_ABBR;
    console.log('State clicked:', state);
    setSelectedState(state);
    setSenators(null);
    setSelectedSenator(null);
    setError(null);
    setLoading(true);

    try {
      const senatorData = await fetchSenatorsByState(state);
      console.log('Received senator data:', senatorData);
      setSenators(senatorData);
    } catch (err) {
      console.error('Error fetching senator data:', err);
      setError('Failed to load senator information. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Style function for the GeoJSON layer
  const style = (feature) => {
    const state = feature.properties.postal;
    const isSelected = state === selectedState;
    return {
      fillColor: isSelected ? '#6B46C1' : '#9F7AEA', // Purple colors
      weight: isSelected ? 2 : 1,
      opacity: 1,
      color: isSelected ? '#553C9A' : '#805AD5',
      dashArray: '3',  // Keep dashed effect
      fillOpacity: isSelected ? 0.4 : 0.1
    };
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

      {selectedState && (
        <div className="member-card-container">
          {loading ? (
            <div className="text-center p-4">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="mt-2">Loading senator information...</p>
            </div>
          ) : error ? (
            <div className="alert alert-danger">{error}</div>
          ) : senators ? (
            <div className="senators-list">
              <h3 className="text-center mb-3">Senators from {selectedState}</h3>
              <div className="d-flex justify-content-center gap-3">
                {senators.map((senator) => (
                  <div 
                    key={senator.id} 
                    className={`senator-option ${selectedSenator?.id === senator.id ? 'selected' : ''}`}
                    onClick={() => setSelectedSenator(senator)}
                  >
                    <h4>{senator.name}</h4>
                    <p className="mb-0">{senator.party}</p>
                  </div>
                ))}
              </div>
              {selectedSenator && (
                <div className="mt-4">
                  <MemberCard 
                    member={selectedSenator}
                    onClose={() => setSelectedSenator(null)}
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

export default Senate; 