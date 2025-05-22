import React, { useCallback, useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Button } from '@/components/ui/button';

interface WebcamCaptureProps {
  onCapture: (imageSrc: string) => void;
  onNewScan: () => void; // New prop to clear chat when a new scan is started
}

const WebcamCapture: React.FC<WebcamCaptureProps> = ({ onCapture, onNewScan }) => {
  const webcamRef = useRef<Webcam>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isCapturing, setIsCapturing] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'webcam' | 'upload'>('webcam');
  const [countdown, setCountdown] = useState<number | null>(null);

  // Handle countdown for webcam capture
  useEffect(() => {
    if (countdown === null) return;
    
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      captureImage();
    }
  }, [countdown]);

  const captureImage = useCallback(() => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        onCapture(imageSrc);
      }
      setIsCapturing(false);
      setCountdown(null);
    }
  }, [webcamRef, onCapture]);
  const startCountdown = () => {
    setIsCapturing(true);
    setCountdown(3);
    onNewScan(); // Clear chat history for new scan
  };
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setIsUploading(true);
      onNewScan(); // Clear chat history for new scan
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
      <div className="flex w-full mb-4 border-b border-border">
        <button
          onClick={() => setActiveTab('webcam')}
          className={`w-1/2 py-3 font-medium text-sm transition-all duration-300 ${
            activeTab === 'webcam' 
              ? 'text-primary border-b-2 border-primary font-semibold' 
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <div className="flex items-center justify-center">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Use Webcam
          </div>
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className={`w-1/2 py-3 font-medium text-sm transition-all duration-300 ${
            activeTab === 'upload' 
              ? 'text-primary border-b-2 border-primary font-semibold' 
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <div className="flex items-center justify-center">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Upload Image
          </div>
        </button>
      </div>
      
      {/* Webcam Tab */}
      {activeTab === 'webcam' && (
        <>
          <div className="relative overflow-hidden rounded-xl border-2 border-border mb-4 w-full futuristic-panel">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{
                width: 480,
                height: 480,
                facingMode: "user"
              }}
              className={`w-full ${isCapturing ? 'animate-pulse-slow' : ''}`}
            />
            
            {/* Scanning overlay */}
            <div className={`absolute inset-0 pointer-events-none ${isCapturing ? 'opacity-100' : 'opacity-0'} transition-opacity duration-300`}>
              {/* Target grid */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-64 h-64 border-2 border-primary/70 rounded-full"></div>
                <div className="absolute w-72 h-72 border border-primary/40 rounded-full animate-pulse-slow"></div>
                <div className="absolute w-80 h-80 border border-primary/20 rounded-full"></div>
                
                {/* Scan line */}
                <div className="absolute h-full w-full overflow-hidden">
                  <div className="h-1 w-full bg-primary/60 absolute top-1/2 transform -translate-y-1/2 animate-gradient"></div>
                </div>
                
                {/* Corner markers */}
                <div className="absolute top-10 left-10 w-8 h-8 border-t-2 border-l-2 border-primary"></div>
                <div className="absolute top-10 right-10 w-8 h-8 border-t-2 border-r-2 border-primary"></div>
                <div className="absolute bottom-10 left-10 w-8 h-8 border-b-2 border-l-2 border-primary"></div>
                <div className="absolute bottom-10 right-10 w-8 h-8 border-b-2 border-r-2 border-primary"></div>
              </div>
              
              {/* Status indicators */}
              <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center">
                <div className="text-xs font-medium text-primary bg-background/70 backdrop-blur-sm px-2 py-1 rounded-full">
                  {isCapturing ? 'SCANNING' : 'READY'}
                </div>
                <div className="text-xs font-medium text-primary bg-background/70 backdrop-blur-sm px-2 py-1 rounded-full">
                  {isCapturing ? 'OPTIMIZING LIGHT' : 'FACE DETECTED'}
                </div>
              </div>
            </div>
            
            {/* Countdown overlay */}
            {countdown !== null && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/30 backdrop-blur-sm">
                <div className="text-6xl font-bold text-white animate-pulse">{countdown}</div>
              </div>
            )}
          </div>
          
          <Button
            onClick={startCountdown}
            disabled={isCapturing}
            className="w-full font-medium bg-primary text-primary-foreground hover:shadow-lg transition-all duration-300"
            variant="default"
          >
            {isCapturing ? (
              <div className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing...
              </div>
            ) : (
              <div className="flex items-center">
                <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Capture Photo
              </div>
            )}
          </Button>
        </>
      )}

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <>
          <div 
            className="flex flex-col items-center justify-center w-full h-64 border-2 border-border border-dashed rounded-lg mb-4 cursor-pointer bg-background/40 hover:bg-background/60 transition-all duration-300 futuristic-panel" 
            onClick={triggerFileInput}
          >
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <div className="relative mb-3">
                <svg className="w-12 h-12 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
                <div className="absolute inset-0 flex items-center justify-center opacity-20">
                  <div className="w-6 h-6 rounded-full bg-primary animate-ping"></div>
                </div>
              </div>
              <p className="mb-2 text-sm text-foreground">
                <span className="font-semibold">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-muted-foreground">
                PNG, JPG or JPEG (MAX. 5MB)
              </p>
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
            className="w-full font-medium bg-primary text-primary-foreground hover:shadow-lg transition-all duration-300"
            variant="default"
          >
            {isUploading ? (
              <div className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </div>
            ) : (
              <div className="flex items-center">
                <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Choose File
              </div>
            )}
          </Button>
        </>
      )}
    </div>
  );
};


export default WebcamCapture;