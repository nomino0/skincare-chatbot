import axios from 'axios';
import { getAuthClient } from '@/lib/firebase';

// Base URL for the API
const API_URL = 'http://localhost:5000';

// Create axios instance with interceptor for Firebase auth
const apiClient = axios.create({
    baseURL: API_URL,
    timeout: 30000
});

// Add request interceptor to include Firebase ID token
apiClient.interceptors.request.use(
    async (config) => {
        try {
            const auth = getAuthClient();
            if (auth?.currentUser) {
                const token = await auth.currentUser.getIdToken();
                config.headers.Authorization = `Bearer ${token}`;
            }
        } catch (error) {
            console.error('Error getting auth token:', error);
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export interface SkinPredictionResult {
    skinType: {
        type: string;
        confidence: number;
    };
    skinIssues: {
        name: string;
        confidence: number;
    }[];
    ai_response?: string;
    demographics?: {
        gender: string;
        age: string;
        race: string;
        confidence: {
            gender: number;
            age: number;
            race: number;
        }
    };
}

export interface UserLocation {
    country: string;
    city?: string;
    lat: number;
    lng: number;
}

export const getUserCountry = async (): Promise<UserLocation> => {
    try {
        const response = await axios.get('https://ipapi.co/json/', { timeout: 5000 });
        return {
            country: response.data.country_name,
            city: response.data.city,
            lat: response.data.latitude,
            lng: response.data.longitude
        };
    } catch (error) {
        console.error('Error getting location:', error);
        return {
            country: 'Unknown',
            city: 'Unknown',
            lat: 0,
            lng: 0
        };
    }
};

export interface ProductRecommendation {
    name: string;
    brand: string;
    price: string;
    currency: string;
    link: string;
    imageUrl: string;
    description: string;
    targetGender?: string;
    targetAgeRange?: string[];
    forSkinType?: string[];
    forSkinIssues?: string[];
}

export const getProductRecommendations = async (
    country: string,
    skinType: string,
    skinIssues: string[],
    gender?: string,
    ageGroup?: string
): Promise<ProductRecommendation[]> => {
    try {
        const response = await apiClient.get(`/api/product-recommendations`, {
            params: { country, skinType, skinIssues, gender, ageGroup }
        });
        return response.data;
    } catch (error) {
        console.error('Error getting product recommendations:', error);
        throw error;
    }
};

export const analyzeSkin = async (imageBase64: string, useGroq: boolean = false): Promise<SkinPredictionResult> => {
    try {
        const response = await apiClient.post(`/api/analyze`, {
            image: imageBase64,
            use_groq: useGroq
        });
        return response.data;
    } catch (error) {
        console.error('Error analyzing skin:', error);
        throw error;
    }
};

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
}

export interface ChatResponse {
    response: string;
    suggestions?: string[];
    productRecommendations?: ProductRecommendation[];
    confidence?: number;
}

export const chatWithAssistant = async (
    message: string,
    conversation: ChatMessage[] = [],
    skinAnalysis?: SkinPredictionResult,
    userLocation?: UserLocation
): Promise<ChatResponse> => {
    try {
        const response = await apiClient.post(`/api/chat`, {
            message,
            conversation,
            skinAnalysis,
            userLocation
        });
        return response.data;
    } catch (error) {
        console.error('Error chatting with assistant:', error);
        throw error;
    }
};

export const sendEmail = async (email: string, results: SkinPredictionResult): Promise<boolean> => {
    try {
        const response = await apiClient.post(`/api/send-analysis-results`, {
            email,
            results
        });
        return response.data.success;
    } catch (error) {
        console.error('Error sending email:', error);
        throw error;
    }
};

export interface DermatologistResult {
    name: string;
    address: string;
    rating: number;
    vicinity: string;
    place_id: string;
}

export const findNearbyDermatologists = async (lat: number, lng: number): Promise<DermatologistResult[]> => {
    try {
        const response = await apiClient.get(`/api/find-dermatologists`, {
            params: { lat, lng }
        });
        return response.data.results;
    } catch (error) {
        console.error('Error finding dermatologists:', error);
        throw error;
    }
};

export interface NearbyStore {
    name: string;
    address: string;
    location: {
        lat: number;
        lng: number;
    };
    rating: number;
    user_ratings_total: number;
    place_id: string;
    open_now?: boolean;
    photo_url?: string;
    store_type: string;
    products_available: string[];
}

export const findNearbyStores = async (
    lat: number,
    lng: number,
    radius: number = 5000,
    productType: string = 'skincare'
): Promise<NearbyStore[]> => {
    try {
        const response = await apiClient.get(`/api/nearby-stores`, {
            params: {
                lat,
                lng,
                radius,
                product_type: productType
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error finding nearby stores:', error);
        return [];
    }
};

export interface NearbyProduct extends ProductRecommendation {
    priceCategory: 'Budget' | 'Moderate' | 'Premium';
    nearbyStores: NearbyStore[];
    storePhotoUrl?: string;
}

export interface NearbyProductsResponse {
    products: NearbyProduct[];
    groupedByPrice: {
        Budget: NearbyProduct[];
        Moderate: NearbyProduct[];
        Premium: NearbyProduct[];
    };
    nearbyStores: NearbyStore[];
}

export const findNearbyProducts = async (
    lat: number,
    lng: number,
    skinType: string,
    skinIssues: string[],
    gender?: string,
    ageGroup?: string,
    radius: number = 5000
): Promise<NearbyProductsResponse> => {
    try {
        const response = await apiClient.get(`/api/nearby-products`, {
            params: {
                lat,
                lng,
                radius,
                skinType,
                skinIssues,
                gender,
                ageGroup
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error finding nearby products:', error);
        return {
            products: [],
            groupedByPrice: { Budget: [], Moderate: [], Premium: [] },
            nearbyStores: []
        };
    }
};

// ===== PHASE 2: NEW API METHODS =====

export interface ScanHistoryItem {
    scanId: string;
    timestamp: string;
    skinType: string | null;
    skinIssues: any[];
    demographics: any;
}

export interface ScanDetails {
    scanId: string;
    timestamp: string;
    skinResults: SkinPredictionResult;
    messages: ChatMessage[];
}

export const getScanHistory = async (): Promise<ScanHistoryItem[]> => {
    try {
        const response = await apiClient.get(`/api/history`);
        return response.data;
    } catch (error) {
        console.error('Error getting scan history:', error);
        throw error;
    }
};

export const getScanDetails = async (scanId: string): Promise<ScanDetails> => {
    try {
        const response = await apiClient.get(`/api/history/${scanId}`);
        return response.data;
    } catch (error) {
        console.error('Error getting scan details:', error);
        throw error;
    }
};

export interface AdminSubmission {
    scanId: string;
    userId: string;
    timestamp: string;
    imagePath: string;
    prediction: {
        skinType: any;
        skinIssues: any[];
        demographics: any;
    };
    hasLabel: boolean;
}

export interface LabelSubmission {
    scanId: string;
    verifiedSkinType: string;
    verifiedIssues: string[];
    notes: string;
}

export const getAdminSubmissions = async (
    status: 'pending' | 'labeled' = 'pending',
    limit: number = 50
): Promise<AdminSubmission[]> => {
    try {
        const response = await apiClient.get(`/api/admin/submissions`, {
            params: { status, limit }
        });
        return response.data;
    } catch (error) {
        console.error('Error getting admin submissions:', error);
        throw error;
    }
};

export const submitLabel = async (label: LabelSubmission): Promise<void> => {
    try {
        await apiClient.post(`/api/admin/label`, label);
    } catch (error) {
        console.error('Error submitting label:', error);
        throw error;
    }
};