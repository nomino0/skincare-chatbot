import React, { useCallback, useRef, useState } from 'react';
import Webcam from 'react-webcam';
import { Button } from '@/components/ui/button';

interface WebcamCaptureProps {
  onCapture: (imageSrc: string) => void;
}

const WebcamCapture: React.FC<WebcamCaptureProps> = ({ onCapture }) => {
  const webcamRef = useRef<Webcam>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isCapturing, setIsCapturing] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'webcam' | 'upload'>('webcam');

  const capture = useCallback(() => {
    if (webcamRef.current) {
      setIsCapturing(true);
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        onCapture(imageSrc);
      }
      setIsCapturing(false);
    }
  }, [webcamRef, onCapture]);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setIsUploading(true);
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        onCapture(result);
        setIsUploading(false);
      };
      reader.onerror = () => {
        console.error('Error reading file');
        setIsUploading(false);
      };
      reader.readAsDataURL(file);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="relative flex flex-col items-center w-full max-w-md mx-auto">
      {/* Tab Selector */}
      <div className="flex w-full mb-4 border-b border-slate-200 dark:border-slate-800">
        <button
          onClick={() => setActiveTab('webcam')}
          className={`w-1/2 py-2 font-medium text-sm ${
            activeTab === 'webcam' 
              ? 'text-primary border-b-2 border-primary' 
              : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
          }`}
        >
          Use Webcam
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className={`w-1/2 py-2 font-medium text-sm ${
            activeTab === 'upload' 
              ? 'text-primary border-b-2 border-primary' 
              : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
          }`}
        >
          Upload Image
        </button>
      </div>
      
      {/* Webcam Tab */}
      {activeTab === 'webcam' && (
        <>
          <div className="overflow-hidden rounded-xl border-2 border-slate-300 dark:border-slate-700 mb-4 w-full">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{
                width: 480,
                height: 480,
                facingMode: "user"
              }}
              className="w-full"
            />
          </div>
          
          <Button
            onClick={capture}
            disabled={isCapturing}
            className="w-full"
          >
            {isCapturing ? "Processing..." : "Capture Photo"}
          </Button>
        </>
      )}

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <>
          <div 
            className="flex flex-col items-center justify-center w-full h-64 border-2 border-slate-300 dark:border-slate-700 border-dashed rounded-lg mb-4 cursor-pointer bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800" 
            onClick={triggerFileInput}
          >
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <svg className="w-10 h-10 mb-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">
                <span className="font-semibold">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">PNG, JPG or JPEG (MAX. 5MB)</p>
            </div>
          </div>
          
          <input 
            ref={fileInputRef}
            type="file" 
            accept="image/png, image/jpeg, image/jpg"
            className="hidden"
            onChange={handleFileUpload}
          />
          
          <Button
            onClick={triggerFileInput}
            disabled={isUploading}
            className="w-full"
          >
            {isUploading ? "Processing..." : "Choose File"}
          </Button>
        </>
      )}
    </div>
  );
};

export default WebcamCapture;