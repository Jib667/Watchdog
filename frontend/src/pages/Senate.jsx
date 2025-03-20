import { useState } from 'react';
import './Senate.css';

const Senate = () => {
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
    <div className="senate-page">
      <header className="page-header">
        <h1>United States <span className="highlight">Senate</span></h1>
        <p>Select a state to view its senators</p>
      </header>

      <div className="content-wrapper">
        <aside className="filters">
          <h3>Filter Senators</h3>
          
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

        <main className="senators-display">
          <div className="us-map-container">
            <p>Interactive US Map will be displayed here</p>
            {/* In a real implementation, we would include an interactive SVG map here */}
          </div>

          <section className="senators-list">
            <h2>Senators</h2>
            <p className="placeholder-message">
              Select a state on the map or use the filters to view senators.
            </p>
            
            {/* Senator cards would be displayed here based on selection */}
          </section>
        </main>
      </div>
    </div>
  );
};

export default Senate; 