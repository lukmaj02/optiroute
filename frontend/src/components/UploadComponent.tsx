import React from 'react';
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

interface UploadComponentProps {
  onUploadComplete: (jobId: string) => void;
}

export const UploadComponent: React.FC<UploadComponentProps> = ({ onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/v1/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { job_id } = response.data;
      onUploadComplete(job_id);
    } catch (err) {
      setError('Upload failed. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  }, [onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    multiple: false,
  });

  return (
    <div className="upload-container">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'uploading' : ''}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <p>Uploading...</p>
        ) : isDragActive ? (
          <p>Drop the CSV file here</p>
        ) : (
          <p>Drag &amp; drop a CSV file here, or click to select one</p>
        )}
      </div>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};