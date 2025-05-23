'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { getAuthClient, getFirestoreClient, saveScanHistory } from '@/lib/firebase';
import { collection, addDoc, serverTimestamp, Timestamp } from 'firebase/firestore';
import { useAuth } from '@/lib/auth-context';

export default function TestFirebase() {
  const [testResult, setTestResult] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const { currentUser } = useAuth();
  const testFirestoreConnection = async () => {
    setIsLoading(true);
    setTestResult('Testing Firestore connection...\n');
    
    try {
      const db = getFirestoreClient();
      if (!db) {
        setTestResult(prev => prev + 'ERROR: Firestore client not available\n');
        return;
      }
      
      setTestResult(prev => prev + 'SUCCESS: Firestore client is available\n');
      
      // Test authentication
      const auth = getAuthClient();
      if (!auth?.currentUser) {
        setTestResult(prev => prev + 'ERROR: No authenticated user\n');
        return;
      }
        setTestResult(prev => prev + `SUCCESS: User authenticated - ${auth.currentUser?.uid}\n`);
      setTestResult(prev => prev + `User email: ${auth.currentUser?.email}\n`);
      
      // Test writing to a test collection first
      try {
        setTestResult(prev => prev + 'Testing write permissions to test collection...\n');        const testDoc = await addDoc(collection(db, 'test'), {
          message: 'Test from frontend',
          timestamp: serverTimestamp(),
          userId: auth.currentUser!.uid
        });
        
        setTestResult(prev => prev + `SUCCESS: Test document created with ID: ${testDoc.id}\n`);
      } catch (writeError) {
        setTestResult(prev => prev + `ERROR writing to test collection: ${writeError}\n`);
        console.error('Write error:', writeError);
      }
      
      // Test the saveScanHistory function
      try {
        setTestResult(prev => prev + 'Testing saveScanHistory function...\n');
        const mockSkinResults = {
          skinType: { type: 'Oily', confidence: 95 },
          skinIssues: [{ name: 'Acne', confidence: 80 }],
          ai_response: 'This is a test AI response'
        };
          const mockMessages = [{
          role: 'assistant' as const,
          content: 'Test message',
          showAnalysis: false,
          suggestions: [],
          timestamp: Timestamp.now()
        }];
        
        const result = await saveScanHistory(auth.currentUser!.uid, mockSkinResults, mockMessages);
        
        if (result) {
          setTestResult(prev => prev + `SUCCESS: Scan history saved with ID: ${result.scanId}\n`);
          setTestResult(prev => prev + `Document ID: ${result.docId}\n`);
        } else {
          setTestResult(prev => prev + 'ERROR: Failed to save scan history - function returned null\n');
        }
      } catch (scanError) {
        setTestResult(prev => prev + `ERROR in saveScanHistory: ${scanError}\n`);
        console.error('Scan save error:', scanError);
      }
      
    } catch (error) {
      console.error('Firebase test error:', error);
      setTestResult(prev => prev + `GENERAL ERROR: ${error}\n`);
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentUser) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">Firebase Test</h1>
        <p>Please log in to test Firebase connectivity.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Firebase Test</h1>
      
      <div className="mb-4">
        <Button 
          onClick={testFirestoreConnection}
          disabled={isLoading}
          className="mb-4"
        >
          {isLoading ? 'Testing...' : 'Test Firestore Connection'}
        </Button>
      </div>
      
      {testResult && (
        <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Test Results:</h3>
          <pre className="text-sm whitespace-pre-wrap">{testResult}</pre>
        </div>
      )}
    </div>
  );
}
