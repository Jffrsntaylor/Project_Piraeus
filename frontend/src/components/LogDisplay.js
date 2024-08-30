import React from 'react';

const LogDisplay = ({ logs, error }) => {
  return (
    <div className="log-display">
      <h3>System Logs</h3>
      {error ? (
        <p className="error">{error}</p>
      ) : (
        <pre>
          {logs.join('\n')}
        </pre>
      )}
    </div>
  );
};

export default LogDisplay;
