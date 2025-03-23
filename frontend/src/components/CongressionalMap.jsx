import { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './CongressionalMap.css';
import L from 'leaflet';

// Fix for the Leaflet icon issue
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix Leaflet's default icon issue
let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const CongressionalMap = ({ 
  mapType,  // 'house' or 'senate'
  geoData, 
  onSelectRegion, 
  selectedRegion,
  style = {} 
}) => {
  const mapRef = useRef(null);
  
  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.invalidateSize();
    }
  }, [mapRef]);

  const getStyle = (feature) => {
    // Check if this region is selected
    const isSelected = selectedRegion && 
      (mapType === 'house' 
        ? (feature.properties.STATENAME === selectedRegion.state && feature.properties.CD === selectedRegion.district)
        : feature.properties.NAME === selectedRegion);
    
    return {
      fillColor: isSelected ? '#ff6b6b' : '#8884d8',
      weight: isSelected ? 2 : 1,
      opacity: 1,
      color: isSelected ? '#ff0000' : '#213547',
      fillOpacity: isSelected ? 0.7 : 0.4
    };
  };

  const onEachFeature = (feature, layer) => {
    const properties = feature.properties;
    
    // Create tooltip content based on map type
    let tooltipContent;
    if (mapType === 'house') {
      tooltipContent = `${properties.STATENAME} - District ${properties.CD}`;
    } else {
      tooltipContent = `${properties.NAME}`;
    }
    
    layer.bindTooltip(tooltipContent);
    
    // Add click handler
    layer.on({
      click: () => {
        if (mapType === 'house') {
          onSelectRegion({
            state: properties.STATENAME,
            district: properties.CD
          });
        } else {
          onSelectRegion(properties.NAME);
        }
      },
      mouseover: (e) => {
        const layer = e.target;
        layer.setStyle({
          weight: 2,
          fillOpacity: 0.7
        });
      },
      mouseout: (e) => {
        const layer = e.target;
        layer.setStyle(getStyle(feature));
      }
    });
  };

  return (
    <div className="map-container" style={{ ...style }}>
      <MapContainer 
        center={[37.8, -96]} 
        zoom={4} 
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {geoData && (
          <GeoJSON 
            data={geoData}
            style={getStyle}
            onEachFeature={onEachFeature}
          />
        )}
      </MapContainer>
    </div>
  );
};

export default CongressionalMap; 