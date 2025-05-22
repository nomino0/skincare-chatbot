'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from 'firebase/auth';

// Helper to get auth from firebase.tsx
async function getFirebaseAuth() {
  if (typeof window === 'undefined') return null;
  try {
    const { getAuthClient, onAuthStateChanged } = await import('@/lib/firebase');
    return { auth: getAuthClient(), onAuthStateChanged };
  } catch (error) {
    console.error('Failed to get auth client:', error);
    return null;
  }
}

// Define a type for the auth context
type AuthContextType = {
  currentUser: User | null;
  loading: boolean;
};

// Create the context with default values
const AuthContext = createContext<AuthContextType>({
  currentUser: null,
  loading: true,
});

// Context Provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    let unsubscribe: (() => void) | undefined;    // Set up auth state listener
    const setupAuth = async () => {
      const firebaseAuth = await getFirebaseAuth();
      if (!firebaseAuth || !firebaseAuth.auth) {
        setLoading(false);
        return;
      }

      unsubscribe = firebaseAuth.onAuthStateChanged((user: User | null) => {
        setCurrentUser(user);
        setLoading(false);
      });
    };

    setupAuth();

    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, []);

  return (
    <AuthContext.Provider value={{ currentUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth() {
  return useContext(AuthContext);
}
