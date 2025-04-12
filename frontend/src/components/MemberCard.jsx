import React, { useEffect, useState } from 'react';
import { Badge } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import './MemberCard.css';

// Define API_BASE_URL - adjust this based on your actual API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Function to generate image variations using the unitedstates/images repo
const generateImageUrlVariations = (bioguideId, baseUrl) => {
    if (!bioguideId) {
        console.warn("generateImageUrlVariations (MemberCard) called without bioguideId, returning only placeholder.");
        return [`${baseUrl}/static/images/placeholder.jpg`]; // Only placeholder if no ID
    }
    
    const githubBaseUrl = 'https://unitedstates.github.io/images/congress';
    // Prioritize smaller image for cards, then larger, then original
    const sizes = ['225x275', '450x550', 'original']; 
    
    const variations = sizes.map(size => `${githubBaseUrl}/${size}/${bioguideId}.jpg`);
    
    // Add local placeholder as the ultimate fallback (using baseUrl provided)
    variations.push(`${baseUrl}/static/images/placeholder.png`); // Use .png
    
    console.log(`[MemberCard] Image URL variations for ${bioguideId}:`, variations);
    return variations;
};

// Updated MemberCard to display more data from the member prop
const MemberCard = ({ member, onClose }) => {
  const navigate = useNavigate();
  const [currentImageUrl, setCurrentImageUrl] = useState(null);
  const [imageUrlIndex, setImageUrlIndex] = useState(0);
  const [imageUrlVariations, setImageUrlVariations] = useState([]);
  
  console.log("MemberCard rendering with member:", member);

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
  const isRepresentative = !!district;
  const phone = member.phone;
  const officeAddress = member.office_address;
  const contactForm = member.contact_form;
  const bioguideId = member.bioguide_id;
  const termStart = member.term_start;
  const termEnd = member.term_end;
  const stateRank = member.state_rank; // For senators
  const senateClass = member.senate_class; // For senators
  
  useEffect(() => {
    const baseUrl = API_BASE_URL; // Use the API base URL for the placeholder fallback
    
    // Generate variations using bioguideId
    const variations = generateImageUrlVariations(bioguideId, baseUrl);
    setImageUrlVariations(variations);
    setImageUrlIndex(0); // Reset to first variation
    
    // Initialize with the first variation (e.g., 225x275 from github)
    if (variations.length > 0) {
        setCurrentImageUrl(variations[0]); 
    } else {
        setCurrentImageUrl(null); // Should not happen if placeholder logic is correct
    }

  }, [member, bioguideId]); // Depend on member and specifically bioguideId
  
  // Function to try the next image URL variation
  const tryNextImageVariation = () => {
    if (imageUrlIndex < imageUrlVariations.length - 1) {
      const nextIndex = imageUrlIndex + 1;
      setImageUrlIndex(nextIndex);
      setCurrentImageUrl(imageUrlVariations[nextIndex]);
      console.log(`Trying image variation ${nextIndex}:`, imageUrlVariations[nextIndex]);
    }
  };
  
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

  // Navigate to advanced profile
  const handleViewAdvancedProfile = () => {
    navigate(`/advanced-profile/${bioguideId}`, { state: { member } });
    onClose(); // Close the modal
  };

  return (
    // Modal Overlay (similar to Login/SignUp)
    <div className="modal-overlay member-card-overlay" onClick={onClose}>
      {/* Apply the dynamic party class here for border styling */}
      <div 
        className={`modal-content member-card-modal ${modalPartyClass}`.trim()} 
        onClick={(e) => e.stopPropagation()}
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
              {isRepresentative && district !== undefined && (
                district === 0 || district === '0' || district === 'At-Large' ? ` - At-Large District` : ` - District ${district}`
              )}
              {!isRepresentative && stateRank && ` - ${stateRank.charAt(0).toUpperCase() + stateRank.slice(1)} Senator`}
            </div>
          </div>
          <button type="button" className="close-button" onClick={onClose} aria-label="Close">
            &times; 
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body member-card-body">
          {/* Use flex layout classes defined in CSS */}
          <div className="row"> 
            {/* Image Column - Use specific class */}
            <div className="col-image">
              <div className="member-card-image-container">
                <img
                  src={currentImageUrl} 
                  alt={`Portrait of ${memberName}`}
                  className="member-card-image"
                  onError={(e) => {
                    console.log("Image failed to load:", currentImageUrl);
                    e.target.onerror = null; // Prevent infinite loop if we reach the end
                    tryNextImageVariation(); // Try next variation on error
                  }}
                />
              </div>
            </div>

            {/* Info Column - Use specific class */}
            <div className="col-info">
              <div className="member-card-info">
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
          <div className="form-actions">
            <button 
              className="action-button view-profile-button" 
              onClick={handleViewAdvancedProfile}
            >
              Advanced Profile
            </button>
            <button 
              className="action-button cancel-button" 
              onClick={onClose}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemberCard; 