import axios from 'axios';

// Base URL for API requests
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';

// Configure axios with base URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Fetch all representatives
export const fetchRepresentatives = async () => {
  try {
    // For now, use mock data until backend is fully implemented
    return MOCK_REPRESENTATIVES;
  } catch (error) {
    console.error('Error fetching representatives:', error);
    throw error;
  }
};

// Fetch representatives by state
export const fetchStateRepresentatives = async (state) => {
  try {
    // For now, filter mock data
    return MOCK_REPRESENTATIVES.filter(rep => rep.state === state);
  } catch (error) {
    console.error(`Error fetching representatives for state ${state}:`, error);
    throw error;
  }
};

// Fetch all senators
export const fetchSenators = async () => {
  try {
    // For now, use mock data until backend is fully implemented
    return MOCK_SENATORS;
  } catch (error) {
    console.error('Error fetching senators:', error);
    throw error;
  }
};

// Fetch senators by state
export const fetchStateSenators = async (stateName) => {
  try {
    // For now, filter mock data
    return MOCK_SENATORS.filter(senator => senator.state_name === stateName);
  } catch (error) {
    console.error(`Error fetching senators for state ${stateName}:`, error);
    throw error;
  }
};

// Mock data for development purposes
const MOCK_REPRESENTATIVES = [
  {
    id: 'R000603',
    name: 'Tom Reed',
    state: 'NY',
    district: '23',
    party: 'R',
    office: '2263 Rayburn House Office Building',
    phone: '202-225-3161',
    website: 'https://reed.house.gov',
    photo_url: 'https://www.congress.gov/img/member/r000603.jpg',
  },
  {
    id: 'W000187',
    name: 'Maxine Waters',
    state: 'CA',
    district: '43',
    party: 'D',
    office: '2221 Rayburn House Office Building',
    phone: '202-225-2201',
    website: 'https://waters.house.gov',
    photo_url: 'https://www.congress.gov/img/member/w000187.jpg',
  },
  {
    id: 'O000172',
    name: 'Alexandria Ocasio-Cortez',
    state: 'NY',
    district: '14',
    party: 'D',
    office: '216 Cannon House Office Building',
    phone: '202-225-3965',
    website: 'https://ocasio-cortez.house.gov',
    photo_url: 'https://www.congress.gov/img/member/o000172.jpg',
  },
  {
    id: 'C001084',
    name: 'Dan Crenshaw',
    state: 'TX',
    district: '2',
    party: 'R',
    office: '412 Cannon House Office Building',
    phone: '202-225-6565',
    website: 'https://crenshaw.house.gov',
    photo_url: 'https://www.congress.gov/img/member/c001084.jpg',
  },
  {
    id: 'S001199',
    name: 'Adam Schiff',
    state: 'CA',
    district: '28',
    party: 'D',
    office: '2309 Rayburn House Office Building',
    phone: '202-225-4176',
    website: 'https://schiff.house.gov',
    photo_url: 'https://www.congress.gov/img/member/s001199.jpg',
  },
  {
    id: 'J000294',
    name: 'Jim Jordan',
    state: 'OH',
    district: '4',
    party: 'R',
    office: '2056 Rayburn House Office Building',
    phone: '202-225-2676',
    website: 'https://jordan.house.gov',
    photo_url: 'https://www.congress.gov/img/member/j000289.jpg',
  },
  {
    id: 'P000593',
    name: 'Nancy Pelosi',
    state: 'CA',
    district: '12',
    party: 'D',
    office: 'H-222 The Capitol',
    phone: '202-225-4965',
    website: 'https://pelosi.house.gov',
    photo_url: 'https://www.congress.gov/img/member/p000560.jpg',
  },
  {
    id: 'M001193',
    name: 'Kevin McCarthy',
    state: 'CA',
    district: '23',
    party: 'R',
    office: 'H-204 The Capitol',
    phone: '202-225-2915',
    website: 'https://kevinmccarthy.house.gov',
    photo_url: 'https://www.congress.gov/img/member/m001156.jpg',
  },
];

const MOCK_SENATORS = [
  {
    id: 'S000148',
    name: 'Bernie Sanders',
    state: 'VT',
    state_name: 'Vermont',
    party: 'I',
    class: '1',
    office: '332 Dirksen Senate Office Building',
    phone: '202-224-5141',
    website: 'https://www.sanders.senate.gov',
    photo_url: 'https://www.congress.gov/img/member/s000033.jpg',
  },
  {
    id: 'W000805',
    name: 'Elizabeth Warren',
    state: 'MA',
    state_name: 'Massachusetts',
    party: 'D',
    class: '1',
    office: '317 Hart Senate Office Building',
    phone: '202-224-4543',
    website: 'https://www.warren.senate.gov',
    photo_url: 'https://www.congress.gov/img/member/w000817.jpg',
  },
  {
    id: 'S001197',
    name: 'Marco Rubio',
    state: 'FL',
    state_name: 'Florida',
    party: 'R',
    class: '3',
    office: '284 Russell Senate Office Building',
    phone: '202-224-3041',
    website: 'https://www.rubio.senate.gov',
    photo_url: 'https://www.congress.gov/img/member/r000595.jpg',
  },
  {
    id: 'S001141',
    name: 'Charles Schumer',
    state: 'NY',
    state_name: 'New York',
    party: 'D',
    class: '3',
    office: '322 Hart Senate Office Building',
    phone: '202-224-6542',
    website: 'https://www.schumer.senate.gov',
    photo_url: 'https://www.congress.gov/img/member/s000148.jpg',
  },
  {
    id: 'M000355',
    name: 'Mitch McConnell',
    state: 'KY',
    state_name: 'Kentucky',
    party: 'R',
    class: '2',
    office: '317 Russell Senate Office Building',
    phone: '202-224-2541',
    website: 'https://www.mcconnell.senate.gov',
    photo_url: 'https://www.congress.gov/img/member/m000355.jpg',
  },
  {
    id: 'C001047',
    name: 'Ted Cruz',
    state: 'TX',
    state_name: 'Texas',
    party: 'R',
    class: '1',
    office: '127A Russell Senate Office Building',
    phone: '202-224-5922',
    website: 'https://www.cruz.senate.gov',
    photo_url: 'https://www.congress.gov/img/member/c001098.jpg',
  },
  {
    id: 'B001230',
    name: 'Cory Booker',
    state: 'NJ',
    state_name: 'New Jersey',
    party: 'D',
    class: '2',
    office: '359 Dirksen Senate Office Building',
    phone: '202-224-3224',
    website: 'https://www.booker.senate.gov',
    photo_url: 'https://www.congress.gov/img/member/b001288.jpg',
  },
  {
    id: 'H001076',
    name: 'Kamala Harris',
    state: 'CA',
    state_name: 'California',
    party: 'D',
    class: '3',
    office: '112 Hart Senate Office Building',
    phone: '202-224-3553',
    website: 'https://www.harris.senate.gov',
    photo_url: 'https://www.congress.gov/img/member/h001075.jpg',
  },
];

export default api; 