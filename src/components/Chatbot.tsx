import React, { useState, useEffect, useRef } from 'react';
import { SkinPredictionResult, sendEmail, findNearbyDermatologists, getUserCountry, findNearbyProducts, NearbyProduct, NearbyProductsResponse, getProductRecommendations, ProductRecommendation } from '../services/api';
import { Button } from '@/components/ui/button';
import SkinAnalysisChart from './SkinAnalysisChart';
import { getAuthClient, saveScanHistory, updateChatHistory, getUserScanHistory, getScanHistoryById, ChatMessage } from '../lib/firebase';
import { Timestamp } from 'firebase/firestore';

// Add this import for the knowledge base
import { skinKnowledgeBase } from '../utils/skinKnowledgeBase';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  showAnalysis?: boolean;
  suggestions?: string[];
  timestamp?: Date;
}

// Match the interface from API
interface DermatologistResult {
  name: string;
  address: string;
  rating: number;
  vicinity: string;
  place_id: string;
}

interface ScanHistoryItem {
  scanId: string;
  timestamp: Date;
  skinResults: SkinPredictionResult;
}

interface ChatbotProps {
  skinResults: SkinPredictionResult | null;
  onNewScanRequest?: () => void; // Callback to request a new scan
  isHistoryScan?: boolean; // Indicates if we're viewing a scan from history
}

