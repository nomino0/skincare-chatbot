'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { RoleProtectedRoute } from '@/components/RoleProtectedRoute';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

interface ScanData {
  scanId: string;
  timestamp: string;
  imagePath: string;
  aiPrediction: {
    skinType: { type: string; confidence: number } | null;
    skinIssues: Array<{ name: string; confidence: number }>;
    demographics: any;
  };
  hasLabel: boolean;
  label?: {
    verifiedSkinType: string;
    verifiedIssues: string[];
    aiWasCorrect: boolean;
    notes: string;
  };
}

interface Stats {
  totalScans: number;
  labeledScans: number;
  pendingScans: number;
  aiAccuracy: number;
}

export default function ProfessionalPortal() {
  const { currentUser, loading } = useAuth();
  const [scans, setScans] = useState<ScanData[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [selectedScan, setSelectedScan] = useState<ScanData | null>(null);
  const [scanImage, setScanImage] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<'pending' | 'labeled' | 'all'>('pending');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  // Label form state
  const [labelForm, setLabelForm] = useState({
    verifiedSkinType: '',
    verifiedIssues: [] as string[],
    aiWasCorrect: false,
    notes: ''
  });

  const SKIN_TYPES = ['Oily', 'Dry', 'Normal', 'Combination', 'Sensitive'];
  const SKIN_ISSUES = ['Acne', 'Redness', 'Dark Spots', 'Wrinkles', 'Dryness', 'Oiliness', 'Large Pores', 'Blackheads'];

  useEffect(() => {
    fetchScans();
    fetchStats();
  }, [statusFilter]);

  const fetchScans = async () => {
    try {
      const response = await fetch(`${API_URL}/api/professional/scans?status=${statusFilter}`);
      if (response.ok) {
        const data = await response.json();
        setScans(data.scans || []);
      }
    } catch (error) {
      console.error('Failed to fetch scans:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/professional/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchScanDetail = async (scanId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/professional/scans/${scanId}`);
      if (response.ok) {
        const data = await response.json();
        setScanImage(data.imageBase64);
        
        // Pre-fill form if already labeled
        if (data.label) {
          setLabelForm({
            verifiedSkinType: data.label.verifiedSkinType || '',
            verifiedIssues: data.label.verifiedIssues || [],
            aiWasCorrect: data.label.aiWasCorrect || false,
            notes: data.label.notes || ''
          });
        } else {
          // Pre-fill with AI prediction
          setLabelForm({
            verifiedSkinType: data.aiPrediction?.skinType?.type || '',
            verifiedIssues: data.aiPrediction?.skinIssues?.map((i: any) => i.name) || [],
            aiWasCorrect: false,
            notes: ''
          });
        }
      }
    } catch (error) {
      console.error('Failed to fetch scan detail:', error);
    }
  };

  const handleSelectScan = (scan: ScanData) => {
    setSelectedScan(scan);
    fetchScanDetail(scan.scanId);
  };

  const handleIssueToggle = (issue: string) => {
    setLabelForm(prev => ({
      ...prev,
      verifiedIssues: prev.verifiedIssues.includes(issue)
        ? prev.verifiedIssues.filter(i => i !== issue)
        : [...prev.verifiedIssues, issue]
    }));
  };

  const handleSubmitLabel = async () => {
    if (!selectedScan) return;
    
    setIsSaving(true);
    try {
      const response = await fetch(`${API_URL}/api/professional/scans/${selectedScan.scanId}/label`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(labelForm)
      });
      
      if (response.ok) {
        // Refresh data
        fetchScans();
        fetchStats();
        setSelectedScan(null);
        setScanImage(null);
      }
    } catch (error) {
      console.error('Failed to save label:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <RoleProtectedRoute allowedRoles={['professional', 'admin']}>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b border-border">
          <div className="container mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-primary">Professional Portal</h1>
                <p className="text-sm text-muted-foreground">Dermatologist Review Dashboard</p>
              </div>
              
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-card rounded-xl p-6 border border-border">
                <div className="text-3xl font-bold text-primary">{stats.totalScans}</div>
                <div className="text-sm text-muted-foreground">Total Scans</div>
              </div>
              <div className="bg-card rounded-xl p-6 border border-border">
                <div className="text-3xl font-bold text-yellow-500">{stats.pendingScans}</div>
                <div className="text-sm text-muted-foreground">Pending Review</div>
              </div>
              <div className="bg-card rounded-xl p-6 border border-border">
                <div className="text-3xl font-bold text-green-500">{stats.labeledScans}</div>
                <div className="text-sm text-muted-foreground">Labeled</div>
              </div>
              <div className="bg-card rounded-xl p-6 border border-border">
                <div className="text-3xl font-bold text-blue-500">{stats.aiAccuracy}%</div>
                <div className="text-sm text-muted-foreground">AI Accuracy</div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Scan List */}
            <div className="bg-card rounded-xl border border-border p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">Scans</h2>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as any)}
                  className="px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                >
                  <option value="pending">Pending</option>
                  <option value="labeled">Labeled</option>
                  <option value="all">All</option>
                </select>
              </div>

              {isLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
                </div>
              ) : scans.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No scans found
                </div>
              ) : (
                <div className="space-y-3 max-h-[500px] overflow-y-auto">
                  {scans.map(scan => (
                    <div
                      key={scan.scanId}
                      onClick={() => handleSelectScan(scan)}
                      className={`p-4 rounded-lg border cursor-pointer transition-all ${
                        selectedScan?.scanId === scan.scanId
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium">{scan.scanId}</div>
                          <div className="text-sm text-muted-foreground">
                            {scan.timestamp ? new Date(scan.timestamp).toLocaleString() : 'Unknown date'}
                          </div>
                          <div className="text-sm mt-1">
                            AI: <span className="text-primary">{scan.aiPrediction?.skinType?.type || 'Unknown'}</span>
                          </div>
                        </div>
                        <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                          scan.hasLabel
                            ? 'bg-green-500/20 text-green-500'
                            : 'bg-yellow-500/20 text-yellow-500'
                        }`}>
                          {scan.hasLabel ? 'Labeled' : 'Pending'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Label Form */}
            <div className="bg-card rounded-xl border border-border p-6">
              <h2 className="text-xl font-semibold mb-6">Review & Label</h2>

              {selectedScan ? (
                <div className="space-y-6">
                  {/* Image Preview */}
                  {scanImage && (
                    <div className="rounded-lg overflow-hidden border border-border">
                      <img
                        src={`data:image/jpeg;base64,${scanImage}`}
                        alt="Scan"
                        className="w-full h-auto"
                      />
                    </div>
                  )}

                  {/* AI Prediction */}
                  <div className="bg-background rounded-lg p-4">
                    <h3 className="font-medium mb-2">AI Prediction</h3>
                    <div className="text-sm space-y-1">
                      <div>
                        Skin Type: <span className="text-primary font-medium">
                          {selectedScan.aiPrediction?.skinType?.type || 'Unknown'}
                        </span>
                        {selectedScan.aiPrediction?.skinType?.confidence && (
                          <span className="text-muted-foreground ml-2">
                            ({Math.round(selectedScan.aiPrediction.skinType.confidence)}%)
                          </span>
                        )}
                      </div>
                      <div>
                        Issues: <span className="text-primary">
                          {selectedScan.aiPrediction?.skinIssues?.map(i => i.name).join(', ') || 'None'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Verified Skin Type */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Verified Skin Type</label>
                    <div className="flex flex-wrap gap-2">
                      {SKIN_TYPES.map(type => (
                        <button
                          key={type}
                          onClick={() => setLabelForm(prev => ({ ...prev, verifiedSkinType: type }))}
                          className={`px-3 py-1 rounded-full text-sm transition-all ${
                            labelForm.verifiedSkinType === type
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-background border border-border hover:border-primary'
                          }`}
                        >
                          {type}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Verified Issues */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Verified Issues</label>
                    <div className="flex flex-wrap gap-2">
                      {SKIN_ISSUES.map(issue => (
                        <button
                          key={issue}
                          onClick={() => handleIssueToggle(issue)}
                          className={`px-3 py-1 rounded-full text-sm transition-all ${
                            labelForm.verifiedIssues.includes(issue)
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-background border border-border hover:border-primary'
                          }`}
                        >
                          {issue}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* AI Correctness */}
                  <div>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={labelForm.aiWasCorrect}
                        onChange={(e) => setLabelForm(prev => ({ ...prev, aiWasCorrect: e.target.checked }))}
                        className="w-4 h-4 rounded border-border"
                      />
                      <span className="text-sm">AI prediction was correct</span>
                    </label>
                  </div>

                  {/* Notes */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Notes</label>
                    <textarea
                      value={labelForm.notes}
                      onChange={(e) => setLabelForm(prev => ({ ...prev, notes: e.target.value }))}
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground resize-none"
                      rows={3}
                      placeholder="Add any observations or notes..."
                    />
                  </div>

                  {/* Submit */}
                  <Button
                    onClick={handleSubmitLabel}
                    disabled={isSaving || !labelForm.verifiedSkinType}
                    className="w-full"
                  >
                    {isSaving ? 'Saving...' : 'Save Label'}
                  </Button>
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  Select a scan from the list to review
                </div>
              )}
            </div>
          </div>

          {/* Export Button */}
          <div className="mt-8 text-center">
            <Button
              variant="outline"
              onClick={() => window.open(`${API_URL}/api/professional/export`, '_blank')}
            >
              📥 Export Labeled Data (for Retraining)
            </Button>
          </div>
        </main>
      </div>
    </RoleProtectedRoute>
  );
}
