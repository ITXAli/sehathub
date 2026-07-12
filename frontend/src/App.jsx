import { useState } from 'react';
import { Stethoscope, Activity, FileText, Microscope, Utensils } from 'lucide-react';
import TriageTab from './features/Triage/TriageTab';
import MediScanTab from './features/MediScan/MediScanTab';
import LabSenseTab from './features/LabSense/LabSenseTab';
import NutriScanTab from './features/NutriScan/NutriScanTab';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('triage');
  const [isOffline, setIsOffline] = useState(true);

  const renderTabContent = () => {
    switch(activeTab) {
      case 'triage': return <TriageTab isOffline={isOffline} />;
      case 'mediscan': return <MediScanTab isOffline={isOffline} />;
      case 'labsense': return <LabSenseTab isOffline={isOffline} />;
      case 'nutriscan': return <NutriScanTab isOffline={isOffline} />;
      default: return <TriageTab isOffline={isOffline} />;
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo">
          <div className="logo-icon">
            <Stethoscope size={28} />
          </div>
          SehatHub AI
        </div>

        <div className="toggle-container">
          <span style={{ color: isOffline ? 'var(--primary-color)' : 'var(--text-secondary)' }}>
            Gemma Edge (Offline)
          </span>
          <label className="switch">
            <input 
              type="checkbox" 
              checked={!isOffline} 
              onChange={() => setIsOffline(!isOffline)} 
            />
            <span className="slider"></span>
          </label>
          <span style={{ color: !isOffline ? 'var(--secondary-color)' : 'var(--text-secondary)' }}>
            Gemma Cloud (Online)
          </span>
        </div>
      </header>

      <div className="tabs">
        <button 
          className={`tab-btn ${activeTab === 'triage' ? 'active' : ''}`}
          onClick={() => setActiveTab('triage')}
        >
          <Activity size={18} /> SehatTriage
        </button>
        <button 
          className={`tab-btn ${activeTab === 'mediscan' ? 'active' : ''}`}
          onClick={() => setActiveTab('mediscan')}
        >
          <FileText size={18} /> MediScan
        </button>
        <button 
          className={`tab-btn ${activeTab === 'labsense' ? 'active' : ''}`}
          onClick={() => setActiveTab('labsense')}
        >
          <Microscope size={18} /> LabSense
        </button>
        <button 
          className={`tab-btn ${activeTab === 'nutriscan' ? 'active' : ''}`}
          onClick={() => setActiveTab('nutriscan')}
        >
          <Utensils size={18} /> NutriScan
        </button>
      </div>

      <main className="tab-content">
        {renderTabContent()}
      </main>
    </div>
  );
}

export default App;
