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
    const response = await axios.get('https://ipapi.co/json/');
    return {
      country: response.data.country_name,
      city: response.data.city,
      lat: response.data.latitude,
      lng: response.data.longitude
    };
  } catch (error) {
    console.error('Error getting location:', error);
    throw error;
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
    const response = await axios.get(`${API_URL}/product-recommendations`, {
      params: { country, skinType, skinIssues, gender, ageGroup }
    });
    return response.data;
  } catch (error) {
    console.error('Error getting product recommendations:', error);
    // For now, return mock data if the endpoint isn't implemented
    return getMockProductRecommendations(skinType, skinIssues, gender, ageGroup);
  }
};

// Mock function for product recommendations (until backend is implemented)
const getMockProductRecommendations = (
  skinType: string,
  skinIssues: string[],
  gender?: string,
  ageGroup?: string
): ProductRecommendation[] => {
  // Mock data - you'd replace this with actual data
  const products: ProductRecommendation[] = [
    // Products for dry skin
    {
      name: "Hydrating Facial Cleanser",
      brand: "CeraVe",
      price: "14.99",
      currency: "USD",
      link: "https://www.cerave.com/skincare/cleansers/hydrating-facial-cleanser",
      imageUrl: "https://www.cerave.com/-/media/project/loreal/brand-sites/cerave/americas/us/products/facial-cleansers/hydrating-facial-cleanser/700x875/cerave_facial_cleanser_16oz_front-700x875-v2.jpg",
      description: "Gentle, moisturizing cleanser with ceramides and hyaluronic acid",
      targetGender: "All",
      targetAgeRange: ["20-29", "30-39", "40-49", "50-59"],
      forSkinType: ["Dry", "Normal"]
    },
    // Male-specific products
    {
      name: "Men's Moisturizing Face Cream",
      brand: "Kiehl's",
      price: "28.00",
      currency: "USD",
      link: "https://www.kiehls.com/skincare/face-moisturizers/facial-fuel-moisturizer/614.html",
      imageUrl: "https://www.kiehls.com/dw/image/v2/AANG_PRD/on/demandware.static/-/Sites-kiehls-master-catalog/default/dw34709de9/nextgen/men/face-fuel/facial-fuel-energizing-moisture-treatment-for-men-kiehls.jpg",
      description: "Energizing face moisturizer for men",
      targetGender: "Male",
      targetAgeRange: ["20-29", "30-39", "40-49"],
      forSkinType: ["Normal", "Dry"]
    },
    // Products for acne
    {
      name: "Acne Treatment Gel",
      brand: "La Roche-Posay",
      price: "32.00",
      currency: "USD",
      link: "https://www.laroche-posay.us/our-products/acne-oily-skin/face-wash-for-oily-skin/effaclar-duo-acne-treatment-883140500759.html",
      imageUrl: "https://www.laroche-posay.us/dw/image/v2/AANG_PRD/on/demandware.static/-/Sites-lrp-us-master-catalog/default/dw570fc1c5/LRP_Effaclar_Duo_1.7oz_3337875598071_00.jpg",
      description: "Dual action acne treatment",
      targetGender: "All",
      targetAgeRange: ["10-19", "20-29"],
      forSkinType: ["Oily", "Combination"],
      forSkinIssues: ["Acne"]
    },
    // Products for aging skin
    {
      name: "Retinol Serum",
      brand: "The Ordinary",
      price: "7.00",
      currency: "USD",
      link: "https://theordinary.com/en-us/retinol-1-in-squalane-100430.html",
      imageUrl: "https://theordinary.com/dw/image/v2/BFKJ_PRD/on/demandware.static/-/Sites-deciem-master/default/dw1a6c13f4/Images/products/The%20Ordinary/Retinol%201pct%20in%20Squalane%2030ml_Regime_M1.png",
      description: "Retinol formula for reducing signs of aging",
      targetGender: "All",
      targetAgeRange: ["30-39", "40-49", "50-59", "60-69"],
      forSkinType: ["All"],
      forSkinIssues: ["Wrinkles", "Fine Lines"]
    }
  ];
  
  // Filter by skin type, issues, gender and age
  return products.filter(product => {
    // Filter by skin type
    if (product.forSkinType && !product.forSkinType.includes(skinType) && !product.forSkinType.includes("All")) {
      return false;
    }
    
    // Filter by skin issues if any are specified
    if (skinIssues.length > 0 && product.forSkinIssues) {
      let hasMatchingIssue = false;
      for (const issue of skinIssues) {
        if (product.forSkinIssues.includes(issue)) {
          hasMatchingIssue = true;
          break;
        }
      }
      if (!hasMatchingIssue) return false;
    }
    
    // Filter by gender
    if (gender && product.targetGender && product.targetGender !== "All" && product.targetGender !== gender) {
      return false;
    }
    
    // Filter by age group
    if (ageGroup && product.targetAgeRange && !product.targetAgeRange.includes(ageGroup)) {
      return false;
    }
    
    return true;
  });
};

// Function to send image to backend for skin prediction
export const analyzeSkin = async (imageBase64: string, useGroq: boolean = false): Promise<SkinPredictionResult> => {
  try {
    const response = await axios.post(`${API_URL}/analyze`, {
      image: imageBase64,
      use_groq: useGroq
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing skin:', error);
    throw error;
  }
};

// Function to send email with results
export const sendEmail = async (email: string, results: SkinPredictionResult): Promise<boolean> => {
  try {
    const response = await axios.post(`${API_URL}/send-email`, {
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
    const response = await axios.get(`${API_URL}/find-dermatologists`, {
      params: { lat, lng }
    });
    return response.data.results;
  } catch (error) {
    console.error('Error finding dermatologists:', error);
    throw error;
  }
};