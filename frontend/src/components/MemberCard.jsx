import React, { useState, useEffect } from 'react';
import { Card, Button, Tabs, Tab, Spinner, Badge, Row, Col, ListGroup } from 'react-bootstrap';
import { fetchMemberSponsored, fetchMemberCosponsored } from '../utils/api';
import './MemberCard.css';

// Fallback image paths for when member photos aren't available
const FALLBACK_IMAGES = {
  house: '/images/default_house.jpg',
  senate: '/images/default_senate.jpg'
};

const MemberCard = ({ member, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [sponsoredBills, setSponsoredBills] = useState([]);
  const [cosponsoredBills, setCosponsoredBills] = useState([]);
  const [activeTab, setActiveTab] = useState('bio');
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadMemberData = async () => {
      if (!member || !member.id) {
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      
      try {
        // Load sponsored and cosponsored legislation in parallel
        const [sponsoredData, cosponsoredData] = await Promise.all([
          fetchMemberSponsored(member.id),
          fetchMemberCosponsored(member.id)
        ]);
        
        setSponsoredBills(sponsoredData.bills || []);
        setCosponsoredBills(cosponsoredData.bills || []);
      } catch (err) {
        console.error('Error loading member data:', err);
        setError('Failed to load some member information. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadMemberData();
  }, [member]);

  if (!member) return null;

  // Handle potentially missing data
  const memberName = member.name || 'Unknown';
  const chamber = member.chamber?.toLowerCase() || 'house';
  const party = member.party || 'Unknown';
  const state = member.state || 'Unknown';
  const district = member.district || '';
  const imageUrl = member.imageUrl || FALLBACK_IMAGES[chamber];
  const url = member.url || '';
  const bioguideId = member.bioguideId || member.id || '';
  
  // Format bills for display
  const formatBill = (bill) => {
    if (!bill) return null;
    
    return (
      <ListGroup.Item key={bill.bill_id || bill.id} className="bill-item">
        <div className="bill-title">
          <strong>{bill.bill_id || bill.number || 'Unknown Bill'}</strong>
          <Badge bg={getBillStatusColor(bill.status)}>
            {bill.status || 'Status Unknown'}
          </Badge>
        </div>
        <p>{bill.title || bill.short_title || 'No title available'}</p>
        <small>
          Introduced: {bill.introduced_date || bill.introducedDate || 'Date unknown'}
        </small>
      </ListGroup.Item>
    );
  };

  // Get appropriate color for bill status
  const getBillStatusColor = (status) => {
    if (!status) return 'secondary';
    
    const lowercaseStatus = status.toLowerCase();
    if (lowercaseStatus.includes('passed') || lowercaseStatus.includes('enacted')) return 'success';
    if (lowercaseStatus.includes('failed') || lowercaseStatus.includes('vetoed')) return 'danger';
    if (lowercaseStatus.includes('introduced')) return 'info';
    if (lowercaseStatus.includes('committee')) return 'primary';
    return 'secondary';
  };

  return (
    <Card className="member-card">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <div>
          <h3>{memberName}</h3>
          <div className="member-subtitle">
            {chamber === 'house' ? 'Representative' : 'Senator'} - {party} 
            {chamber === 'house' ? ` - ${state}-${district}` : ` - ${state}`}
          </div>
        </div>
        <Button variant="close" onClick={onClose} />
      </Card.Header>
      
      <Card.Body>
        <Row className="mb-4">
          <Col md={4} className="text-center">
            <div className="member-image-container">
              <img 
                src={imageUrl} 
                alt={memberName} 
                className="member-image" 
                onError={(e) => {
                  e.target.src = FALLBACK_IMAGES[chamber];
                }}
              />
            </div>
            <div className="mt-3">
              {url && (
                <a href={url} target="_blank" rel="noopener noreferrer" className="btn btn-sm btn-outline-primary mt-2">
                  Official Website
                </a>
              )}
              {bioguideId && (
                <a 
                  href={`https://bioguide.congress.gov/search/bio/${bioguideId}`} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="btn btn-sm btn-outline-secondary mt-2 ms-2"
                >
                  Biography
                </a>
              )}
            </div>
          </Col>
          
          <Col md={8}>
            <Tabs
              activeKey={activeTab}
              onSelect={(k) => setActiveTab(k)}
              className="mb-3"
            >
              <Tab eventKey="bio" title="Biography">
                <div className="member-bio">
                  {member.biography ? (
                    <p>{member.biography}</p>
                  ) : (
                    <p>
                      {memberName} is a {chamber === 'house' ? 'Representative' : 'Senator'} from the state of {state}
                      {chamber === 'house' ? `, representing the ${district} district` : ''}.
                      {party && ` ${memberName} is a member of the ${party} party.`}
                    </p>
                  )}
                </div>
              </Tab>
              
              <Tab eventKey="sponsored" title="Sponsored Bills">
                {loading ? (
                  <div className="text-center p-4">
                    <Spinner animation="border" variant="primary" />
                    <p className="mt-2">Loading sponsored legislation...</p>
                  </div>
                ) : error ? (
                  <div className="alert alert-danger">{error}</div>
                ) : sponsoredBills.length > 0 ? (
                  <ListGroup className="bill-list">
                    {sponsoredBills.slice(0, 5).map(formatBill)}
                  </ListGroup>
                ) : (
                  <p className="text-muted">No sponsored bills available.</p>
                )}
              </Tab>
              
              <Tab eventKey="cosponsored" title="Cosponsored Bills">
                {loading ? (
                  <div className="text-center p-4">
                    <Spinner animation="border" variant="primary" />
                    <p className="mt-2">Loading cosponsored legislation...</p>
                  </div>
                ) : error ? (
                  <div className="alert alert-danger">{error}</div>
                ) : cosponsoredBills.length > 0 ? (
                  <ListGroup className="bill-list">
                    {cosponsoredBills.slice(0, 5).map(formatBill)}
                  </ListGroup>
                ) : (
                  <p className="text-muted">No cosponsored bills available.</p>
                )}
              </Tab>
            </Tabs>
          </Col>
        </Row>
      </Card.Body>
      
      <Card.Footer className="text-center">
        <Button variant="secondary" onClick={onClose}>Close</Button>
      </Card.Footer>
    </Card>
  );
};

export default MemberCard; 