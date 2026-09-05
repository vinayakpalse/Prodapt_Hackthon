import React, { useState, useRef } from 'react';
import { UploadCloud, File, X, CheckCircle, Loader2 } from 'lucide-react';
import Button from './Button';
import { uploadDocument } from '../services/api';

const UploadCard = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState('idle'); // idle | uploading | success
  const [statusText, setStatusText] = useState('');
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleRemove = () => {
    setFile(null);
    setStatus('idle');
  };

  const handleGenerate = async () => {
    setStatus('uploading');
    
    // Simulate generation stages
    setStatusText('Analyzing your study material...');
    setTimeout(() => setStatusText('Identifying topics...'), 1000);
    setTimeout(() => setStatusText('Generating questions and flashcards...'), 2000);

    const result = await uploadDocument(file);
    
    setStatus('success');
    setStatusText('Your learning material is ready!');
    
    setTimeout(() => {
      onUploadSuccess(result.topics);
      setStatus('idle');
      setFile(null);
    }, 1500);
  };

  return (
    <div className="bg-white rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 p-8 max-w-3xl mx-auto mb-12">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Turn your study material into a personalized learning experience</h2>
        <p className="text-gray-500">Upload your notes, documents, or study material and let AI create quizzes and flashcards for you.</p>
      </div>

      {!file && status === 'idle' && (
        <div 
          className={`border-2 border-dashed rounded-xl p-10 text-center transition-colors cursor-pointer
            ${isDragging ? 'border-primary bg-primary/5' : 'border-gray-300 hover:border-primary/50 hover:bg-gray-50'}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input 
            type="file" 
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden" 
            accept=".pdf,.docx,.txt"
          />
          <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4 text-primary">
            <UploadCloud size={32} />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-1">Upload your study material</h3>
          <p className="text-gray-500 mb-4">Drag & drop your file here or Browse Files</p>
          <p className="text-xs text-gray-400">Supported: PDF, DOCX, TXT. Max size: 10MB</p>
        </div>
      )}

      {file && status === 'idle' && (
        <div className="border border-gray-200 rounded-xl p-6 bg-gray-50">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-white rounded-lg shadow-sm border border-gray-100 flex items-center justify-center text-primary">
                <File size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-500 font-medium">Selected file:</p>
                <p className="text-gray-900 font-semibold">{file.name}</p>
                <p className="text-xs text-gray-500 mt-0.5">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
              </div>
            </div>
            <button 
              onClick={handleRemove}
              className="text-gray-400 hover:text-error transition-colors p-2"
              title="Remove file"
            >
              <X size={20} />
            </button>
          </div>
          <Button onClick={handleGenerate} className="w-full text-base py-3 shadow-md shadow-primary/20">
            Generate Learning Material
          </Button>
        </div>
      )}

      {status === 'uploading' && (
        <div className="border border-gray-200 rounded-xl p-10 text-center bg-gray-50 flex flex-col items-center justify-center min-h-[200px]">
          <Loader2 className="w-10 h-10 text-primary animate-spin mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">{statusText}</h3>
          <p className="text-sm text-gray-500 mt-2 max-w-sm">This usually takes a few seconds depending on the document size.</p>
        </div>
      )}

      {status === 'success' && (
        <div className="border border-green-200 rounded-xl p-10 text-center bg-green-50 flex flex-col items-center justify-center min-h-[200px]">
          <CheckCircle className="w-12 h-12 text-green-500 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">{statusText}</h3>
        </div>
      )}
    </div>
  );
};

export default UploadCard;
