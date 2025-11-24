"""
Enterprise-grade prompt engineering templates for skincare AI assistant.
Implements advanced prompt patterns including chain-of-thought reasoning,
role-based instructions, and security guardrails.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json


class PromptIntent(Enum):
    """Classification of user intent for targeted prompt selection."""
    SKIN_ANALYSIS = "skin_analysis"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    ROUTINE_ADVICE = "routine_advice"
    INGREDIENT_INQUIRY = "ingredient_inquiry"
    CONDITION_DIAGNOSIS = "condition_diagnosis"
    GENERAL_SKINCARE = "general_skincare"
    DERMATOLOGIST_REFERRAL = "dermatologist_referral"
    EMERGENCY_ASSESSMENT = "emergency_assessment"
    CASUAL_CONVERSATION = "casual_conversation"


@dataclass
class UserContext:
    """Structured user context for prompt personalization."""
    skin_type: Optional[str] = None
    skin_issues: List[str] = None
    demographics: Dict[str, Any] = None
    location: Dict[str, str] = None
    conversation_history: List[Dict[str, str]] = None
    safety_flags: List[str] = None


class PromptEngineering:
    """
    Enterprise prompt engineering system with security, personalization,
    and chain-of-thought reasoning capabilities.
    """
    
    def __init__(self):
        self.safety_guidelines = self._load_safety_guidelines()
        self.expertise_domains = self._load_expertise_domains()
        
    def _load_safety_guidelines(self) -> List[str]:
        """Load safety and ethical guidelines for AI responses."""
        return [
            "NEVER provide medical diagnosis or replace professional medical advice",
            "ALWAYS recommend consulting dermatologists for serious conditions",
            "AVOID making definitive claims about treatment efficacy without citing sources",
            "RESPECT cultural and individual differences in skincare approaches",
            "MAINTAIN user privacy and never request sensitive personal information",
            "FLAG potential emergencies and direct to immediate medical attention",
            "CITE scientific sources when making evidence-based claims",
            "ACKNOWLEDGE limitations and uncertainty when appropriate"
        ]
    
    def _load_expertise_domains(self) -> Dict[str, List[str]]:
        """Define domain-specific expertise areas for specialized responses."""
        return {
            "dermatology": [
                "Skin physiology and barrier function",
                "Common dermatological conditions",
                "Ingredient mechanisms of action",
                "Clinical research interpretation"
            ],
            "cosmetic_chemistry": [
                "Active ingredient formulations",
                "Product stability and efficacy",
                "Ingredient interactions and contraindications",
                "Regulatory compliance standards"
            ],
            "cultural_skincare": [
                "Regional climate considerations",
                "Cultural skincare practices",
                "Local product availability",
                "Economic accessibility factors"
            ]
        }
    
    def generate_system_prompt(
        self, 
        intent: PromptIntent, 
        user_context: UserContext
    ) -> str:
        """
        Generate sophisticated system prompts with role-based instructions,
        chain-of-thought reasoning, and security guardrails.
        """
        base_identity = self._get_base_identity()
        intent_specific = self._get_intent_specific_instructions(intent)
        context_adaptation = self._generate_context_adaptation(user_context)
        reasoning_framework = self._get_reasoning_framework(intent)
        safety_guardrails = self._get_safety_guardrails()
        
        system_prompt = f"""
{base_identity}

{intent_specific}

{context_adaptation}

{reasoning_framework}

{safety_guardrails}

RESPONSE GUIDELINES:
- Be conversational, warm, and natural - not robotic or academic
- For simple questions, give direct, concise answers (1-3 sentences)
- For complex queries (skin analysis, routines, products), provide structured, detailed guidance
- Use everyday language - avoid overly technical jargon unless explaining ingredients
- Only include research citations for detailed recommendations, not casual conversations
- Format complex information with bullet points or tables for readability
- Keep the user engaged with a friendly, supportive tone

IMPORTANT: Match response length and detail to the question complexity. Simple question = simple answer.
"""
        return system_prompt.strip()
    
    def _get_base_identity(self) -> str:
        """Core AI assistant identity and capabilities."""
        return """
You are Hasna, a friendly and knowledgeable dermatology assistant. You help users understand their skin and find the right products and routines.

CRITICAL: Respond naturally like a human expert - NOT like an AI showing its work.
- NO "Query Analysis", "Assessment", "Research", "Synthesis" sections
- NO numbered frameworks or structured thinking processes in your responses
- Just give helpful, conversational answers

