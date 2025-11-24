"""
Enterprise Chat Service for handling sophisticated chatbot interactions.
Implements advanced prompt engineering, context management, and security.
"""

import logging
import time
from typing import Dict, List, Any, Optional

from ..utils.groq_client import GroqClient
from ..services.product_service import ProductService
from ..utils.prompt_templates import (
    PromptEngineering, 
    PromptIntent, 
    UserContext, 
    create_prompt_engineer
)

logger = logging.getLogger(__name__)


class ChatService:
    """
    Enterprise chat service with advanced prompt engineering, 
    context management, and security guardrails.
    """
    
    def __init__(self, groq_client: GroqClient, product_service: ProductService):
        """
        Initialize the enterprise chat service.
        
        Args:
            groq_client: GROQ API client for generating responses.
            product_service: Product service for dynamic recommendations.
        """
        self.groq_client = groq_client
        self.product_service = product_service
        self.prompt_engineer = create_prompt_engineer()
        
        # Enterprise configuration
        self.max_history_length = 15
        self.max_response_tokens = 3072
        self.security_enabled = True
        
        # Hasna's personality and system prompt - CONVERSATIONAL & NATURAL
        self.system_prompt = """
        You are Hasna, a friendly skincare expert who gives helpful, natural advice. Talk like a knowledgeable friend, not a textbook.
        
        CONVERSATION STYLE - CRITICAL:
        - Keep responses SHORT (2-4 sentences for simple questions, longer only when analyzing skin results)
        - ALWAYS ask follow-up questions to keep the conversation flowing
        - Don't dump all information at once - give bite-sized advice and wait for the user to respond
        - Talk naturally like texting a friend, not writing an essay
        - NEVER use tables, lists with dashes, or structured formats
        - Match the user's energy - if they're brief, you be brief
        - Write in flowing paragraphs like telling a story
        
        FORMATTING RULES - CRITICAL:
        - NO TABLES ever - they break the layout
        - NO bullet points or numbered lists
        - Write in natural flowing paragraphs
        - Use line breaks between thoughts
        - Think: storytelling, not documentation
        
        WHEN THE USER SHARES SCAN RESULTS:
        1. First response: Give a quick, friendly overview (3-4 sentences max) and ask what they want to focus on
        2. Wait for their reply before diving into details
        3. Only share detailed routines/products if they ask for them
        4. When giving advice, write it as flowing paragraphs, not lists
        
        NEVER:
        - Write long paragraphs explaining everything at once
        - Use tables, bullet points, or structured formats
        - Give complete routines without checking if they want them
        - Overwhelm with too much information
        
        ALWAYS:
        - Keep the user engaged with questions
        - Let THEM guide what they want to know more about
        - Be conversational and warm
        - Write in story format with natural flow
        - Remember: SHORT responses that invite dialogue
        
        Example good response to scan results:
        "Looks like you have combination skin with some concerns around your T-zone. The good news is this is super manageable! What would you like to focus on first - dealing with oil control, or addressing the dry patches?"
        
        Example BAD response (too long, too structured):
        *long detailed explanation with tables, lists, and complete routine*
        """
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        skin_analysis: Optional[Dict[str, Any]] = None,
        user_location: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate enterprise-grade AI responses with sophisticated prompt engineering,
        context awareness, and security guardrails.
        
        Args:
            user_message: The user's input message.
            conversation_history: Previous conversation messages.
            skin_analysis: User's skin analysis results for context.
            user_location: User's location information.
            
        Returns:
            Dictionary containing the response and metadata.
            
        Raises:
            ValueError: If message generation fails.
        """
        try:
            # 1. SECURITY VALIDATION
            if self.security_enabled and not self._validate_input_security(user_message):
                return self._generate_security_response()
            
            # 2. CONTEXT PREPARATION
            user_context = self._build_user_context(
                skin_analysis, user_location, conversation_history
            )
            
            # 3. INTENT CLASSIFICATION
            intent = self.prompt_engineer.classify_intent(user_message, conversation_history or [])
            logger.info(f"Classified intent: {intent.value}")
            
            # 3.5. CASUAL CONVERSATION SHORTCUT
            if intent == PromptIntent.CASUAL_CONVERSATION:
                return self._handle_casual_conversation(user_message)
            
            # 4. SAFETY ASSESSMENT
            safety_flags = self.prompt_engineer.extract_safety_flags(user_message, skin_analysis)
            user_context.safety_flags = safety_flags
            
            # 5. EMERGENCY HANDLING
            if intent == PromptIntent.EMERGENCY_ASSESSMENT or safety_flags:
                return self._handle_emergency_response(user_message, safety_flags)
            
            # 6. DYNAMIC PROMPT GENERATION
            system_prompt = self.prompt_engineer.generate_system_prompt(intent, user_context)
            user_prompt = self.prompt_engineer.generate_user_prompt(
                user_message, intent, user_context
            )
            
            # 7. CONVERSATION PREPARATION
            messages = self._build_conversation_messages(
                system_prompt, user_prompt, conversation_history, user_context
            )
            
            # 8. AI RESPONSE GENERATION
            response_text = self.groq_client.generate_chat_response(
                messages=messages,
                max_tokens=self.max_response_tokens,
                temperature=0.7
            )
            
            # 9. DYNAMIC CONTENT ENHANCEMENT
            enhanced_response = self._enhance_response_with_dynamic_content(
                response_text, intent, user_context
            )
            
            # 10. RESPONSE PACKAGING
            return self._package_response(enhanced_response, intent, user_context)
            
        except Exception as e:
            logger.error(f"Error in enterprise chat generation: {e}")
            return self._generate_fallback_response(str(e))
    
    def _validate_input_security(self, user_message: str) -> bool:
        """Validate user input for security threats."""
        # Check for injection attempts, inappropriate content, etc.
        dangerous_patterns = [
            'script>', 'javascript:', 'data:', '<iframe', 'eval(', 'exec(',
            'system(', 'shell_exec', '__import__', 'subprocess'
        ]
        
        message_lower = user_message.lower()
        return not any(pattern in message_lower for pattern in dangerous_patterns)
    
    def _generate_security_response(self) -> Dict[str, Any]:
        """Generate security violation response."""
        return {
            "response": "I'm sorry, but I can't process that request. Please rephrase your question about skincare in a clear, straightforward manner.",
            "suggestions": ["Ask about skin types", "Request product recommendations", "General skincare questions"],
            "security_flag": True
        }
    
    def _build_user_context(
        self,
        skin_analysis: Optional[Dict[str, Any]],
        user_location: Optional[Dict[str, str]],
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> UserContext:
        """Build comprehensive user context for prompt engineering."""
        context = UserContext()
        
        if skin_analysis:
            context.skin_type = skin_analysis.get('skinType', {}).get('type')
            context.skin_issues = [
                issue.get('name') for issue in skin_analysis.get('skinIssues', [])
                if issue.get('confidence', 0) > 50
            ]
            context.demographics = skin_analysis.get('demographics', {})
        
        if user_location:
            context.location = user_location
            
        if conversation_history:
            context.conversation_history = conversation_history[-self.max_history_length:]
            
        return context
    
    def _handle_casual_conversation(self, user_message: str) -> Dict[str, Any]:
        """Handle casual conversations with short, natural responses."""
        message_lower = user_message.lower().strip()
        
        # Define simple responses for common casual interactions
        casual_responses = {
            "how are you": "I'm doing well, thank you for asking! I'm here to help with any skincare questions you may have. Let me know how I can assist you further!",
            "hello": "Hello! I'm here to help you with skincare advice and product recommendations. What can I help you with today?",
            "hi": "Hi there! How can I help you with your skincare journey today?",
            "hey": "Hey! I'm your skincare assistant. What questions do you have about your skin?",
            "thanks": "You're very welcome! I'm always here if you need more skincare guidance.",
            "thank you": "You're very welcome! Feel free to ask me anything about skincare anytime.",
            "good": "That's great to hear! Is there anything specific about skincare I can help you with?",
            "ok": "Perfect! Let me know if you have any skincare questions or concerns.",
            "okay": "Sounds good! I'm here whenever you need skincare advice or product recommendations."
        }
        
        # Check for exact matches first
        for phrase, response in casual_responses.items():
            if phrase in message_lower:
                return {
                    "response": response,
                    "intent": "casual_conversation",
                    "response_type": "casual",
                    "processing_time": 0.1,
                    "context_used": False
                }
        
        # Default casual response for other short messages
        return {
            "response": "I'm here to help with any skincare questions you might have! Feel free to ask about your skin concerns, product recommendations, or skincare routines.",
            "intent": "casual_conversation", 
            "response_type": "casual",
            "processing_time": 0.1,
            "context_used": False
        }
    
    def _handle_emergency_response(
        self, 
        user_message: str, 
        safety_flags: List[str]
    ) -> Dict[str, Any]:
        """Handle emergency situations with immediate medical referral."""
        return {
            "response": """I notice you may be experiencing a serious skin condition that requires immediate professional attention. 

