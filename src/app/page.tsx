'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import WebcamCapture from '../components/WebcamCapture';
import Chatbot from '../components/Chatbot';
import { analyzeSkin, SkinPredictionResult } from '../services/api';
import { ArrowPathIcon, CameraIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { getScanHistoryById } from '@/lib/firebase';
import axios from 'axios';

// Error type for better error handling
interface AnalysisError {
  type: 'no_face' | 'server_error' | 'network_error' | 'unknown';
  message: string;
  suggestion: string;
}

export default function Home() {
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [skinResults, setSkinResults] = useState<SkinPredictionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isWebcamActive, setIsWebcamActive] = useState(true);
  const [isHistoryScan, setIsHistoryScan] = useState<boolean>(false);
  const [analysisError, setAnalysisError] = useState<AnalysisError | null>(null);
  const searchParams = useSearchParams();
  const { currentUser, userRole, loading } = useAuth();
  
  // Load scan history data
  const loadHistoryScan = async (scanId: string) => {
    if (!currentUser) return;
    
    try {
      setIsWebcamActive(false);
      setIsAnalyzing(true);
      
      const historyData = await getScanHistoryById(currentUser.uid, scanId);
      
      if (historyData) {
        setIsHistoryScan(true);
        setCapturedImage(null); // We don't have the actual image in history
        setSkinResults(historyData.skinResults);
      }
    } catch (error) {
      console.error('Error loading scan history:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  // Check if we're viewing a specific scan from history
  useEffect(() => {
    const scanId = searchParams.get('scanId');
    if (scanId && currentUser) {
      loadHistoryScan(scanId);
    }
  }, [searchParams, currentUser]);
  
  // Parse error from API response
  const parseError = (error: any): AnalysisError => {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || error.response?.data?.error || error.message;
      
      // Check for specific error types
      if (message?.toLowerCase().includes('no face detected') || message?.toLowerCase().includes('face')) {
        return {
          type: 'no_face',
          message: 'No face detected in the image',
          suggestion: 'Please ensure your face is clearly visible, well-lit, and centered in the frame. Try removing glasses or accessories that may cover your face.'
        };
      }
      
      if (error.response?.status === 500) {
        return {
          type: 'server_error',
          message: 'Server error occurred',
          suggestion: 'Our servers are experiencing issues. Please try again in a few moments.'
        };
      }
      
      if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
        return {
          type: 'network_error',
          message: 'Network connection error',
          suggestion: 'Please check your internet connection and try again.'
        };
      }
    }
    
    return {
      type: 'unknown',
      message: 'An unexpected error occurred',
      suggestion: 'Please try again. If the problem persists, contact support.'
    };
  };
  
  const handleCapture = async (imageSrc: string) => {
    setCapturedImage(imageSrc);
    setIsWebcamActive(false);
    setIsAnalyzing(true);
    setAnalysisError(null); // Clear previous errors
    
    try {
      // Remove data:image/jpeg;base64, prefix
      const base64Data = imageSrc.split(',')[1];
      const results = await analyzeSkin(base64Data);
      setSkinResults(results);
    } catch (error) {
      console.error('Error analyzing skin:', error);
      const parsedError = parseError(error);
      setAnalysisError(parsedError);
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  const handleReset = () => {
    setCapturedImage(null);
    setSkinResults(null);
    setAnalysisError(null);
    setIsWebcamActive(true);
  };
  
  // Handle new scan request from Chatbot
  const handleNewScanRequest = () => {
    handleReset();
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
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-4">
            Take a clear photo of your face for instant AI skin analysis and personalized recommendations.
          </p>
          
          {/* Portal Links */}
          <div className="flex justify-center gap-4">
            {userRole === 'admin' && (
              <Button asChild variant="outline" size="sm">
                <Link href="/admin">Admin Portal</Link>
              </Button>
            )}
            {(userRole === 'professional' || userRole === 'admin') && (
              <Button asChild variant="outline" size="sm">
                <Link href="/professional">Professional Portal</Link>
              </Button>
            )}
          </div>
        </header>

        {analysisError && (
          <div className="max-w-2xl mx-auto mb-8 bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex items-start gap-3">
            <ExclamationTriangleIcon className="h-6 w-6 text-destructive shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-destructive mb-1">{analysisError.message}</h3>
              <p className="text-sm text-foreground/80 mb-2">{analysisError.suggestion}</p>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setAnalysisError(null)}
                className="text-xs h-8 border-destructive/30 hover:bg-destructive/10"
              >
                Dismiss
              </Button>
            </div>
          </div>
        )}

        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-md border border-slate-200 dark:border-slate-800">
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <CameraIcon className="h-5 w-5 mr-2 text-primary" />
              Skin Analysis
            </h2>
            
            {isWebcamActive ? (
              <WebcamCapture onCapture={handleCapture} onNewScan={handleNewScanRequest} />
            ) : (
              <div className="space-y-4">
                {/* Show captured image or placeholder */}
                <div className="relative">
                  {capturedImage ? (
                    <>
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
                    </>
                  ) : (
                    /* Show placeholder when viewing history or during analysis */
                    <div className="w-full aspect-square rounded-xl border-2 border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800/50 flex items-center justify-center">
                      <div className="text-center text-slate-400">
                        <CameraIcon className="h-16 w-16 mx-auto mb-2" />
                        <p className="text-sm">Image preview unavailable</p>
                      </div>
                    </div>
                  )}
                </div>
                
                {isHistoryScan && skinResults && (
                  <div className="mb-4 px-4 py-3 bg-primary/10 rounded-lg border border-primary/20 text-sm">
                    <p className="font-medium flex items-center mb-1">
                      <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Viewing previous skin analysis
                    </p>
                    <p className="text-muted-foreground text-xs">This is a past analysis from your history.</p>
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
            <Chatbot 
              skinResults={skinResults} 
              onNewScanRequest={handleNewScanRequest}
              isHistoryScan={isHistoryScan}
            />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