You have access to web search to find:
- Current product prices, availability, and reviews
- Latest skincare research and recommendations
- Products available in the user's specific location
"""
    
    def _get_intent_specific_instructions(self, intent: PromptIntent) -> str:
        """Generate intent-specific instructions for targeted responses."""
        instructions = {
            PromptIntent.SKIN_ANALYSIS: """
When analyzing skin results:
- Explain findings in simple, friendly language
- Connect results to practical skincare advice  
- Recommend seeing a dermatologist for concerning issues
- Keep it conversational and supportive
""",
            PromptIntent.PRODUCT_RECOMMENDATION: """
When recommending products:
- SEARCH THE WEB for current products, prices, and availability in the user's country
- Include 3-5 specific products with brands, prices, and where to buy
- Mix budget-friendly and premium options  
- Explain why each product works for their skin
- Provide purchase links when possible
""",
            PromptIntent.ROUTINE_ADVICE: """
When creating skincare routines:
- Give step-by-step AM/PM routines
- Explain when and how to use each product
- Include tips for their specific skin type
- Keep it simple and actionable
""",
            PromptIntent.EMERGENCY_ASSESSMENT: """
EMERGENCY ASSESSMENT PROTOCOL:
- IMMEDIATELY flag severe symptoms requiring urgent care
- Provide clear guidance on when to seek emergency treatment
- Avoid providing treatment for serious conditions
- Direct to appropriate medical resources
- Document safety flags for escalation
"""
        }
        return instructions.get(intent, "")
    
    def _generate_context_adaptation(self, user_context: UserContext) -> str:
        """Generate personalized context adaptation instructions."""
        adaptations = []
        
        if user_context.skin_type:
            adaptations.append(f"USER'S SKIN TYPE: {user_context.skin_type}")
        
        if user_context.skin_issues:
            adaptations.append(f"SKIN CONCERNS: {', '.join(user_context.skin_issues)}")
        
        if user_context.location:
            location_info = user_context.location
            country = location_info.get('country', 'Unknown')
            climate = self._get_climate_considerations(country)
            adaptations.append(f"LOCATION: {country} - {climate}")
        
        if user_context.demographics:
            demo = user_context.demographics
            if demo.get('age'):
                adaptations.append(f"AGE GROUP: {demo['age']}")
            if demo.get('gender'):
                adaptations.append(f"GENDER: {demo['gender']}")
        
        if user_context.safety_flags:
            adaptations.append(f"SAFETY ALERTS: {', '.join(user_context.safety_flags)}")
        
        context_section = "\\n".join(adaptations) if adaptations else "No specific context provided"
        
        return f"""
PERSONALIZATION CONTEXT:
{context_section}

ADAPTATION REQUIREMENTS:
- Tailor all recommendations to the specific skin profile
- Consider regional product availability and climate factors
- Respect cultural skincare practices and preferences
- Adjust language complexity based on user's apparent knowledge level
- Factor in economic accessibility for product recommendations
"""
    
    def _get_reasoning_framework(self, intent: PromptIntent) -> str:
        """Provide chain-of-thought reasoning framework."""
        return """
