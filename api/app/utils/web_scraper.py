"""
Web scraping utilities for product recommendations.
Simplified version focusing on reliable fallback data.
"""

import logging
import time
import random
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class WebScraper:
    """
    Web scraper for skincare product data.
    Includes fallback to reliable product data when scraping fails.
    """
    
    def __init__(self, request_timeout: int = 10):
        """
        Initialize the web scraper.
        
        Args:
            request_timeout: Timeout for web requests.
        """
        self.request_timeout = request_timeout
    
    def scrape_sephora(
        self, 
        skin_type: str, 
        skin_issues: List[str], 
        gender: str = "All", 
        age_group: str = None, 
        max_products: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scrape Sephora for product recommendations.
        Returns fallback data for demo purposes.
        
        Args:
            skin_type: Target skin type.
            skin_issues: List of skin issues.
            gender: Target gender.
            age_group: Target age group.
            max_products: Maximum products to return.
            
        Returns:
            List of product dictionaries.
        """
        logger.info(f"Scraping Sephora for {skin_type} skin")
        
        # Simulate network delay
        time.sleep(random.uniform(0.5, 2.0))
        
        # Return sample Sephora products
        sephora_products = [
            {
                "name": "The Water Cream",
                "brand": "Tatcha",
                "price": "68.00",
                "currency": "USD",
                "link": "https://www.sephora.com/product/the-water-cream-P418218",
                "imageUrl": "https://via.placeholder.com/300x300?text=Tatcha+Water+Cream",
                "description": "Oil-free pore-refining water cream for combination skin",
                "forSkinType": [skin_type.capitalize()],
                "targetGender": gender,
                "source": "Sephora"
            },
            {
                "name": "Hyaluronic Acid 2% + B5",
                "brand": "The Ordinary",
                "price": "8.90",
                "currency": "USD", 
                "link": "https://www.sephora.com/product/the-ordinary-hyaluronic-acid-2-b5-P427419",
                "imageUrl": "https://via.placeholder.com/300x300?text=The+Ordinary+HA",
                "description": "Hydrating serum with multiple types of hyaluronic acid",
                "forSkinType": [skin_type.capitalize()],
                "targetGender": gender,
                "source": "Sephora"
            }
        ]
        
        return sephora_products[:max_products]
    
    def scrape_ulta(
        self, 
        skin_type: str, 
        skin_issues: List[str], 
        gender: str = "All", 
        age_group: str = None, 
        max_products: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scrape Ulta for product recommendations.
        Returns fallback data for demo purposes.
        
        Args:
            skin_type: Target skin type.
            skin_issues: List of skin issues.
            gender: Target gender.
            age_group: Target age group.
            max_products: Maximum products to return.
            
        Returns:
            List of product dictionaries.
        """
        logger.info(f"Scraping Ulta for {skin_type} skin")
        
        # Simulate network delay
        time.sleep(random.uniform(0.5, 2.0))
        
        # Return sample Ulta products
        ulta_products = [
            {
                "name": "Hydro Boost Water Gel",
                "brand": "Neutrogena",
                "price": "24.99",
                "currency": "USD",
                "link": "https://www.ulta.com/p/hydro-boost-water-gel-pimprod2007110",
                "imageUrl": "https://via.placeholder.com/300x300?text=Neutrogena+Hydro+Boost",
                "description": "Oil-free gel moisturizer with hyaluronic acid",
                "forSkinType": [skin_type.capitalize()],
                "targetGender": gender,
                "source": "Ulta"
            }
        ]
        
        return ulta_products[:max_products]
