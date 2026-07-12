const API_URL = 'http://localhost:8000/api';

export const triageSymptoms = async (symptoms, isOffline) => {
  const response = await fetch(`${API_URL}/triage/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symptoms, is_offline: isOffline })
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'API Error');
  }
  return response.json();
};

export const processMediScan = async (file, isOffline) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('is_offline', isOffline);
  const response = await fetch(`${API_URL}/mediscan/`, {
    method: 'POST',
    body: formData
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'API Error');
  }
  return response.json();
};

export const processLabSense = async (file, isOffline) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('is_offline', isOffline);
  const response = await fetch(`${API_URL}/labsense/`, {
    method: 'POST',
    body: formData
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'API Error');
  }
  return response.json();
};

export const processNutriScan = async (file, isOffline) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('is_offline', isOffline);
  const response = await fetch(`${API_URL}/nutriscan/`, {
    method: 'POST',
    body: formData
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'API Error');
  }
  return response.json();
};
