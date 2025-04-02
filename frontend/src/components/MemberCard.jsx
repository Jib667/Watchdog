import React from 'react';
import { Card, Button, Badge, Row, Col } from 'react-bootstrap';
// Removed import for utils/api.js as bill fetching is removed
// import { fetchMemberSponsored, fetchMemberCosponsored } from '../utils/api';
import './MemberCard.css';

// Simpler fallback image
const FALLBACK_IMAGE = '/static/images/placeholder.jpg';

// Simplified MemberCard to just display static info from props
const MemberCard = ({ member, onClose }) => {

  if (!member) return null;

  // Extract data from the member prop (static data)
  const memberName = member.name || 'Unknown Member';
  const party = member.party || 'Unknown Party';
  const state = member.state || '';
  const district = member.district;
  const website = member.website;
  const imageUrl = member.image_filename ? `/static/images/${member.image_filename}` : FALLBACK_IMAGE;
  const isRepresentative = !!district; // Simple check if it's a rep or senator

  // Determine party class for styling
  const partyLower = party.toLowerCase();
  let partyClass = 'unknown';
  if (partyLower === 'democrat' || partyLower === 'democratic') {
    partyClass = 'democrat';
  } else if (partyLower === 'republican') {
    partyClass = 'republican';
  } else if (partyLower === 'independent' || partyLower === 'independence') {
    partyClass = 'independent';
  }

  return (
    // Use a modal-like overlay structure
    <div className="member-card-overlay" onClick={onClose}>
      <Card className="member-card-modal" onClick={(e) => e.stopPropagation()}>
        <Card.Header className="d-flex justify-content-between align-items-center">
          {/* Header with Name and Title */}
          <div>
            <h3 className="member-card-name">{memberName}</h3>
            <div className="member-card-subtitle">
              {isRepresentative ? 'Representative' : 'Senator'}
              {state && ` - ${state}`}
              {isRepresentative && district && ` - District ${district}`}
            </div>
          </div>
          {/* Use standard Bootstrap close button */}
          <Button variant="close" onClick={onClose} aria-label="Close" />
        </Card.Header>

        <Card.Body>
          <Row className="mb-4">
            {/* Image Column */}
            <Col md={4} className="text-center mb-3 mb-md-0">
              <div className="member-card-image-container">
                <img
                  src={imageUrl}
                  alt={`Portrait of ${memberName}`}
                  className="member-card-image"
                  onError={(e) => {
                    e.target.onerror = null; // Prevent infinite loop
                    e.target.src = FALLBACK_IMAGE;
                  }}
                />
              </div>
            </Col>

            {/* Info Column */}
            <Col md={8}>
               <div className="member-card-info">
                 <h4>Details</h4>
                 <p>
                   <strong>Party: </strong>
                   <Badge pill bg={partyClass === 'democrat' ? 'primary' : partyClass === 'republican' ? 'danger' : 'secondary'}>
                    {party}
                   </Badge>
                 </p>
                 <p><strong>State:</strong> {state}</p>
                 {isRepresentative && district && (
                    <p><strong>District:</strong> {district}</p>
                 )}
                 {website && (
                    <p>
                        <strong>Website: </strong>
                        <a href={website} target="_blank" rel="noopener noreferrer">
                            {website}
                        </a>
                    </p>
                 )}
                 {/* Add more static details here if available in member data */}
               </div>
            </Col>
          </Row>
        </Card.Body>

        <Card.Footer className="text-center">
          <Button variant="secondary" onClick={onClose}>Close</Button>
        </Card.Footer>
      </Card>
    </div>
  );
};

export default MemberCard; 