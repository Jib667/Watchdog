import React, { useEffect, useState } from 'react';
import { Badge } from 'react-bootstrap';
import './MemberCard.css';

// Define API_BASE_URL - adjust this based on your actual API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Function to generate different possible image filename variations
const generateImageUrlVariations = (name, baseUrl) => {
  if (!name) return [];
  
  const variations = [];
  
  // Clean the name by removing suffixes
  let cleanedName = name.replace(/,?\s+(jr\.?|sr\.?|i{1,3}|iv|v)$/i, '').trim();
  console.log("Name after removing suffixes:", cleanedName);
  
  // Handle nicknames in different quote formats: "Rick", 'Rick', "Rick", etc.
  // \u201C and \u201D are unicode for curly quotes
  cleanedName = cleanedName.replace(/\s+[\"\'\u201C\u201D]([^\"\']+)[\"\'\u201C\u201D]\s+/g, ' ');
  console.log("Name after removing quoted nicknames:", cleanedName);
  
  // Remove middle names and initials - keep only first and last name
  if (cleanedName.split(' ').length > 2) {
    const parts = cleanedName.split(' ');
    cleanedName = `${parts[0]} ${parts[parts.length - 1]}`;
  }
  console.log("Name simplified to first and last:", cleanedName);
  
  // Normalize accented characters (á, é, í, ó, ú, ñ, etc.)
  const normalizedName = cleanedName.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  console.log("Normalized name:", normalizedName);
  
  // First priority: firstname_lastname
  const firstName = normalizedName.split(' ')[0];
  const lastName = normalizedName.split(' ').pop();
  
  // Add variations
  // 1. firstname_lastname (highest priority)
  variations.push(`${baseUrl}/static/images/${firstName.toLowerCase()}_${lastName.toLowerCase()}.jpg`);
  
  // 2. lastname_firstname
  variations.push(`${baseUrl}/static/images/${lastName.toLowerCase()}_${firstName.toLowerCase()}.jpg`);
  
  // 3. Full normalized name (all parts joined with underscores)
  if (normalizedName.split(' ').length > 2) {
    variations.push(`${baseUrl}/static/images/${normalizedName.toLowerCase().replace(/\s+/g, '_').replace(/\./g, '').replace(/'/g, '')}.jpg`);
  }
  
  // Always try with just the first letter of first name + last name
  variations.push(`${baseUrl}/static/images/${firstName.charAt(0).toLowerCase()}_${lastName.toLowerCase()}.jpg`);
  
  // Last resort: placeholder
  variations.push(`${baseUrl}/static/images/placeholder.jpg`);
  
  // Log the variations for debugging
  console.log("Image URL variations:", variations);
  
  return variations;
};

// Updated MemberCard to display more data from the member prop
const MemberCard = ({ member, onClose }) => {
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
  
  // Handle image URL to ensure it's properly formed
  useEffect(() => {
    const baseUrl = API_BASE_URL;
    
    // Generate all possible image URL variations
    const variations = generateImageUrlVariations(memberName, baseUrl);
    setImageUrlVariations(variations);
    setImageUrlIndex(0); // Reset to first variation
    setCurrentImageUrl(variations[0]); // Start with first variation
  }, [member, memberName]);
  
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
          <div className="form-actions centered">
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