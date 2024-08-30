import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import ContainerGrid from './components/ContainerGrid';
import MetricsDisplay from './components/MetricsDisplay';

function App() {
  const [containers, setContainers] = useState([]);
  const [metrics, setMetrics] = useState({});

  useEffect(() => {
    // Fetch initial data from backend
    // This is a placeholder and should be replaced with actual API calls
    fetchContainers();
    fetchMetrics();
  }, []);

  const fetchContainers = () => {
    // Placeholder for API call to get containers
    setContainers([
      { id: 'C001', position: { x: 0, y: 0, z: 0 } },
      { id: 'C002', position: { x: 1, y: 0, z: 0 } },
      // ... more containers
    ]);
  };

  const fetchMetrics = () => {
    // Placeholder for API call to get metrics
    setMetrics({
      totalContainers: 100,
      totalMoves: 500,
      optimizedMoves: 400,
      moneySaved: 1000,
      efficiencyIncrease: 20,
      carbonReduction: 500
    });
  };

  const removeContainer = (containerId) => {
    // Placeholder for API call to remove container
    setContainers(containers.filter(c => c.id !== containerId));
    // After removing, we should re-fetch metrics
    fetchMetrics();
  };

  return (
    <div className="App">
      <h1>Eco-Friendly Container Yard Management</h1>
      <Dashboard>
        <ContainerGrid containers={containers} onRemoveContainer={removeContainer} />
        <MetricsDisplay metrics={metrics} />
      </Dashboard>
    </div>
  );
}

export default App;
