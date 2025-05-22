'use client';

import React, { useEffect, useState } from 'react';
import { getAuthClient, getUserScanHistory } from '@/lib/firebase';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';

interface ScanHistoryItem {
  scanId: string;
  timestamp: Date;
  skinResults: any;
  docId?: string;
  skinType?: string;
  skinIssuesCount?: number;
  lastMessageContent?: string;
}

export default function ScanHistoryDashboard() {
  const [scanHistory, setScanHistory] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const loadScanHistory = async () => {
      setLoading(true);
      const auth = getAuthClient();
      if (auth?.currentUser) {
        try {
          const history = await getUserScanHistory(auth.currentUser.uid);
          const formattedHistory = history.map(item => ({
            scanId: item.scanId,
            timestamp: item.timestamp instanceof Date 
              ? item.timestamp 
              : new Date(item.timestamp.seconds * 1000),
            skinResults: item.skinResults,
            docId: item.docId
          }));
          setScanHistory(formattedHistory);
        } catch (error) {
          console.error('Error loading scan history:', error);
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    };

    loadScanHistory();
  }, []);

  const viewScan = (scanId: string) => {
    // Navigate to home page with scan ID
    router.push(`/?scanId=${scanId}`);
  };  

  const getSkinType = (scan: ScanHistoryItem) => {
    return scan.skinResults?.skinType?.type || scan.skinType || 'Unknown';
  };

  const getMostCommonSkinType = (scans: ScanHistoryItem[]): string => {
    if (!scans || scans.length === 0) return 'None';
    
    // Count occurrences of each skin type
    const typeCounts: Record<string, number> = {};
    
    scans.forEach(scan => {
      const skinType = getSkinType(scan);
      typeCounts[skinType] = (typeCounts[skinType] || 0) + 1;
    });
    
    // Find the type with the highest count
    let mostCommonType = 'Unknown';
    let highestCount = 0;
    
    Object.entries(typeCounts).forEach(([type, count]) => {
      if (count > highestCount) {
        mostCommonType = type;
        highestCount = count;
      }
    });
    
    return mostCommonType;
  };

  const getIssuesCount = (scan: ScanHistoryItem) => {
    return scan.skinResults?.skinIssues?.length || scan.skinIssuesCount || 0;
  };

  return (    <div className="bg-white dark:bg-slate-900 rounded-xl shadow-md p-6 border border-slate-200 dark:border-slate-800 mt-8">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold">Skin Analysis History</h3>
        <Button 
          onClick={() => router.push('/')}
          variant="outline"
          size="sm"
        >
          New Analysis
        </Button>
      </div>

      {loading ? (
        <div className="py-10 flex justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
        </div>
      ) : scanHistory.length === 0 ? (
        <div className="py-10 text-center">
          <p className="text-slate-500 dark:text-slate-400">No skin analysis history found.</p>
          <Button 
            onClick={() => router.push('/')}
            className="mt-4"
          >
            Start Your First Analysis
          </Button>
        </div>
      ) : (
        <div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
              <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Total Analyses</div>
              <div className="text-2xl font-semibold">{scanHistory.length}</div>
            </div>
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
              <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Latest Analysis</div>
              <div className="text-sm font-medium">{scanHistory.length > 0 ? format(scanHistory[0].timestamp, 'PP') : '-'}</div>
            </div>
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
              <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Most Common Type</div>
              <div className="text-sm font-medium">
                {scanHistory.length > 0 
                  ? getMostCommonSkinType(scanHistory)
                  : '-'
                }
              </div>
            </div>
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
              <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">Total Issues Found</div>
              <div className="text-2xl font-semibold">
                {scanHistory.reduce((total, scan) => total + getIssuesCount(scan), 0)}
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {scanHistory.map((scan, index) => (
            <div 
              key={scan.scanId} 
              className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => viewScan(scan.scanId)}
            >
              <div className="flex items-center mb-2">
                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center mr-3 text-primary">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium">Skin Analysis #{index + 1}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {format(scan.timestamp, 'PPP p')}
                  </p>
                </div>
              </div>              <div className="pl-2 border-l-2 border-primary/30 ml-1.5 mt-3">
                <div className="text-sm mb-1">
                  <span className="text-slate-600 dark:text-slate-400">Skin Type:</span>{' '}
                  <span className="font-medium">{getSkinType(scan)}</span>
                </div>
                <div className="text-sm mb-1">
                  <span className="text-slate-600 dark:text-slate-400">Detected Issues:</span>{' '}
                  <span className="font-medium">{getIssuesCount(scan)}</span>
                </div>
                {scan.lastMessageContent && (
                  <div className="text-xs text-slate-500 dark:text-slate-400 mt-2 italic line-clamp-2">
                    "{scan.lastMessageContent}"
                  </div>
                )}
              </div>

              <Button
                variant="ghost"
                size="sm"
                className="w-full mt-3 text-primary"
              >
                View Details
              </Button>
            </div>
          ))}
        </div>
        </div>
      )}
    </div>
  );
}
