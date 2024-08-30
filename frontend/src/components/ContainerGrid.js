import React, { useState } from 'react';

const ContainerGrid = ({ containers, onRemoveContainer, onManualPlace }) => {
  const [selectedContainer, setSelectedContainer] = useState(null);
  const gridSize = { x: 10, y: 10, z: 5 }; // Adjust based on your yard configuration

  const handleContainerClick = (container) => {
    setSelectedContainer(container);
  };

  const handleCellClick = (x, y, z) => {
    if (selectedContainer) {
      onManualPlace(selectedContainer.id, { x, y, z });
      setSelectedContainer(null);
    }
  };

  const renderGrid = () => {
    const grid = [];
    for (let z = 0; z < gridSize.z; z++) {
      const layer = [];
      for (let y = 0; y < gridSize.y; y++) {
        const row = [];
        for (let x = 0; x < gridSize.x; x++) {
          const container = containers.find(c => c.position.x === x && c.position.y === y && c.position.z === z);
          row.push(
            <div
              key={`${x}-${y}-${z}`}
              className={`cell ${container ? 'occupied' : 'empty'} ${selectedContainer ? 'selectable' : ''}`}
              onClick={() => handleCellClick(x, y, z)}
            >
              {container && container.id}
            </div>
          );
        }
        layer.push(<div key={`${y}-${z}`} className="row">{row}</div>);
      }
      grid.push(<div key={z} className="layer">{layer}</div>);
    }
    return grid;
  };

  return (
    <div className="container-grid">
      <h3>Container Yard Visualization</h3>
      <div className="grid-3d">{renderGrid()}</div>
      <div className="container-list">
        <h4>Container List</h4>
        {containers.map(container => (
          <div key={container.id} className={`container-item ${selectedContainer === container ? 'selected' : ''}`}>
            <span onClick={() => handleContainerClick(container)}>{container.id}</span>
            <span>Position: ({container.position.x}, {container.position.y}, {container.position.z})</span>
            <button onClick={() => onRemoveContainer(container.id)}>Remove</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ContainerGrid;