const Chatbot: React.FC<ChatbotProps> = ({ skinResults, onNewScanRequest, isHistoryScan = false }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I am Hasna, your dermatology assistant. I can help analyze your skin and provide personalized skincare recommendations. Please take a face scan to get started.',
      suggestions: ['How does this work?', 'What can you help with?']
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [dermatologists, setDermatologists] = useState<DermatologistResult[]>([]);
  const [nearbyProducts, setNearbyProducts] = useState<NearbyProductsResponse | null>(null);
  const [showNearbyProducts, setShowNearbyProducts] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null);
  const [selectedSuggestion, setSelectedSuggestion] = useState<string | null>(null);
  const [hasScanResults, setHasScanResults] = useState<boolean>(false);
  const [currentScanId, setCurrentScanId] = useState<string | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanHistoryItem[]>([]);
  const [isViewingHistory, setIsViewingHistory] = useState<boolean>(false);
  const [showHistoryPanel, setShowHistoryPanel] = useState<boolean>(false);

  // Load user's scan history from Firebase
  useEffect(() => {
    const loadScanHistory = async () => {
      const auth = getAuthClient();
      if (auth?.currentUser) {
        try {
          const history = await getUserScanHistory(auth.currentUser.uid);
          const formattedHistory = history.map(item => ({
            scanId: item.scanId,
            timestamp: item.timestamp instanceof Date ? item.timestamp : new Date(item.timestamp.seconds * 1000),
            skinResults: item.skinResults
          }));
          setScanHistory(formattedHistory);
        } catch (error) {
          console.error('Error loading scan history:', error);
        }
      }
    };

    loadScanHistory();
  }, []);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Function to generate responses using the LLM
  const generateLLMResponse = async (prompt: string, context?: any) => {
    setIsLoading(true);
    try {
      // In a real implementation, this would call your backend API to use GROQ
      // For now, we'll simulate a response
      
      // Build context for the LLM
      const skinType = skinResults?.skinType.type.toLowerCase() || '';
      const skinIssues = skinResults?.skinIssues.map(issue => issue.name.toLowerCase()) || [];
      
      let response = "";
      let showAnalysis = false;
      let suggestions: string[] = [];
      
      // Just for demo purposes - in reality this would be handled by the LLM
      // This simulates what the LLM would do with the knowledge base
      if (prompt.includes("skin results") || prompt.includes("analyze my skin")) {
        // Initial analysis response
        showAnalysis = true;
        
        if (skinResults?.ai_response) {
          response = `${skinResults.ai_response}`;
        } else {
          response = `I've completed your skin analysis, and here's what I found! Your primary skin type is ${skinResults?.skinType.type}.`;
          
          if (skinIssues.length > 0) {
            response += ` I've also identified some specific concerns that we can address together.`;
          } else {
            response += ` I'm pleased to report that your skin looks quite healthy with no significant concerns detected!`;
          }
        }
        
        // Add suggestions after analysis
        suggestions = [
          'Recommend products',
          'Suggest a routine',
          'Find a dermatologist',
          'Tell me more about my skin type'
        ];
      } else if (prompt.includes("routine") || prompt.includes("regimen")) {
        // Get a routine response from the knowledge base
        response = skinKnowledgeBase.getRoutine(skinType, skinIssues);
        suggestions = ['Morning routine', 'Evening routine', 'Weekly treatments'];      } else if (prompt.includes("product") || prompt.includes("recommend")) {
        // Get text recommendations from the knowledge base (as fallback)
        response = skinKnowledgeBase.getProductRecommendations(skinType, skinIssues);
        suggestions = ['Budget options', 'Luxury products', 'Natural ingredients'];
        
        try {
          // Get actual product recommendations with Tunisian currency and localization
          const realProducts = await getProductRecommendations(
            "Tunisia", // Set to Tunisia for proper currency
            skinResults?.skinType.type || '',
            skinResults?.skinIssues.map(issue => issue.name) || [],
            skinResults?.demographics?.gender,
            skinResults?.demographics?.age
          );
          
          // Create product data for visualization
          const onlineProducts: NearbyProduct[] = realProducts.map(product => {
            // Determine price category based on price
            let priceCategory: 'Budget' | 'Moderate' | 'Premium';
            const price = parseFloat(product.price);
            
            if (product.currency === 'TND') {
              priceCategory = price < 50 ? 'Budget' : price < 100 ? 'Moderate' : 'Premium';
            } else {
              priceCategory = price < 15 ? 'Budget' : price < 30 ? 'Moderate' : 'Premium';
            }
            
            return {
              ...product,
              priceCategory,
              nearbyStores: []
            };
          });
          
          // Group by price
          const groupedProducts = {
            Budget: onlineProducts.filter(p => p.priceCategory === 'Budget'),
            Moderate: onlineProducts.filter(p => p.priceCategory === 'Moderate'),
            Premium: onlineProducts.filter(p => p.priceCategory === 'Premium')
          };
          
          // Set the state to display products
          setNearbyProducts({
            products: onlineProducts,
            groupedByPrice: groupedProducts,
            nearbyStores: []
          });
          setShowNearbyProducts(true);
          
          // Update response for Tunisian products
          response = "Here are some skincare products available in Tunisia that would work well for your skin type. I've organized them by price category.";
          
        } catch (error) {
          console.error('Error getting Tunisian product recommendations:', error);
          // Fallback to text response already set above
        }
      } else if (prompt.includes("doctor") || prompt.includes("dermatologist")) {
        response = "I'd be happy to help you find a dermatologist nearby! I'll need to access your location for that. Is it okay if I access your location?";
        suggestions = ['Yes, share my location', 'Not now'];
      } else if (prompt.toLowerCase().includes("yes, share my location")) {
        // User agreed to share location
        getUserLocation();
        response = "Thank you! I'm searching for dermatologists near you...";
      } else {
        // General conversation - this would be handled more naturally by the LLM
        response = skinKnowledgeBase.getGeneralResponse(prompt, skinType, skinIssues);
        suggestions = ['Tell me about my skin', 'Skincare tips', 'Product recommendations'];      }
      
      addAssistantMessage(response, showAnalysis, suggestions);
      
      // Save chat history after each assistant response
      if (hasScanResults && currentScanId && !isHistoryScan) {
        setTimeout(() => {
          saveChatSession();
        }, 500); // Small delay to ensure the new message is included
      }
    } catch (error) {
      console.error('Error generating LLM response:', error);
      addAssistantMessage("I seem to be having a technical hiccup. Could we try that again?");
    } finally {
      setIsLoading(false);
    }
  };
  // Find dermatologists
  const findDermatologists = async (lat: number, lng: number) => {
    try {
      const results = await findNearbyDermatologists(lat, lng);
      setDermatologists(results);
      if (results.length > 0) {
        addAssistantMessage(`I've found ${results.length} dermatologists near you. Here are the top options:`, false, ['Make an appointment', 'See more options']);
      } else {
        addAssistantMessage("I couldn't find any dermatologists in your immediate area. Try expanding your search radius or consult your healthcare provider for a referral.");
      }
    } catch (error) {
      console.error('Error finding dermatologists:', error);
      addAssistantMessage("I'm having trouble finding dermatologists right now. Please try again later or search online for dermatologists in your area.");
    }
  };

  // Find nearby products with skin profile
  const findNearbyProductsForSkin = async (lat: number, lng: number) => {
    try {
      setIsLoading(true);
      addAssistantMessage("Searching for skincare products near you that match your skin profile...");
      
      const results = await findNearbyProducts(
        lat, 
        lng, 
        skinResults?.skinType.type || '', 
        skinResults?.skinIssues.map(issue => issue.name) || [],
        skinResults?.demographics?.gender,
        skinResults?.demographics?.age
      );
      
      if (results.products.length > 0) {
        setNearbyProducts(results);
        setShowNearbyProducts(true);
        
        // Give a friendly message about the products
        let budgetCount = results.groupedByPrice.Budget.length;
        let moderateCount = results.groupedByPrice.Moderate.length;
        let premiumCount = results.groupedByPrice.Premium.length;
        
        let message = `I've found ${results.products.length} skincare products near you that would work well for your ${skinResults?.skinType.type || ''} skin!`;
        
        if (budgetCount > 0 && moderateCount > 0 && premiumCount > 0) {
          message += ` I've grouped them by price range so you can find options that fit your budget.`;
        } else if (budgetCount > 0) {
          message += ` There are some great budget-friendly options available.`;
        } else if (premiumCount > 0) {
          message += ` There are some premium products that would be excellent for your skin concerns.`;
        }
        
        addAssistantMessage(message, false, ['Show budget options', 'Show premium options', 'Close']);
      } else {
        addAssistantMessage(
          "I couldn't find any specific products near you that match your skin profile. Would you like to see some online options instead?",
          false,
          ['Show online options', 'Tell me more about my skin type']
        );
      }
    } catch (error) {
      console.error('Error finding nearby products:', error);
      addAssistantMessage(
        "I'm having trouble finding products near you right now. Would you like to see some general recommendations instead?",
        false,
        ['Show general recommendations', 'Try again later']
      );
    } finally {
      setIsLoading(false);
    }
  };
  // Find nearby stores with skincare products
  const findSkinCareStores = async (lat: number, lng: number, productType: string = 'skincare') => {
    try {
      const results = await findNearbyProducts(lat, lng, skinResults?.skinType.type || '', skinResults?.skinIssues.map(issue => issue.name) || []);
      
      if (results.products.length > 0) {
        // Extract unique stores from products
        const uniqueStores = Array.from(
          new Set(
            results.products
              .filter(product => product.nearbyStores && product.nearbyStores.length > 0)
              .flatMap(product => product.nearbyStores || [])
              .map(store => store.place_id)
          )
        );
        
        const stores = results.products
          .flatMap(product => product.nearbyStores || [])
          .filter((store, index, self) => 
            index === self.findIndex(s => s.place_id === store.place_id)
          );
        
        let storeMessage = `I've found ${stores.length} stores near you that carry skincare products. Here are some options:\n\n`;
        
        // Add the top 3 stores to the message
        stores.slice(0, 3).forEach((store, index) => {
          storeMessage += `${index + 1}. **${store.name}**\n`;
          storeMessage += `   📍 ${store.address || 'Address unavailable'}\n`;
          if (store.rating) {
            storeMessage += `   ⭐ Rating: ${store.rating}/5 (${store.user_ratings_total || 'N/A'} reviews)\n`;
          }
          storeMessage += `   ${store.open_now ? '✅ Open now' : '❌ Currently closed'}\n`;
          storeMessage += '\n';
        });
        
        addAssistantMessage(
          storeMessage,
          false, 
          ['Get directions', 'More stores', 'Product recommendations']
        );
      } else {
        addAssistantMessage(
          "I couldn't find any skincare stores in your immediate area. Would you like to try online shopping instead?",
          false,
          ['Online shopping options', 'Expand search radius']
        );
      }
    } catch (error) {
      console.error('Error finding nearby stores:', error);
      addAssistantMessage(
        "I'm having trouble finding stores near you right now. Would you like to see some online product recommendations instead?",
        false,
        ['Show online options', 'Try again later']
      );
    }
  };  // Enhanced getUserLocation to support both dermatologists and products searches
  const getUserLocation = (searchType: 'dermatologists' | 'products' = 'dermatologists') => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          setUserLocation({ lat, lng });
          
          // Determine which search to perform
          if (searchType === 'dermatologists') {
            findDermatologists(lat, lng);
          } else {
            findNearbyProductsForSkin(lat, lng);
          }
        },
        (error) => {
          console.error('Error getting location:', error);
          addAssistantMessage(
            `I couldn't access your location. You can try again or explore online options instead.`,
            false,
            ['Try again', 'Online options']
          );
        }
      );
    } else {
      addAssistantMessage(
        `Location services are not supported by your browser. Would you like to see online product recommendations instead?`,
        false,
        ['Online options', 'Show product recommendations']
      );
    }  };

  // Add a message from the assistant
  const addAssistantMessage = (content: string, showAnalysis: boolean = false, suggestions: string[] = []) => {
    setMessages(prevMessages => [
      ...prevMessages, 
      { 
        role: 'assistant', 
        content, 
        showAnalysis,
        suggestions
      }
    ]);
  };  // Handle user message
  const handleUserMessage = async (userMessage: string) => {
    setInputValue('');
    
    // Check if we have scan results before responding (except for general questions)
    if (!hasScanResults && 
        !userMessage.toLowerCase().includes('how does this work') && 
        !userMessage.toLowerCase().includes('what can you help with')) {
      addAssistantMessage(
        "I need to analyze your skin before I can give personalized advice. Please take a face scan first.",
        false,
        ['How does this work?', 'What can you help with?']
      );
      return;
    }
    
    // Check for specific requests before sending to LLM
    const lowerCaseMessage = userMessage.toLowerCase();
    
    // Check if user is asking about nearby dermatologists
    if (lowerCaseMessage.includes('dermatologist') && 
        (lowerCaseMessage.includes('near') || lowerCaseMessage.includes('nearby') || 
         lowerCaseMessage.includes('find') || lowerCaseMessage.includes('local'))) {
      addAssistantMessage("I'd be happy to help you find a dermatologist nearby! I'll need to access your location for that. Is it okay if I access your location?");
      return;
    }
      // Check if user is asking about nearby products or stores
    if ((lowerCaseMessage.includes('product') || lowerCaseMessage.includes('buy') || 
         lowerCaseMessage.includes('purchase') || lowerCaseMessage.includes('where') || 
         lowerCaseMessage.includes('nearby') || lowerCaseMessage.includes('local') ||
         lowerCaseMessage.includes('recommend') || lowerCaseMessage.includes('skincare')) && 
        (lowerCaseMessage.includes('near') || lowerCaseMessage.includes('nearby') || 
         lowerCaseMessage.includes('find') || lowerCaseMessage.includes('where can i') || 
         lowerCaseMessage.includes('available') || lowerCaseMessage.includes('get'))) {
      
      if (nearbyProducts) {
        // We already have product data, just show it
        setShowNearbyProducts(true);
        addAssistantMessage("Here are the skincare products I recommend for your skin profile that are available nearby:", false,
          ['Show budget options', 'Show premium options', 'Close']);
        return;
      } else {
        // Need to get location and search for products
        addAssistantMessage("I can help you find skincare products nearby that match your skin profile! I'll need to access your location for that. Is it okay if I access your location?", false,
          ['Yes, share my location', 'No, show online options']);
        return;
      }
    }
      // Handle direct requests for product categories
    if (lowerCaseMessage.includes('budget option') || 
        lowerCaseMessage.includes('cheap product') || 
        lowerCaseMessage.includes('affordable') ||
        lowerCaseMessage.includes('show budget options')) {
      
      if (nearbyProducts) {
        // We already have product data, just highlight budget options
        setShowNearbyProducts(true);
        addAssistantMessage("Here are some budget-friendly options for your skin type!");
        return;
      } else if (userLocation) {
        // We have location but no products yet
        findNearbyProductsForSkin(userLocation.lat, userLocation.lng);
        return;
      } else {
        // Need to get location first
        addAssistantMessage("I'll need your location to find affordable products near you. Is it okay if I access your location?");
        return;
      }
    }
    
    if (lowerCaseMessage.includes('premium') || 
        lowerCaseMessage.includes('high end') || 
        lowerCaseMessage.includes('luxury') ||
        lowerCaseMessage.includes('show premium options')) {
      
      if (nearbyProducts) {
        // We already have product data, just highlight premium options
        setShowNearbyProducts(true);
        addAssistantMessage("Here are some premium options for your skin type!");
        return;
      } else if (userLocation) {
        // We have location but no products yet
        findNearbyProductsForSkin(userLocation.lat, userLocation.lng);
        return;
      } else {
        // Need to get location first
        addAssistantMessage("I'll need your location to find premium products near you. Is it okay if I access your location?");
        return;
      }
    }
      // Handle showing moderate price products
    if (lowerCaseMessage.includes('moderate') || 
        lowerCaseMessage.includes('mid-range') || 
        lowerCaseMessage.includes('medium price') ||
        lowerCaseMessage.includes('show moderate options')) {
      
      if (nearbyProducts) {
        // We already have product data, just highlight moderate options
        setShowNearbyProducts(true);
        addAssistantMessage("Here are some moderately priced options for your skin type!");
        return;
      } else if (userLocation) {
        // We have location but no products yet
        findNearbyProductsForSkin(userLocation.lat, userLocation.lng);
        return;
      } else {
        // Need to get location first
        addAssistantMessage("I'll need your location to find moderately priced products near you. Is it okay if I access your location?");
        return;
      }
    }
      // Handle online options
    if (lowerCaseMessage.includes('online') || 
        lowerCaseMessage.includes('internet') || 
        lowerCaseMessage.includes('website') ||
        lowerCaseMessage.includes('shop online') ||
        lowerCaseMessage.includes('no, show online options') ||
        lowerCaseMessage.includes('show online options') ||
        lowerCaseMessage.includes('recommend products')) {
      
      // First, show a loading message
      addAssistantMessage("Let me find some skincare products available in Tunisia that would work well for your skin type...");
      
      try {
        // Get actual product recommendations with Tunisian currency and localization
        const skinType = skinResults?.skinType.type || '';
        const skinIssues = skinResults?.skinIssues.map(issue => issue.name) || [];
        const gender = skinResults?.demographics?.gender;
        const ageGroup = skinResults?.demographics?.age;
        
        // Get product recommendations from our mock API (which now has Tunisian products)
        const realProducts = await getProductRecommendations(
          "Tunisia", // Explicitly set to Tunisia
          skinType,
          skinIssues,
          gender,
          ageGroup
        );
        
        // Create proper NearbyProducts data
        const onlineProducts: NearbyProduct[] = realProducts.map(product => {
          // Determine price category based on price
          let priceCategory: 'Budget' | 'Moderate' | 'Premium';
          const price = parseFloat(product.price);
          
          if (product.currency === 'TND') {
            priceCategory = price < 50 ? 'Budget' : price < 100 ? 'Moderate' : 'Premium';
          } else {
            priceCategory = price < 15 ? 'Budget' : price < 30 ? 'Moderate' : 'Premium';
          }
          
          return {
            ...product,
            priceCategory,
            nearbyStores: []
          };
        });
        
        // Group by price
        const groupedProducts = {
          Budget: onlineProducts.filter(p => p.priceCategory === 'Budget'),
          Moderate: onlineProducts.filter(p => p.priceCategory === 'Moderate'),
          Premium: onlineProducts.filter(p => p.priceCategory === 'Premium')
        };
        
        // Set the state to display products
        setNearbyProducts({
          products: onlineProducts,
          groupedByPrice: groupedProducts,
          nearbyStores: []
        });
        setShowNearbyProducts(true);
        
        // Add assistant message
        addAssistantMessage(
          "Here are some products available in Tunisia that would work well for your skin type! I've organized them by price category.",
          false,
          ['Tell me more about these products', 'How should I use these?', 'Find local stores']
        );
        
      } catch (error) {
        console.error('Error getting product recommendations:', error);
        
        // Fallback to text recommendations from knowledge base
        const skinType = skinResults?.skinType.type.toLowerCase() || '';
        const skinIssues = skinResults?.skinIssues.map(issue => issue.name.toLowerCase()) || [];
        let response = skinKnowledgeBase.getProductRecommendations(skinType, skinIssues);
        addAssistantMessage(response, false, 
          ['Tell me more about these products', 'How should I use these?', 'Find local stores']);
      }
      
      return;
    }
    
    // Handle close request for products display
    if (lowerCaseMessage.includes('close') && showNearbyProducts) {
      setShowNearbyProducts(false);
      addAssistantMessage("I've closed the product recommendations. Is there anything else you'd like to know about your skin?");
      return;
    }    // Check if user agreed to share location for products
    if ((lowerCaseMessage.includes('yes') || lowerCaseMessage.includes('sure') || 
         lowerCaseMessage.includes('okay') || lowerCaseMessage.includes('ok')) && 
        (lowerCaseMessage.includes('location') || lowerCaseMessage.includes('share') || 
         lowerCaseMessage.includes('access') || lowerCaseMessage === 'yes, share my location') && 
        (messages[messages.length-1]?.content?.includes('skincare products nearby') ||
         messages[messages.length-1]?.content?.includes('products near you') ||
         messages[messages.length-1]?.content?.includes('find affordable products') ||
         messages[messages.length-1]?.content?.includes('find premium products') ||
         messages[messages.length-1]?.content?.includes('find moderately priced products'))) {
      // User agreed to share location for products
      getUserLocation('products');
      addAssistantMessage("Thank you! I'm searching for skincare products near you that match your skin profile...");
      return;
    }
    
    // Check if user agreed to share location for dermatologists
    if ((lowerCaseMessage.includes('yes') || lowerCaseMessage.includes('sure') || 
         lowerCaseMessage.includes('okay') || lowerCaseMessage.includes('ok')) && 
        (lowerCaseMessage.includes('location') || lowerCaseMessage.includes('share') || 
         lowerCaseMessage.includes('access') || lowerCaseMessage === 'yes, share my location') && 
        messages[messages.length-1]?.content?.includes('dermatologist nearby')) {
      // User agreed to share location for dermatologists
      getUserLocation('dermatologists');
      addAssistantMessage("Thank you! I'm searching for dermatologists near you...");
      return;
    }
    
    // Process message with LLM for other cases
    generateLLMResponse(userMessage);
    
    // Save chat history after each message if we have scan results
    if (hasScanResults && currentScanId) {
      setTimeout(() => {
        saveChatSession();
      }, 500); // Small delay to ensure the new message is included
    }
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion: string) => {
    setSelectedSuggestion(suggestion);
    setTimeout(() => {
      setMessages(prevMessages => [
        ...prevMessages,
        { role: 'user', content: suggestion }
      ]);
      handleUserMessage(suggestion);
      setSelectedSuggestion(null);
    }, 300);
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    
    const userMessage = inputValue.trim();
    setMessages(prevMessages => [
      ...prevMessages,
      { role: 'user', content: userMessage }
    ]);
    
    handleUserMessage(userMessage);
  };

  // Clear chat and create new scan session
  const handleNewScan = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Starting a new skin analysis session. Please wait while I process your scan...',
        suggestions: []
      }
    ]);
    setHasScanResults(false);
    setCurrentScanId(null);
    setIsViewingHistory(false);
    setShowHistoryPanel(false);
  };
  // Save the current chat session to Firebase
  const saveChatSession = async () => {
    if (!skinResults || !currentScanId) {
      console.log('Cannot save chat session - missing data:', { 
        hasSkinResults: !!skinResults, 
        hasCurrentScanId: !!currentScanId 
      });
      return;
    }
    
    const auth = getAuthClient();
    if (!auth?.currentUser) {
      console.log('Cannot save chat session - no authenticated user');
      return;
    }
    
    const userId = auth.currentUser.uid;
    console.log('Saving chat session for scan:', currentScanId);
    
    // Format messages for Firestore
    const firestoreMessages = messages.map(msg => ({
      role: msg.role,
      content: msg.content,
      showAnalysis: msg.showAnalysis || false,
      suggestions: msg.suggestions || [],
      timestamp: Timestamp.now() // Use Firebase Timestamp
    })) as ChatMessage[];
    
    // Update the chat history in Firestore
    try {
      const success = await updateChatHistory(userId, currentScanId, firestoreMessages);
      if (success) {
        console.log('Chat history updated successfully');
      } else {
        console.error('Failed to update chat history');
      }
    } catch (error) {
      console.error('Error saving chat session:', error);
    }
  };

  // Load a specific scan history
  const loadScanHistorySession = async (scanId: string) => {
    const auth = getAuthClient();
    if (!auth?.currentUser) return;
    
    try {
      const historyData = await getScanHistoryById(auth.currentUser.uid, scanId);
      
      if (historyData) {
        // Set the current scan ID
        setCurrentScanId(scanId);
        setIsViewingHistory(true);
        
        // Set the skin results
        // This is a simplified approach - in a real app you might need to convert timestamps
        const formattedMessages = historyData.messages.map(msg => ({
          role: msg.role,
          content: msg.content,
          showAnalysis: msg.showAnalysis || false,
          suggestions: msg.suggestions || []
        }));
        
        setMessages(formattedMessages);
        setHasScanResults(true);
      }
    } catch (error) {
      console.error('Error loading scan history session:', error);
    }
  };

  // Request a new scan
  const requestNewScan = () => {
    if (onNewScanRequest) {
      onNewScanRequest();
    }
  };
  // Add skin analysis results as a message when they become available
  useEffect(() => {
    if (skinResults && !isViewingHistory) {
      // Set scan status
      setHasScanResults(true);
      
      // For history scans, don't save to Firebase again
      if (isHistoryScan) {
        // Just update the UI state
        setCurrentScanId(Date.now().toString());
        generateLLMResponse("Analyze these skin results and provide a friendly summary", skinResults);
        return;
      }
      
      // Generate a scan ID if we don't have one
      if (!currentScanId) {
        setCurrentScanId(Date.now().toString());
      }
        // Save the initial scan to Firebase
      const saveInitialScan = async () => {
        const auth = getAuthClient();
        if (auth?.currentUser) {
          try {
            console.log('Attempting to save scan for user:', auth.currentUser.uid);
            console.log('Skin results:', skinResults);
            
            const initialMessages = [
              {
                role: 'assistant' as const,
                content: 'I\'ve completed your skin analysis. Examining the results...',
                showAnalysis: false,
                suggestions: [],
                timestamp: Timestamp.now()
              }
            ] as ChatMessage[];
            
            const result = await saveScanHistory(
              auth.currentUser.uid,
              skinResults,
              initialMessages
            );
            
            if (result) {
              console.log('Scan saved successfully with ID:', result.scanId);
              setCurrentScanId(result.scanId);
            } else {
              console.error('Failed to save scan - no result returned');
            }
          } catch (error) {
            console.error('Error saving initial scan:', error);
            // Show user-friendly error message
            addAssistantMessage("I'm having trouble saving your scan data. Please check your internet connection and try again.");
          }
        } else {
          console.error('No authenticated user found');
        }
      };
      
      saveInitialScan();
      
      // Use the LLM to generate a natural response based on the skin results
      generateLLMResponse("Analyze these skin results and provide a friendly summary", skinResults);
    }
  }, [skinResults, isViewingHistory, isHistoryScan, currentScanId]);
  
  // Helper function to get online product recommendations with proper currency and localization
  const getOnlineProductRecommendations = async () => {
    try {
      const skinType = skinResults?.skinType.type || '';
      const skinIssues = skinResults?.skinIssues.map(issue => issue.name) || [];
      const gender = skinResults?.demographics?.gender;
      const ageGroup = skinResults?.demographics?.age;
      
      // Try to get actual product recommendations from API with proper localization
      const realProducts = await getProductRecommendations(
        "Tunisia", // Set to Tunisia for proper currency
        skinType,
        skinIssues,
        gender,
        ageGroup
      );
      
      // Convert to NearbyProduct format
      const onlineProducts: NearbyProduct[] = realProducts.map(product => {
        // Determine price category based on price
        let priceCategory: 'Budget' | 'Moderate' | 'Premium';
        const price = parseFloat(product.price);
        
        if (product.currency === 'TND') {
          priceCategory = price < 50 ? 'Budget' : price < 100 ? 'Moderate' : 'Premium';
        } else {
          priceCategory = price < 15 ? 'Budget' : price < 30 ? 'Moderate' : 'Premium';
        }
        
        return {
          ...product,
          priceCategory,
          nearbyStores: []
        };
      });
      
      // Group by price
      const groupedProducts = {
        Budget: onlineProducts.filter(p => p.priceCategory === 'Budget'),
        Moderate: onlineProducts.filter(p => p.priceCategory === 'Moderate'),
        Premium: onlineProducts.filter(p => p.priceCategory === 'Premium')
      };
      
      // Set the state to display products
      setNearbyProducts({
        products: onlineProducts,
        groupedByPrice: groupedProducts,
        nearbyStores: []
      });
      setShowNearbyProducts(true);
      
      return {
        success: true,
        message: "Here are some product recommendations for your skin type available in Tunisia! I've organized them by price category."
      };
    } catch (error) {
      console.error('Error getting real product recommendations:', error);
      return {
        success: false,
        message: "I couldn't find localized product recommendations. Here are some general options that might work for your skin type."
      };
    }
  };
  
  return (
    <div className="flex flex-col h-[80vh] bg-background rounded-xl shadow-lg futuristic-panel overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-primary flex items-center justify-between rounded-t-xl">
        <h2 className="text-lg font-secondary font-semibold text-white">Skin Assistant</h2>
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => setShowHistoryPanel(!showHistoryPanel)}
            className="p-1.5 rounded-full bg-white/10 hover:bg-white/20 text-white/90 transition-all"
            title="View History"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          <button 
            onClick={requestNewScan}
            className="p-1.5 rounded-full bg-white/10 hover:bg-white/20 text-white/90 transition-all"
            title="New Scan"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          <span className="inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Scan History Panel */}
        {showHistoryPanel && (
          <div className="w-56 border-r border-border bg-background/50 backdrop-blur-sm animate-slide-in-left">
            <div className="p-3 border-b border-border">
              <h3 className="text-sm font-medium">Scan History</h3>
              <p className="text-xs text-muted-foreground">Previous analyses</p>
            </div>
            <div className="overflow-y-auto h-full">
              {scanHistory.length > 0 ? (
                scanHistory.map((scan, i) => (
                  <button 
                    key={i}
                    onClick={() => loadScanHistorySession(scan.scanId)}
                    className={`w-full p-3 text-left border-b border-border hover:bg-primary/5 transition-colors ${currentScanId === scan.scanId ? 'bg-primary/10' : ''}`}
                  >
                    <div className="flex items-center mb-1">
                      <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center mr-2 text-primary">
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                        </svg>
                      </div>
                      <span className="text-xs font-medium truncate">
                        Skin Analysis
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground pl-8">
                      {new Date(scan.timestamp).toLocaleDateString()} · {new Date(scan.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </p>
                  </button>
                ))
              ) : (
                <div className="p-4 text-center text-muted-foreground text-sm">
                  No scan history yet
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ scrollbarWidth: 'thin' }}>
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'assistant' ? 'justify-start' : 'justify-end'}`}>
              <div 
                className={`${
                  message.role === 'assistant' 
                    ? 'bot-message' 
                    : 'user-message'
                } max-w-[85%]`}
              >
                {/* Message content */}
                <div className="whitespace-pre-line">
                  {message.content}
                </div>
                
                {/* Skin analysis visualization */}
                {message.showAnalysis && skinResults && (
                  <div className="mt-4">
                    <SkinAnalysisChart skinResults={skinResults} />
                  </div>
                )}
                
                {/* Suggestion chips */}
                {message.role === 'assistant' && message.suggestions && message.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {message.suggestions.map((suggestion, i) => (
                      <button
                        key={i}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className={`text-xs px-3 py-1.5 rounded-full border border-primary/30 bg-primary/10 hover:bg-primary/20 text-primary transition-all duration-200 ${selectedSuggestion === suggestion ? 'bg-primary/30' : ''}`}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bot-message !p-3">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-primary/70 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-primary/70 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-primary/70 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      {/* Dermatologists Results */}
      {dermatologists.length > 0 && (
        <div className="p-4 bg-background/50 backdrop-blur-sm border-t border-border flex-shrink-0">
          <h3 className="font-medium gradient-text mb-2">Nearby Dermatologists</h3>
          <div className="overflow-x-auto pb-2">
            <div className="flex space-x-4">
              {dermatologists.slice(0, 5).map((doctor, index) => (
                <div key={index} className="min-w-[220px] p-3 futuristic-panel rounded-lg">
                  <div className="flex items-center mb-1">
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center mr-2">
                      <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <p className="font-secondary font-medium text-sm">{doctor.name}</p>
                  </div>
                  <p className="text-xs text-muted-foreground mb-1">{doctor.vicinity}</p>
                  <div className="flex items-center">
                    <div className="flex">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <svg key={i} className={`w-3 h-3 ${i < Math.floor(doctor.rating || 0) ? 'text-amber-400' : 'text-gray-300'}`} fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      ))}
                    </div>
                    <span className="text-xs ml-1 text-muted-foreground">{doctor.rating?.toFixed(1) || 'N/A'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
        {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-border flex-shrink-0">
        {!hasScanResults && (
          <div className="mb-3 px-4 py-2 bg-primary/10 text-primary text-sm rounded-lg flex items-center">
            <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{isViewingHistory ? "You're viewing a previous scan. Take a new scan to continue." : "Please take a face scan to get personalized recommendations."}</span>
          </div>
        )}
        
        {isViewingHistory && (
          <div className="mb-3 flex space-x-2">
            <Button 
              onClick={requestNewScan}
              variant="outline" 
              className="w-full text-sm"
            >
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              </svg>
              Take New Scan
            </Button>
          </div>
        )}
        
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={hasScanResults ? "Type your message..." : "Ask how it works or take a scan to begin"}
            className="flex-1 p-3 bg-background font-sans border border-border rounded-full focus:ring-2 focus:ring-primary/30 focus:border-primary focus:outline-none transition-all duration-200"
            disabled={isLoading || (isViewingHistory && !hasScanResults)}
          />
          <Button
            type="submit"
            disabled={isLoading || !inputValue.trim() || (isViewingHistory && !hasScanResults)}
            className="rounded-full h-12 w-12 p-0 bg-primary hover:shadow-lg transition-all duration-300 hover:opacity-90"
          >
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </Button>
        </div>
      </form>
        {/* Nearby Products Display - New Component */}
      {showNearbyProducts && nearbyProducts && (
        <div className="p-4 border-t border-border flex-shrink-0">
          <h3 className="font-medium gradient-text mb-2">Recommended Products Near You</h3>
          <NearbyProductsDisplay 
            products={nearbyProducts} 
            onClose={() => setShowNearbyProducts(false)} 
          />
        </div>
      )}
    </div>
  );
};

// NearbyProductsDisplay component to show products classified by price
interface NearbyProductsDisplayProps {
  products: NearbyProductsResponse;
  onClose: () => void;
}

const NearbyProductsDisplay: React.FC<NearbyProductsDisplayProps> = ({ products, onClose }) => {
  const [activeCategory, setActiveCategory] = useState<'Budget' | 'Moderate' | 'Premium'>('Moderate');
  
  const categories = [
    { value: 'Budget', label: '💰 Budget' },
    { value: 'Moderate', label: '💰💰 Moderate' },
    { value: 'Premium', label: '💰💰💰 Premium' }
  ] as const;
  
  // Check if the active category has any products, if not switch to one that does
  useEffect(() => {
    if (products.groupedByPrice[activeCategory].length === 0) {
      // Find the first category that has products
      const categoryWithProducts = categories.find(
        category => products.groupedByPrice[category.value].length > 0
      );
      
      if (categoryWithProducts) {
        setActiveCategory(categoryWithProducts.value);
      }
    }
  }, [products, activeCategory]);
  
  return (
    <div className="nearby-products-container mt-4 p-4 rounded-lg bg-white dark:bg-gray-800 shadow-md">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-medium">Recommended Products Near You</h3>
        <button 
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
      
      {/* Price category tabs */}
      <div className="flex border-b mb-4">
        {categories.map(category => (
          <button 
            key={category.value}
            className={`py-2 px-4 ${activeCategory === category.value 
              ? 'border-b-2 border-blue-500 font-medium text-blue-600 dark:text-blue-400' 
              : 'text-gray-600 dark:text-gray-400'}`}
            onClick={() => setActiveCategory(category.value)}
            disabled={products.groupedByPrice[category.value].length === 0}
          >
            {category.label}
            {products.groupedByPrice[category.value].length > 0 && (
              <span className="ml-1 text-xs">({products.groupedByPrice[category.value].length})</span>
            )}
          </button>
        ))}
      </div>
      
      {/* Product grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 overflow-y-auto max-h-96">
        {products.groupedByPrice[activeCategory].length > 0 ? (
          products.groupedByPrice[activeCategory].map((product, index) => (
            <div key={index} className="product-card border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
              {/* Product image */}
              <div className="h-40 bg-gray-100 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
                {product.imageUrl ? (
                  <img 
                    src={product.imageUrl} 
                    alt={`${product.brand} ${product.name}`} 
                    className="object-contain h-full w-full"
                  />
                ) : (
                  <div className="text-gray-400">No image</div>
                )}
              </div>
              
              {/* Product info */}
              <div className="p-3">
                <div className="font-medium text-sm text-gray-500 dark:text-gray-400">{product.brand}</div>
                <h4 className="font-bold">{product.name}</h4>
                <div className="text-lg font-bold text-blue-600 dark:text-blue-400 mt-1">
                  {product.currency}{product.price}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">{product.description}</p>
                
                {/* Store availability */}
                {product.nearbyStores && product.nearbyStores.length > 0 && (
                  <div className="mt-2">
                    <div className="text-sm font-medium mb-1">Available at:</div>
                    {product.nearbyStores.slice(0, 2).map((store, storeIndex) => (
                      <div key={storeIndex} className="flex items-center text-sm mb-1">
                        <span className="mr-1">📍</span>
                        <a 
                          href={`https://www.google.com/maps/place/?q=place_id:${store.place_id}`} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-500 hover:underline truncate"
                        >
                          {store.name}
                        </a>
                        {store.open_now !== undefined && (
                          <span className={`ml-1 text-xs ${store.open_now ? 'text-green-500' : 'text-red-500'}`}>
                            {store.open_now ? '(Open)' : '(Closed)'}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Product link button */}
                {product.link && (
                  <a 
                    href={product.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-3 block w-full text-center py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  >
                    Buy Now
                  </a>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-2 text-center py-8 text-gray-500 dark:text-gray-400">
            No products found in this price category near you.
          </div>
        )}
      </div>
      
      {/* Footer note */}
      <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
        Note: Product availability may vary. Check store websites for confirmed stock.
      </div>
    </div>
  );
};

export default Chatbot;