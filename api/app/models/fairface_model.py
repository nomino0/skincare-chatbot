"""
FairFace Model for demographic prediction.
Handles PyTorch FairFace model loading and inference for age, gender, and race prediction.
"""

import logging
import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from typing import Dict, Optional, Any
import cv2
from PIL import Image
from torchvision import transforms

logger = logging.getLogger(__name__)


class FairFaceModel:
    """
    Wrapper class for the FairFace PyTorch model.
    Handles model loading, preprocessing, and demographic prediction.
    """
    
    # Class constants
    RACE_CATEGORIES = [
        'White', 'Black', 'Latino_Hispanic', 'East Asian', 
        'Southeast Asian', 'Indian', 'Middle Eastern'
    ]
    GENDER_CATEGORIES = ['Male', 'Female']
    AGE_CATEGORIES = [
        '0-2', '3-9', '10-19', '20-29', '30-39', 
        '40-49', '50-59', '60-69', '70+'
    ]
    INPUT_SIZE = (224, 224)
    
    def __init__(self, model_path: Path):
        """
        Initialize the FairFace model.
        
        Args:
            model_path: Path to the FairFace model file.
        """
        self.model_path = model_path
        self.model: Optional[torch.nn.Module] = None
        self.is_loaded = False
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Define image transformations
        self.transform = transforms.Compose([
            transforms.Resize(self.INPUT_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Try to load the model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the FairFace PyTorch model."""
        try:
            if self.model_path.exists():
                logger.info(f"Attempting to load FairFace model from: {self.model_path}")
                
                # Load the model
                self.model = torch.load(
                    str(self.model_path), 
                    map_location=self.device
                )
                
                # Set to evaluation mode
                self.model.eval()
                self.is_loaded = True
                
                logger.info(f"Successfully loaded FairFace model from: {self.model_path}")
            else:
                logger.warning(f"FairFace model not found at: {self.model_path}")
                self.is_loaded = False
                
        except Exception as e:
            logger.error(f"Error loading FairFace model: {e}")
            self.is_loaded = False
            self.model = None
    
    def is_model_loaded(self) -> bool:
        """Check if the model is successfully loaded."""
        return self.is_loaded and self.model is not None
    
    def preprocess_image(self, face_image: np.ndarray) -> torch.Tensor:
        """
        Preprocess face image for FairFace model input.
        
        Args:
            face_image: Face image as numpy array (BGR format from OpenCV).
            
        Returns:
            Preprocessed image tensor ready for model inference.
            
        Raises:
            ValueError: If image preprocessing fails.
        """
        try:
            # Convert BGR to RGB
            face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(face_rgb)
            
            # Apply transformations
            img_tensor = self.transform(pil_image)
            
            # Add batch dimension
            img_tensor = img_tensor.unsqueeze(0)
            
            # Move to appropriate device
            img_tensor = img_tensor.to(self.device)
            
            return img_tensor
            
        except Exception as e:
            logger.error(f"Error preprocessing image for FairFace: {e}")
            raise ValueError(f"Image preprocessing failed: {e}")
    
    def predict(self, face_image: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Predict demographics from face image.
        
        Args:
            face_image: Face image as numpy array (BGR format).
            
        Returns:
            Dictionary with demographic predictions or None if prediction fails.
        """
        if not self.is_model_loaded():
            logger.warning("FairFace model is not loaded. Cannot make predictions.")
            return None
        
        try:
            # Preprocess the image
            img_tensor = self.preprocess_image(face_image)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(img_tensor)
                
                # Handle different output formats
                if isinstance(outputs, (list, tuple)) and len(outputs) >= 3:
                    race_outputs, gender_outputs, age_outputs = outputs[:3]
                else:
                    # If single output, try to split it
                    logger.warning("Unexpected FairFace model output format")
                    return None
                
                # Apply softmax to get probabilities
                race_scores = F.softmax(race_outputs, dim=1).squeeze().cpu().numpy()
                gender_scores = F.softmax(gender_outputs, dim=1).squeeze().cpu().numpy()
                age_scores = F.softmax(age_outputs, dim=1).squeeze().cpu().numpy()
                
                # Get highest probability categories
                race_idx = np.argmax(race_scores)
                gender_idx = np.argmax(gender_scores)
                age_idx = np.argmax(age_scores)
                
                return {
                    'race': self.RACE_CATEGORIES[race_idx],
                    'gender': self.GENDER_CATEGORIES[gender_idx],
                    'age': self.AGE_CATEGORIES[age_idx],
                    'confidence': {
                        'race': float(np.max(race_scores)),
                        'gender': float(np.max(gender_scores)),
                        'age': float(np.max(age_scores))
                    },
                    'all_scores': {
                        'race': {
                            category: float(score) 
                            for category, score in zip(self.RACE_CATEGORIES, race_scores)
                        },
                        'gender': {
                            category: float(score) 
                            for category, score in zip(self.GENDER_CATEGORIES, gender_scores)
                        },
                        'age': {
                            category: float(score) 
                            for category, score in zip(self.AGE_CATEGORIES, age_scores)
                        }
                    }
                }
                
        except Exception as e:
            logger.error(f"Error during FairFace prediction: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information.
        """
        if not self.is_model_loaded():
            return {
                "status": "not_loaded", 
                "error": "FairFace model not loaded",
                "model_path": str(self.model_path)
            }
        
        try:
            # Count parameters
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            
            return {
                "status": "loaded",
                "model_path": str(self.model_path),
                "device": str(self.device),
                "total_parameters": total_params,
                "trainable_parameters": trainable_params,
                "race_categories": self.RACE_CATEGORIES,
                "gender_categories": self.GENDER_CATEGORIES,
                "age_categories": self.AGE_CATEGORIES,
                "input_size": self.INPUT_SIZE
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
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
    
    def set_device(self, device: str) -> None:
        """
        Set the device for model inference.
        
        Args:
            device: Device string ('cpu' or 'cuda').
        """
        try:
            self.device = torch.device(device)
            if self.model is not None:
                self.model = self.model.to(self.device)
            logger.info(f"Set FairFace model device to: {self.device}")
        except Exception as e:
            logger.error(f"Error setting device: {e}")


def create_fairface_model(model_path: Path) -> FairFaceModel:
    """
    Factory function to create a FairFaceModel instance.
    
    Args:
        model_path: Path to the FairFace model file.
        
    Returns:
        Configured FairFaceModel instance.
    """
    return FairFaceModel(model_path=model_path)
