'use client';

import { useState } from 'react';
import WebcamCapture from '../components/WebcamCapture';
import Chatbot from '../components/Chatbot';
import { analyzeSkin, SkinPredictionResult } from '../services/api';
import { ArrowPathIcon, CameraIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function Home() {
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [skinResults, setSkinResults] = useState<SkinPredictionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isWebcamActive, setIsWebcamActive] = useState(true);
  const { currentUser, loading } = useAuth();
  
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

  if (loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!currentUser) {
    return (
      <div className="container mx-auto px-4 py-16 flex flex-col items-center">
        <div className="max-w-3xl text-center mb-12">
          <h1 className="text-4xl font-bold text-primary mb-4 sm:text-5xl">Analyze Your Skin with AI</h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 mb-8">
            Get personalized skin analysis and recommendations from our AI dermatology assistant.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild className="px-8 py-6 text-lg">
              <Link href="/login">Log In</Link>
            </Button>
            <Button asChild variant="outline" className="px-8 py-6 text-lg">
              <Link href="/signup">Sign Up</Link>
            </Button>
          </div>
        </div>
        
        <div className="w-full max-w-6xl bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-950/50 dark:to-indigo-950/50 rounded-xl p-8 shadow-md">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            <div>
              <h2 className="text-2xl font-bold mb-3">How It Works</h2>
              <ul className="space-y-3">
                <li className="flex items-start gap-2">
                  <span className="inline-flex items-center justify-center rounded-full bg-primary/10 w-6 h-6 mt-0.5 text-primary text-sm font-medium">1</span>
                  <span>Create an account or log in to access the skin analysis tool</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="inline-flex items-center justify-center rounded-full bg-primary/10 w-6 h-6 mt-0.5 text-primary text-sm font-medium">2</span>
                  <span>Capture a photo of your face with the webcam</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="inline-flex items-center justify-center rounded-full bg-primary/10 w-6 h-6 mt-0.5 text-primary text-sm font-medium">3</span>
                  <span>Our AI analyzes your skin type and detects potential issues</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="inline-flex items-center justify-center rounded-full bg-primary/10 w-6 h-6 mt-0.5 text-primary text-sm font-medium">4</span>
                  <span>Get personalized recommendations from our AI assistant</span>
                </li>
              </ul>
            </div>
            <div className="flex justify-center">
              <div className="relative w-64 h-64 bg-white dark:bg-slate-800 rounded-full shadow-md overflow-hidden border-4 border-white dark:border-slate-700">
                <div className="absolute inset-0 flex items-center justify-center text-slate-300 dark:text-slate-600">
                  <CameraIcon className="h-24 w-24" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary mb-2">Skin Analyzer</h1>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Capture your face to analyze your skin type and get personalized recommendations from our AI dermatology assistant.
          </p>
        </header>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-md border border-slate-200 dark:border-slate-800">
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <CameraIcon className="h-5 w-5 mr-2 text-primary" />
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
                      className="w-full rounded-xl border-2 border-slate-300 dark:border-slate-700" 
                    />
                    {skinResults && (
                      <div className="absolute top-2 right-2 bg-green-500 text-white rounded-full p-1">
                        <CheckCircleIcon className="h-5 w-5" />
                      </div>
                    )}
                  </div>
                )}
                
                <div className="flex space-x-3">
                  <Button
                    onClick={handleReset}
                    variant="outline"
                    className="flex-1"
                  >
                    <ArrowPathIcon className="h-5 w-5 inline-block mr-1" />
                    Take Another Photo
                  </Button>
                </div>
                
                {isAnalyzing && (
                  <div className="flex justify-center items-center py-4">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
                    <span className="ml-2 text-slate-600 dark:text-slate-400">Analyzing skin...</span>
                  </div>
                )}
                
                {skinResults && (
                  <div className="mt-4 p-4 bg-slate-100 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
                    <h3 className="font-medium text-primary">Analysis Results:</h3>
                    <p className="mt-1">
                      <span className="font-medium text-slate-800 dark:text-slate-200">Skin Type:</span>{" "}
                      <span className="text-slate-600 dark:text-slate-400">
                        {skinResults.skinType.type} ({skinResults.skinType.confidence.toFixed(2)}%)
                      </span>
                    </p>
                    {skinResults.skinIssues.length > 0 && (
                      <div className="mt-2">
                        <span className="font-medium text-slate-800 dark:text-slate-200">Detected Issues:</span>
                        <ul className="text-slate-600 dark:text-slate-400 list-disc pl-5 mt-1">
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
    </ProtectedRoute>
  );
}
