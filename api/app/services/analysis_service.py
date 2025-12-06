"""
Analysis Service for skin analysis functionality.
Handles image processing, face detection, and AI model predictions.
"""

import logging
import base64
import numpy as np
from typing import Dict, Any, Optional
import cv2

from ..models.skin_analysis_model import SkinAnalysisModel
from ..models.fairface_model import FairFaceModel
from ..utils.image_processing import ImageProcessor
from ..utils.groq_client import GroqClient

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Service class for handling skin analysis operations.
    Coordinates between image processing, model predictions, and external AI services.
    """
    
    def __init__(
        self, 
        skin_model: SkinAnalysisModel,
        fairface_model: FairFaceModel,
        image_processor: ImageProcessor,
        groq_client: Optional[GroqClient] = None
    ):
        """
        Initialize the analysis service.
        
        Args:
            skin_model: Skin analysis model instance.
            fairface_model: FairFace demographic model instance.
            image_processor: Image processing utility.
            groq_client: Optional GROQ API client for fallback analysis.
        """
        self.skin_model = skin_model
        self.fairface_model = fairface_model
        self.image_processor = image_processor
        self.groq_client = groq_client
    
    def analyze_skin(self, image_data: str, use_groq: bool = False) -> Dict[str, Any]:
        """
        Perform complete skin analysis on an image.
        
        Args:
            image_data: Base64 encoded image data.
            use_groq: Whether to use GROQ API instead of local models.
            
        Returns:
            Dictionary containing analysis results.
            
        Raises:
            ValueError: If image processing or analysis fails.
        """
        try:
            # Decode and validate image
            image = self._decode_image(image_data)
            
            # Extract face from image
            face = self.image_processor.crop_face(image)
            if face is None:
                raise ValueError("No face detected in the image")
            
            # Use GROQ API if requested or if local models are not available
            if use_groq or not self.skin_model.is_model_loaded():
                if self.groq_client:
                    try:
                        return self._analyze_with_groq(image_data, face)
                    except Exception as e:
                        logger.error(f"GROQ analysis failed: {e}")
                        if not self.skin_model.is_model_loaded():
                            raise ValueError(f"Both local model and GROQ API failed: {e}")
                        logger.info("Falling back to local model")
                else:
                    if not self.skin_model.is_model_loaded():
                        raise ValueError("No analysis method available: local model not loaded and GROQ client not configured")
            
            # Use local models
            return self._analyze_with_local_models(face)
            
        except Exception as e:
            logger.error(f"Error in skin analysis: {e}")
            raise ValueError(f"Analysis failed: {e}")
    
    def _decode_image(self, image_data: str) -> np.ndarray:
        """
        Decode base64 image data to numpy array.
        
        Args:
            image_data: Base64 encoded image.
            
        Returns:
            Decoded image as numpy array.
            
        Raises:
            ValueError: If image decoding fails.
        """
        try:
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            return image
            
        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            raise ValueError(f"Invalid image format: {e}")
    
    def _analyze_with_local_models(self, face: np.ndarray) -> Dict[str, Any]:
        """
        Analyze skin using local AI models.
        
        Args:
            face: Cropped face image.
            
        Returns:
            Analysis results from local models.
        """
        results = {}
        
        # Get skin analysis prediction
        if self.skin_model.is_model_loaded():
            skin_prediction = self.skin_model.predict(face)
            results.update(skin_prediction)
        else:
            logger.warning("Skin analysis model not loaded")
            results.update({
                "skinType": {"type": "Unknown", "confidence": 0.0},
                "skinIssues": []
            })
        
        
        # Get demographic prediction (optional - will work without FairFace model)
        if self.fairface_model and self.fairface_model.is_model_loaded():
            demographics = self.fairface_model.predict(face)
            if demographics:
                results["demographics"] = demographics
                
                # Add personalized advice based on demographics
                results["personalizedAdvice"] = self._generate_personalized_advice(
                    results.get("skinType", {}).get("type", "Normal"),
                    results.get("skinIssues", []),
                    demographics
                )
        else:
            # Add default demographics for API compatibility
            results["demographics"] = {
                "age": "20-29",
                "gender": "Unknown",
                "race": "Unknown",
                "confidence": {
                    "age": 0.0,
                    "gender": 0.0,
                    "race": 0.0
                }
            }
            logger.info("FairFace model not available - using default demographics")
        
        return results
    
    def _analyze_with_groq(self, image_data: str, face: np.ndarray) -> Dict[str, Any]:
        """
        Analyze skin using GROQ API.
        
        Args:
            image_data: Original base64 image data.
            face: Cropped face image (for demographic analysis).
            
        Returns:
            Analysis results from GROQ API.
        """
        # Get analysis from GROQ
        groq_results = self.groq_client.analyze_skin(image_data)
        
        # Try to get demographics from local FairFace model if available
        if self.fairface_model.is_model_loaded():
            demographics = self.fairface_model.predict(face)
            if demographics:
                groq_results["demographics"] = demographics
        
        # If no demographics available, add default values for API compatibility
        if "demographics" not in groq_results:
            groq_results["demographics"] = {
                "age": "20-29",
                "gender": "Unknown", 
                "race": "Unknown",
                "confidence": {
                    "age": 0.0,
                    "gender": 0.0,
                    "race": 0.0
                }
            }
        
        return groq_results
    
    def _generate_personalized_advice(
        self, 
        skin_type: str, 
        skin_issues: list, 
        demographics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate personalized skincare advice based on analysis results.
        
        Args:
            skin_type: Detected skin type.
            skin_issues: List of detected skin issues.
            demographics: Demographic information.
            
        Returns:
            Personalized advice dictionary.
        """
        advice = {
            "routine": [],
            "ingredients": [],
            "avoid": [],
            "lifestyle": []
        }
        
        # Base routine for skin type
        if skin_type.lower() == "dry":
            advice["routine"] = [
                "Use a gentle, hydrating cleanser",
                "Apply moisturizer while skin is still damp",
                "Use a humidifier in dry environments",
                "Limit hot water exposure"
            ]
            advice["ingredients"] = [
                "Hyaluronic acid", "Ceramides", "Glycerin", "Squalane"
            ]
            advice["avoid"] = [
                "Harsh exfoliants", "Alcohol-based products", "Long hot showers"
            ]
        elif skin_type.lower() == "oily":
            advice["routine"] = [
                "Use a foaming or gel cleanser",
                "Don't skip moisturizer - use oil-free formulas",
                "Use blotting papers during the day",
                "Exfoliate regularly but gently"
            ]
            advice["ingredients"] = [
                "Salicylic acid", "Niacinamide", "Clay", "Zinc"
            ]
            advice["avoid"] = [
                "Over-cleansing", "Heavy oils", "Pore strips"
            ]
        else:  # Normal/Combination
            advice["routine"] = [
                "Use a balanced cleanser",
                "Moisturize daily",
                "Use different products for different face zones if needed",
                "Regular gentle exfoliation"
            ]
            advice["ingredients"] = [
                "Vitamin C", "Hyaluronic acid", "Niacinamide"
            ]
        
        # Age-specific advice
        age = demographics.get("age", "")
        if age in ["20-29", "30-39"]:
            advice["lifestyle"].append("Start using sunscreen daily for prevention")
            advice["ingredients"].append("Vitamin C for antioxidant protection")
        elif age in ["40-49", "50-59", "60-69", "70+"]:
            advice["lifestyle"].append("Focus on anti-aging and hydration")
            advice["ingredients"].extend(["Retinol", "Peptides", "AHA/BHA"])
        
        # Issue-specific advice
        for issue in skin_issues:
            issue_name = issue.get("name", "").lower()
            if issue_name == "acne":
                advice["ingredients"].append("Salicylic acid or Benzoyl peroxide")
                advice["lifestyle"].append("Avoid touching your face frequently")
            elif issue_name == "redness":
                advice["ingredients"].append("Niacinamide or Centella asiatica")
                advice["avoid"].append("Fragrant products")
            elif issue_name == "bags":
                advice["routine"].append("Use caffeine-based eye creams")
                advice["lifestyle"].append("Ensure adequate sleep and hydration")
        
        return advice
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get the status of all analysis service components.
        
        Returns:
            Status information for all service components.
        """
        return {
            "skin_model": self.skin_model.get_model_info(),
            "fairface_model": self.fairface_model.get_model_info(),
            "groq_client": {
                "available": self.groq_client is not None,
                "configured": self.groq_client.is_configured() if self.groq_client else False
            },
            "image_processor": {
                "available": True,
                "face_detection": self.image_processor.is_face_detection_available()
            }
        }
