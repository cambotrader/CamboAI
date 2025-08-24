import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, CategoryScale, LinearScale } from 'chart.js';
import ModuleTogglePanel from './components/ModuleTogglePanel';
import './App.css';

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale);

const data = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  datasets: [
    {
      label: 'Sample Trade Signal',
      data: [120, 135, 128, 145, 138],
      borderColor: '#007bff',
      backgroundColor: 'rgba(0, 123, 255, 0.2)',
      tension: 0.4,
    },
  ],
};

function App() {
  const [activeTab, setActiveTab] = useState<'chart' | 'modules'>('modules');

  return (
    <div className="app-container">
      <nav className="app-nav">
        <div className="nav-brand">
          <h1>🚀 Cambo AI Trader Station</h1>
        </div>
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'modules' ? 'active' : ''}`}
            onClick={() => setActiveTab('modules')}
          >
            🔧 Module Control
          </button>
          <button 
            className={`nav-tab ${activeTab === 'chart' ? 'active' : ''}`}
            onClick={() => setActiveTab('chart')}
          >
            📊 Chart View
          </button>
        </div>
      </nav>

      <main className="app-main">
        {activeTab === 'modules' && <ModuleTogglePanel />}
        {activeTab === 'chart' && (
          <div className="chart-container">
            <h2>Cambo AI Chart Module</h2>
            <Line data={data} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
