import React from 'react';

const Dashboard = ({ children }) => {
  return (
    <div className="dashboard">
      <h2>Container Yard Dashboard</h2>
      {children}
    </div>
  );
};

export default Dashboard;