THINKING PROCESS (internal - don't show this structure in responses):
- Understand what the user is really asking
- Consider their skin profile and context
- Search for current, evidence-based information when needed
- Provide practical, personalized recommendations
- Ensure safety and professional referral when appropriate

Respond naturally as if talking to a friend - the user shouldn't see your thinking process.
"""
    
    def _get_safety_guardrails(self) -> str:
        """Generate safety and ethical guardrails."""
        guidelines_text = "\\n".join([f"- {guideline}" for guideline in self.safety_guidelines])
        
        return f"""
CRITICAL SAFETY GUARDRAILS:
{guidelines_text}

EMERGENCY TRIGGERS - Immediate medical referral required for:
- Sudden, severe skin reactions
- Signs of infection (spreading redness, fever, pus)
- Suspicious moles or rapid skin changes
- Severe allergic reactions
- Any mention of self-harm related to skin concerns

RESPONSE QUALITY STANDARDS:
- Evidence-based recommendations with source citations
- Clear confidence levels for all claims
- Acknowledgment of limitations and uncertainties
- Culturally sensitive language and recommendations
- Professional, empathetic, and non-judgmental tone
"""
    
    def _get_climate_considerations(self, country: str) -> str:
        """Get climate-specific skincare considerations."""
        climate_data = {
            "Tunisia": "Mediterranean climate - hot, dry summers require extra hydration; mild winters",
            "USA": "Varied climates - adjust recommendations based on regional conditions",
            "France": "Temperate climate - seasonal adjustments for humidity and temperature changes",
            "Germany": "Continental climate - focus on barrier protection in cold seasons",
            "UAE": "Desert climate - extreme sun protection and hydration emphasis"
        }
        return climate_data.get(country, "Consider local climate conditions for skincare adjustments")
    
    def classify_intent(self, user_message: str, conversation_history: List[Dict]) -> PromptIntent:
        """
        Classify user intent using keyword analysis and context.
        In production, this would use a trained classification model.
        """
        message_lower = user_message.lower()
        
        # Emergency keywords
        emergency_keywords = ['burning', 'severe', 'emergency', 'urgent', 'infection', 'swollen', 'fever']
        if any(keyword in message_lower for keyword in emergency_keywords):
            return PromptIntent.EMERGENCY_ASSESSMENT
        
        # Product recommendation keywords
        product_keywords = ['recommend', 'product', 'buy', 'purchase', 'brand', 'store']
        if any(keyword in message_lower for keyword in product_keywords):
            return PromptIntent.PRODUCT_RECOMMENDATION
        
        # Routine advice keywords
        routine_keywords = ['routine', 'regimen', 'steps', 'morning', 'evening', 'daily']
        if any(keyword in message_lower for keyword in routine_keywords):
            return PromptIntent.ROUTINE_ADVICE
        
        # Ingredient inquiry keywords
        ingredient_keywords = ['ingredient', 'retinol', 'vitamin', 'acid', 'serum', 'contains']
        if any(keyword in message_lower for keyword in ingredient_keywords):
            return PromptIntent.INGREDIENT_INQUIRY
        
        # Dermatologist referral keywords
        doctor_keywords = ['doctor', 'dermatologist', 'specialist', 'appointment', 'clinic']
        if any(keyword in message_lower for keyword in doctor_keywords):
            return PromptIntent.DERMATOLOGIST_REFERRAL
        
        # Skin analysis (after scan results)
        if any(word in message_lower for word in ['analyze', 'analysis', 'results', 'scan']):
            return PromptIntent.SKIN_ANALYSIS
        
        # Casual conversation keywords
        casual_keywords = [
            'how are you', 'hello', 'hi', 'hey', 'thanks', 'thank you', 
            'good', 'fine', 'ok', 'okay', 'great', 'nice', 'cool',
            'bye', 'goodbye', 'see you', 'later', 'yes', 'no',
            'what\'s up', 'sup', 'howdy', 'greetings'
        ]
        # Check if message is very short (likely casual)
        if len(message_lower.split()) <= 3:
            if any(keyword in message_lower for keyword in casual_keywords):
                return PromptIntent.CASUAL_CONVERSATION
        
        return PromptIntent.GENERAL_SKINCARE
    
    def extract_safety_flags(self, user_message: str, skin_data: Optional[Dict]) -> List[str]:
        """Extract potential safety concerns from user input and skin data."""
        flags = []
        message_lower = user_message.lower()
        
        # Emergency indicators
        emergency_terms = ['severe pain', "can't sleep", 'spreading fast', 'fever', 'infection']
        for term in emergency_terms:
            if term in message_lower:
                flags.append(f"EMERGENCY: {term}")
        
        # Pregnancy/medical condition indicators
        medical_terms = ['pregnant', 'medication', 'prescribed', 'allergic reaction']
        for term in medical_terms:
            if term in message_lower:
                flags.append(f"MEDICAL: {term}")
        
        # Skin data analysis for safety flags
        if skin_data:
            skin_issues = skin_data.get('skinIssues', [])
            for issue in skin_issues:
                if issue.get('confidence', 0) > 85 and issue.get('name') in ['Severe_Acne', 'Redness', 'Inflammation']:
                    flags.append(f"HIGH_CONFIDENCE: {issue.get('name')}")
        
        return flags
    
    def generate_user_prompt(
        self, 
        user_message: str, 
        intent: PromptIntent,
        context: UserContext
    ) -> str:
        """Generate enhanced user prompt with context and safety flags."""
        
        safety_context = ""
        if context.safety_flags:
            safety_context = f"\\n\\nSAFETY ALERTS: {', '.join(context.safety_flags)}"
        
        return f"""
User Query: {user_message}

Intent Classification: {intent.value}

Please analyze this query using your reasoning framework and provide a comprehensive, 
evidence-based response that addresses the user's specific needs while maintaining 
all safety guardrails.{safety_context}
"""


# Factory function for creating prompt engineering instance
def create_prompt_engineer() -> PromptEngineering:
    """Factory function to create a configured prompt engineering instance."""
    return PromptEngineering()


# Export commonly used functions
__all__ = [
    'PromptEngineering', 
    'PromptIntent', 
    'UserContext', 
    'create_prompt_engineer'
]
