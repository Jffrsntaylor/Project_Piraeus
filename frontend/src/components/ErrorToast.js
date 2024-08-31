import React from 'react';

const ErrorToast = ({ message, onClose }) => (
  <div className="error-toast">
    <p>{message}</p>
    <button onClick={onClose}>×</button>
  </div>
);

export default ErrorToast;
