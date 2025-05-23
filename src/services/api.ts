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
  // Detect user's country from browser and adjust currency accordingly
  const userCountry = navigator.language || "en-US";
  const isTunisia = userCountry.includes("TN") || userCountry.includes("AR") || 
                    window.location.hostname.endsWith('.tn');
  
  // Set currency based on location (default to TND for Tunisia)
  const currency = isTunisia ? "TND" : "USD";
  
  // Price conversion factor (approximate)
  const priceFactor = currency === "TND" ? 3.1 : 1; // 1 USD ≈ 3.1 TND
  
  // Mock data - tailored for Tunisian market and international brands available in Tunisia
  const products: ProductRecommendation[] = [
    // Products for dry skin
    {
      name: "Hydrating Facial Cleanser",
      brand: "CeraVe",
      price: (14.99 * priceFactor).toFixed(2),
      currency: currency,
      link: "https://www.cerave.com/skincare/cleansers/hydrating-facial-cleanser",
      imageUrl: "https://www.cerave.com/-/media/project/loreal/brand-sites/cerave/americas/us/products/facial-cleansers/hydrating-facial-cleanser/700x875/cerave_facial_cleanser_16oz_front-700x875-v2.jpg",
      description: "Gentle, moisturizing cleanser with ceramides and hyaluronic acid" + (isTunisia ? " - Available at Fatales and pharmacies in Tunisia" : ""),
      targetGender: "All",
      targetAgeRange: ["20-29", "30-39", "40-49", "50-59"],
      forSkinType: ["Dry", "Normal"]
    },    // Male-specific products
    {
      name: "Men's Moisturizing Face Cream",
      brand: "Nivea Men",
      price: (35 * priceFactor).toFixed(2),
      currency: currency,
      link: "https://www.nivea.tn/produits/nivea-men-creme-hydratante",
      imageUrl: "https://www.nivea.tn/-/media/nivea/local/tn/anti-aging/93373-website-master-local_anti-aging-page-phase2_pdp-image_970x1400px_12.png",
      description: "Energizing face moisturizer for men" + (isTunisia ? " - Available in most supermarkets and pharmacies across Tunisia" : ""),
      targetGender: "Male",
      targetAgeRange: ["20-29", "30-39", "40-49"],
      forSkinType: ["Normal", "Dry"]
    },
    // Products for acne
    {
      name: "Effaclar Duo+ Cream",
      brand: "La Roche-Posay",
      price: (85 * priceFactor).toFixed(2),
      currency: currency,
      link: "https://www.laroche-posay.tn/effaclar/effaclar-duo-creme-anti-imperfections",
      imageUrl: "https://www.laroche-posay.tn/-/media/project/loreal/brand-sites/lrp/africa-me/north-africa/products/effaclar/effaclar-duo--anti-imperfections/la-roche-posay-face-care-effaclar-duo-anti-imperfections-40ml-3337875598071-front.png",
      description: "Dual action acne treatment" + (isTunisia ? " - Available at Para pharmacies and Fatales in Tunisia" : ""),
      targetGender: "All",
      targetAgeRange: ["10-19", "20-29"],
      forSkinType: ["Oily", "Combination"],
      forSkinIssues: ["Acne"]
    },
    // Products for aging skin
    {
      name: "Redermic R Anti-Aging Concentrate",
      brand: "La Roche-Posay",
      price: (110 * priceFactor).toFixed(2),
      currency: currency,
      link: "https://www.laroche-posay.tn/redermic/redermic-r-creme-anti-age-intensif",
      imageUrl: "https://www.laroche-posay.tn/-/media/project/loreal/brand-sites/lrp/africa-me/north-africa/products/redermic/redermic-r-anti-aging/la-roche-posay-face-care-redermic-r-30ml-3337872414091-front.png",
      description: "Retinol formula for reducing signs of aging" + (isTunisia ? " - Found in premium pharmacies and beauty stores in Tunisia" : ""),
      targetGender: "All",
      targetAgeRange: ["30-39", "40-49", "50-59", "60-69"],
      forSkinType: ["All"],
      forSkinIssues: ["Wrinkles", "Fine Lines"]
    },
    // Adding Tunisian local brand
    {
      name: "Argan Oil Face Serum",
      brand: "Tunisie Naturelle",
      price: "49.90",
      currency: "TND",
      link: "https://www.facebook.com/Tunisie.Naturelle/",
      imageUrl: "https://scontent.ftun16-1.fna.fbcdn.net/v/t1.6435-9/123959476_3421100184666921_2298290823891497739_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=5f2048&_nc_ohc=8Js5xj5h4ygAX8Zv9kD&_nc_ht=scontent.ftun16-1.fna&oh=00_AfB8DMDa7LdOKQqTRSjh9OQUa6m6RnPzQXUW4GGAgVD11Q&oe=65962A6D",
      description: "Natural argan oil serum for all skin types - Made in Tunisia with traditional Berber methods",
      targetGender: "All",
      targetAgeRange: ["20-29", "30-39", "40-49", "50-59"],
      forSkinType: ["Dry", "Normal", "Combination"],
      forSkinIssues: ["Dryness", "Wrinkles"]
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
    const response = await axios.get(`${API_URL}/nearby-stores`, {
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
    const response = await axios.get(`${API_URL}/nearby-products`, {
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