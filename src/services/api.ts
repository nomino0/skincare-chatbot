import axios from 'axios';

// Base URL for the API
const API_URL = 'http://localhost:5000'; // Assuming your Python backend runs on port 5000

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

// Add user location tracking
export interface UserLocation {
  country: string;
  city?: string;
  lat: number;
  lng: number;
}

// Function to get user's location including country
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
    // Return default location instead of throwing
    return {
      country: 'Unknown',
      city: 'Unknown',
      lat: 0,
      lng: 0
    };
  }
};

// Function to get products available in user's country
export interface ProductRecommendation {
  name: string;
  brand: string;
  price: string;
  currency: string;
  link: string;
  imageUrl: string;
  description: string;
  targetGender?: string; // 'Male', 'Female', or 'All'
  targetAgeRange?: string[]; // e.g. ['20-29', '30-39']
  forSkinType?: string[]; // e.g. ['Dry', 'Normal']
  forSkinIssues?: string[]; // e.g. ['Acne', 'Redness']
}

export const getProductRecommendations = async (
  country: string,
  skinType: string,
  skinIssues: string[],
  gender?: string,
  ageGroup?: string
): Promise<ProductRecommendation[]> => {
  try {
    const response = await axios.get(`${API_URL}/api/product-recommendations`, {
      params: { country, skinType, skinIssues, gender, ageGroup }
    });
    return response.data;
  } catch (error) {
    console.error('Error getting product recommendations:', error);
    // Instead of returning mock data, throw the error to let the UI handle it
    throw error;
  }
};

// Function to send image to backend for skin prediction
export const analyzeSkin = async (imageBase64: string, useGroq: boolean = false): Promise<SkinPredictionResult> => {
  try {
    const response = await axios.post(`${API_URL}/api/analyze`, {
      image: imageBase64,
      use_groq: useGroq
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing skin:', error);
    throw error;
  }
};

// Chat functionality interfaces
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

// Function to chat with the AI assistant
export const chatWithAssistant = async (
  message: string,
  conversation: ChatMessage[] = [],
  skinAnalysis?: SkinPredictionResult,
  userLocation?: UserLocation
): Promise<ChatResponse> => {
  try {
    const response = await axios.post(`${API_URL}/api/chat`, {
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

// Function to send email with results
export const sendEmail = async (email: string, results: SkinPredictionResult): Promise<boolean> => {
  try {
    const response = await axios.post(`${API_URL}/api/send-analysis-results`, {
      email,
      results
    });
    return response.data.success;
  } catch (error) {
    console.error('Error sending email:', error);
    throw error;
  }
};

// Function to find nearby dermatologists
export interface DermatologistResult {
  name: string;
  address: string;
  rating: number;
  vicinity: string;
  place_id: string;
}

export const findNearbyDermatologists = async (lat: number, lng: number): Promise<DermatologistResult[]> => {
  try {
    const response = await axios.get(`${API_URL}/api/find-dermatologists`, {
      params: { lat, lng }
    });
    return response.data.results;
  } catch (error) {
    console.error('Error finding dermatologists:', error);
    throw error;
  }
};

// Interface for nearby store results
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

// Function to find nearby beauty and skincare stores
export const findNearbyStores = async (
  lat: number, 
  lng: number, 
  radius: number = 5000,
  productType: string = 'skincare'
): Promise<NearbyStore[]> => {
  try {
    const response = await axios.get(`${API_URL}/api/nearby-stores`, {
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

// Interface for nearby product results
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

// Function to find nearby products grouped by price category
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
    const response = await axios.get(`${API_URL}/api/nearby-products`, {
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
    // Return empty response
    return {
      products: [],
      groupedByPrice: { Budget: [], Moderate: [], Premium: [] },
      nearbyStores: []
    };
  }
};