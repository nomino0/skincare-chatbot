"""
GROQ API client for AI-powered chat responses and image analysis.
"""

import logging
import requests
import json
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Client for interacting with the GROQ API.
    Handles chat completions and image analysis.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.groq.com",
        default_model: str = "groq/compound-mini",
        timeout: int = 30
    ):
        """
        Initialize the GROQ client.
        
        Args:
            api_key: GROQ API key.
            base_url: Base URL for GROQ API.
            default_model: Default model to use for completions.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.default_model = default_model
        self.timeout = timeout
        
        # Prepare headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def is_configured(self) -> bool:
        """
        Check if the client is properly configured.
        
        Returns:
            True if API key is available.
        """
        return bool(self.api_key and self.api_key != "")
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 0.9
    ) -> str:
        """
        Generate a chat response using GROQ API.
        
        Args:
            messages: List of conversation messages.
            model: Model to use (uses default if None).
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.
            top_p: Top-p sampling parameter.
            
        Returns:
            Generated response text.
            
        Raises:
            ValueError: If API request fails.
        """
        if not self.is_configured():
            raise ValueError("GROQ API key not configured")
        
        try:
            url = f"{self.base_url}/openai/v1/chat/completions"
            
            payload = {
                "messages": messages,
                "model": model or self.default_model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    raise ValueError("Invalid response format from GROQ API")
            else:
                error_msg = f"GROQ API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            raise ValueError(f"Failed to connect to GROQ API: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ValueError(f"Unexpected error in GROQ API call: {e}")
    
    def analyze_skin(self, image_base64: str) -> Dict[str, Any]:
        """
        Analyze skin using GROQ's vision capabilities.
        
        Args:
            image_base64: Base64 encoded image data.
            
        Returns:
            Dictionary with skin analysis results.
            
        Raises:
            ValueError: If analysis fails.
        """
        if not self.is_configured():
            raise ValueError("GROQ API key not configured")
        
        try:
            url = f"{self.base_url}/openai/v1/chat/completions"
            
            # Prepare the vision analysis prompt
            messages = [
                {
                    "role": "system",
                    "content": "You are a dermatology expert AI. Analyze the image to determine skin type (Normal, Dry, or Oily) and identify any skin issues like Acne, Redness, or Bags under eyes. Provide confidence levels for each assessment."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this facial image and identify the skin type and any skin issues present."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            payload = {
                "model": self.default_model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 500
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    ai_analysis = result['choices'][0]['message']['content']
                    
                    # Parse the AI analysis
                    parsed_results = self._parse_skin_analysis(ai_analysis)
                    parsed_results['ai_response'] = ai_analysis
                    
                    return parsed_results
                else:
                    raise ValueError("Invalid response format from GROQ API")
            else:
                error_msg = f"GROQ API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            logger.error(f"Error in skin analysis: {e}")
            raise ValueError(f"Skin analysis failed: {e}")
    
    def _parse_skin_analysis(self, ai_response: str) -> Dict[str, Any]:
        """
        Parse AI response into structured skin analysis results.
        
        Args:
            ai_response: Raw AI response text.
            
        Returns:
            Structured analysis results.
        """
        # Initialize default results
        skin_type = "Normal"
        skin_type_confidence = 70.0
        skin_issues = []
        
        ai_lower = ai_response.lower()
        
        # Parse skin type
        if "dry" in ai_lower:
            skin_type = "Dry"
            skin_type_confidence = 85.0 if "very dry" in ai_lower else 75.0
        elif "oily" in ai_lower:
            skin_type = "Oily"
            skin_type_confidence = 85.0 if "very oily" in ai_lower else 75.0
        elif "combination" in ai_lower:
            skin_type = "Combination"
            skin_type_confidence = 80.0
        
        # Parse skin issues
        issue_patterns = {
            "acne": ["acne", "pimples", "breakouts", "blemishes"],
            "redness": ["redness", "inflammation", "irritation", "red"],
            "bags": ["bags", "dark circles", "under-eye", "puffiness"],
            "wrinkles": ["wrinkles", "fine lines", "aging", "lines"],
            "dullness": ["dull", "lackluster", "tired", "lifeless"],
            "pores": ["large pores", "visible pores", "enlarged pores"]
        }
        
        for issue_name, patterns in issue_patterns.items():
            for pattern in patterns:
                if pattern in ai_lower:
                    # Determine confidence based on severity words
                    if any(severity in ai_lower for severity in ["severe", "significant", "major"]):
                        confidence = 85.0
                    elif any(severity in ai_lower for severity in ["mild", "slight", "minor"]):
                        confidence = 60.0
                    else:
                        confidence = 70.0
                    
                    skin_issues.append({
                        "name": issue_name.capitalize(),
                        "confidence": confidence
                    })
                    break  # Only add each issue once
        
        return {
            "skinType": {
                "type": skin_type,
                "confidence": skin_type_confidence
            },
            "skinIssues": skin_issues
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to GROQ API.
        
        Returns:
            Dictionary with test results.
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "API key not configured"
            }
        
        try:
            # Simple test request
            messages = [
                {"role": "user", "content": "Hello, this is a test message. Please respond with 'Test successful'."}
            ]
            
            response = self.generate_chat_response(
                messages=messages,
                max_tokens=50,
                temperature=0.1
            )
            
            return {
                "success": True,
                "response": response,
                "model": self.default_model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models (if supported by API).
        
        Returns:
            List of available model names.
        """
        try:
            url = f"{self.base_url}/openai/v1/models"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                return [model['id'] for model in result.get('data', [])]
            else:
                logger.warning(f"Failed to get models: {response.status_code}")
                return [self.default_model]
                
        except Exception as e:
            logger.warning(f"Error getting models: {e}")
            return [self.default_model]
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        This is a rough estimation.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Estimated token count.
        """
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_client_info(self) -> Dict[str, Any]:
        """
        Get information about the client configuration.
        
        Returns:
            Client configuration information.
        """
        return {
            "base_url": self.base_url,
            "default_model": self.default_model,
            "timeout": self.timeout,
            "configured": self.is_configured(),
            "api_key_length": len(self.api_key) if self.api_key else 0
        }
