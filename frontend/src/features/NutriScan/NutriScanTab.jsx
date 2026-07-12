import { useState } from 'react';
import { Utensils, Loader2 } from 'lucide-react';
import ImageUploader from '../../components/ImageUploader';
import { processNutriScan } from '../../services/api';

export default function NutriScanTab({ isOffline }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleProcess = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const data = await processNutriScan(file, isOffline);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to process food image.');
    } finally {
      setLoading(false);
    }
  };

  const getSafetyBadge = (score) => {
    const s = score.toLowerCase();
    if (s.includes('high')) return <span className="badge badge-high">{score}</span>;
    if (s.includes('medium')) return <span className="badge badge-medium">{score}</span>;
    return <span className="badge badge-low">{score}</span>;
  }

  return (
    <div>
      <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Utensils color="var(--primary-color)" /> NutriScan (Cal AI)
      </h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        Upload a photo of local food. Gemma 4 Vision estimates macros and provides a diabetic safety score.
      </p>

      <ImageUploader onImageSelected={setFile} />

      <button className="btn" onClick={handleProcess} disabled={loading || !file}>
        {loading ? <span className="loading"><Loader2 className="spinner" size={20} /> Analyzing Food...</span> : 'Analyze Meal'}
      </button>

      {error && <p style={{ color: 'var(--danger-color)', marginTop: '1rem' }}>{error}</p>}

      {result && (
        <div className="result-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div>
              <h3>{result.food_identified}</h3>
              <p style={{ color: 'var(--text-secondary)' }}>Estimated Calories: <strong>{result.estimated_calories} kcal</strong></p>
            </div>
            {getSafetyBadge(result.glycemic_safety_score)}
          </div>
          
          <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
            <h4 style={{ marginBottom: '0.25rem' }}>Dietary Advice</h4>
            <p style={{ color: 'var(--text-secondary)' }}>{result.advice}</p>
          </div>
        </div>
      )}
    </div>
  );
}
