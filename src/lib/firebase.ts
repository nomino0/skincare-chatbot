'use client';

import { initializeApp, getApps } from 'firebase/app';
import { 
  getAuth,
  onAuthStateChanged as firebaseOnAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  createUserWithEmailAndPassword,
  signOut,
  User,
  sendEmailVerification,
  updateProfile,
  sendPasswordResetEmail,
  Auth
} from 'firebase/auth';
import { 
  getFirestore,  
  collection, 
  addDoc, 
  doc, 
  getDocs,
  updateDoc,
  query, 
  where, 
  orderBy, 
  serverTimestamp,
  Timestamp,
  DocumentData
} from 'firebase/firestore';

// Firebase configuration - using environment variables for security
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

// Debug: Log the config to verify environment variables are loaded
if (typeof window !== 'undefined') {
  console.log('Firebase Config Debug:', {
    apiKey: firebaseConfig.apiKey ? `${firebaseConfig.apiKey.substring(0, 10)}...` : 'MISSING',
    authDomain: firebaseConfig.authDomain || 'MISSING',
    projectId: firebaseConfig.projectId || 'MISSING',
    storageBucket: firebaseConfig.storageBucket || 'MISSING',
    messagingSenderId: firebaseConfig.messagingSenderId || 'MISSING',
    appId: firebaseConfig.appId ? `${firebaseConfig.appId.substring(0, 15)}...` : 'MISSING',
  });
}

// Initialize Firebase only once on the client side
let firebaseApp: ReturnType<typeof initializeApp> | undefined;
let auth: Auth | undefined;
let db: ReturnType<typeof getFirestore> | undefined;

// Function to ensure Firebase is initialized
function initializeFirebaseIfNeeded() {
  if (typeof window === 'undefined') {
    return;
  }

  // If already initialized, return
  if (auth && db) {
    return;
  }

  try {
    // Check if already initialized
    const existingApps = getApps();
    if (existingApps.length === 0) {
      console.log('Initializing Firebase with config:', {
        apiKey: firebaseConfig.apiKey ? '✓ Set' : '✗ Missing',
        authDomain: firebaseConfig.authDomain ? '✓ Set' : '✗ Missing',
        projectId: firebaseConfig.projectId ? '✓ Set' : '✗ Missing',
      });
      firebaseApp = initializeApp(firebaseConfig);
    } else {
      firebaseApp = existingApps[0];
    }
    auth = getAuth(firebaseApp);
    db = getFirestore(firebaseApp);
    console.log('Firebase initialized successfully');
  } catch (error) {
    console.error('Error initializing Firebase:', error);
  }
}

// Initialize on module load for client side
if (typeof window !== 'undefined') {
  initializeFirebaseIfNeeded();
}

// Export auth for direct use
export function getAuthClient(): Auth | null {
  if (typeof window === 'undefined') {
    return null;
  }
  
  // Ensure Firebase is initialized before returning auth
  initializeFirebaseIfNeeded();
  
  if (!auth) {
    console.error('Firebase Auth is not available. Check that Firebase is initialized correctly.');
    return null;
  }
  return auth;
}

// Export auth state change listener for hooks to use
export function onAuthStateChanged(callback: (user: User | null) => void): () => void {
  const authClient = getAuthClient();
  if (!authClient) return () => {};
  
  return firebaseOnAuthStateChanged(authClient, callback);
}

// Authentication functions
export const signIn = (email: string, password: string) => {
  const authClient = getAuthClient();
  if (!authClient) return Promise.reject(new Error('Firebase Auth is only available on the client'));
  return signInWithEmailAndPassword(authClient, email, password);
};

export const signUp = (email: string, password: string) => {
  const authClient = getAuthClient();
  if (!authClient) return Promise.reject(new Error('Firebase Auth is only available on the client'));
  return createUserWithEmailAndPassword(authClient, email, password);
};

export const logout = () => {
  const authClient = getAuthClient();
  if (!authClient) return Promise.reject(new Error('Firebase Auth is only available on the client'));
  return signOut(authClient);
};

// Send verification email
export const sendVerificationEmail = () => {
  const authClient = getAuthClient();
  if (!authClient || !authClient.currentUser) return Promise.reject(new Error('No authenticated user'));
  return sendEmailVerification(authClient.currentUser);
};

// Update user profile
export const updateUserProfile = (displayName?: string, photoURL?: string) => {
  const authClient = getAuthClient();
  if (!authClient || !authClient.currentUser) return Promise.reject(new Error('No authenticated user'));
  return updateProfile(authClient.currentUser, { displayName, photoURL });
};

// Password reset
export const resetPassword = (email: string) => {
  const authClient = getAuthClient();
  if (!authClient) return Promise.reject(new Error('Firebase Auth is only available on the client'));
  return sendPasswordResetEmail(authClient, email);
};

