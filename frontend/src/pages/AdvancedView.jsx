import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useLocation, useParams, Link, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Spinner, Alert, Badge, ListGroup, Image } from 'react-bootstrap';
import './AdvancedView.css'; // Updated CSS import
import { useSelector } from 'react-redux';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function AdvancedView() {
    const [member, setMember] = useState(null);
    const [loading, setLoading] = useState(false); // Start false, set true during fetch
    const [error, setError] = useState('');
    const [states, setStates] = useState([]);
    const [committees, setCommittees] = useState([]); // Add committees state
    const [searchTerm, setSearchTerm] = useState({
        name: '',
        state: '',
        party: '',
        memberType: '', // Added memberType
        district: '',
        committee: '' // Add committee search term
    });
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [imagesLoaded, setImagesLoaded] = useState({});
    
    const preloadedImages = useRef(new Map());
    const location = useLocation();
    const { memberId } = useParams(); // Get memberId from URL if present
    const navigate = useNavigate();

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

    // Load committees for dropdown
    const loadCommittees = useCallback(async () => {
        try {
            const response = await fetch(`${API_URL}/api/congress/committees`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (Array.isArray(data)) {
                setCommittees(data);
            } else {
                console.error("Fetched committees data is not an array:", data);
                throw new Error("Invalid data format for committees");
            }
        } catch (err) {
            console.error("Failed to fetch committees:", err);
            setError("Failed to load committee list.");
            setCommittees([]);
        }
    }, []);

    // Load data when component mounts
    useEffect(() => {
        loadStates();
        loadCommittees(); // Load committees on mount
    }, [loadStates, loadCommittees]);

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
        console.log("AdvancedView mounting or dependencies changed.");
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
        if (searchTerm.memberType) queryParams.append('type', searchTerm.memberType);
        if (searchTerm.district && searchTerm.memberType === 'rep') queryParams.append('district', searchTerm.district);
        if (searchTerm.committee) queryParams.append('committee', searchTerm.committee); 

        const searchUrl = `${API_URL}/api/congress/search?${queryParams.toString()}`;
        // console.log("Search URL:", searchUrl);

        try {
            const response = await fetch(searchUrl);
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
            
            // Debug committee filtering
            /*
            if (searchTerm.committee) {
                console.log("Committee filtering debug:");
                console.log(`- Looking for committee ID: ${searchTerm.committee}`);
                console.log(`- Found ${data.length} members after filtering`);
                
                if (data.length === 0) {
                    // Check if any member has committee data at all
                    try {
                        const testResponse = await fetch(`${API_URL}/api/congress/search`);
                        if (testResponse.ok) {
                            const allMembers = await testResponse.json();
                            const membersWithCommittees = allMembers.filter(m => 
                                m.committees && m.committees.length > 0);
                            
                            console.log(`- Total members with committee data: ${membersWithCommittees.length} out of ${allMembers.length}`);
                            
                            if (membersWithCommittees.length > 0) {
                                console.log("- Sample of committee data:");
                                const sampleMember = membersWithCommittees[0];
                                console.log(`  Member: ${sampleMember.name}`);
                                console.log(`  Committees: ${JSON.stringify(sampleMember.committees.slice(0, 3))}`);
                            }
                            
                            // Check if any member has this specific committee
                            const membersWithThisCommittee = allMembers.filter(m => 
                                m.committees && m.committees.some(c => c.committee_id === searchTerm.committee));
                            
                            console.log(`- Members with selected committee: ${membersWithThisCommittee.length}`);
                            
                            if (membersWithThisCommittee.length > 0) {
                                console.log('- Committee exists but API filtering failed, showing manually filtered results instead');
                                setSearchResults(membersWithThisCommittee);
                                setIsSearching(false);
                                return;
                            }
                        }
                    } catch (err) {
                        console.error("Fallback committee search failed:", err);
                    }
                } else {
                    // If we found results, show the first few
                    console.log(`- First ${Math.min(3, data.length)} members in committee:`)
                    for (let i = 0; i < Math.min(3, data.length); i++) {
                        const member = data[i];
                        const committeeMatch = member.committees?.find(c => c.committee_id === searchTerm.committee);
                        console.log(`  ${member.name} - ${committeeMatch ? committeeMatch.name : 'Unknown role'}`);
                    }
                }
            }
            */
            
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
        setSearchTerm({ 
            name: '', 
            state: '', 
            party: '', 
            memberType: '', 
            district: '',
            committee: '' // Clear committee too
        });
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

    // Render the search form with committee dropdown
    const renderSearchForm = () => (
        <Form onSubmit={handleSearchSubmit} className="mb-4">
            <div className="search-container">
                {/* Member Name Input */}
                <div>
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
                </div>
                
                {/* Member Type Select */}
                <div>
                    <Form.Group controlId="formMemberType">
                        <Form.Label visuallyHidden>Member Type</Form.Label>
                        <Form.Select name="memberType" value={searchTerm.memberType} onChange={handleSearchChange}>
                            <option value="">Any Type</option>
                            <option value="rep">Representative</option>
                            <option value="sen">Senator</option>
                        </Form.Select>
                    </Form.Group>
                </div>
                
                {/* State Select */}
                <div>
                    <Form.Group controlId="formState">
                        <Form.Label visuallyHidden>State</Form.Label>
                        <Form.Select name="state" value={searchTerm.state} onChange={handleSearchChange} disabled={!states.length}>
                            <option value="">Any State</option>
                            {Array.isArray(states) && states.map(s => <option key={s} value={s}>{s}</option>)}
                            {!states.length && <option>Loading States...</option>}
                        </Form.Select>
                    </Form.Group>
                </div>
                
                {/* Party Select */}
                <div>
                    <Form.Group controlId="formParty">
                        <Form.Label visuallyHidden>Party</Form.Label>
                        <Form.Select name="party" value={searchTerm.party} onChange={handleSearchChange}>
                            <option value="">Any Party</option>
                            <option value="Democrat">Democrat</option>
                            <option value="Republican">Republican</option>
                            <option value="Independent">Independent</option>
                        </Form.Select>
                    </Form.Group>
                </div>
                
                {/* Committee Select - New dropdown */}
                <div>
                    <Form.Group controlId="formCommittee">
                        <Form.Label visuallyHidden>Committee</Form.Label>
                        <Form.Select 
                            name="committee" 
                            value={searchTerm.committee} 
                            onChange={(e) => {
                                const committeeId = e.target.value;
                                // console.log(`Selected committee ID: ${committeeId}`);
                                
                                // Also log the matching committee name for reference
                                /*
                                if (committeeId) {
                                    const selectedCommittee = committees.find(c => c.committee_id === committeeId);
                                    if (selectedCommittee) {
                                        console.log(`Selected committee name: ${selectedCommittee.name}`);
                                        console.log(`Committee details: ${JSON.stringify(selectedCommittee)}`);
                                    }
                                }
                                */
                                handleSearchChange(e);
                            }}
                            disabled={!committees.length}
                        >
                            <option value="">Any Committee</option>
                            {Array.isArray(committees) && committees.map(committee => (
                                <option key={committee.committee_id} value={committee.committee_id}>
                                    {committee.name} ({committee.committee_id})
                                </option>
                            ))}
                            {!committees.length && <option>Loading Committees...</option>}
                        </Form.Select>
                    </Form.Group>
                </div>
                
                {/* Buttons */}
                <div className="button-container">
                    <Button variant="primary" type="submit" disabled={isSearching}>
                        {isSearching ? <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" /> : 'Search'}
                    </Button>
                    <Button variant="secondary" onClick={handleClearSearch}>
                        Clear
                    </Button>
                </div>
            </div>
            
            {/* Conditionally render District field in a separate row if needed */}
            {searchTerm.memberType === 'rep' && (
                <div className="mt-2">
                    <Form.Group controlId="formDistrict">
                        <Form.Label visuallyHidden>District</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="District"
                            name="district"
                            value={searchTerm.district}
                            onChange={handleSearchChange}
                        />
                    </Form.Group>
                </div>
            )}
        </Form>
    );

    // Render search results with improved styling
    const renderSearchResults = () => (
        <div className="search-results">
            <h3 className="mt-4 mb-3">Search Results...</h3>
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
                                            // console.log("Image failed to load:", res.currentImageUrl);
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

    // --- Add State for Vote History ---
    const [voteHistory, setVoteHistory] = useState([]);
    const [loadingVotes, setLoadingVotes] = useState(false);
    const [voteError, setVoteError] = useState('');
    // --- End Vote History State ---
    
    // --- Add State for Vote Year Filter ---
    const [selectedVoteYear, setSelectedVoteYear] = useState('All');
    // --- End Vote Year Filter State ---

    // --- Add State for Bill/Keyword Filter ---
    const [filterBillNumber, setFilterBillNumber] = useState('');
    const [filterKeyword, setFilterKeyword] = useState('');
    // --- End Bill/Keyword Filter State ---

    // --- Calculate available vote years ---
    const availableVoteYears = useMemo(() => {
        // console.log("[VOTE_YEARS] Recalculating available years from voteHistory length:", voteHistory.length);
        const yearSet = new Set();
        let invalidDateCount = 0;
        
        voteHistory.forEach((vote, index) => {
            if (!vote.date) {
                // console.log(`[VOTE_YEARS_DETAIL] Vote index ${index}: Missing date`);
                return;
            }
            try {
                const dateObj = new Date(vote.date);
                const year = dateObj.getFullYear(); // Get year regardless of validity for logging
                
                // Detailed Log for EVERY vote (will be verbose!)
                // console.log(`[VOTE_YEARS_DETAIL] Vote index ${index}: Date='${vote.date}', ParsedYear=${year}, IsNaN=${isNaN(dateObj.getTime())}`);
                
                if (!isNaN(dateObj.getTime())) {
                    yearSet.add(year);
                } else {
                    invalidDateCount++;
                    // Only log invalid dates once to avoid flooding console
                    if (invalidDateCount < 10) { // Log first few invalid dates
                         // console.warn(`[VOTE_YEARS] Invalid date format encountered: ${vote.date} for vote_id: ${vote.vote_id || 'N/A'}`); 
                    }
                }
            } catch (e) { 
                 // console.error(`[VOTE_YEARS] Error parsing date string: ${vote.date}`, e);
                 invalidDateCount++;
            }
        });
        
        if (invalidDateCount >= 10) {
             // console.warn(`[VOTE_YEARS] ... and ${invalidDateCount - 9} more invalid date formats encountered.`);
        }
        
        const sortedYears = Array.from(yearSet).sort((a, b) => b - a);
        // console.log("[VOTE_YEARS] Final calculated unique years (using Set):", sortedYears); // Log the final list
        return sortedYears;
    }, [voteHistory]);
    // --- End Calculate Vote Years ---

    // --- Filtering Logic (moved outside render function) ---
    const filteredVotes = useMemo(() => {
        // console.log(`[VOTE_FILTER] Filtering votes. Year: ${selectedVoteYear}, Bill: ${filterBillNumber}, Keyword: ${filterKeyword}`); // DEBUG
        let votesToFilter = voteHistory;

        // Filter by Year
        if (selectedVoteYear !== 'All') {
            const targetYear = parseInt(selectedVoteYear);
            votesToFilter = votesToFilter.filter(vote => {
                if (!vote.date) return false;
                try {
                    const voteYear = new Date(vote.date).getFullYear();
                    const match = voteYear === targetYear;
                    // if (!match && voteYear > 2006) { // Add more specific logging if needed
                    //    console.log(`[VOTE_FILTER_MISMATCH] Vote Year: ${voteYear}, Target Year: ${targetYear}, Date: ${vote.date}`);
                    // }
                    return match;
                } catch (e) {
                    console.error("Error parsing date for filtering:", vote.date, e);
                    return false;
                }
            });
        }

        // Filter by Bill Number (case-insensitive, partial match)
        if (filterBillNumber.trim()) {
            const lowerFilterBill = filterBillNumber.trim().toLowerCase();
            votesToFilter = votesToFilter.filter(vote => 
                (vote.bill_number && vote.bill_number.toLowerCase().includes(lowerFilterBill)) ||
                (vote.bill_type && vote.bill_type.toLowerCase().includes(lowerFilterBill)) // Also check type (e.g., HR, S)
            );
        }

        // Filter by Keyword (case-insensitive, partial match in question or description)
        if (filterKeyword.trim()) {
            const lowerFilterKeyword = filterKeyword.trim().toLowerCase();
            votesToFilter = votesToFilter.filter(vote => 
                (vote.question && vote.question.toLowerCase().includes(lowerFilterKeyword)) ||
                (vote.description && vote.description.toLowerCase().includes(lowerFilterKeyword))
            );
        }
        
        // console.log(`[VOTE_FILTER] Filtered votes count after all filters: ${votesToFilter.length}`); // DEBUG
        return votesToFilter;
    }, [voteHistory, selectedVoteYear, filterBillNumber, filterKeyword]);
    // --- End Filtering Logic ---

    // --- Add useEffect to Fetch Vote History ---
    useEffect(() => {
        const fetchVoteHistory = async () => {
            if (member && member.bioguide_id) {
                setLoadingVotes(true);
                setVoteError('');
                setVoteHistory([]); // Clear previous votes
                // console.log(`Fetching vote history for bioguide_id: ${member.bioguide_id}`);
                try {
                    const response = await fetch(`${API_URL}/api/members/${member.bioguide_id}/votes`);
                    if (!response.ok) {
                        // Handle specific errors if possible, e.g., 404 for no history
                        if (response.status === 404) {
                            setVoteError('No vote history found for this member.');
                        } else {
                            throw new Error(`HTTP error fetching votes! status: ${response.status}`);
                        }
                        setVoteHistory([]); // Ensure empty on error
                    } else {
                        const data = await response.json();
                        // console.log("Vote history fetched:", data);
                        // --- DEBUG: Log dates of first/last few votes ---
                        /*
                        if (Array.isArray(data) && data.length > 0) {
                            const firstFewDates = data.slice(0, 5).map(v => v.date);
                            const lastFewDates = data.slice(-5).map(v => v.date);
                            console.log("[VOTE_DATE_CHECK] Dates of first 5 votes received:", firstFewDates);
                            console.log("[VOTE_DATE_CHECK] Dates of last 5 votes received:", lastFewDates);
                        }
                        */
                        // --- END DEBUG ---
                        if (Array.isArray(data)) {
                            setVoteHistory(data);
                            if (data.length === 0) {
                                setVoteError('No vote history found for this member.'); // Explicit message if empty array returned
                            }
                        } else {
                            console.error("Fetched vote history is not an array:", data);
                            throw new Error("Invalid vote history format");
                        }
                    }
                } catch (err) {
                    console.error("Failed to fetch vote history:", err);
                    setVoteError(err.message || 'Failed to load vote history.');
                    setVoteHistory([]);
                } finally {
                    setLoadingVotes(false);
                }
            } else {
                // Clear votes if no member or no bioguide_id
                setVoteHistory([]);
                setLoadingVotes(false);
                setVoteError('');
            }
        };

        fetchVoteHistory();
    }, [member]); // Re-run when member changes
    // --- End Vote History Fetch Effect ---

    // --- Helper Function to Render Vote History ---
    const renderVoteHistory = () => {
        // console.log(`[VOTE_RENDER] Rendering votes. Selected year: ${selectedVoteYear}`); // DEBUG (No longer needed here)
        // --- Filtering Logic MOVED OUTSIDE ---
        // const filteredVotes = useMemo(() => { ... }, [voteHistory, selectedVoteYear]); // MOVED

        if (loadingVotes) {
            return (
                <div className="text-center my-3">
                    <Spinner animation="border" size="sm" />
                    <p className="mt-1 small text-white-50">Loading Votes...</p>
                </div>
            );
        }

        // Show error message *before* checking filteredVotes length
        if (voteError && voteHistory.length === 0) {
            // Only show the main fetch error if we actually have no votes at all
            return <p className="text-center text-warning small mt-3">{voteError}</p>;
        }

        // Handle case where votes exist but none match the selected year filter
        if (!loadingVotes && voteHistory.length > 0 && filteredVotes.length === 0) {
            return <p className="text-center text-white-50 small mt-3">No votes found for the year {selectedVoteYear}.</p>;
        }

        // If there was no initial fetch error, but the voteHistory array is empty, show the voteError message (e.g., "No vote history found")
        if (!loadingVotes && voteHistory.length === 0 && voteError) {
             return <p className="text-center text-warning small mt-3">{voteError}</p>;
        }

        // If loading is done, no error, and the original history is empty, return null quietly (should be caught by voteError usually)
        if (!loadingVotes && voteHistory.length === 0 && !voteError) {
             return null;
        }

        // Helper to format vote position with styling
        const formatVotePosition = (position) => {
            if (!position) return <span className="vote-position vote-other">N/A</span>;
            const posLower = position.toLowerCase();
            let className = 'vote-position';
            if (posLower.includes('yea') || posLower.includes('yes') || posLower.includes('aye')) {
                className += ' vote-yea';
            } else if (posLower.includes('nay') || posLower.includes('no')) {
                className += ' vote-nay';
            } else {
                className += ' vote-other'; // For Present, Not Voting, etc.
            }
            return <span className={className}>{position}</span>;
        };

        return (
            <div className="vote-history-section">
                {/* --- Title & Filter Row --- */}
                <Row className="mb-3 justify-content-center align-items-center"> {/* Center title and filters */}
                    {/* Title */}
                    <Col xs={12} md="auto" className="mb-2 mb-md-0">
                        <h5 className="text-white section-title mb-0">Vote History</h5>
                    </Col>
                    {/* Year Filter */}
                    <Col xs={6} sm={4} md={2} className="mb-2 mb-md-0">
                        {availableVoteYears.length > 0 && (
                            <Form.Group controlId="voteYearFilter">
                                <Form.Label visuallyHidden>Filter by Year</Form.Label>
                                <Form.Select 
                                    size="sm" 
                                    value={selectedVoteYear} 
                                    onChange={(e) => setSelectedVoteYear(e.target.value)}
                                    aria-label="Filter votes by year"
                                >
                                    <option value="All">All Years</option>
                                    {availableVoteYears.map(year => (
                                        <option key={year} value={year}>{year}</option>
                                    ))}
                                </Form.Select>
                            </Form.Group>
                        )}
                    </Col>
                     {/* Bill Filter */}
                    <Col xs={6} sm={4} md={3} className="mb-2 mb-md-0">
                        <Form.Group controlId="voteBillFilter">
                            <Form.Label visuallyHidden>Filter by Bill Number</Form.Label>
                            <Form.Control 
                                type="text" 
                                size="sm" 
                                placeholder="Bill (e.g., HR 22)"
                                value={filterBillNumber}
                                onChange={(e) => setFilterBillNumber(e.target.value)}
                                aria-label="Filter votes by bill number"
                            />
                         </Form.Group>
                    </Col>
                    {/* Keyword Filter */}
                    <Col xs={12} sm={4} md={4} className="mb-2 mb-md-0">
                         <Form.Group controlId="voteKeywordFilter">
                            <Form.Label visuallyHidden>Filter by Keyword</Form.Label>
                            <Form.Control 
                                type="text" 
                                size="sm" 
                                placeholder="Keyword (in question/desc)"
                                value={filterKeyword}
                                onChange={(e) => setFilterKeyword(e.target.value)}
                                aria-label="Filter votes by keyword"
                            />
                        </Form.Group>
                    </Col>
                </Row>
                {/* --- End Filter Row --- */}
                
                <div className="vote-scroll-container">
                    <ListGroup variant="flush" className="vote-list">
                        {filteredVotes.map((vote, index) => (
                            <ListGroup.Item key={vote.vote_id || `vote-${index}`} className="vote-item bg-transparent border-secondary text-white">
                                <div className="vote-details mb-1">
                                    <span className="vote-date">{new Date(vote.date).toLocaleDateString()}</span>
                                    <span className="vote-chamber mx-1">({vote.chamber || 'Chamber N/A'})</span>
                                    {vote.bill_number && (
                                        <span className="vote-bill">
                                            {vote.bill_type?.toUpperCase() || ''} {vote.bill_number}
                                        </span>
                                    )}
                                </div>
                                <div className="vote-question mb-1">{vote.question}</div>
                                {vote.description && (
                                    <div className="vote-description text-white-50 mb-2">{vote.description}</div>
                                )}
                                <div className="vote-member-action">
                                    <strong>Vote:</strong> {formatVotePosition(vote.member_vote_position)}
                                    <span className="vote-result ms-2 text-white-50">({vote.result || 'Result N/A'})</span>
                                </div>
                                {vote.source_url && (
                                    <div className="vote-source mt-1">
                                        <a href={vote.source_url} target="_blank" rel="noopener noreferrer" className="small text-info">
                                            View Source
                                        </a>
                                    </div>
                                )}
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                </div>
            </div>
        );
    };
    // --- End Vote History Render Function ---

    // Render member profile details with committee and vote information
    const renderMemberProfile = () => {
        if (!member) return null;

        // Determine party class for styling
        const partyClass = member.party === 'Democrat' ? 'democrat-border' : 
                          member.party === 'Republican' ? 'republican-border' : 'independent-border';
        const badgeVariant = member.party === 'Democrat' ? 'primary' : 
                            member.party === 'Republican' ? 'danger' : 'info';

        const subcommitteesOnly = member.committees?.filter(c => c.is_subcommittee) || [];
        const seenSubcommitteeIds = new Set();
        const uniqueSubcommittees = subcommitteesOnly.filter(committee => {
            if (!committee.committee_id) return false;
            if (!seenSubcommitteeIds.has(committee.committee_id)) {
                seenSubcommitteeIds.add(committee.committee_id);
                return true;
            }
            return false;
        });

        const getRolePriority = (role) => {
            const roleLower = role?.toLowerCase();
            if (roleLower === 'chairman' || roleLower === 'chair') return 0;
            if (roleLower === 'vice chairman' || roleLower === 'vice chair') return 1;
            if (roleLower === 'ranking member') return 2;
            if (roleLower === 'ex officio') return 3;
            return 99;
        };

        uniqueSubcommittees.sort((a, b) => getRolePriority(a.role) - getRolePriority(b.role));

        return (
            <Card className={`member-profile-card ${partyClass}`}>
                <Card.Header className="profile-header">
                    <Row className="align-items-center">
                        <Col className="text-center">
                            <h2 className="h3 mb-1 text-white member-name-orbitron">{member.name}</h2>
                            <div className="d-flex align-items-center justify-content-center mt-2">
                                <Badge pill bg={badgeVariant} className="me-2">
                                    {member.party}
                                </Badge>
                                <span className="text-white opacity-90" style={{ fontSize: '0.95rem' }}>
                                    {member.state}
                                    {(member.member_type === 'rep' || member.member_type === 'representative') && member.district && ` - District ${member.district}`}
                                    {(member.member_type === 'sen' || member.member_type === 'senator') && member.state_rank && ` - ${member.state_rank.charAt(0).toUpperCase() + member.state_rank.slice(1)} Senator`}
                                </span>
                            </div>
                        </Col>
                    </Row>
                </Card.Header>
                <Card.Body>
                    <Row className="mb-4 align-items-stretch">
                        {/* === Left Column: Image === */}
                        <Col md={4} className="text-center mb-4 mb-md-0 d-flex flex-column">
                            <div className="profile-image-container flex-grow-1">
                                <Image
                                    src={currentImageUrl} 
                                    onError={(e) => {
                                        // console.log("Image failed to load:", currentImageUrl);
                                        e.target.onerror = null; // Prevent infinite loop
                                        handleImageError(); // Try next variation
                                    }}
                                    className="profile-image"
                                    style={{ 
                                        width: '100%', 
                                        maxWidth: '300px',
                                        height: 'auto',
                                        objectFit: 'cover',
                                        backgroundColor: '#f0f0f0',
                                        borderRadius: '8px',
                                        display: 'block', 
                                        margin: '0 auto' 
                                    }}
                                    alt={`Portrait of ${member.name}`}
                                />
                            </div>
                        </Col>
                        
                        {/* === Middle Column: General Information === */}
                        <Col md={4} className="mb-4 mb-md-0 d-flex flex-column">
                            <div className="flex-grow-1">
                            <h4 className="mb-3 text-white section-title">General Information</h4>
                            <ListGroup variant="flush">
                                {(member.term_start || member.term_end) && (
                                    <ListGroup.Item className="border-0 mb-2 rounded info-item">
                                        <span className="info-label">Current Term</span>
                                        <span className="info-value">{member.term_start || '?'} to {member.term_end || '?'}</span>
                                    </ListGroup.Item>
                                )}
                                {member.office_address && (
                                    <ListGroup.Item className="border-0 mb-2 rounded info-item">
                                        <span className="info-label">Office</span>
                                        <span className="info-value">{member.office_address}</span>
                                    </ListGroup.Item>
                                )}
                                {member.phone && (
                                    <ListGroup.Item className="border-0 mb-2 rounded info-item">
                                        <span className="info-label">Phone</span>
                                        <span className="info-value">
                                            <a href={`tel:${member.phone}`} className="text-white">{member.phone}</a>
                                        </span>
                                    </ListGroup.Item>
                                )}
                                {member.website && (
                                    <ListGroup.Item className="border-0 mb-2 rounded info-item">
                                        <span className="info-label">Website</span>
                                        <span className="info-value">
                                            <a href={member.website} target="_blank" rel="noopener noreferrer" className="text-white">{member.website}</a>
                                        </span>
                                    </ListGroup.Item>
                                )}
                                <ListGroup.Item className="border-0 mb-2 rounded info-item">
                                    <span className="info-label">Contact Form</span>
                                    <span className="info-value">
                                        {member.contact_form ? (
                                            <a href={member.contact_form} target="_blank" rel="noopener noreferrer" className="text-white">Official Contact Form</a>
                                        ) : (
                                                <span></span> 
                                        )}
                                    </span>
                                </ListGroup.Item>
                                {member.bioguide_id && (
                                    <ListGroup.Item className="border-0 mb-2 rounded info-item">
                                        <span className="info-label">BioGuide ID</span>
                                        <span className="info-value">{member.bioguide_id}</span>
                                    </ListGroup.Item>
                                )}
                            </ListGroup>
                            </div>
                        </Col>
                        
                        {/* === Right Column: Committee Assignments (Restored) === */}
                        <Col md={4} className="d-flex flex-column">
                            <div className="flex-grow-1">
                                {/* Committee Assignments Section */}
                            {uniqueSubcommittees && uniqueSubcommittees.length > 0 ? (
                                    <div className="committee-section mb-4">
                                        <h5 className="mb-3 text-white section-title">Committee Assignments</h5>
                                    <div className="committee-scroll-container"> 
                                        <ListGroup className="committee-assignments-list">
                                            {uniqueSubcommittees.map((committee, index) => (
                                                <ListGroup.Item 
                                                    key={`${committee.committee_id}-${index}`}
                                                    className="bg-transparent text-white border-secondary committee-item-profile"
                                                >
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div>
                                                            <strong>{committee.name}</strong>
                                                            {committee.is_subcommittee && (
                                                                <div className="text-muted small">
                                                                    {committee.parent_committee}
                                                                </div>
                                                            )}
                                                        </div>
                                                        {committee.role && committee.role !== 'Member' && (
                                                            <Badge 
                                                                bg={committee.role === 'Chairman' ? 'primary' : 
                                                                    committee.role === 'Ranking Member' ? 'info' : 'secondary'}
                                                                className="ms-2"
                                                            >
                                                                {committee.role}
                                                            </Badge>
                                                        )}
                                                    </div>
                                                </ListGroup.Item>
                                            ))}
                                        </ListGroup>
                                    </div>
                                    </div> 
                            ) : (
                                    <div className="text-center text-white-50 my-4">
                                    No current committee assignments found.
                                </div>
                            )}
                            </div>
                        </Col>
                    </Row>
                    
                    {/* --- Vote History Row (Full Width) --- */}
                    <Row className="mt-3"> 
                        <Col xs={12}>
                             {renderVoteHistory()} 
                        </Col>
                    </Row>
                    
                </Card.Body>
            </Card>
        );
    };

    // Main component rendering logic
    return (
        <Container className="advanced-view-container">
            <div className="search-section">
                <h2>Advanced Member Search</h2>
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

export default AdvancedView; 