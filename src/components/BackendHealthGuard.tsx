'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

// We use the same URL as in api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function BackendHealthGuard({ children }: { children: React.ReactNode }) {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let mounted = true;

    const checkHealth = async () => {
      try {
        // Short timeout for health check
        await axios.get(`${API_URL}/health`, { timeout: 5000 });
        if (mounted) setIsHealthy(true);
      } catch (error) {
        console.error('Backend health check failed:', error);
        if (mounted) setIsHealthy(false);
      }
    };

    // Initial check
    checkHealth();

    // Poll interval depends on state
    // If healthy, check every 30s
    // If unhealthy, check every 5s to auto-recover
    const intervalTime = isHealthy === false ? 5000 : 30000;
    const interval = setInterval(checkHealth, intervalTime);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [isHealthy, retryCount]);

  // Loading state (initial check)
  if (isHealthy === null) {
    return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center bg-white dark:bg-slate-950">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-500 dark:text-slate-400 font-medium">Connecting to services...</p>
        </div>
      </div>
    );
  }

  // Error state (backend down)
  if (isHealthy === false) {
    return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-50 dark:bg-slate-950 p-4">
        <div className="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow-xl max-w-md w-full text-center border border-slate-200 dark:border-slate-800">
          <div className="mb-6 flex justify-center">
            <div className="h-20 w-20 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
               <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-10 h-10 text-red-600 dark:text-red-400">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                </svg>
            </div>
          </div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">Service Unavailable</h2>
          <p className="text-slate-600 dark:text-slate-400 mb-8">
            We cannot connect to the backend server. The service might be down for maintenance or experiencing issues.
          </p>
          <div className="space-y-3">
            <button 
                onClick={() => {
                    setIsHealthy(null); // Reset to loading to force immediate check
                    setRetryCount(c => c + 1);
                }}
                className="w-full px-4 py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 transition-colors shadow-lg shadow-primary/25"
            >
                Retry Connection
            </button>
            <p className="text-xs text-slate-400 mt-4">
                Auto-retrying in 5 seconds...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
