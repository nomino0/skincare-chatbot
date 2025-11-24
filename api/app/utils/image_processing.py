"""
Image Processing utilities for face detection and image manipulation.
"""

import logging
import cv2
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Utility class for image processing operations.
    Handles face detection, image preprocessing, and validation.
    """
    
    def __init__(self):
        """Initialize the image processor with face detection cascade."""
        self.face_cascade = None
        self._load_face_cascade()
    
    def _load_face_cascade(self) -> None:
        """Load the Haar cascade for face detection."""
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                logger.error("Failed to load face detection cascade")
                self.face_cascade = None
            else:
                logger.info("Face detection cascade loaded successfully")
                
        except Exception as e:
            logger.error(f"Error loading face cascade: {e}")
            self.face_cascade = None
    
    def crop_face(self, image: np.ndarray, scale_factor: float = 1.1, min_neighbors: int = 5) -> Optional[np.ndarray]:
        """
        Detect and crop the largest face from an image.
        
        Args:
            image: Input image as numpy array (BGR format).
            scale_factor: How much the image size is reduced at each scale.
            min_neighbors: How many neighbors each candidate rectangle should have to retain it.
            
        Returns:
            Cropped face image or None if no face detected.
        """
        if self.face_cascade is None:
            logger.error("Face cascade not loaded")
            return None
        
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                logger.warning("No faces detected in image")
                return None
            
            # Get the largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            # Add some padding around the face
            padding = int(min(w, h) * 0.1)
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            
            # Crop the face
            face = image[y:y+h, x:x+w]
            
            logger.info(f"Face detected and cropped: {w}x{h} at ({x}, {y})")
            return face
            
        except Exception as e:
            logger.error(f"Error during face detection: {e}")
            return None
    
    def detect_multiple_faces(self, image: np.ndarray) -> list:
        """
        Detect all faces in an image.
        
        Args:
            image: Input image as numpy array.
            
        Returns:
            List of face rectangles (x, y, w, h).
        """
        if self.face_cascade is None:
            return []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
            return faces.tolist()
        except Exception as e:
            logger.error(f"Error detecting multiple faces: {e}")
            return []
    
    def validate_image(self, image: np.ndarray) -> bool:
        """
        Validate if the image is suitable for processing.
        
        Args:
            image: Input image to validate.
            
        Returns:
            True if image is valid for processing.
        """
        if image is None:
            return False
        
        # Check if image has proper dimensions
        if len(image.shape) not in [2, 3]:
            return False
        
        # Check minimum size
        if image.shape[0] < 50 or image.shape[1] < 50:
            return False
        
        # Check maximum size (to prevent memory issues)
        if image.shape[0] > 4000 or image.shape[1] > 4000:
            return False
        
        return True
    
    def resize_image(self, image: np.ndarray, target_size: Tuple[int, int], maintain_aspect: bool = True) -> np.ndarray:
        """
        Resize an image to target size.
        
        Args:
            image: Input image to resize.
            target_size: Target (width, height).
            maintain_aspect: Whether to maintain aspect ratio.
            
        Returns:
            Resized image.
        """
        try:
            if maintain_aspect:
                # Calculate aspect ratio
                h, w = image.shape[:2]
                target_w, target_h = target_size
                
                # Calculate scaling factor
                scale = min(target_w / w, target_h / h)
                new_w = int(w * scale)
                new_h = int(h * scale)
                
                # Resize image
                resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
                
                # Add padding if needed
                if new_w != target_w or new_h != target_h:
                    # Create a new image with target size
                    if len(image.shape) == 3:
                        padded = np.zeros((target_h, target_w, image.shape[2]), dtype=image.dtype)
                    else:
                        padded = np.zeros((target_h, target_w), dtype=image.dtype)
                    
                    # Calculate padding offsets
                    y_offset = (target_h - new_h) // 2
                    x_offset = (target_w - new_w) // 2
                    
                    # Place resized image in center
                    padded[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                    return padded
                else:
                    return resized
            else:
                # Direct resize without maintaining aspect ratio
                return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
                
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return image
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply basic image enhancement for better analysis.
        
        Args:
            image: Input image to enhance.
            
        Returns:
            Enhanced image.
        """
        try:
            # Convert to LAB color space for better enhancement
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels and convert back to BGR
            enhanced_lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image
    
    def normalize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize image pixel values to [0, 1] range.
        
        Args:
            image: Input image to normalize.
            
        Returns:
            Normalized image.
        """
        try:
            return image.astype(np.float32) / 255.0
        except Exception as e:
            logger.error(f"Error normalizing image: {e}")
            return image
    
    def is_face_detection_available(self) -> bool:
        """
        Check if face detection is available.
        
        Returns:
            True if face detection cascade is loaded.
        """
        return self.face_cascade is not None
    
    def get_image_stats(self, image: np.ndarray) -> dict:
        """
        Get basic statistics about an image.
        
        Args:
            image: Input image.
            
        Returns:
            Dictionary with image statistics.
        """
        try:
            stats = {
                "shape": image.shape,
                "dtype": str(image.dtype),
                "size_bytes": image.nbytes,
                "min_value": float(np.min(image)),
                "max_value": float(np.max(image)),
                "mean_value": float(np.mean(image))
            }
            
            if len(image.shape) == 3:
                stats["channels"] = image.shape[2]
                stats["channel_means"] = [float(np.mean(image[:, :, i])) for i in range(image.shape[2])]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting image stats: {e}")
            return {"error": str(e)}
