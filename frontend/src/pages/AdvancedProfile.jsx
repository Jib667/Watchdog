import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useLocation, useParams, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Spinner, Alert, Badge, ListGroup, Image } from 'react-bootstrap';
import './AdvancedProfile.css'; // Ensure CSS is imported

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function AdvancedProfile() {
    const [member, setMember] = useState(null);
    const [loading, setLoading] = useState(false); // Start false, set true during fetch
    const [error, setError] = useState('');
    const [states, setStates] = useState([]);
    const [searchTerm, setSearchTerm] = useState({
        name: '',
        state: '',
        party: '',
        memberType: '', // Added memberType
        district: '' // Added district
    });
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [imagesLoaded, setImagesLoaded] = useState({});
    
    const preloadedImages = useRef(new Map());
    const location = useLocation();
    const { memberId } = useParams(); // Get memberId from URL if present

    // ----- Image Handling With Pre-Caching -----
    const [currentImageUrl, setCurrentImageUrl] = useState('');
    const [imageUrlVariations, setImageUrlVariations] = useState([]);
    const [currentVariationIndex, setCurrentVariationIndex] = useState(0);
    const [imageError, setImageError] = useState(false);

    // Function to generate all possible image variations for a member name
    const generateImageUrlVariations = useCallback((name) => {
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
        variations.push(`${API_URL}/static/images/${firstName.toLowerCase()}_${lastName.toLowerCase()}.jpg`);
        
        // 2. lastname_firstname
        variations.push(`${API_URL}/static/images/${lastName.toLowerCase()}_${firstName.toLowerCase()}.jpg`);
        
        // 3. Full normalized name (all parts joined with underscores)
        if (normalizedName.split(' ').length > 2) {
            variations.push(`${API_URL}/static/images/${normalizedName.toLowerCase().replace(/\s+/g, '_').replace(/\./g, '').replace(/'/g, '')}.jpg`);
        }
        
        // Always try with just the first letter of first name + last name
        variations.push(`${API_URL}/static/images/${firstName.charAt(0).toLowerCase()}_${lastName.toLowerCase()}.jpg`);
        
        // Last resort: placeholder
        variations.push(`${API_URL}/static/images/placeholder.jpg`);
        
        // Log the variations for debugging
        console.log("Image URL variations:", variations);
        
        return variations;
    }, []);

    // Function to preload an image
    const preloadImage = useCallback((src) => {
        return new Promise((resolve, reject) => {
            // If already preloaded, resolve immediately
            if (preloadedImages.current.has(src)) {
                resolve(src);
                return;
            }
            
            const img = new Image();
            img.src = src;
            img.onload = () => {
                preloadedImages.current.set(src, true);
                resolve(src);
            };
            img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
        });
    }, []);

    // Try to load images in sequence
    const tryLoadImages = useCallback(async (variations) => {
        // If no variations, return placeholder immediately
        if (!variations || variations.length === 0) {
            return { 
                src: `${API_URL}/static/images/placeholder.jpg`, 
                index: -1 
            };
        }
        
        // Try placeholder first to ensure it's cached
        try {
            await preloadImage(`${API_URL}/static/images/placeholder.jpg`);
        } catch (err) {
            console.error("Failed to preload placeholder image", err);
        }
        
        // Set a timeout to avoid blocking too long
        const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error("Image loading timed out")), 3000)
        );
        
        for (const [index, src] of variations.entries()) {
            try {
                // Race between image loading and timeout
                await Promise.race([
                    preloadImage(src),
                    timeoutPromise
                ]);
                return { src, index };
            } catch (err) {
                console.log(`Image failed to load: ${src}`);
                // Continue to next variation
            }
        }
        
        // If all failed, return the placeholder
        return { 
            src: `${API_URL}/static/images/placeholder.jpg`, 
            index: variations.length - 1 
        };
    }, [preloadImage]);

    // Effect to set up and load image when member changes
    useEffect(() => {
        if (!member?.name) return;
        
        // Generate all possible image URL variations
        const variations = generateImageUrlVariations(member.name);
        setImageUrlVariations(variations);
        setCurrentVariationIndex(0); // Reset to first variation
        setCurrentImageUrl(variations[0]); // Start with first variation
    }, [member, generateImageUrlVariations]);

    // Handle image loading error - try next variation
    const handleImageError = useCallback(() => {
        if (currentVariationIndex < imageUrlVariations.length - 1) {
            const nextIndex = currentVariationIndex + 1;
            setCurrentVariationIndex(nextIndex);
            setCurrentImageUrl(imageUrlVariations[nextIndex]);
            console.log(`Trying image variation ${nextIndex}:`, imageUrlVariations[nextIndex]);
        }
    }, [currentVariationIndex, imageUrlVariations]);
    // ----- End Image Handling -----

    // Preload images for search results
    useEffect(() => {
        if (!searchResults.length) return;
        
        const preloadResultImages = async () => {
            for (const member of searchResults) {
                // Skip if already loaded
                if (imagesLoaded[member.congress_id]) continue;
                
                const variations = generateImageUrlVariations(member.name);
                try {
                    const { src } = await tryLoadImages(variations);
                    member.loadedImageSrc = src;
                    setImagesLoaded(prev => ({ ...prev, [member.congress_id]: true }));
                } catch (err) {
                    console.error(`Failed to preload image for ${member.name}:`, err);
                    member.loadedImageSrc = `${API_URL}/static/images/placeholder.jpg`;
                }
            }
        };
        
        preloadResultImages();
    }, [searchResults, generateImageUrlVariations, tryLoadImages, imagesLoaded]);

    // Fetch states for the dropdown
    const loadStates = useCallback(async () => {
        try {
            const response = await fetch(`${API_URL}/api/congress/states`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            // console.log("States fetched:", data);
            if (Array.isArray(data)) {
                setStates(data.sort()); // Sort states alphabetically
            } else {
                console.error("Fetched states data is not an array:", data);
                throw new Error("Invalid data format for states");
            }
        } catch (err) {
            console.error("Failed to fetch states:", err);
            setError('Failed to load state list. Using fallback.');
            // Fallback to hardcoded states if fetch fails
            const fallbackStates = [
                "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
                "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
                "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
                "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
                "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
                "New Hampshire", "New Jersey", "New Mexico", "New York",
                "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
                "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
                "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
                "West Virginia", "Wisconsin", "Wyoming"
            ];
            setStates(fallbackStates.sort());
        }
    }, []);

    // Fetch member data by ID
    const loadMemberById = useCallback(async (id) => {
        setLoading(true);
        setError('');
        setMember(null); // Clear previous member data
        setSearchResults([]); // Clear search results when loading specific member
        console.log(`Attempting to load member by ID: ${id}`);
        
        // Scroll to top of the page
        window.scrollTo(0, 0);
        
        try {
            const response = await fetch(`${API_URL}/api/congress/member/${id}`);
             if (!response.ok) {
                if (response.status === 404) {
                    throw new Error(`Member with ID ${id} not found.`);
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            }
            const data = await response.json();
             if (!data) {
                throw new Error("Received empty data for member.");
            }
            console.log("Member data fetched by ID:", data);
            setMember(data);
        } catch (err) {
            console.error(`Failed to fetch member ${id}:`, err);
            setError(err.message || 'Failed to load member data.');
            setMember(null); // Ensure member is null on error
        } finally {
            setLoading(false);
        }
    }, []);

    // Add this state to store all members
    const [allMembers, setAllMembers] = useState([]);

    // Add a function to load all members
    const loadAllMembers = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const response = await fetch(`${API_URL}/api/congress/members`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log("All members fetched:", data);
            if (Array.isArray(data)) {
                // Sort alphabetically by name
                data.sort((a, b) => a.name.localeCompare(b.name));
                setAllMembers(data);
                setSearchResults(data); // Show all members in search results
            } else {
                console.error("Fetched members data is not an array:", data);
                throw new Error("Invalid data format for members");
            }
        } catch (err) {
            console.error("Failed to fetch all members:", err);
            // Instead of showing an error, fall back to searching with empty parameters
            console.log("Falling back to search with empty parameters");
            try {
                const searchResponse = await fetch(`${API_URL}/api/congress/search`);
                if (searchResponse.ok) {
                    const searchData = await searchResponse.json();
                    if (Array.isArray(searchData)) {
                        searchData.sort((a, b) => a.name.localeCompare(b.name));
                        setAllMembers(searchData);
                        setSearchResults(searchData);
                    } else {
                        throw new Error("Invalid search data format");
                    }
                } else {
                    throw new Error(`Search fallback failed: ${searchResponse.status}`);
                }
            } catch (searchErr) {
                console.error("Search fallback failed:", searchErr);
                // Only set the error if both methods fail
                setError('Failed to load members list. Try using the search form.');
                setAllMembers([]);
                setSearchResults([]);
            }
        } finally {
            setLoading(false);
        }
    }, []);

    // Load member data when memberId changes
    useEffect(() => {
        console.log("AdvancedProfile mounting or dependencies changed.");
        loadStates(); // Load states on component mount

        // Prioritize member data passed via location state
        if (location.state?.member) {
            console.log("Member data found in location state:", location.state.member);
            setMember(location.state.member);
            setLoading(false); // Already have data, no loading needed
            setError('');
            setSearchResults([]); // Clear search results if showing direct member profile
            window.scrollTo(0, 0); // Scroll to top when loading member from state
        }
        // If no location state, check URL parameters for memberId
        else if (memberId) {
            console.log(`Member ID found in URL: ${memberId}. Fetching...`);
            loadMemberById(memberId);
        }
        // Otherwise, load all members and show them in search results
        else {
            console.log("No specific member requested. Loading all members.");
            setMember(null);
            loadAllMembers();
        }
    }, [location.state, memberId, loadStates, loadMemberById, loadAllMembers]); 
    
    // Add a new effect specifically for scrolling to top when member changes
    useEffect(() => {
        if (member) {
            window.scrollTo(0, 0);
        }
    }, [member]);

    const handleSearchChange = (event) => {
        const { name, value } = event.target;
        setSearchTerm(prev => ({ ...prev, [name]: value }));
    };

    const handleSearchSubmit = async (event) => {
        event.preventDefault();
        setIsSearching(true);
        setError('');
        setMember(null); // Clear specific member view when searching
        setSearchResults([]); // Clear previous results
        console.log("Submitting search with terms:", searchTerm);

        // Construct query parameters, excluding empty values
        const queryParams = new URLSearchParams();
        if (searchTerm.name) queryParams.append('name', searchTerm.name);
        if (searchTerm.state) queryParams.append('state', searchTerm.state);
        if (searchTerm.party) queryParams.append('party', searchTerm.party);
        if (searchTerm.memberType) queryParams.append('type', searchTerm.memberType); // Add type
        if (searchTerm.district && searchTerm.memberType === 'rep') queryParams.append('district', searchTerm.district); // Add district only for reps

        try {
            // console.log(`Fetching: ${API_URL}/api/congress/search?${queryParams.toString()}`);
            const response = await fetch(`${API_URL}/api/congress/search?${queryParams.toString()}`);
            if (!response.ok) {
                 if (response.status === 404) {
                    throw new Error("No members found matching your criteria.");
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            }
            const data = await response.json();
            console.log("Search results received:", data);
             if (!Array.isArray(data)) {
                 console.error("Search response is not an array:", data);
                throw new Error("Received invalid search results format.");
            }
            setSearchResults(data);
             if (data.length === 0) {
                setError("No members found matching your criteria.");
            }

        } catch (err) {
            console.error("Search failed:", err);
            setError(err.message || 'Failed to perform search.');
            setSearchResults([]); // Clear results on error
        } finally {
            setIsSearching(false);
        }
    };

     const handleClearSearch = () => {
        setSearchTerm({ name: '', state: '', party: '', memberType: '', district: '' });
        setError('');
        setMember(null); // Clear member view if resetting search
        
        // Show loading spinner briefly
        setLoading(true);
        
        // Use a simple empty search to get all members
        fetch(`${API_URL}/api/congress/search`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (Array.isArray(data)) {
                    // Sort alphabetically by name
                    data.sort((a, b) => a.name.localeCompare(b.name));
                    setSearchResults(data);
                } else {
                    throw new Error("Invalid data format");
                }
            })
            .catch(err => {
                console.error("Failed to fetch all members:", err);
                // Try loadAllMembers as a fallback
                loadAllMembers();
            })
            .finally(() => {
                setLoading(false);
            });
    };

    // Render the search form
    const renderSearchForm = () => (
        <Form onSubmit={handleSearchSubmit} className="mb-4">
            {/* Removed Title: <h2>Search for a Member</h2> */}
            <Row className="g-2 align-items-end"> {/* Use g-2 for smaller gutters */}
                <Col md={4} xs={12}>
                    <Form.Group controlId="formMemberName">
                        <Form.Label visuallyHidden>Member Name</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Enter Member Name"
                            name="name"
                            value={searchTerm.name}
                            onChange={handleSearchChange}
                        />
                    </Form.Group>
                </Col>
                <Col md={2} xs={6}>
                     <Form.Group controlId="formMemberType">
                        <Form.Label visuallyHidden>Member Type</Form.Label>
                        <Form.Select name="memberType" value={searchTerm.memberType} onChange={handleSearchChange}>
                            <option value="">Any Type</option>
                            <option value="rep">Representative</option>
                            <option value="sen">Senator</option>
                        </Form.Select>
                    </Form.Group>
                </Col>
                 <Col md={2} xs={6}>
                    <Form.Group controlId="formState">
                         <Form.Label visuallyHidden>State</Form.Label>
                        <Form.Select name="state" value={searchTerm.state} onChange={handleSearchChange} disabled={!states.length}>
                            <option value="">Any State</option>
                            {Array.isArray(states) && states.map(s => <option key={s} value={s}>{s}</option>)}
                             {!states.length && <option>Loading States...</option>}
                        </Form.Select>
                    </Form.Group>
                </Col>
                 {/* Conditionally render District field only if Member Type is Representative */}
                 {searchTerm.memberType === 'rep' && (
                    <Col md={1} xs={4}>
                        <Form.Group controlId="formDistrict">
                            <Form.Label visuallyHidden>District</Form.Label>
                            <Form.Control
                                type="text" // Or number, depending on expected input
                                placeholder="Dist"
                                name="district"
                                value={searchTerm.district}
                                onChange={handleSearchChange}
                                disabled={searchTerm.memberType !== 'rep'} // Disable if not rep
                            />
                        </Form.Group>
                    </Col>
                 )}
                <Col md={searchTerm.memberType === 'rep' ? 1 : 2} xs={searchTerm.memberType === 'rep' ? 4 : 6}> {/* Adjust width based on district field visibility */}
                    <Form.Group controlId="formParty">
                         <Form.Label visuallyHidden>Party</Form.Label>
                        <Form.Select name="party" value={searchTerm.party} onChange={handleSearchChange}>
                            <option value="">Any Party</option>
                            <option value="Democrat">Democrat</option>
                            <option value="Republican">Republican</option>
                            <option value="Independent">Independent</option>
                            {/* Add other parties if needed */}
                        </Form.Select>
                    </Form.Group>
                </Col>
                <Col md="auto" xs={4}> {/* Use auto width for buttons */}
                    <Button variant="primary" type="submit" disabled={isSearching} className="w-100">
                        {isSearching ? <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" /> : 'Search'}
                    </Button>
                </Col>
                 <Col md="auto" xs={4}>
                    <Button variant="secondary" onClick={handleClearSearch} className="w-100">Clear</Button>
                </Col>
            </Row>
        </Form>
    );

    // Render search results with improved styling
    const renderSearchResults = () => (
        <div className="search-results">
            <h3 className="mt-4 mb-3">Search Results</h3>
            <ListGroup>
                {searchResults.map(res => {
                    // Determine party class for styling
                    const partyClass = res.party === 'Democrat' ? 'democrat-border' : 
                                      res.party === 'Republican' ? 'republican-border' : 'independent-border';
                    
                    // Process image URL for this result if not already done
                    if (!res.currentImageUrl) {
                        res.imageUrlVariations = generateImageUrlVariations(res.name);
                        res.currentImageUrl = res.imageUrlVariations[0];
                        res.imageUrlIndex = 0;
                    }
                    
                    // Function to try next image variation
                    const tryNextImageVariation = (result) => {
                        if (result.imageUrlIndex < result.imageUrlVariations.length - 1) {
                            result.imageUrlIndex++;
                            result.currentImageUrl = result.imageUrlVariations[result.imageUrlIndex];
                            return result.currentImageUrl;
                        }
                        return result.currentImageUrl;
                    };
                    
                    return (
                        <ListGroup.Item 
                            key={res.congress_id || res.bioguide_id} 
                            action 
                            as={Link} 
                            to={`/advanced-profile/${res.congress_id}`}
                            className={`mb-2 ${partyClass}`}
                            onClick={() => {
                                // Programmatically scroll to top when link is clicked
                                window.scrollTo(0, 0);
                            }}
                        >
                            <Row className="align-items-center">
                                <Col xs="auto" className="pe-0">
                                    <Image
                                        src={res.currentImageUrl} 
                                        onError={(e) => {
                                            console.log("Image failed to load:", res.currentImageUrl);
                                            e.target.onerror = null; // Prevent infinite loop
                                            const nextUrl = tryNextImageVariation(res);
                                            if (nextUrl) {
                                                e.target.src = nextUrl;
                                            }
                                        }}
                                        roundedCircle
                                        style={{ 
                                            width: '50px', 
                                            height: '50px', 
                                            objectFit: 'cover',
                                            backgroundColor: '#f1f1f1'
                                        }}
                                        alt={`${res.name}`}
                                    />
                                </Col>
                                <Col>
                                    <div className="d-flex flex-column">
                                        <strong>{res.name}</strong>
                                        <span>
                                            {res.party} - {res.state} {res.district ? `(District ${res.district})` : '(Senator)'}
                                        </span>
                                    </div>
                                </Col>
                            </Row>
                        </ListGroup.Item>
                    );
                })}
            </ListGroup>
        </div>
    );

     // Render member profile details
    const renderMemberProfile = () => {
        if (!member) return null;

        // Determine party class for styling
        const partyClass = member.party === 'Democrat' ? 'democrat-border' : 
                          member.party === 'Republican' ? 'republican-border' : 'independent-border';
        
        // Determine badge color based on party
        const badgeVariant = member.party === 'Democrat' ? 'primary' : 
                            member.party === 'Republican' ? 'danger' : 'info';

        // Basic details
        let details = `${member.state}`;
        if (member.member_type === 'representative' && member.district) {
            details += ` - District ${member.district}`;
        } else if (member.member_type === 'senator') {
            details += ` - Senator${member.state_rank ? ` (${member.state_rank})` : ''}`;
        }

        return (
            <Card className={`member-profile-card ${partyClass}`}>
                <Card.Header className="profile-header">
                    <Row className="align-items-center">
                        <Col className="text-center">
                            <h2 className="h3 mb-0 text-white member-name-orbitron">{member.name}</h2>
                            <div className="d-flex align-items-center justify-content-center mt-2">
                                <Badge pill bg={badgeVariant} className="me-2">
                                    {member.party}
                                </Badge>
                                <span className="text-white opacity-90">{details}</span>
                            </div>
                        </Col>
                    </Row>
                </Card.Header>
                <Card.Body>
                    <Row>
                        <Col md={4} className="text-center mb-4 mb-md-0">
                            <div className="profile-image-container">
                                <Image
                                    src={currentImageUrl} 
                                    onError={(e) => {
                                        console.log("Image failed to load:", currentImageUrl);
                                        e.target.onerror = null; // Prevent infinite loop if we reach the end
                                        handleImageError(); // Try next variation on error
                                    }}
                                    className="profile-image"
                                    style={{ 
                                        width: '250px', 
                                        height: '300px', 
                                        objectFit: 'cover',
                                        backgroundColor: '#f0f0f0',
                                        borderRadius: '8px'
                                    }}
                                    alt={`Portrait of ${member.name}`}
                                />
                            </div>
                        </Col>
                        <Col md={8}>
                            <Row>
                                <Col md={6}>
                                    <h5 className="mb-3 text-white">Contact Information</h5>
                                    <ListGroup variant="flush">
                                        {member.office_address && (
                                            <ListGroup.Item className="border-0 mb-2 rounded info-item" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                                                <span className="info-label">Office</span>
                                                <span className="info-value">{member.office_address}</span>
                                            </ListGroup.Item>
                                        )}
                                        {member.phone && (
                                            <ListGroup.Item className="border-0 mb-2 rounded info-item" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                                                <span className="info-label">Phone</span>
                                                <span className="info-value">
                                                    <a href={`tel:${member.phone}`} className="text-white">{member.phone}</a>
                                                </span>
                                            </ListGroup.Item>
                                        )}
                                        {member.website && (
                                            <ListGroup.Item className="border-0 mb-2 rounded info-item" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                                                <span className="info-label">Website</span>
                                                <span className="info-value">
                                                    <a href={member.website} target="_blank" rel="noopener noreferrer" className="text-white">{member.website}</a>
                                                </span>
                                            </ListGroup.Item>
                                        )}
                                        {member.contact_form && (
                                            <ListGroup.Item className="border-0 mb-2 rounded info-item" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                                                <span className="info-label">Contact Form</span>
                                                <span className="info-value">
                                                    <a href={member.contact_form} target="_blank" rel="noopener noreferrer" className="text-white">Online Form</a>
                                                </span>
                                            </ListGroup.Item>
                                        )}
                                    </ListGroup>
                                </Col>
                                <Col md={6}>
                                    <h5 className="mb-3 text-white">Congressional Details</h5>
                                    <ListGroup variant="flush">
                                        <ListGroup.Item className="border-0 mb-2 rounded info-item" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                                            <span className="info-label">Bioguide ID</span>
                                            <span className="info-value">{member.bioguide_id || 'N/A'}</span>
                                        </ListGroup.Item>
                                        {member.term_start && member.term_end && (
                                            <ListGroup.Item className="border-0 mb-2 rounded info-item" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                                                <span className="info-label">Current Term</span>
                                                <span className="info-value">{member.term_start} to {member.term_end}</span>
                                            </ListGroup.Item>
                                        )}
                                        {member.member_type === 'senator' && member.senate_class && (
                                            <ListGroup.Item className="border-0 mb-2 rounded info-item" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                                                <span className="info-label">Senate Class</span>
                                                <span className="info-value">{member.senate_class}</span>
                                            </ListGroup.Item>
                                        )}
                                        <ListGroup.Item className="border-0 mb-2 rounded info-item" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                                            <span className="info-label">Committees</span>
                                            <span className="info-value">(Coming Soon)</span>
                                        </ListGroup.Item>
                                        <ListGroup.Item className="border-0 mb-2 rounded info-item" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                                            <span className="info-label">Recent Votes</span>
                                            <span className="info-value">(Coming Soon)</span>
                                        </ListGroup.Item>
                                    </ListGroup>
                                </Col>
                            </Row>
                        </Col>
                    </Row>
                </Card.Body>
            </Card>
        );
    };


    // Main component rendering logic
    return (
        <Container className="advanced-profile-container">
            <div className="search-section">
                {renderSearchForm()}
            </div>

            {loading && (
                <div className="text-center my-5">
                    <Spinner animation="border" role="status" className="loading-spinner">
                        <span className="visually-hidden">Loading...</span>
                    </Spinner>
                    <p className="mt-2 loading-text">Loading member data...</p>
                </div>
            )}

            {error && !isSearching && !loading && (
                <Alert variant="danger" onClose={() => setError('')} dismissible>
                    {error}
                </Alert>
            )}

            {!loading && member && (
                renderMemberProfile()
            )}

            {!loading && !member && searchResults.length > 0 && (
                renderSearchResults()
            )}

            {error && isSearching && !loading && (
                <Alert variant="warning" className="mt-4">
                    {error}
                </Alert>
            )}
        </Container>
    );
}

export default AdvancedProfile; 