// Google Authentication
const googleProvider = new GoogleAuthProvider();
export const signInWithGoogle = () => {
  const authClient = getAuthClient();
  if (!authClient) return Promise.reject(new Error('Google sign-in is only available on the client'));
  return signInWithPopup(authClient, googleProvider);
};

// Export Firestore for direct use
export function getFirestoreClient() {
  if (typeof window === 'undefined') {
    return null;
  }
  
  // Ensure Firebase is initialized before returning Firestore
  initializeFirebaseIfNeeded();
  
  return db || null;
}

// Types for chat and scan history
export interface ScanHistory {
  userId: string;
  timestamp: Timestamp;
  scanId: string;
  skinResults: any; // Skin prediction results
  messages: ChatMessage[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Timestamp;
  showAnalysis?: boolean;
  suggestions?: string[];
}

// Save a new scan with initial chat history
export const saveScanHistory = async (userId: string, skinResults: any, initialMessages: ChatMessage[]) => {
  try {
    const firestoreClient = getFirestoreClient();
    if (!firestoreClient) {
      console.error('Firestore client not available');
      return null;
    }

    // Create a unique scan ID
    const scanId = Date.now().toString();
    
    // Convert messages to plain objects (Firebase doesn't support serverTimestamp in arrays)
    const messagesForSave = initialMessages.map(msg => ({
      ...msg,
      timestamp: msg.timestamp || Timestamp.now()
    }));
    
    // Add the scan history document
    const docRef = await addDoc(collection(firestoreClient, 'scanHistory'), {
      userId,
      scanId,
      timestamp: serverTimestamp(),
      skinResults,
      messages: messagesForSave
    });
    
    console.log('Scan history saved successfully:', { scanId, docId: docRef.id });
    return { scanId, docId: docRef.id };
  } catch (error) {
    console.error('Error saving scan history:', error);
    return null;
  }
};

// Update chat messages for a specific scan
export const updateChatHistory = async (userId: string, scanId: string, newMessages: ChatMessage[]) => {
  try {
    const firestoreClient = getFirestoreClient();
    if (!firestoreClient) return false;
    
    // Find the scan document
    const scanQuery = query(
      collection(firestoreClient, 'scanHistory'),
      where('userId', '==', userId),
      where('scanId', '==', scanId)
    );
    
    const querySnapshot = await getDocs(scanQuery);
    
    if (querySnapshot.empty) {
      console.error('Scan history not found');
      return false;
    }
    
    // Get the first matching document
    const scanDoc = querySnapshot.docs[0];
    
    // Format new messages with server timestamp
    const messagesWithTimestamp = newMessages.map(msg => ({
      ...msg,
      timestamp: serverTimestamp()
    }));
    
    // Update the main document with the latest messages
    await updateDoc(doc(firestoreClient, 'scanHistory', scanDoc.id), {
      messages: messagesWithTimestamp,
      lastUpdated: serverTimestamp()
    });
    
    console.log('Chat history updated successfully for scan:', scanId);
    return true;
  } catch (error) {
    console.error('Error updating chat history:', error);
    return false;
  }
};

// Get all scan history for a user
export const getUserScanHistory = async (userId: string) => {
  try {
    const firestoreClient = getFirestoreClient();
    if (!firestoreClient) return [];
    
    const scanQuery = query(
      collection(firestoreClient, 'scanHistory'),
      where('userId', '==', userId),
      orderBy('timestamp', 'desc')
    );
    
    const querySnapshot = await getDocs(scanQuery);
    
    return querySnapshot.docs.map(doc => {
      const data = doc.data() as ScanHistory;
      return {
        ...data,
        docId: doc.id,
        // Add derived fields for easier display
        skinType: data.skinResults?.skinType?.type || 'Unknown',
        skinIssuesCount: data.skinResults?.skinIssues?.length || 0,
        lastMessageContent: data.messages?.length > 0 
          ? data.messages[data.messages.length - 1].content 
          : ''
      };
    });
  } catch (error) {
    console.error('Error getting user scan history:', error);
    return [];
  }
};

// Get a specific scan history by ID
export const getScanHistoryById = async (userId: string, scanId: string) => {
  try {
    const firestoreClient = getFirestoreClient();
    if (!firestoreClient) return null;
    
    const scanQuery = query(
      collection(firestoreClient, 'scanHistory'),
      where('userId', '==', userId),
      where('scanId', '==', scanId)
    );
    
    const querySnapshot = await getDocs(scanQuery);
    
    if (querySnapshot.empty) {
      return null;
    }
    
    const scanDoc = querySnapshot.docs[0];
    const data = scanDoc.data() as ScanHistory;
    
    return {
      ...data,
      docId: scanDoc.id
    };
  } catch (error) {
    console.error('Error getting scan history by ID:', error);
    return null;
  }
};
