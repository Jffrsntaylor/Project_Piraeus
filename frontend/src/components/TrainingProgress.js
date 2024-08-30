import React from 'react';

const TrainingProgress = ({ progress, error }) => {
  return (
    <div className="training-progress">
      <h3>Training Progress</h3>
      {error ? (
        <p className="error">{error}</p>
      ) : (
        <ul>
          <li><strong>Episodes:</strong> {progress.episodes}</li>
          <li><strong>Epsilon:</strong> {progress.epsilon?.toFixed(4)}</li>
          <li><strong>Loss:</strong> {progress.loss?.toFixed(4)}</li>
          <li><strong>Accuracy:</strong> {progress.accuracy?.toFixed(4)}</li>
        </ul>
      )}
    </div>
  );
};

export default TrainingProgress;
