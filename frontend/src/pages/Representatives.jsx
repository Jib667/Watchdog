import { useState } from 'react';
import './Representatives.css';

const Representatives = () => {
  const [selectedState, setSelectedState] = useState('');
  
  // This would be fetched from the API in a real implementation
  const states = [
    { code: 'AL', name: 'Alabama' },
    { code: 'AK', name: 'Alaska' },
    { code: 'AZ', name: 'Arizona' },
    // ... other states would be included
    { code: 'WY', name: 'Wyoming' },
  ];

  return (
    <div className="representatives-page">
      <header className="page-header">
        <h1>House of <span className="highlight">Representatives</span></h1>
        <p>Select a state to view its representatives</p>
      </header>

      <div className="content-wrapper">
        <aside className="filters">
          <h3>Filter Representatives</h3>
          
          <div className="filter-group">
            <label htmlFor="state-select">State:</label>
            <select 
              id="state-select"
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
            >
              <option value="">All States</option>
              {states.map((state) => (
                <option key={state.code} value={state.code}>
                  {state.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label htmlFor="party-select">Party:</label>
            <select id="party-select">
              <option value="">All Parties</option>
              <option value="democratic">Democratic</option>
              <option value="republican">Republican</option>
              <option value="independent">Independent</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label htmlFor="committee-select">Committee:</label>
            <select id="committee-select">
              <option value="">All Committees</option>
              <option value="agriculture">Agriculture</option>
              <option value="appropriations">Appropriations</option>
              <option value="armed-services">Armed Services</option>
              {/* Add more committees */}
            </select>
          </div>
        </aside>

        <main className="representatives-display">
          <div className="us-map-container">
            <p>Interactive US Map will be displayed here</p>
            {/* In a real implementation, we would include an interactive SVG map here */}
          </div>

          <section className="representatives-list">
            <h2>Representatives</h2>
            <p className="placeholder-message">
              Select a state on the map or use the filters to view representatives.
            </p>
            
            {/* Representative cards would be displayed here based on selection */}
          </section>
        </main>
      </div>
    </div>
  );
};

export default Representatives; 