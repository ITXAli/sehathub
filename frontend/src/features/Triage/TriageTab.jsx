import { useState } from 'react';
import { Activity, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { triageSymptoms } from '../../services/api';

export default function TriageTab({ isOffline }) {
  const [symptoms, setSymptoms] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!symptoms) return;
    setLoading(true);
    setError('');
    try {
      const data = await triageSymptoms(symptoms, isOffline);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze symptoms.');
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyBadge = (urgency) => {
    switch(urgency.toLowerCase()) {
      case 'high': return <span className="badge badge-high"><AlertTriangle size={14} className="inline mr-1" /> High Urgency</span>;
      case 'medium': return <span className="badge badge-medium"><Activity size={14} className="inline mr-1" /> Medium Urgency</span>;
      default: return <span className="badge badge-low"><CheckCircle2 size={14} className="inline mr-1" /> Routine</span>;
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Activity color="var(--primary-color)" /> SehatTriage
      </h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        Enter patient symptoms for offline, instant AI triage and action steps.
      </p>
      
      <div className="input-group">
        <label>Patient Symptoms</label>
        <textarea 
          rows="4" 
          placeholder="e.g., high fever, joint pain, rash for 3 days"
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
        />
      </div>

      <button className="btn" onClick={handleAnalyze} disabled={loading || !symptoms}>
        {loading ? <span className="loading"><Activity className="spinner" size={20} /> Analyzing...</span> : 'Analyze Symptoms'}
      </button>

      {error && <p style={{ color: 'var(--danger-color)', marginTop: '1rem' }}>{error}</p>}

      {result && (
        <div className="result-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3>Triage Result</h3>
            {getUrgencyBadge(result.urgency)}
          </div>
          <h4>Immediate Action Steps:</h4>
          <ul style={{ paddingLeft: '1.5rem', marginTop: '0.5rem', color: 'var(--text-secondary)' }}>
            {result.action_steps.map((step, idx) => (
              <li key={idx} style={{ marginBottom: '0.25rem' }}>{step}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