Please consider:
- Contacting a dermatologist immediately if symptoms are severe
- Visiting an urgent care center for rapidly worsening conditions
- Calling emergency services if you're experiencing severe allergic reactions

I'm here to provide general skincare guidance, but professional medical evaluation is essential for your safety.""",
            "suggestions": ["Find emergency care", "Contact dermatologist", "General skincare info"],
            "emergency_flag": True,
            "safety_flags": safety_flags
        }
    
    def _build_conversation_messages(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]],
        user_context: Optional[UserContext] = None
    ) -> List[Dict[str, str]]:
        """Build conversation messages with enterprise prompt engineering."""
        
        # CRITICAL: Inject skin analysis context into system prompt
        enhanced_system_prompt = system_prompt
        if user_context:
            context_info = "\n\n🔍 USER'S SKIN PROFILE (YOU ALREADY HAVE THIS INFO - DON'T ASK FOR IT):\n"
            
            if user_context.skin_type:
                context_info += f"✓ Skin Type: {user_context.skin_type}\n"
            
            if user_context.skin_issues:
                issues_str = ", ".join(user_context.skin_issues)
                context_info += f"✓ Detected Issues: {issues_str}\n"
            
            if user_context.demographics:
                demo = user_context.demographics
                if demo.get('age'):
                    context_info += f"✓ Age: {demo['age']}\n"
                if demo.get('gender'):
                    context_info += f"✓ Gender: {demo['gender']}\n"
            
            if user_context.location:
                country = user_context.location.get('country', 'Unknown')
                context_info += f"✓ Location: {country}\n"
            
            context_info += "\n⚠️ CRITICAL: You ALREADY have their complete skin analysis above. NEVER ask for skin type, age, concerns, or gender. Use this data immediately to give personalized advice.\n"
            
            enhanced_system_prompt = system_prompt + context_info
        
        messages = [{"role": "system", "content": enhanced_system_prompt}]
        
        # Add relevant conversation history
        if conversation_history:
            recent_history = conversation_history[-self.max_history_length:]
            for msg in recent_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current user prompt
        messages.append({"role": "user", "content": user_prompt})
        
        return messages
    
    def _enhance_response_with_dynamic_content(
        self,
        response_text: str,
        intent: PromptIntent,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """Enhance AI response with dynamic product data and recommendations."""
        enhanced_response = {"response": response_text}
        
        # Add dynamic product recommendations for product-related intents
        if intent in [PromptIntent.PRODUCT_RECOMMENDATION, PromptIntent.ROUTINE_ADVICE]:
            try:
                products = self._get_dynamic_product_recommendations(user_context)
                if products:
                    enhanced_response["productRecommendations"] = products
                    
            except Exception as e:
                logger.warning(f"Failed to get dynamic products: {e}")
        
        return enhanced_response
    
    def _get_dynamic_product_recommendations(
        self, 
        user_context: UserContext
    ) -> Optional[List[Dict[str, Any]]]:
        """Get real-time product recommendations (no static data)."""
        try:
            if not user_context.skin_type:
                return None
                
            country = user_context.location.get('country', 'United States') if user_context.location else 'United States'
            gender = user_context.demographics.get('gender', 'All') if user_context.demographics else 'All'
            age_group = user_context.demographics.get('age', '') if user_context.demographics else ''
            
            # Get live product data from service
            products = self.product_service.get_product_recommendations(
                skin_type=user_context.skin_type,
                skin_issues=user_context.skin_issues or [],
                gender=gender,
                age_group=age_group,
                country=country,
                max_products=5
            )
            
            # Validate that we got real product data
            if not products or (isinstance(products, list) and len(products) > 0 and 'message' in products[0]):
                return None
                
            return products
            
        except Exception as e:
            logger.error(f"Error getting dynamic products: {e}")
            return None
    
    def _package_response(
        self,
        enhanced_response: Dict[str, Any],
        intent: PromptIntent,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """Package final response with suggestions and metadata."""
        packaged = enhanced_response.copy()
        
        # Detect if response requires yes/no answer
        response_text = packaged.get("response", "").lower()
        requires_yes_no = self._detect_yes_no_question(response_text)
        packaged["requiresYesNo"] = requires_yes_no
        
        # Add intelligent suggestions based on intent and context
        suggestions = self._generate_intelligent_suggestions(intent, user_context)
        if suggestions:
            packaged["suggestions"] = suggestions
            
        # Add metadata
        packaged["intent"] = intent.value
        packaged["timestamp"] = int(time.time())
        
        return packaged
    
    def _detect_yes_no_question(self, response_text: str) -> bool:
        """Detect if AI response is asking a yes/no question."""
        # Check for explicit yes/no patterns
        yes_no_patterns = [
            r"would you like",
            r"do you want",
            r"should i",
            r"are you",
            r"have you",
            r"did you",
            r"can i",
            r"\?.*\b(yes|no)\b",
            r"interested in",
            r"want me to"
        ]
        
        import re
        for pattern in yes_no_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
        
        return False
    
    def _generate_intelligent_suggestions(
        self,
        intent: PromptIntent,
        user_context: UserContext
    ) -> List[str]:
        """Generate contextual suggestions based on intent and user profile."""
        suggestions = []
        
        skin_type = user_context.skin_type or "your skin"
        
        if intent == PromptIntent.SKIN_ANALYSIS:
            suggestions = [
                f"What products work best for {skin_type} skin?",
                "Can you create a skincare routine for me?",
                "What ingredients should I look for?"
            ]
        elif intent == PromptIntent.PRODUCT_RECOMMENDATION:
            suggestions = [
                "How should I use these products?",
                "What's a good morning routine?",
                "Are there any ingredients to avoid?"
            ]
        elif intent == PromptIntent.ROUTINE_ADVICE:
            suggestions = [
                "How often should I use these products?",
                "Can you recommend specific brands?",
                "What about seasonal adjustments?"
            ]
        else:
            suggestions = [
                "Tell me about my skin analysis",
                "Recommend products for me",
                "Create a skincare routine"
            ]
            
        return suggestions
    
    def _generate_fallback_response(self, error_msg: str) -> Dict[str, Any]:
        """Generate fallback response when AI generation fails."""
        logger.error(f"Chat service fallback triggered: {error_msg}")
        
        return {
            "response": """I'm currently updating my knowledge base to provide you with the most accurate and current skincare advice. Please try asking your question again, or I can help you with:

- General skincare guidance
- Skin type information  
- Basic product categories
- When to see a dermatologist

What would you like to know about skincare?""",
            "suggestions": [
                "Tell me about skin types",
                "Basic skincare routine",
                "When to see a doctor"
            ],
            "fallback": True
        }
    def validate_message(self, message: str) -> bool:
        """
        Validate a user message before processing.
        
        Args:
            message: User's message to validate.
            
        Returns:
            True if message is valid for processing.
        """
        if not message or not message.strip():
            return False
        
        # Check message length (reasonable limit)
        if len(message) > 2000:
            return False
        
        # Security validation
        return self._validate_input_security(message)
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get the status of the enterprise chat service.
        
        Returns:
            Status information for the chat service.
        """
        return {
            "service_type": "enterprise",
            "groq_client": {
                "available": self.groq_client is not None,
                "configured": self.groq_client.is_configured() if self.groq_client else False
            },
            "product_service": {
                "available": self.product_service is not None
            },
            "prompt_engineering": {
                "available": self.prompt_engineer is not None,
                "security_enabled": self.security_enabled
            },
            "configuration": {
                "max_history_length": self.max_history_length,
                "max_response_tokens": self.max_response_tokens
            }
        }
