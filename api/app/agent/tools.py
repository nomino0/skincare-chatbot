"""
LangGraph tools for the skincare agent.
These tools expose existing services to the agent.
"""
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

# Global references to services (will be injected)
_analysis_service = None
_product_service = None

def set_services(analysis_service, product_service):
    """Inject service dependencies."""
    global _analysis_service, _product_service
    _analysis_service = analysis_service
    _product_service = product_service

@tool
def analyze_skin_image(image_data: str) -> Dict[str, Any]:
    """
    Analyze a skin image and return skin type, issues, and demographics.
    
    Args:
        image_data: Base64 encoded image string
        
    Returns:
        Dictionary with skinType, skinIssues, and demographics
    """
    try:
        if not _analysis_service:
            return {"error": "Analysis service not available"}
        
        results = _analysis_service.analyze_skin(image_data)
        return results
    except Exception as e:
        logger.error(f"Error in analyze_skin_image tool: {e}")
        return {"error": str(e)}

@tool
def get_product_recommendations(
    skin_type: str,
    skin_issues: List[str],
    country: str = "United States",
    gender: str = "All",
    age_group: str = "",
    max_products: int = 5
) -> List[Dict[str, Any]]:
    """
    Get personalized product recommendations based on skin profile.
    
    Args:
        skin_type: User's skin type (Dry, Oily, Normal, Combination)
        skin_issues: List of skin concerns (Acne, Redness, etc.)
        country: User's country for localized recommendations
        gender: User's gender
        age_group: User's age group
        max_products: Maximum number of products to return
        
    Returns:
        List of product recommendations with name, brand, price, etc.
    """
    try:
        if not _product_service:
            return [{"error": "Product service not available"}]
        
        products = _product_service.get_product_recommendations(
            skin_type=skin_type,
            skin_issues=skin_issues,
            country=country,
            gender=gender,
            age_group=age_group,
            max_products=max_products
        )
        return products
    except Exception as e:
        logger.error(f"Error in get_product_recommendations tool: {e}")
        return [{"error": str(e)}]

@tool
def find_nearby_stores(
    latitude: float,
    longitude: float,
    radius: int = 5000
) -> List[Dict[str, Any]]:
    """
    Find nearby stores that sell skincare products.
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        radius: Search radius in meters
        
    Returns:
        List of nearby stores with name, address, rating
    """
    try:
        if not _product_service:
            return [{"error": "Product service not available"}]
        
        stores = _product_service.find_nearby_stores(
            latitude=latitude,
            longitude=longitude,
            radius=radius
        )
        return stores
    except Exception as e:
        logger.error(f"Error in find_nearby_stores tool: {e}")
        return [{"error": str(e)}]

# Export all tools
AGENT_TOOLS = [
    analyze_skin_image,
    get_product_recommendations,
    find_nearby_stores
]
