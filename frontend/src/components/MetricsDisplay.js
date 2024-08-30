import React from 'react';

const MetricsDisplay = ({ metrics }) => {
  return (
    <div className="metrics-display">
      <h3>Yard Metrics</h3>
      <ul>
        <li>Total Containers: {metrics.totalContainers}</li>
        <li>Total Moves: {metrics.totalMoves}</li>
        <li>Optimized Moves: {metrics.optimizedMoves}</li>
        <li>Money Saved: ${metrics.moneySaved}</li>
        <li>Efficiency Increase: {metrics.efficiencyIncrease}%</li>
        <li>Carbon Reduction: {metrics.carbonReduction} kg CO2</li>
      </ul>
    </div>
  );
};

export default MetricsDisplay;
