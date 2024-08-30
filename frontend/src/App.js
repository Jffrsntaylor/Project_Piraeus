import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import ContainerGrid from './components/ContainerGrid';
import MetricsDisplay from './components/MetricsDisplay';
import LogDisplay from './components/LogDisplay';
import TrainingProgress from './components/TrainingProgress';
import './App.css';

function App() {
  const [containers, setContainers] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [logs, setLogs] = useState([]);
  const [trainingProgress, setTrainingProgress] = useState({});
  const [logsError, setLogsError] = useState(null);
  const [trainingProgressError, setTrainingProgressError] = useState(null);

  useEffect(() => {
    fetchData();
    fetchLogs();
    fetchTrainingProgress();
    const interval = setInterval(() => {
      fetchLogs();
      fetchTrainingProgress();
    }, 5000); // Fetch logs and training progress every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [containersResponse, metricsResponse] = await Promise.all([
        axios.get('/containers'),
        axios.get('/metrics')
      ]);
      setContainers(containersResponse.data);
      setMetrics(metricsResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('An error occurred while fetching data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const removeContainer = async (containerId) => {
    try {
      await axios.post(`/remove_container/${containerId}`);
      fetchData();
    } catch (error) {
      console.error('Error removing container:', error);
      setError('An error occurred while removing the container. Please try again.');
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
      try {
        await axios.post('/upload_csv', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        fetchData();
      } catch (error) {
        console.error('Error uploading CSV:', error);
        setError('An error occurred while uploading the CSV file. Please try again.');
      }
    }
  };

  const manualPlaceContainer = async (containerId, position) => {
    try {
      await axios.post(`/manual_place_container/${containerId}`, position);
      fetchData();
    } catch (error) {
      console.error('Error manually placing container:', error);
      setError('An error occurred while manually placing the container. Please try again.');
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await axios.get('/logs');
      setLogs(response.data);
      setLogsError(null);
    } catch (error) {
      console.error('Error fetching logs:', error);
      setLogsError('Failed to fetch logs. Please try again later.');
    }
  };

  const fetchTrainingProgress = async () => {
    try {
      const response = await axios.get('/training_progress');
      setTrainingProgress(response.data);
      setTrainingProgressError(null);
    } catch (error) {
      console.error('Error fetching training progress:', error);
      setTrainingProgressError('Failed to fetch training progress. Please try again later.');
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Eco-Friendly Container Yard Management</h1>
        <div className="file-upload">
          <label htmlFor="csv-upload" className="file-upload-label">Upload CSV</label>
          <input id="csv-upload" type="file" accept=".csv" onChange={handleFileUpload} />
        </div>
      </header>
      <Dashboard>
        <ContainerGrid
          containers={containers}
          onRemoveContainer={removeContainer}
          onManualPlace={manualPlaceContainer}
        />
        <MetricsDisplay metrics={metrics} />
        <TrainingProgress progress={trainingProgress} error={trainingProgressError} />
        <LogDisplay logs={logs} error={logsError} />
      </Dashboard>
    </div>
  );
}

export default App;
