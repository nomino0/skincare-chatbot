'use client';

import { useState, useEffect } from 'react';
import { updateUserProfile } from '@/lib/firebase';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { LoadingScreen } from '@/components/ui/loading';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  );
}

function SettingsContent() {
  const { currentUser, loading } = useAuth();
  const router = useRouter();
  const [displayName, setDisplayName] = useState('');
  const [updateLoading, setUpdateLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  useEffect(() => {
    if (currentUser?.displayName) {
      setDisplayName(currentUser.displayName);
    }
  }, [currentUser]);

  if (loading) {
    return <LoadingScreen />;
  }

  if (!currentUser) return null;

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setUpdateLoading(true);
    setMessage(null);    try {
      await updateUserProfile(displayName);
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } catch (error) {
      console.error('Error updating profile:', error);
      setMessage({ type: 'error', text: 'Failed to update profile. Please try again.' });
    } finally {
      setUpdateLoading(false);
    }
  };
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Account Settings</h1>
        
        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-md p-6 border border-slate-200 dark:border-slate-800">
          {message && (
            <div className={`p-4 mb-6 rounded-md ${
              message.type === 'success' 
                ? 'bg-green-50 text-green-800 dark:bg-green-900/30 dark:text-green-300' 
                : 'bg-red-50 text-red-800 dark:bg-red-900/30 dark:text-red-300'
            }`}>
              {message.text}
            </div>
          )}
          
          <form onSubmit={handleUpdateProfile}>
            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  value={currentUser.email || ''}
                  disabled
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
                />
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  Your email cannot be changed
                </p>
              </div>
              
              <div>
                <label htmlFor="displayName" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Display Name
                </label>
                <input
                  type="text"
                  id="displayName"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Enter your display name"
                />
              </div>
            </div>
            
            <div className="mt-8 flex justify-end space-x-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push('/profile')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={updateLoading}
              >
                {updateLoading ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </div>
        
        <div className="mt-6 text-right">
          <Link href="/profile" className="text-sm text-primary hover:underline">
            Back to Profile
          </Link>
        </div>
      </div>
    </div>
  );
}
