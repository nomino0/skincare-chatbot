import React, { useState, useEffect, useRef } from 'react';
import { SkinPredictionResult, sendEmail, findNearbyDermatologists, DermatologistResult } from '../services/api';

// Add this import for the knowledge base
import { skinKnowledgeBase } from '../utils/skinKnowledgeBase';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatbotProps {
  skinResults: SkinPredictionResult | null;
}

const Chatbot: React.FC<ChatbotProps> = ({ skinResults }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I am Hasna, your dermatology assistant. I can help analyze your skin and provide personalized skincare recommendations.'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [dermatologists, setDermatologists] = useState<DermatologistResult[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null);

  // Add skin analysis results as a message when they become available
  useEffect(() => {
    if (skinResults) {
      // Use the LLM to generate a natural response based on the skin results
      generateLLMResponse("Analyze these skin results and provide a friendly summary", skinResults);
    }
  }, [skinResults]);

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
      
      // Just for demo purposes - in reality this would be handled by the LLM
      // This simulates what the LLM would do with the knowledge base
      if (prompt.includes("skin results")) {
        // Initial analysis response
        if (skinResults?.ai_response) {
          response = `✨ Your skin analysis is complete! Here's what I found:\n\n${skinResults.ai_response}\n\nWould you like me to suggest some skincare products based on these results? Or would you prefer to find a dermatologist near you?`;
        } else {
          response = `I've completed your skin analysis! Here's what I found:\n\n✨ Skin Type: ${skinResults?.skinType.type} (${skinResults?.skinType.confidence.toFixed(2)}% confidence)\n\n`;
          
          if (skinIssues.length > 0) {
            response += `I've detected these skin concerns: ${skinResults?.skinIssues
              .map(issue => `${issue.name} (${issue.confidence.toFixed(2)}% confidence)`)
              .join(', ')}\n\n`;
          } else {
            response += "Good news! I didn't detect any significant skin issues.\n\n";
          }
          
          response += "Would you like me to suggest some personalized skincare recommendations? Or perhaps help you find a dermatologist nearby?";
        }
      } else if (prompt.includes("routine") || prompt.includes("regimen")) {
        // Get a routine response from the knowledge base
        response = skinKnowledgeBase.getRoutine(skinType, skinIssues);
      } else if (prompt.includes("product") || prompt.includes("recommend")) {
        // Get product recommendations from the knowledge base
        response = skinKnowledgeBase.getProductRecommendations(skinType, skinIssues);
      } else if (prompt.includes("doctor") || prompt.includes("dermatologist")) {
        response = "I'd love to help you find a dermatologist nearby! I'll need to access your location for that. Is it okay if I access your location?";
      } else {
        // General conversation - this would be handled more naturally by the LLM
        response = skinKnowledgeBase.getGeneralResponse(prompt, skinType, skinIssues);
      }
      
      addAssistantMessage(response);
    } catch (error) {
      console.error('Error generating LLM response:', error);
      addAssistantMessage("I seem to be having a technical hiccup. Could we try that again?");
    } finally {
      setIsLoading(false);
    }
  };

  // Get user's location for dermatologist search
  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
          // Once we have location, search for dermatologists
          searchDermatologists(position.coords.latitude, position.coords.longitude);
        },
        (error) => {
          console.error("Error getting location:", error);
          addAssistantMessage("Oh no, I couldn't access your location! For me to find nearby dermatologists, could you please allow location access in your browser? 📍");
        }
      );
    } else {
      addAssistantMessage("It looks like your browser doesn't support location sharing, which I need to find dermatologists near you. Maybe try a different browser or device?");
    }
  };

  // Function to search for dermatologists once we have location
  const searchDermatologists = async (lat: number, lng: number) => {
    try {
      setIsLoading(true);
      const results = await findNearbyDermatologists(lat, lng);
      setDermatologists(results);
      
      if (results.length > 0) {
        // Use the LLM to generate a natural response
        const doctorInfo = results.slice(0, 3).map(doctor => ({
          name: doctor.name,
          rating: doctor.rating,
          address: doctor.vicinity
        }));
        
        generateLLMResponse("Generate a friendly response about these dermatologists", doctorInfo);
      } else {
        addAssistantMessage("I searched the area but couldn't find any dermatologists listed nearby. Would you like me to suggest some online dermatology services instead, or perhaps expand the search area?");
      }
    } catch (error) {
      console.error('Error finding dermatologists:', error);
      addAssistantMessage("I'm having a bit of trouble with the dermatologist search right now. Would you like to try again, or should I focus on giving you personalized skincare advice instead?");
    } finally {
      setIsLoading(false);
    }
  };

  const addAssistantMessage = (content: string) => {
    setMessages(prevMessages => [
      ...prevMessages,
      { role: 'assistant', content }
    ]);
  };

  const handleUserMessage = async (userMessage: string) => {
    // Check for specific actions first
    const message = userMessage.toLowerCase();
    
    // If asking for location permission for dermatologists
    if (message.includes("yes") && messages[messages.length - 1].content.includes("access your location")) {
      getUserLocation();
      return;
    }
    
    // If trying to send an email
    if (message.includes('email') || message.includes('send') || message.includes('mail')) {
      const emailRegex = /[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+/;
      const emailMatch = userMessage.match(emailRegex);
      
      if (emailMatch && skinResults) {
        const email = emailMatch[0];
        try {
          await sendEmail(email, skinResults);
          addAssistantMessage(`Perfect! ✅ I've sent your skin analysis results to ${email}. Is there anything else you'd like help with today?`);
          return;
        } catch (error) {
          console.error('Error sending email:', error);
          addAssistantMessage("I'm having trouble sending the email right now. Would you like me to try again or perhaps I can give you recommendations here instead?");
          return;
        }
      } else if (skinResults) {
        addAssistantMessage("I'd be happy to email your results! What's your email address?");
        return;
      }
    }
    
    // For all other messages, use the LLM to generate a response
    // In a real implementation, pass the entire conversation history
    generateLLMResponse(userMessage, {
      skinResults,
      conversationHistory: messages
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() === '') return;
    
    const userMessage = inputValue;
    setInputValue('');
    
    setMessages(prevMessages => [
      ...prevMessages,
      { role: 'user', content: userMessage }
    ]);
    
    handleUserMessage(userMessage);
  };

  return (
    <div className="flex flex-col h-[868px] bg-gray-50 rounded-xl shadow-lg">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-xl flex-shrink-0">
        <h2 className="text-lg font-semibold">Skin Assistant</h2>
      </div>
      
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4" style={{ maxHeight: 'calc(100% - 140px)' }}>
        {messages.map((message, index) => (
          <div 
            key={index}
            className={`${
              message.role === 'assistant' 
                ? 'ml-2 max-w-[80%] bg-blue-100 text-gray-800 rounded-lg p-3 mb-3' 
                : 'mr-2 ml-auto max-w-[80%] bg-blue-500 text-white rounded-lg p-3 mb-3'
            }`}
          >
            <p className="whitespace-pre-line">{message.content}</p>
          </div>
        ))}
        {isLoading && (
          <div className="ml-2 bg-blue-100 rounded-lg p-3 max-w-[80%] mb-3">
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Dermatologists Results */}
      {dermatologists.length > 0 && (
        <div className="p-4 bg-blue-50 border-t border-blue-100 flex-shrink-0">
          <h3 className="font-medium text-blue-800 mb-2">Nearby Dermatologists</h3>
          <div className="overflow-x-auto">
            <div className="flex space-x-4">
              {dermatologists.slice(0, 5).map((doctor, index) => (
                <div key={index} className="min-w-[200px] p-3 bg-white rounded-lg shadow">
                  <p className="font-medium">{doctor.name}</p>
                  <p className="text-sm text-gray-600">{doctor.vicinity}</p>
                  <p className="text-sm">⭐ {doctor.rating || 'N/A'}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-4 border-t flex-shrink-0">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 border rounded"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700 transition-colors"
            disabled={isLoading || !inputValue.trim()}
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chatbot;