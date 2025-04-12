import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useLocation, useParams, Link, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Spinner, Alert, Badge, ListGroup, Image, ProgressBar } from 'react-bootstrap';
import { FixedSizeList } from 'react-window'; // Import react-window
import './AdvancedView.css'; // Updated CSS import
import { useSelector } from 'react-redux';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Custom Hook for Debouncing
function useDebounce(value, delay) {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
        // Set timeout to update debounced value after delay
        const handler = setTimeout(() => {
            console.log(`[useDebounce] Updating debounced value for: ${value} (after ${delay}ms)`);
            setDebouncedValue(value);
        }, delay);

        // Cleanup function to clear timeout if value changes before delay
        return () => {
            clearTimeout(handler);
        };
    }, [value, delay]); // Re-run effect if value or delay changes

    return debouncedValue;
}

// Simple Error Boundary Component
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI.
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // You can also log the error to an error reporting service
        console.error("ErrorBoundary caught an error:", error, errorInfo);
        this.setState({ error: error, errorInfo: errorInfo });
    }

    render() {
        if (this.state.hasError) {
            // You can render any custom fallback UI
            return (
                <Alert variant="danger">
                    <Alert.Heading>Something went wrong while rendering the vote history.</Alert.Heading>
                    <p>
                        There was an issue displaying the votes. Please try refreshing or clearing the filters.
                    </p>
                    {/* Optionally display error details for debugging */}
                    {/* 
                    <hr />
                    <p className="mb-0">
                        {this.state.error && this.state.error.toString()}
                        <br />
                        {this.state.errorInfo && this.state.errorInfo.componentStack}
                    </p>
                    */}
                </Alert>
            );
        }

        return this.props.children; 
    }
}

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

    // Scroll to top of page when component mounts or when member changes
    useEffect(() => {
        window.scrollTo(0, 0);
    }, [member, memberId]);
    
    // ----- Image Handling With Pre-Caching -----
    const [currentImageUrl, setCurrentImageUrl] = useState('');
    const [imageUrlVariations, setImageUrlVariations] = useState([]);
    const [currentVariationIndex, setCurrentVariationIndex] = useState(0);
    const [imageError, setImageError] = useState(false);

    // Function to generate image variations using the unitedstates/images repo
    const generateImageUrlVariations = useCallback((bioguideId) => {
        if (!bioguideId) {
            console.warn("generateImageUrlVariations called without bioguideId, returning only placeholder.");
            return [`${API_URL}/static/images/placeholder.png`]; // Only placeholder if no ID
        }
        
        const baseUrl = 'https://unitedstates.github.io/images/congress';
        const sizes = ['450x550', '225x275', 'original']; // Try larger sizes first
        
        const variations = sizes.map(size => `${baseUrl}/${size}/${bioguideId}.jpg`);
        
        // Add local placeholder as the ultimate fallback
        variations.push(`${API_URL}/static/images/placeholder.png`); // Use .png
        
        console.log(`Image URL variations for ${bioguideId}:`, variations);
        return variations;
    }, []); // API_URL could be a dependency if it might change, but likely stable

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
        const variations = generateImageUrlVariations(member.bioguide_id);
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
                
                const variations = generateImageUrlVariations(member.bioguide_id);
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
        console.log(`[loadMemberById] Attempting to load member by ID: ${id}`);

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
            console.log("[loadMemberById] Member data fetched by ID:", data);
            console.log("[loadMemberById] state_rank from fetched data:", data?.state_rank);
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

    // Load member data when memberId changes or via location state
    useEffect(() => {
        console.log("AdvancedView mounting or dependencies changed.");
        loadStates(); // Load states on component mount

        // Prioritize member data passed via location state
        if (location.state?.member) {
            let memberDataFromState = { ...location.state.member }; // Clone to modify
            console.log("[Effect] Member data found in location state:", memberDataFromState);

            // Check if member_type is missing and try to infer it
            if (!memberDataFromState.member_type) {
                console.warn("[Effect] member_type missing in location state. Attempting to infer...");
                if (memberDataFromState.state_rank) {
                    memberDataFromState.member_type = 'sen'; // Infer Senator
                    console.log("[Effect] Inferred member_type: sen (due to state_rank)");
                } else if (memberDataFromState.district) {
                    memberDataFromState.member_type = 'rep'; // Infer Representative
                    console.log("[Effect] Inferred member_type: rep (due to district)");
                } else {
                     console.warn("[Effect] Could not infer member_type from location state data.");
                }
            }
            
            console.log("[Effect] Final state_rank from location state data:", memberDataFromState?.state_rank);
            setMember(memberDataFromState); // Use the potentially modified data
            setLoading(false); // Already have data, no loading needed
            setError('');
            setSearchResults([]); // Clear search results if showing direct member profile
            window.scrollTo(0, 0); // Scroll to top when loading member from state
        }
        // If no location state, check URL parameters for memberId
        else if (memberId) {
            console.log(`[Effect] Member ID found in URL: ${memberId}. Fetching via loadMemberById...`);
            // Ensure previous state is cleared before loading
            setMember(null);
            setError('');
            setSearchResults([]);
            loadMemberById(memberId);
        }
        // Otherwise, load all members and show them in search results
        else {
            console.log("[Effect] No specific member requested. Loading all members.");
            setMember(null);
            setSearchResults([]); // Clear any previous search results
            setLoading(false);
            loadAllMembers();
        }
        
    }, [location.state, memberId, loadStates, loadMemberById, loadAllMembers]);
    
    // Add a new effect specifically for scrolling to top when member changes
    useEffect(() => {
        // Ensure scroll happens after potential re-render
        if (member) {
            console.log("[ScrollEffect] Member updated, attempting scroll to top.");
            const timer = setTimeout(() => {
                window.scrollTo(0, 0);
                console.log("[ScrollEffect] Scrolled to top.");
            }, 0); // Execute after current stack
            return () => clearTimeout(timer); // Cleanup timeout
        }
    }, [member]);

    // Effect to ensure complete member data when navigated via state
    useEffect(() => {
        // Only run if we have a member object but didn't load via URL memberId initially
        if (member && !memberId) {
            const isSenator = member.member_type === 'sen' || member.member_type === 'senator';
            const isRep = member.member_type === 'rep' || member.member_type === 'representative';
            const missingSenatorRank = isSenator && !member.state_rank;
            const missingRepDistrict = isRep && !member.district;

            // If essential data seems missing and we likely got member from location.state
            if (missingSenatorRank || missingRepDistrict) {
                console.log("[Refetch Check] Incomplete data detected from location.state. Refetching full profile.");
                const idToFetch = member.congress_id || member.bioguide_id;
                if (idToFetch) {
                    loadMemberById(idToFetch);
                }
            }
        }
    }, [member, memberId, loadMemberById]); // Depend on member, memberId, and the fetch function

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

    // Render search results with improved styling and virtualization
    const renderSearchResults = () => {
        
        // Define the Row component for react-window search results
        const MemberRow = ({ index, style }) => {
            const res = searchResults[index];
            if (!res) return null;

            // Determine party class for styling
            const partyClass = res.party === 'Democrat' ? 'democrat-border' : 
                              res.party === 'Republican' ? 'republican-border' : 'independent-border';
            
            // Ensure image properties are initialized (might be redundant if preloaded elsewhere)
            if (!res.currentImageUrl) {
                res.imageUrlVariations = generateImageUrlVariations(res.bioguide_id);
                res.currentImageUrl = res.imageUrlVariations[0];
                res.imageUrlIndex = 0;
            }
            
            // Function to try next image variation (scoped within the row)
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
                    to={`/advanced-profile/${res.congress_id}`} // Use congress_id for linking
                    style={style} // Apply style provided by react-window
                    className={`mb-2 ${partyClass} member-search-result-item`} // Added specific class
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
                                    {res.party} - {res.state}
                                    {(res.member_type === 'rep' || res.member_type === 'representative') && res.district && (
                                        ` - District ${res.district}`
                                    )}
                                    {(res.member_type === 'sen' || res.member_type === 'senator') && res.state_rank && (
                                        ` - ${res.state_rank.charAt(0).toUpperCase() + res.state_rank.slice(1)} Senator`
                                    )}
                                </span>
                            </div>
                        </Col>
                    </Row>
                </ListGroup.Item>
            );
        };

        const MEMBER_ITEM_HEIGHT = 75; // Estimate height for member result items
        // Calculate a reasonable height for the list container, e.g., based on viewport or a fixed max
        const listHeight = Math.min(searchResults.length * MEMBER_ITEM_HEIGHT, window.innerHeight * 0.6);

        return (
            <div className="search-results">
                <h3 className="mt-4 mb-3">Search Results ({searchResults.length})</h3>
                <FixedSizeList
                    height={listHeight} // Dynamic height or a fixed value
                    itemCount={searchResults.length}
                    itemSize={MEMBER_ITEM_HEIGHT}
                    width={'100%'}
                    className="member-search-list" // Add class for styling
                >
                    {MemberRow}
                </FixedSizeList>
            </div>
        );
    };

    // --- Add State for Vote History ---
    const [voteHistory, setVoteHistory] = useState([]);
    const [loadingVotes, setLoadingVotes] = useState(false);
    const [voteError, setVoteError] = useState('');
    // --- End Vote History State ---
    
    // --- Add State for Vote Year Filter ---
    const [selectedVoteYear, setSelectedVoteYear] = useState('All');
    // --- End Vote Year Filter State ---

    // --- Add State for Vote Type Filter ---
    const [selectedVoteType, setSelectedVoteType] = useState('All'); // New state for type filter
    // --- End Vote Type Filter State ---

    // --- Add State for Bill/Keyword Filter ---
    // Local state for immediate input value
    const [localFilterBillNumber, setLocalFilterBillNumber] = useState('');
    const [localFilterKeyword, setLocalFilterKeyword] = useState('');
    // Debounced state used for actual filtering
    const filterBillNumber = useDebounce(localFilterBillNumber, 400); // 400ms delay
    const filterKeyword = useDebounce(localFilterKeyword, 400);     // 400ms delay
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
        // Ensure this depends on the DEBOUNCED values
        console.log(`[VOTE_FILTER] START: Filtering votes. Year: ${selectedVoteYear}, Type: ${selectedVoteType}, Bill: ${filterBillNumber}, Keyword: ${filterKeyword}`); // DEBUG
        const startTime = performance.now(); // Start timing
        
        let votesToFilter = voteHistory;
        
        // DEBUG: Log all unique vote types present in the data for troubleshooting
        if (selectedVoteType !== 'All') {
            const uniqueTypes = new Set();
            votesToFilter.forEach(vote => {
                if (vote && vote.type) uniqueTypes.add(vote.type);
            });
            console.log('[VOTE_TYPE_DEBUG] Unique vote types in data:', Array.from(uniqueTypes));
        }

        // Filter by Year (assuming date parsing is robust or handled separately)
        if (selectedVoteYear !== 'All') {
            const targetYear = parseInt(selectedVoteYear);
            votesToFilter = votesToFilter.filter(vote => {
                if (!vote || !vote.date) return false;
                try {
                    const voteYear = new Date(vote.date).getFullYear();
                    return !isNaN(voteYear) && voteYear === targetYear;
                } catch (e) {
                    console.error("Error parsing date for year filtering:", vote.date, e);
                    return false;
                }
            });
        }

        // Filter by Vote Type (Enhanced with better logging)
        if (selectedVoteType !== 'All') {
            console.log(`[VOTE_TYPE_FILTER] Starting with ${votesToFilter.length} votes, filtering for type: "${selectedVoteType}"`);
            
            // Log the first 10 vote categories and types to see what we're working with
            votesToFilter.slice(0, 10).forEach((vote, i) => {
                console.log(`[VOTE_TYPE_DEBUG] Vote #${i} category: "${vote?.category || 'undefined'}", type: "${vote?.type || 'undefined'}"`);
            });
            
            // DEBUG: Log all unique vote categories present in the data for troubleshooting
            const uniqueCategories = new Set();
            votesToFilter.forEach(vote => {
                if (vote && vote.category) uniqueCategories.add(vote.category);
            });
            console.log('[VOTE_TYPE_DEBUG] Unique vote categories in data:', Array.from(uniqueCategories));
            
            // Helper function for normalized string comparison
            const normalizeString = (str) => {
                if (!str) return '';
                return str.toLowerCase()
                    .replace(/\s+/g, ' ')  // Normalize spaces
                    .trim();               // Remove leading/trailing spaces
            };
            
            // Get normalized version of selected filter
            const normalizedFilter = normalizeString(selectedVoteType);
            console.log(`[VOTE_TYPE_DEBUG] Normalized filter: "${normalizedFilter}"`);
            
            // Enhanced filtering with more logging
            let matchCount = 0;
            const filteredResult = votesToFilter.filter((vote, index) => {
                if (!vote) return false;
                
                // Get the category value (the field we want to filter on)
                const voteCategory = vote.category || '';
                const normalizedCategory = normalizeString(voteCategory);
                
                // Try various matching strategies
                let match = false;
                
                // 1. Exact category match (main filter approach)
                if (normalizedCategory === normalizedFilter) {
                    match = true;
                    console.log(`[VOTE_TYPE_DEBUG] EXACT CATEGORY MATCH for "${voteCategory}"`);
                }
                // 2. Partial match if needed for fuzzy matching
                else if (normalizedCategory.includes(normalizedFilter) || normalizedFilter.includes(normalizedCategory)) {
                    match = true;
                    console.log(`[VOTE_TYPE_DEBUG] PARTIAL CATEGORY MATCH between "${voteCategory}" and "${selectedVoteType}"`);
                }
                // 3. Special case handling
                else if (normalizedFilter === 'bills/resolutions') {
                    match = ['passage', 'passage-suspension', 'legislation'].includes(normalizedCategory);
                }
                
                // Detailed logging for first 10 items regardless of match
                if (index < 10) {
                    console.log(`[VOTE_TYPE_DEBUG] #${index}: Category="${voteCategory}" | Filter="${selectedVoteType}" | Match=${match}`);
                }
                
                if (match) matchCount++;
                return match;
            });
            
            console.log(`[VOTE_TYPE_FILTER] Found ${matchCount} matching votes of type "${selectedVoteType}"`);
            votesToFilter = filteredResult;
        }

        // Filter by Bill Number (using DEBOUNCED value)
        if (filterBillNumber.trim()) {
            const lowerFilterBill = filterBillNumber.trim().toLowerCase();
            votesToFilter = votesToFilter.filter(vote => {
                if (!vote) return false;
                // Check if bill_number exists and is a string before calling includes
                const billNumberMatch = typeof vote.bill_number === 'string' && vote.bill_number.toLowerCase().includes(lowerFilterBill);
                // Check if bill_type exists and is a string before calling includes
                const billTypeMatch = typeof vote.bill_type === 'string' && vote.bill_type.toLowerCase().includes(lowerFilterBill);
                return billNumberMatch || billTypeMatch;
            });
        }

        // Filter by Keyword (using DEBOUNCED value)
        if (filterKeyword.trim()) {
            const lowerFilterKeyword = filterKeyword.trim().toLowerCase();
            votesToFilter = votesToFilter.filter(vote => {
                if (!vote) return false;
                // Check if question exists and is a string before calling includes
                const questionMatch = typeof vote.question === 'string' && vote.question.toLowerCase().includes(lowerFilterKeyword);
                // Check if description exists and is a string before calling includes
                const descriptionMatch = typeof vote.description === 'string' && vote.description.toLowerCase().includes(lowerFilterKeyword);
                return questionMatch || descriptionMatch;
            });
        }
        
        const endTime = performance.now(); // End timing
        console.log(`[VOTE_FILTER] END: Filtering took ${(endTime - startTime).toFixed(2)}ms. Found ${votesToFilter.length} votes.`);
        return votesToFilter;
    }, [voteHistory, selectedVoteYear, selectedVoteType, filterBillNumber, filterKeyword]); // ADD selectedVoteType to dependencies
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

        // Helper to generate Congress.gov link based on vote data
        const generateCongressDotGovLink = (vote) => {
            if (!vote) return null;
            
            // Extract congress number and year from vote_id if available
            let congress = vote.congress;
            let session = vote.session || '1';
            let year = null;
            
            if (vote.vote_id) {
                // Format is often like "h525-109.2005" or similar
                const parts = vote.vote_id.split('-');
                if (parts.length > 1) {
                    const secondPart = parts[1];
                    const congressYearParts = secondPart.split('.');
                    if (congressYearParts.length > 1) {
                        congress = congressYearParts[0];
                        year = congressYearParts[1];
                        // Try to determine session from year
                        if (year) {
                            const yearNum = parseInt(year);
                            const congressStartYear = parseInt(congress) * 2 + 1787;
                            if (yearNum === congressStartYear || yearNum === congressStartYear + 1) {
                                session = (yearNum === congressStartYear) ? '1' : '2';
                            }
                        }
                    }
                }
            }
            
            // If we still don't have congress, try to extract from date
            if (!congress && vote.date) {
                try {
                    year = new Date(vote.date).getFullYear();
                    // Calculate Congress number based on year
                    // Congress starts in odd-numbered years
                    // 1st Congress: 1789-1791, 113th: 2013-2015
                    const estimatedCongress = Math.floor((year - 1789) / 2) + 1;
                    congress = estimatedCongress.toString();
                    
                    // Calculate session number (1 or 2) based on year
                    const congressStartYear = estimatedCongress * 2 + 1787;
                    session = (year === congressStartYear) ? '1' : '2';
                } catch (e) {
                    console.error("Error parsing date for Congress calculation:", e);
                }
            }
            
            // --- PRIORITIZE LINK TYPES BASED ON VOTE DATA ---
            
            // BILL VOTE: HIGHEST PRIORITY FOR "ON PASSAGE" VOTES
            // For votes on bill passages, check first if we have direct bill data
            if (vote.type?.toLowerCase().includes('passage') || 
                vote.question?.toLowerCase().includes('passage') ||
                vote.category === 'passage') {
                
                // If bill data exists directly in vote object
                if (vote.bill && vote.bill.number && vote.bill.type) {
                    const billType = vote.bill.type || '';
                    const billNumber = vote.bill.number || '';
                    const billCongress = vote.bill.congress || congress;
                    
                    if (billCongress && billType && billNumber) {
                        console.log('[LinkGen] Using direct Bill Link for passage vote');
                        return `https://www.congress.gov/bill/${billCongress}th-congress/${getBillTypeForUrl(billType)}/${billNumber}`;
                    }
                }
                
                // Try to extract bill info from question if available
                if (vote.question) {
                    const billInfo = extractBillInfoFromQuestion(vote.question);
                    if (billInfo && billInfo.type && billInfo.number && congress) {
                        console.log('[LinkGen] Using extracted Bill Link from question for passage vote');
                        return `https://www.congress.gov/bill/${congress}th-congress/${getBillTypeForUrl(billInfo.type)}/${billInfo.number}`;
                    }
                }
            }
            
            // DIRECT BILL LINK FOR ANY VOTE WITH BILL INFO
            if (vote.bill && vote.bill.number && vote.bill.type) {
                const billType = vote.bill.type || '';
                const billNumber = vote.bill.number || '';
                const billCongress = vote.bill.congress || congress;
                
                if (billCongress && billType && billNumber) {
                    console.log('[LinkGen] Using direct Bill Link from vote.bill data');
                    return `https://www.congress.gov/bill/${billCongress}th-congress/${getBillTypeForUrl(billType)}/${billNumber}`;
                }
            }
            
            // NOMINATION HANDLING
            if (vote.category === 'nomination' || vote.type?.toLowerCase().includes('nomination')) {
                console.log('[LinkGen] Processing nomination vote:', vote.question);
                
                // Try to extract nomination number from JSON data
                if (vote.nomination && vote.nomination.number && congress) {
                    console.log('[LinkGen] Using Nomination Link from JSON data');
                    return `https://www.congress.gov/nomination/${congress}th-congress/${vote.nomination.number}`;
                }
                
                // Try to extract nomination number from question with improved regex
                if (vote.question) {
                    // Handle formats like "PN11-13" or "PN 11-13" (hyphenated format)
                    const hyphenatedNomMatch = vote.question.match(/PN\s*(\d+)-(\d+)/i);
                    if (hyphenatedNomMatch && hyphenatedNomMatch[1] && hyphenatedNomMatch[2] && congress) {
                        console.log(`[LinkGen] Extracted hyphenated nomination: PN${hyphenatedNomMatch[1]}-${hyphenatedNomMatch[2]}`);
                        // Use the full hyphenated format for URL
                        return `https://www.congress.gov/nomination/${congress}th-congress/${hyphenatedNomMatch[1]}/${hyphenatedNomMatch[2]}`;
                    }
                    
                    // Fallback for standard "PN123" format (single number)
                    const standardNomMatch = vote.question.match(/PN\s*(\d+)(?!-)/i);
                    if (standardNomMatch && standardNomMatch[1] && congress) {
                        console.log(`[LinkGen] Extracted standard nomination: PN${standardNomMatch[1]}`);
                        return `https://www.congress.gov/nomination/${congress}th-congress/${standardNomMatch[1]}`;
                    }
                }
            }
            
            // TREATY HANDLING
            if (vote.category === 'treaty' || vote.type?.toLowerCase().includes('treaty') || vote.question?.toLowerCase().includes('treaty doc')) {
                console.log('[LinkGen] Processing treaty vote:', vote.question);
                
                // Extract treaty doc number from question with improved regex
                if (vote.question) {
                    // Pattern for "Treaty Doc. 117-1" format
                    const treatyMatch = vote.question.match(/Treaty\s+Doc(?:\.|ocument)?\s*(?:No\.?)?\s*(\d+)[-.](\d+)/i);
                    if (treatyMatch && treatyMatch[1] && treatyMatch[2]) {
                        const congressNum = treatyMatch[1];
                        const docNum = treatyMatch[2];
                        console.log(`[LinkGen] Extracted treaty document: congress=${congressNum}, doc=${docNum}`);
                        
                        // Fixed URL format for treaty documents
                        return `https://www.congress.gov/treaty-document/${congressNum}-${docNum}`;
                    }
                    
                    // Alternative pattern for just "Treaty Doc. 5" (single number)
                    const simpleTreatyMatch = vote.question.match(/Treaty\s+Doc(?:\.|ocument)?\s*(?:No\.?)?\s*(\d+)(?!\d*[-.])/i);
                    if (simpleTreatyMatch && simpleTreatyMatch[1] && congress) {
                        console.log(`[LinkGen] Extracted simple treaty document: ${simpleTreatyMatch[1]}`);
                        return `https://www.congress.gov/treaty-document/${congress}-${simpleTreatyMatch[1]}`;
                    }
                }
                
                // Direct link if we have the treaty number in the JSON
                if (vote.treaty && vote.treaty.number && congress) {
                    console.log('[LinkGen] Using Treaty Link from JSON data');
                    
                    // Format treaty number to match Congress.gov expectations
                    let treatyNumberStr = vote.treaty.number.toString();
                    
                    // If it's a simple number and doesn't already contain congress number, add it
                    if (!treatyNumberStr.includes('-') && !treatyNumberStr.includes('.')) {
                        treatyNumberStr = `${congress}-${treatyNumberStr}`;
                    }
                    
                    return `https://www.congress.gov/treaty-document/${treatyNumberStr}`;
                }
                
                // Fallback to roll call vote if we couldn't get a treaty-specific link
                if (congress && vote.chamber && vote.number) {
                    console.log('[LinkGen] Falling back to roll call for treaty vote');
                    const chamber = vote.chamber === 'h' ? 'house' : 'senate';
                    return `https://www.congress.gov/roll-call-vote/${congress}th-congress/${session}/${chamber}/vote-${vote.number}`;
                }
            }
            
            // AMENDMENT HANDLING
            if (vote.category === 'amendment' || vote.type?.toLowerCase().includes('amendment')) {
                if (vote.amendment && vote.amendment.number) {
                    const amendNumber = vote.amendment.number;
                    const chamber = vote.chamber === 'h' ? 'house' : 'senate';
                    console.log('[LinkGen] Using Amendment Link');
                    return `https://www.congress.gov/amendment/${congress}th-congress/${chamber}-amendment/${amendNumber}`;
                }
                
                // Try to extract amendment number from question
                if (vote.question) {
                    const amendMatch = vote.question.match(/(?:H|S)\.?\s*Amdt\.?\s*(\d+)/i);
                    if (amendMatch && amendMatch[1] && congress) {
                        const chamber = vote.question.toLowerCase().startsWith('h') ? 'house' : 'senate';
                        console.log('[LinkGen] Using Amendment Link from question');
                        return `https://www.congress.gov/amendment/${congress}th-congress/${chamber}-amendment/${amendMatch[1]}`;
                    }
                }
            }
            
            // Try to extract bill info from question if we don't have bill data directly
            if (vote.question) {
                const billInfo = extractBillInfoFromQuestion(vote.question);
                if (billInfo && billInfo.type && billInfo.number && congress) {
                    console.log('[LinkGen] Using Bill Link extracted from question text');
                    return `https://www.congress.gov/bill/${congress}th-congress/${getBillTypeForUrl(billInfo.type)}/${billInfo.number}`;
                }
            }
            
            // DIRECT ROLL CALL VOTE LINK
            if (congress && vote.chamber && vote.number) {
                const chamber = vote.chamber === 'h' ? 'house' : 'senate';
                console.log('[LinkGen] Using Roll Call Vote Link');
                return `https://www.congress.gov/roll-call-vote/${congress}th-congress/${session}/${chamber}/vote-${vote.number}`;
            }
            
            // Last resort - if all else fails, link to Congress.gov search
            if (vote.question && congress) {
                const questionText = encodeURIComponent(vote.question);
                console.log('[LinkGen] Fallback to search');
                return `https://www.congress.gov/search?q={"source":"all","congress":"${congress}","search":"${questionText}"}`;
            }
            
            // Absolute fallback
            return "https://www.congress.gov/";
        };
        
        // Helper function to extract bill info from question text
        const extractBillInfoFromQuestion = (questionText) => {
            if (!questionText) return null;
            
            // Match common bill formats WITH or WITHOUT dots
            // Updated regex to match both "H.R. 123" and "H R 123" formats
            const billMatch = questionText.match(/H\.?\s*R\.?\s*(\d+)|S\.?\s*(\d+)|H\.?\s*J\.?\s*Res\.?\s*(\d+)|S\.?\s*J\.?\s*Res\.?\s*(\d+)|H\.?\s*Con\.?\s*Res\.?\s*(\d+)|S\.?\s*Con\.?\s*Res\.?\s*(\d+)|H\.?\s*Res\.?\s*(\d+)|S\.?\s*Res\.?\s*(\d+)/i);
            
            if (billMatch) {
                let billType = '';
                let billNumber = '';
                
                if (billMatch[1]) { 
                    billType = 'hr'; 
                    billNumber = billMatch[1]; 
                } else if (billMatch[2]) { 
                    billType = 's'; 
                    billNumber = billMatch[2]; 
                } else if (billMatch[3]) { 
                    billType = 'hjres'; 
                    billNumber = billMatch[3]; 
                } else if (billMatch[4]) { 
                    billType = 'sjres'; 
                    billNumber = billMatch[4]; 
                } else if (billMatch[5]) { 
                    billType = 'hconres'; 
                    billNumber = billMatch[5]; 
                } else if (billMatch[6]) { 
                    billType = 'sconres';
                    billNumber = billMatch[6]; 
                } else if (billMatch[7]) { 
                    billType = 'hres'; 
                    billNumber = billMatch[7]; 
                } else if (billMatch[8]) { 
                    billType = 'sres'; 
                    billNumber = billMatch[8]; 
                }
                
                if (billType && billNumber) {
                    console.log(`[Bill Extraction] Found bill: ${billType}-${billNumber} in text: "${questionText}"`);
                    return { type: billType, number: billNumber };
                }
            }
            
            // Log failures to help with debugging
            console.log(`[Bill Extraction] Failed to extract bill info from: "${questionText}"`);
            return null;
        }
        
        // Helper to convert bill type to URL format
        const getBillTypeForUrl = (type) => {
            switch (type.toLowerCase()) {
                case 'hr': return 'house-bill';
                case 'hres': return 'house-resolution';
                case 'hjres': return 'house-joint-resolution';
                case 'hconres': return 'house-concurrent-resolution';
                case 's': return 'senate-bill';
                case 'sres': return 'senate-resolution';
                case 'sjres': return 'senate-joint-resolution';
                case 'sconres': return 'senate-concurrent-resolution';
                default: return type;
            }
        };

        // Define the Row component for react-window
        const VoteRow = ({ index, style }) => {
            const vote = filteredVotes[index];
            if (!vote) return null; // Handle potential edge case

            const congressDotGovLink = generateCongressDotGovLink(vote);

            return (
                <ListGroup.Item 
                    key={vote.vote_id || `vote-${index}`}
                    style={style} // Apply style provided by react-window
                    className="vote-item bg-transparent border-secondary text-white"
                >
                    <div className="vote-details mb-1">
                        <span className="vote-date">{new Date(vote.date).toLocaleDateString()}</span>
                        <span className="vote-chamber mx-1">({vote.chamber || 'Chamber N/A'})</span>
                        {/* Display Vote Type */}
                        {vote.type && <Badge bg="secondary" pill className="ms-1 vote-type-badge">{vote.type}</Badge>} 
                        {vote.bill_number && (
                            <span className="vote-bill ms-1">
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
                    <div className="vote-links mt-1 d-flex flex-column">
                        {vote.source_url && (
                            <a href={vote.source_url} target="_blank" rel="noopener noreferrer" className="small text-info mb-1">
                                View Source
                            </a>
                        )}
                        {congressDotGovLink && (
                            <a href={congressDotGovLink} target="_blank" rel="noopener noreferrer" className="small text-info">
                                Detailed Information
                            </a>
                        )}
                    </div>
                </ListGroup.Item>
            );
        };

        const ITEM_HEIGHT = 150; // Estimate average height - adjust as needed!

        return (
            <div className="vote-history-section">
                {/* Filter Row - Always visible */}
                <Row className="mb-3 align-items-end vote-filter-row justify-content-start">
                    {/* Year Filter */}
                    <Col xs={6} md={2} className="mb-2 mb-md-0"> 
                        <Form.Group controlId="voteYearFilter">
                            <Form.Label>Year</Form.Label>
                            <Form.Select 
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
                    </Col>
                    {/* Vote Type Filter (New) */}
                    <Col xs={6} md={2} className="mb-2 mb-md-0">
                        <Form.Group controlId="voteTypeFilter">
                            <Form.Label>Type</Form.Label>
                            <Form.Select 
                                value={selectedVoteType}
                                onChange={(e) => setSelectedVoteType(e.target.value)}
                                aria-label="Filter votes by type"
                            >
                                <option value="All">All Types</option>
                                <option value="nomination">Nominations</option>
                                <option value="passage">Bill Passage</option>
                                <option value="passage-suspension">Suspension</option>
                                <option value="cloture">Cloture</option>
                                <option value="amendment">Amendments</option>
                                <option value="impeachment">Impeachment</option>
                                <option value="procedural">Procedural</option>
                                <option value="treaty">Treaties</option>
                                <option value="veto-override">Veto Override</option>
                                <option value="miscellaneous">Miscellaneous</option>
                            </Form.Select>
                        </Form.Group>
                    </Col>
                    {/* Bill Filter */}
                    <Col xs={12} md={3} className="mb-2 mb-md-0">
                        <Form.Group controlId="voteBillFilter">
                            <Form.Label>Bill Number</Form.Label>
                            <Form.Control 
                                type="text"
                                placeholder="Bill (e.g., HR 22)"
                                value={localFilterBillNumber}
                                onChange={(e) => setLocalFilterBillNumber(e.target.value || '')}
                                aria-label="Filter votes by bill number"
                                name="billFilter"
                                autoComplete="off"
                                role="searchbox"
                            />
                        </Form.Group>
                    </Col>
                    {/* Keyword Filter */}
                    <Col xs={12} md={3} className="mb-2 mb-md-0">
                        <Form.Group controlId="voteKeywordFilter">
                            <Form.Label>Keyword Search</Form.Label>
                            <Form.Control
                                type="text"
                                placeholder="Keyword (in question/desc)"
                                value={localFilterKeyword}
                                onChange={(e) => setLocalFilterKeyword(e.target.value || '')}
                                aria-label="Filter votes by keyword"
                                name="keywordFilter"
                                autoComplete="off"
                                role="searchbox"
                            />
                        </Form.Group>
                    </Col>
                    {/* Clear Button */}
                    <Col xs={12} md={2} className="d-flex align-items-end">
                        <Button 
                            variant="secondary" 
                            onClick={() => {
                                setSelectedVoteYear('All');
                                setSelectedVoteType('All'); // Reset type filter
                                setLocalFilterBillNumber('');
                                setLocalFilterKeyword('');
                            }}
                            className="w-100"
                            aria-label="Clear vote filters"
                        >
                            Clear
                        </Button>
                    </Col>
                </Row>

                {/* Container always visible */}
                <div className="vote-scroll-container">
                    {/* Loading state INSIDE container */}
                    {loadingVotes ? (
                        <div className="text-center my-5 vote-loading-indicator">
                            {/* Wrapper to control ProgressBar width */}
                            <div style={{ maxWidth: '300px', margin: '0 auto' }}> 
                                <ProgressBar 
                                    animated 
                                    now={100} 
                                    label="Loading Votes..." 
                                    visuallyHidden 
                                    style={{ height: '10px' }} 
                                />
                            </div>
                            <p className="mt-2 small text-white-50">Loading Votes...</p>
                        </div>
                    ) : voteError && voteHistory.length === 0 ? (
                        <p className="text-center text-warning small mt-3">{voteError}</p>
                    ) : voteHistory.length > 0 && filteredVotes.length === 0 ? (
                        <p className="text-center text-white-50 small mt-3">No votes found matching filters.</p> /* Updated message */
                    ) : voteHistory.length === 0 && !voteError ? (
                        <p className="text-center text-white-50 small mt-3">No vote history available for this member.</p> /* Handle case with 0 initial votes */
                    ) : (
                        /* Replace direct map with FixedSizeList */
                        <FixedSizeList
                            height={450} /* Match container height from CSS */
                            itemCount={filteredVotes.length}
                            itemSize={ITEM_HEIGHT} /* Use estimated item height */
                            width={'100%'} /* Take full width */
                            className="vote-list no-scrollbar" /* Add no-scrollbar class */
                            style={{
                                overflowY: 'visible', /* Make inner scrollbar invisible */
                                overflowX: 'hidden'
                            }}
                        >
                            {VoteRow} 
                        </FixedSizeList>
                    )}
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

        // Log member details right before rendering the card header
        console.log("[renderMemberProfile] Rendering card header. Member data:", member);
        console.log("[renderMemberProfile] member.member_type:", member?.member_type);
        console.log("[renderMemberProfile] member.state_rank:", member?.state_rank);
        console.log("[renderMemberProfile] member.district:", member?.district);

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
                                    {/* Explicit check for Rep type */}
                                    {(member.member_type === 'rep' || member.member_type === 'representative') && member.district && (
                                        ` - District ${member.district}`
                                    )}
                                    {/* Explicit check for Sen type and state_rank */}
                                    {(member.member_type === 'sen' || member.member_type === 'senator') && member.state_rank && (
                                        ` - ${member.state_rank.charAt(0).toUpperCase() + member.state_rank.slice(1)} Senator`
                                    )}
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
                        
                        {/* === Right Column: Contains Info and Committees === */}
                        <Col md={8}>
                           <Row className="h-100"> {/* Nested row */}
                               {/* === Nested Left: General Information === */}
                               <Col md={6} className="mb-4 mb-md-0 d-flex flex-column">
                                   <div className="flex-grow-1 general-info-section"> {/* Added class */}
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
                               
                               {/* === Nested Right: Committee Assignments === */}
                               <Col md={6} className="d-flex flex-column">
                                   <div className="flex-grow-1 committee-section"> {/* Use existing class or make new one */}
                                       {uniqueSubcommittees && uniqueSubcommittees.length > 0 ? (
                                           <>
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
                                           </> 
                                       ) : (
                                           <div className="text-center text-white-50 my-4">
                                               No current committee assignments found.
                                           </div>
                                       )}
                                   </div>
                               </Col>
                           </Row> {/* End Nested Row */}
                        </Col> {/* End Right Column */}
                    </Row>
                    
                    {/* --- Vote History Row (Full Width) --- */}
                    <Row className="mt-0"> {/* Changed from mt-3 to mt-0 to remove top margin */}
                        <Col xs={12}>
                            <ErrorBoundary>
                                {renderVoteHistory()} 
                            </ErrorBoundary>
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