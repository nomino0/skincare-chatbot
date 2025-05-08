'use client';

import { useState } from 'react';
import WebcamCapture from '../components/WebcamCapture';
import Chatbot from '../components/Chatbot';
import { analyzeSkin, SkinPredictionResult } from '../services/api';
import { ArrowPathIcon, CameraIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

export default function Home() {
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [skinResults, setSkinResults] = useState<SkinPredictionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isWebcamActive, setIsWebcamActive] = useState(true);
  
  const handleCapture = async (imageSrc: string) => {
    setCapturedImage(imageSrc);
    setIsWebcamActive(false);
    setIsAnalyzing(true);
    
    try {
      // Remove data:image/jpeg;base64, prefix
      const base64Data = imageSrc.split(',')[1];
      const results = await analyzeSkin(base64Data);
      setSkinResults(results);
    } catch (error) {
      console.error('Error analyzing skin:', error);
      // Handle error
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  const handleReset = () => {
    setCapturedImage(null);
    setSkinResults(null);
    setIsWebcamActive(true);
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-800 mb-2">Skin Analyzer</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Capture your face to analyze your skin type and get personalized recommendations from our AI dermatology assistant.
          </p>
        </header>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          <div className="bg-white p-6 rounded-xl shadow-md">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <CameraIcon className="h-5 w-5 mr-2 text-blue-600" />
              Skin Analysis
            </h2>
            
            {isWebcamActive ? (
              <WebcamCapture onCapture={handleCapture} />
            ) : (
              <div className="space-y-4">
                {capturedImage && (
                  <div className="relative">
                    <img 
                      src={capturedImage} 
                      alt="Captured" 
                      className="w-full rounded-xl border-2 border-gray-300" 
                    />
                    {skinResults && (
                      <div className="absolute top-2 right-2 bg-green-500 text-white rounded-full p-1">
                        <CheckCircleIcon className="h-5 w-5" />
                      </div>
                    )}
                  </div>
                )}
                
                <div className="flex space-x-3">
                  <button
                    onClick={handleReset}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 font-medium text-sm rounded-lg shadow-sm hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-opacity-75 transition-colors"
                  >
                    <ArrowPathIcon className="h-5 w-5 inline-block mr-1" />
                    Take Another Photo
                  </button>
                </div>
                
                {isAnalyzing && (
                  <div className="flex justify-center items-center py-4">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600"></div>
                    <span className="ml-2 text-gray-600">Analyzing skin...</span>
                  </div>
                )}
                
                {skinResults && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
                    <h3 className="font-medium text-blue-800">Analysis Results:</h3>
                    <p className="mt-1">
                      <span className="font-medium text-gray-800">Skin Type:</span> {skinResults.skinType.type} ({skinResults.skinType.confidence.toFixed(2)}%)
                    </p>
                    {skinResults.skinIssues.length > 0 && (
                      <div className="mt-2">
                        <span className="font-medium text-gray-800">Detected Issues:</span>
                        <ul className="list-disc pl-5 mt-1">
                          {skinResults.skinIssues.map((issue, index) => (
                            <li key={index}>
                              {issue.name} ({issue.confidence.toFixed(2)}%)
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
          
          <div>
            <Chatbot skinResults={skinResults} />
          </div>
        </div>
      </div>
    </main>
  );
}
