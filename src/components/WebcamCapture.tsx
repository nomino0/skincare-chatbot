import React, { useCallback, useRef, useState } from 'react';
import Webcam from 'react-webcam';

interface WebcamCaptureProps {
  onCapture: (imageSrc: string) => void;
}

const WebcamCapture: React.FC<WebcamCaptureProps> = ({ onCapture }) => {
  const webcamRef = useRef<Webcam>(null);
  const [isCapturing, setIsCapturing] = useState<boolean>(false);

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

  return (
    <div className="relative flex flex-col items-center">
      <div className="overflow-hidden rounded-xl border-2 border-gray-300 mb-4">
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
      
      <button
        onClick={capture}
        disabled={isCapturing}
        className="px-6 py-2.5 bg-blue-600 text-white font-medium text-sm rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75 transition-colors disabled:bg-gray-400"
      >
        {isCapturing ? "Processing..." : "Capture Photo"}
      </button>
    </div>
  );
};

export default WebcamCapture;