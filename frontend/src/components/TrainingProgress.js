import React from 'react';

const TrainingProgress = ({ progress, error }) => {
  return (
    <div className="training-progress">
      <h3>Training Progress</h3>
      {error ? (
        <p className="error">{error}</p>
      ) : (
        <ul>
          <li>Episodes: {progress.episodes}</li>
          <li>Epsilon: {progress.epsilon?.toFixed(4)}</li>
          <li>Loss: {progress.loss?.toFixed(4)}</li>
          <li>Accuracy: {progress.accuracy?.toFixed(4)}</li>
        </ul>
      )}
    </div>
  );
};

export default TrainingProgress;
