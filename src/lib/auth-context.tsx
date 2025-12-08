'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from 'firebase/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

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
  userRole: 'user' | 'admin' | 'professional' | null;
  optOutDataCollection: boolean;
  loading: boolean;
  refreshRole: () => Promise<'user' | 'admin' | 'professional' | null>;
  updateProfile: (data: { optOutDataCollection: boolean }) => Promise<void>;
};

// Create the context with default values
const AuthContext = createContext<AuthContextType>({
  currentUser: null,
  userRole: null,
  optOutDataCollection: false,
  loading: true,
  refreshRole: async () => null,
  updateProfile: async () => {},
});

// Context Provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [userRole, setUserRole] = useState<'user' | 'admin' | 'professional' | null>(null);
  const [optOutDataCollection, setOptOutDataCollection] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);

  const fetchUserRole = async (user: User) => {
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${API_URL}/api/user/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserRole(data.role);
        setOptOutDataCollection(data.optOutDataCollection || false);
        return data.role;
      } else {
        console.error('Failed to fetch user role');
        setUserRole('user'); // Default to user on error
        setOptOutDataCollection(false);
        return 'user';
      }
    } catch (error) {
      console.error('Error fetching user role:', error);
      setUserRole('user');
      setOptOutDataCollection(false);
      return 'user';
    }
  };

  useEffect(() => {
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    let unsubscribe: (() => void) | undefined;
    
    const setupAuth = async () => {
      const firebaseAuth = await getFirebaseAuth();
      if (!firebaseAuth || !firebaseAuth.auth) {
        setLoading(false);
        return;
      }

      unsubscribe = firebaseAuth.onAuthStateChanged(async (user: User | null) => {
        setCurrentUser(user);
        
        if (user) {
          await fetchUserRole(user);
        } else {
          setUserRole(null);
          setOptOutDataCollection(false);
        }
        
        setLoading(false);
      });
    };

    setupAuth();

    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, []);

  const refreshRole = async () => {
    if (currentUser) {
      return await fetchUserRole(currentUser);
    }
    return null;
  };

  const updateProfile = async (data: { optOutDataCollection: boolean }) => {
    if (!currentUser) return;
    
    try {
      const token = await currentUser.getIdToken();
      const response = await fetch(`${API_URL}/api/user/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        setOptOutDataCollection(responseData.optOutDataCollection);
      } else {
        throw new Error('Failed to update profile');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ currentUser, userRole, optOutDataCollection, loading, refreshRole, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth() {
  return useContext(AuthContext);
}
