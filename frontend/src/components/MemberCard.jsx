import React from 'react';
import { Card, Button, Badge, Row, Col } from 'react-bootstrap';
// Removed import for utils/api.js as bill fetching is removed
// import { fetchMemberSponsored, fetchMemberCosponsored } from '../utils/api';
import './MemberCard.css';

// Updated MemberCard to display more data from the member prop
const MemberCard = ({ member, onClose }) => {
  console.log("MemberCard rendering with member:", member); // Log on render

  if (!member) {
    console.log("MemberCard returning null because member is missing.");
    return null;
  }

  // Extract data from the member prop
  const memberName = member.name || 'Unknown Member';
  const party = member.party || 'Unknown Party';
  const state = member.state || '';
  const district = member.district; // Null/undefined for senators
  const website = member.website;
  // Use the correct image_url field from core.py
  const imageUrl = member.image_url;
  const isRepresentative = !!district;
  const phone = member.phone;
  const officeAddress = member.office_address;
  const contactForm = member.contact_form;
  const bioguideId = member.bioguide_id;
  const termStart = member.term_start;
  const termEnd = member.term_end;
  const stateRank = member.state_rank; // For senators
  const senateClass = member.senate_class; // For senators

  // Determine party class for styling the MODAL BORDER
  const partyLower = party ? party.toLowerCase() : '';
  let modalPartyClass = '';
  if (partyLower === 'democrat') {
    modalPartyClass = 'party-democrat';
  } else if (partyLower === 'republican') {
    modalPartyClass = 'party-republican';
  } else if (partyLower === 'independent') {
    modalPartyClass = 'party-independent';
  }

  return (
    // Modal Overlay (similar to Login/SignUp)
    <div className="modal-overlay member-card-overlay" onClick={onClose}>
      {/* Apply the dynamic party class here for border styling */}
      <div 
        className={`modal-content member-card-modal ${modalPartyClass}`.trim()} 
        onClick={(e) => e.stopPropagation()}
        style={{ backgroundColor: '#1e3a5f', color: 'white' }}
      >
        {/* Modal Header */}
        <div className="modal-header member-card-header">
          <div className="member-card-title-section">
            {/* Add specific class for Orbitron font targeting */}
            <h2 className="member-card-name member-card-name-orbitron"> 
              {memberName || 'Member Details'}
            </h2>
            <div className="member-card-subtitle">
              {isRepresentative ? 'Representative' : 'Senator'}
              {state && ` - ${state}`}
              {isRepresentative && district && ` - District ${district}`}
              {!isRepresentative && stateRank && ` - ${stateRank.charAt(0).toUpperCase() + stateRank.slice(1)} Senator`}
            </div>
          </div>
          <button type="button" className="close-button" onClick={onClose} aria-label="Close">
            &times; 
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body member-card-body" style={{ backgroundColor: '#1e3a5f', color: 'white' }}>
          {/* Use flex layout classes defined in CSS */}
          <div className="row" style={{ display: 'flex', flexWrap: 'nowrap' }}> 
            {/* Image Column - Use specific class */}
            <div className="col-image" style={{ 
                flex: '0 0 140px', 
                maxWidth: '140px', 
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                backgroundColor: '#1e3a5f'
              }}>
              <div className="member-card-image-container">
                <img
                  src={imageUrl} 
                  alt={`Portrait of ${memberName}`}
                  className="member-card-image"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = '/static/images/placeholder.jpg';
                  }}
                />
              </div>
            </div>

            {/* Info Column - Use specific class */}
            <div className="col-info" style={{ 
                flex: '1', 
                minWidth: '0', 
                paddingLeft: '15px',
                textAlign: 'left',
                backgroundColor: '#1e3a5f',
                color: 'white'
              }}>
              <div className="member-card-info" style={{ textAlign: 'left', color: 'white' }}>
                {/* Keep details as paragraphs for now, can adjust styling in CSS */}
                <p>
                  <strong>Party: </strong>
                  <Badge pill bg={partyLower === 'democrat' ? 'primary' : partyLower === 'republican' ? 'danger' : 'secondary'}>
                    {party || 'N/A'}
                  </Badge>
                </p>
                <p><strong>State:</strong> {state}</p>
                {isRepresentative && district && (
                  <p><strong>District:</strong> {district}</p>
                )}
                {!isRepresentative && senateClass && (
                  <p><strong>Senate Class:</strong> {senateClass}</p>
                )}
                {termStart && termEnd && (
                    <p><strong>Current Term:</strong> {termStart} to {termEnd}</p>
                )}
                {phone && (
                  <p><strong>Phone:</strong> {phone}</p>
                )}
                {officeAddress && (
                  <p><strong>Office:</strong> {officeAddress}</p>
                )}
                {website && (
                  <p>
                    <strong>Website: </strong>
                    <a href={website} target="_blank" rel="noopener noreferrer">
                      {website}
                    </a>
                  </p>
                )}
                 {contactForm && (
                  <p>
                    <strong>Contact Form: </strong>
                    <a href={contactForm} target="_blank" rel="noopener noreferrer">
                      Official Contact Form
                    </a>
                  </p>
                )}
                {bioguideId && (
                  <p><strong>BioGuide ID:</strong> {bioguideId}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer member-card-footer">
          {/* Center the button like login/signup modals */}
          <div className="form-actions centered">
              <button type="button" className="action-button cancel-button" onClick={onClose}>
                Close
              </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemberCard; 