import React from 'react';

const Dashboard = ({ children }) => {
  return (
    <div className="dashboard">
      <div className="dashboard-left">{children[0]}</div>
      <div className="dashboard-right">
        {children.slice(1)}
      </div>
    </div>
  );
};

export default Dashboard;
