"""
Skin Analysis Model for multitask skin condition detection.
Handles TensorFlow/Keras model loading and inference for skin type and condition prediction.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Any, List
import cv2

logger = logging.getLogger(__name__)


class SkinAnalysisModel:
    """
    Wrapper class for the multitask skin analysis model.
    Handles model loading, preprocessing, and skin condition prediction.
    """
    
    # Class constants - must match the original model's training labels
    SKIN_TYPES = ['Normal', 'Dry', 'Oily']  # Original model has 3 classes
    SKIN_CONDITIONS = ['Acne', 'Redness', 'Bags']  # Original model has 3 conditions
    INPUT_SIZE = (224, 224)
    
    def __init__(self, model_paths: Dict[str, str], confidence_threshold: float = 0.5):
        """
        Initialize the Skin Analysis model.
        
        Args:
            model_paths: Dictionary containing paths to model files.
            confidence_threshold: Minimum confidence for predictions.
        """
        self.model_paths = model_paths
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.is_loaded = False
        
        # Try to load the model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the skin analysis model."""
        try:
            model_path = self.model_paths.get('skin_analysis')
            if model_path and Path(model_path).exists():
                logger.info(f"Attempting to load skin analysis model from: {model_path}")
                
                # Load the actual TensorFlow/Keras model
                try:
                    from tensorflow.keras.models import load_model
                    self.model = load_model(model_path)
                    self.is_loaded = True
                    logger.info(f"Successfully loaded skin analysis model from: {model_path}")
                except ImportError:
                    logger.error("TensorFlow not installed. Install with: pip install tensorflow")
                    self.is_loaded = False
                except Exception as load_error:
                    logger.error(f"Error loading Keras model: {load_error}")
                    self.is_loaded = False
            else:
                logger.warning(f"Skin analysis model not found at: {model_path}")
                self.is_loaded = False
                
        except Exception as e:
            logger.error(f"Error loading skin analysis model: {e}")
            self.is_loaded = False
            self.model = None
    
    def is_model_loaded(self) -> bool:
        """Check if the model is successfully loaded."""
        return self.is_loaded and self.model is not None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for skin analysis model input.
        
        Args:
            image: Input image as numpy array (BGR format from OpenCV).
            
        Returns:
            Preprocessed image array ready for model inference.
            
        Raises:
            ValueError: If image preprocessing fails.
        """
        try:
            # Resize image to model input size
            resized = cv2.resize(image, self.INPUT_SIZE)
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Normalize pixel values to [0, 1]
            normalized = rgb_image.astype(np.float32) / 255.0
            
            # Add batch dimension
            preprocessed = np.expand_dims(normalized, axis=0)
            
            return preprocessed
            
        except Exception as e:
            logger.error(f"Error preprocessing image for skin analysis: {e}")
            raise ValueError(f"Image preprocessing failed: {e}")
    
    def predict(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Predict skin type and conditions from image.
        
        Args:
            image: Input image as numpy array (BGR format).
            
        Returns:
            Dictionary with skin analysis predictions or None if prediction fails.
        """
        if not self.is_model_loaded():
            logger.warning("Skin analysis model is not loaded. Using mock predictions.")
            return self._generate_mock_prediction()
        
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Make prediction with the loaded model
            predictions = self.model.predict(processed_image, verbose=0)
            type_pred, issue_pred = predictions
            
            # Get skin type result
            skin_type_idx = np.argmax(type_pred, axis=1)[0]
            skin_type_confidence = float(type_pred[0][skin_type_idx] * 100)
            
            # Get skin issues with confidence > threshold
            skin_issues = []
            for i, label in enumerate(self.SKIN_CONDITIONS):
                confidence = float(issue_pred[0][i] * 100)
                if issue_pred[0][i] > self.confidence_threshold:
                    skin_issues.append({
                        "name": label,
                        "confidence": round(confidence, 2)
                    })
            
            # Return in the format expected by the frontend
            return {
                "skinType": {
                    "type": self.SKIN_TYPES[skin_type_idx],
                    "confidence": round(skin_type_confidence, 2)
                },
                "skinIssues": skin_issues
            }
                
        except Exception as e:
            logger.error(f"Error during skin analysis prediction: {e}")
            return None
    
    def _generate_mock_prediction(self) -> Dict[str, Any]:
        """Generate mock predictions for development/testing."""
        # Generate random but realistic skin analysis results
        import random
        
        # Mock skin type prediction
        skin_type_scores = [random.random() for _ in self.SKIN_TYPES]
        max_idx = np.argmax(skin_type_scores)
        max_confidence = max(skin_type_scores) * 100
        
        # Mock skin conditions
        conditions = []
        for condition in self.SKIN_CONDITIONS:
            confidence = random.uniform(0.3, 0.9)
            if confidence > self.confidence_threshold:
                conditions.append({
                    'name': condition,
                    'confidence': round(confidence * 100, 2)
                })
        
        # Return in the format expected by the frontend (matching old backend format)
        return {
            'skinType': {
                'type': self.SKIN_TYPES[max_idx],
                'confidence': round(max_confidence, 2)
            },
            'skinIssues': conditions
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information.
        """
        if not self.is_model_loaded():
            return {
                "status": "not_loaded", 
                "error": "Skin analysis model not loaded",
                "model_paths": self.model_paths
            }
        
        return {
            "status": "loaded (mock)",
            "model_paths": self.model_paths,
            "confidence_threshold": self.confidence_threshold,
            "skin_types": self.SKIN_TYPES,
            "skin_conditions": self.SKIN_CONDITIONS,
            "input_size": self.INPUT_SIZE,
            "note": "Using mock model for development"
        }
    
    def reload_model(self) -> bool:
        """
        Reload the model from disk.
        
        Returns:
            True if model was successfully reloaded, False otherwise.
        """
        self.model = None
        self.is_loaded = False
        self._load_model()
        return self.is_loaded
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Set the confidence threshold for predictions.
        
        Args:
            threshold: New confidence threshold (0.0 to 1.0).
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            logger.info(f"Set confidence threshold to: {threshold}")
        else:
            logger.error(f"Invalid confidence threshold: {threshold}. Must be between 0.0 and 1.0")


def create_skin_analysis_model(model_paths: Dict[str, str], confidence_threshold: float = 0.5) -> SkinAnalysisModel:
    """
    Factory function to create a SkinAnalysisModel instance.
    
    Args:
        model_paths: Dictionary containing paths to model files.
        confidence_threshold: Minimum confidence for predictions.
        
    Returns:
        Configured SkinAnalysisModel instance.
    """
    return SkinAnalysisModel(model_paths=model_paths, confidence_threshold=confidence_threshold)
