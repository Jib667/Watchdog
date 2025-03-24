import React, { useState, useEffect } from 'react';
import { Card, Button, Tabs, Tab, Spinner, Row, Col } from 'react-bootstrap';
import MemberCard from './MemberCard';
import './SenatorSelector.css';

const SenatorSelector = ({ senators, state, onClose }) => {
  const [selectedSenator, setSelectedSenator] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (senators && senators.length > 0) {
      setSelectedSenator(senators[0]);
    }
  }, [senators]);

  if (!senators || senators.length === 0) {
    return (
      <Card className="senator-selector">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h3>Senators for {state}</h3>
          <Button variant="close" onClick={onClose} />
        </Card.Header>
        <Card.Body className="text-center p-5">
          {loading ? (
            <>
              <Spinner animation="border" variant="primary" />
              <p className="mt-2">Loading senator information...</p>
            </>
          ) : error ? (
            <div className="alert alert-danger">{error}</div>
          ) : (
            <p>No senator information available for {state}.</p>
          )}
        </Card.Body>
      </Card>
    );
  }

  return (
    <div className="senator-container">
      {senators.length > 1 ? (
        <div className="senator-tabs-container">
          <Tabs
            activeKey={selectedSenator?.id || 'none'}
            onSelect={(key) => {
              const senator = senators.find(s => s.id === key);
              if (senator) setSelectedSenator(senator);
            }}
            className="senator-tabs"
          >
            {senators.map(senator => (
              <Tab 
                key={senator.id} 
                eventKey={senator.id} 
                title={
                  <div className="senator-tab-title">
                    <span>{senator.name}</span>
                    <span className="senator-tab-party">({senator.party})</span>
                  </div>
                }
              />
            ))}
          </Tabs>
        </div>
      ) : null}
      
      {selectedSenator && (
        <MemberCard 
          member={selectedSenator} 
          onClose={onClose} 
        />
      )}
    </div>
  );
};

export default SenatorSelector; 