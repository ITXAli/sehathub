import { useState } from 'react';
import { FileText, Loader2 } from 'lucide-react';
import ImageUploader from '../../components/ImageUploader';
import { processMediScan } from '../../services/api';

export default function MediScanTab({ isOffline }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleProcess = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const data = await processMediScan(file, isOffline);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to process prescription.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <FileText color="var(--primary-color)" /> MediScan
      </h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        Upload a handwritten prescription. Gemma 4 Vision translates it into a clear, structured dosage card.
      </p>

      <ImageUploader onImageSelected={setFile} />

      <button className="btn" onClick={handleProcess} disabled={loading || !file}>
        {loading ? <span className="loading"><Loader2 className="spinner" size={20} /> Processing...</span> : 'Translate Prescription'}
      </button>

      {error && <p style={{ color: 'var(--danger-color)', marginTop: '1rem' }}>{error}</p>}

      {result && result.medicines && result.medicines.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3 style={{ marginBottom: '-0.5rem' }}>Extracted Prescription ({result.medicines.length} Medicines)</h3>
          {result.medicines.map((med, index) => (
            <div key={index} className="result-card">
              <h4 style={{ color: 'var(--primary-color)', fontSize: '1.25rem', marginBottom: '1rem' }}>{med.medicine_name}</h4>
              <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: '1fr 1fr' }}>
                <div>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Dosage</p>
                  <p style={{ fontWeight: '600', fontSize: '1.125rem' }}>{med.dosage}</p>
                </div>
                <div>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Timing</p>
                  <p style={{ fontWeight: '600', fontSize: '1.125rem' }}>{med.timing}</p>
                </div>
              </div>
              <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Instructions</p>
                <p style={{ fontWeight: '500' }}>{med.instructions}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
