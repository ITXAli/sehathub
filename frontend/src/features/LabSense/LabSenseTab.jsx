import { useState } from 'react';
import { Microscope, Loader2 } from 'lucide-react';
import ImageUploader from '../../components/ImageUploader';
import { processLabSense } from '../../services/api';

export default function LabSenseTab({ isOffline }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleProcess = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const data = await processLabSense(file, isOffline);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to process lab report.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Microscope color="var(--primary-color)" /> LabSense
      </h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        Upload a blood test report. Gemma 4 Vision identifies out-of-range markers and explains them simply.
      </p>

      <ImageUploader onImageSelected={setFile} />

      <button className="btn" onClick={handleProcess} disabled={loading || !file}>
        {loading ? <span className="loading"><Loader2 className="spinner" size={20} /> Analyzing Report...</span> : 'Analyze Lab Report'}
      </button>

      {error && <p style={{ color: 'var(--danger-color)', marginTop: '1rem' }}>{error}</p>}

      {result && (
        <div className="result-card">
          <h3>Lab Analysis</h3>
          <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>{result.summary_explanation}</p>
          
          <h4 style={{ marginBottom: '0.5rem' }}>Out of Range Biomarkers</h4>
          <div style={{ display: 'grid', gap: '0.75rem', marginBottom: '1.5rem' }}>
            {result.out_of_range_biomarkers.map((marker, idx) => (
              <div key={idx} style={{ padding: '0.75rem', backgroundColor: 'white', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: '500' }}>{marker.name}</span>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{marker.value}</span>
                  <span className={`badge ${marker.status.toLowerCase() === 'high' ? 'badge-high' : 'badge-medium'}`}>
                    {marker.status}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div style={{ padding: '1rem', backgroundColor: '#e0f2fe', borderRadius: 'var(--radius-md)' }}>
            <h4 style={{ color: '#0369a1', marginBottom: '0.25rem' }}>Dietary Advice</h4>
            <p style={{ color: '#0c4a6e', fontSize: '0.95rem' }}>{result.dietary_advice}</p>
          </div>
        </div>
      )}
    </div>
  );
}
