'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { getAdminSubmissions, submitLabel, AdminSubmission, LabelSubmission } from '@/services/api';
import { RoleProtectedRoute } from '@/components/RoleProtectedRoute';

export default function AdminPage() {
  const { currentUser, loading } = useAuth();
  const router = useRouter();
  const [submissions, setSubmissions] = useState<AdminSubmission[]>([]);
  const [selectedSubmission, setSelectedSubmission] = useState<AdminSubmission | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [labelForm, setLabelForm] = useState({
    verifiedSkinType: '',
    verifiedIssues: [] as string[],
    notes: ''
  });

  // Removed redundant auth check useEffect as RoleProtectedRoute handles it

  useEffect(() => {
    if (currentUser) {
      loadSubmissions();
    }
  }, [currentUser]);

  const loadSubmissions = async () => {
    setIsLoading(true);
    try {
      const data = await getAdminSubmissions('pending', 50);
      setSubmissions(data);
    } catch (error) {
      console.error('Error loading submissions:', error);
      alert('Failed to load submissions. Make sure you have admin access.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitLabel = async () => {
    if (!selectedSubmission) return;

    try {
      const label: LabelSubmission = {
        scanId: selectedSubmission.scanId,
        verifiedSkinType: labelForm.verifiedSkinType,
        verifiedIssues: labelForm.verifiedIssues,
        notes: labelForm.notes
      };

      await submitLabel(label);
      alert('Label submitted successfully!');
      setSelectedSubmission(null);
      setLabelForm({ verifiedSkinType: '', verifiedIssues: [], notes: '' });
      loadSubmissions();
    } catch (error) {
      console.error('Error submitting label:', error);
      alert('Failed to submit label');
    }
  };

  const toggleIssue = (issue: string) => {
    setLabelForm(prev => ({
      ...prev,
      verifiedIssues: prev.verifiedIssues.includes(issue)
        ? prev.verifiedIssues.filter(i => i !== issue)
        : [...prev.verifiedIssues, issue]
    }));
  };

  return (
    <RoleProtectedRoute allowedRoles={['admin']}>
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-primary mb-2">Admin Portal</h1>
          <p className="text-slate-600 dark:text-slate-400">
            Professional labeling for active learning
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Submissions List */}
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-md p-6 border border-slate-200 dark:border-slate-800">
            <h2 className="text-xl font-semibold mb-4">Pending Submissions ({submissions.length})</h2>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {submissions.map((submission) => (
                <div
                  key={submission.scanId}
                  onClick={() => setSelectedSubmission(submission)}
                  className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                    selectedSubmission?.scanId === submission.scanId
                      ? 'border-primary bg-primary/10'
                      : 'border-slate-200 dark:border-slate-700 hover:border-primary/50'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-medium text-sm">Scan #{submission.scanId.slice(0, 8)}</span>
                    <span className="text-xs text-slate-500">
                      {new Date(submission.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">
                    <div>Predicted: {submission.prediction.skinType?.type || 'Unknown'}</div>
                    <div>Issues: {submission.prediction.skinIssues?.length || 0}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Labeling Form */}
          <div className="bg-white dark:bg-slate-900 rounded-xl shadow-md p-6 border border-slate-200 dark:border-slate-800">
            {selectedSubmission ? (
              <>
                <h2 className="text-xl font-semibold mb-4">Label Submission</h2>
                
                {/* Image Preview */}
                <div className="mb-6">
                  <div className="w-full aspect-square rounded-lg border-2 border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800/50 flex items-center justify-center">
                    <div className="text-center text-slate-400">
                      <p className="text-sm">Image: {selectedSubmission.imagePath}</p>
                      <p className="text-xs mt-2">Image preview not available</p>
                    </div>
                  </div>
                </div>

                {/* AI Prediction */}
                <div className="mb-6 p-4 bg-slate-100 dark:bg-slate-800/50 rounded-lg">
                  <h3 className="font-medium mb-2">AI Prediction:</h3>
                  <p className="text-sm">
                    <span className="font-medium">Skin Type:</span>{' '}
                    {selectedSubmission.prediction.skinType?.type || 'Unknown'}
                  </p>
                  <p className="text-sm">
                    <span className="font-medium">Issues:</span>{' '}
                    {selectedSubmission.prediction.skinIssues?.map((i: any) => i.name).join(', ') || 'None'}
                  </p>
                </div>

                {/* Verified Skin Type */}
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Verified Skin Type</label>
                  <select
                    value={labelForm.verifiedSkinType}
                    onChange={(e) => setLabelForm({ ...labelForm, verifiedSkinType: e.target.value })}
                    className="w-full p-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800"
                  >
                    <option value="">Select...</option>
                    <option value="Dry">Dry</option>
                    <option value="Oily">Oily</option>
                    <option value="Normal">Normal</option>
                    <option value="Combination">Combination</option>
                  </select>
                </div>

                {/* Verified Issues */}
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Verified Issues</label>
                  <div className="grid grid-cols-2 gap-2">
                    {['Acne', 'Redness', 'Dark Spots', 'Wrinkles', 'Dryness', 'Oiliness'].map((issue) => (
                      <label key={issue} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={labelForm.verifiedIssues.includes(issue)}
                          onChange={() => toggleIssue(issue)}
                          className="rounded"
                        />
                        <span className="text-sm">{issue}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Notes */}
                <div className="mb-6">
                  <label className="block text-sm font-medium mb-2">Notes</label>
                  <textarea
                    value={labelForm.notes}
                    onChange={(e) => setLabelForm({ ...labelForm, notes: e.target.value })}
                    className="w-full p-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800"
                    rows={3}
                    placeholder="Additional observations..."
                  />
                </div>

                <div className="flex space-x-3">
                  <Button onClick={handleSubmitLabel} className="flex-1">
                    Submit Label
                  </Button>
                  <Button
                    onClick={() => {
                      setSelectedSubmission(null);
                      setLabelForm({ verifiedSkinType: '', verifiedIssues: [], notes: '' });
                    }}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-400">
                <p>Select a submission to label</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </RoleProtectedRoute>
  );
}
