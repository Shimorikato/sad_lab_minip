import React from 'react';
import './App.css';
import TrafficGraph from './TrafficGraph';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚦 Traffic Management System</h1>
        <p>Real-time traffic density visualization</p>
      </header>
      <main className="App-main">
        <TrafficGraph />
      </main>
    </div>
  );
}

export default App;
