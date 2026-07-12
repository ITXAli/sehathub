import { useState, useRef } from 'react';
import { UploadCloud } from 'lucide-react';

export default function ImageUploader({ onImageSelected }) {
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setPreview(url);
      onImageSelected(file);
    }
  };

  return (
    <div 
      className="upload-zone" 
      onClick={() => fileInputRef.current.click()}
    >
      <input 
        type="file" 
        accept="image/*" 
        style={{ display: 'none' }} 
        ref={fileInputRef}
        onChange={handleFileChange}
      />
      
      {!preview ? (
        <>
          <UploadCloud className="upload-icon" />
          <h4>Click or Drag to Upload</h4>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', fontSize: '0.875rem' }}>
            Supports JPG, PNG, WEBP
          </p>
        </>
      ) : (
        <div>
          <p style={{ fontWeight: '500', marginBottom: '1rem', color: 'var(--primary-color)' }}>Image Selected (Click to change)</p>
          <img src={preview} alt="Preview" className="file-preview" />
        </div>
      )}
    </div>
  );
}
