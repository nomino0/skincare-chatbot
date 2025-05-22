'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { sendVerificationEmail } from '@/lib/firebase';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import * as Avatar from "@radix-ui/react-avatar";
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  );
}

function ProfileContent() {
  const { currentUser } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [verificationSent, setVerificationSent] = useState(false);
  const [verificationLoading, setVerificationLoading] = useState(false);

  if (!currentUser) return null;

  const handleSendVerification = async () => {
    setVerificationLoading(true);
    try {
      await sendVerificationEmail();
      setVerificationSent(true);
    } catch (error) {
      console.error('Error sending verification email:', error);
    } finally {
      setVerificationLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Your Profile</h1>
        
        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-md p-6 border border-slate-200 dark:border-slate-800">
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <Avatar.Root className="h-24 w-24 rounded-full overflow-hidden">
              {currentUser.photoURL ? (
                <Avatar.Image 
                  src={currentUser.photoURL} 
                  alt={currentUser.displayName || currentUser.email || "User profile"} 
                  className="h-full w-full object-cover"
                />
              ) : (
                <Avatar.Fallback className="flex h-full w-full items-center justify-center bg-primary/10 text-primary text-2xl">
                  {(currentUser.displayName?.charAt(0) || currentUser.email?.charAt(0) || "U").toUpperCase()}
                </Avatar.Fallback>
              )}
            </Avatar.Root>
            
            <div className="flex-1">
              <h2 className="text-2xl font-semibold">
                {currentUser.displayName || 'User'}
              </h2>
              <p className="text-slate-600 dark:text-slate-400">{currentUser.email}</p>
              
              <div className="mt-2 flex items-center space-x-2">
                {currentUser.emailVerified ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                    Verified
                  </span>
                ) : (
                  <>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300">
                      Not Verified
                    </span>
                    
                    {currentUser.providerData[0]?.providerId === 'password' && (
                      <div className="ml-2">
                        {verificationSent ? (
                          <p className="text-green-600 dark:text-green-400 text-xs">
                            Verification email sent!
                          </p>
                        ) : (
                          <Button
                            onClick={handleSendVerification}
                            disabled={verificationLoading}
                            className="text-xs h-6 px-2"
                            variant="outline"
                            size="sm"
                          >
                            {verificationLoading ? 'Sending...' : 'Verify Email'}
                          </Button>
                        )}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
          
          <div className="mt-8 border-t border-slate-200 dark:border-slate-800 pt-6">
            <h3 className="text-lg font-medium mb-4">Account Information</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Email</p>
                <p className="font-medium">{currentUser.email}</p>
              </div>
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Account Created</p>
                <p className="font-medium">{currentUser.metadata.creationTime}</p>
              </div>
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Last Sign In</p>
                <p className="font-medium">{currentUser.metadata.lastSignInTime}</p>
              </div>
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400">Authentication Provider</p>
                <p className="font-medium">
                  {currentUser.providerData[0]?.providerId === 'password' 
                    ? 'Email/Password' 
                    : currentUser.providerData[0]?.providerId === 'google.com' 
                      ? 'Google' 
                      : currentUser.providerData[0]?.providerId}
                </p>
              </div>
            </div>
          </div>
          
          <div className="mt-8 flex justify-end space-x-3">
            <Button 
              variant="outline" 
              onClick={() => router.push('/')}
            >
              Back to Home
            </Button>
            <Button
              onClick={() => router.push('/settings')}
            >
              Edit Profile
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}