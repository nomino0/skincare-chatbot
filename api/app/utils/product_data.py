"""
Product database with reliable skincare product data.
Provides fallback product recommendations when web scraping fails.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ProductDatabase:
    """
    Database of reliable skincare products for recommendations.
    Organized by skin type and concerns.
    """
    
    def __init__(self):
        """Initialize the product database."""
        self.products = self._load_product_data()
    
    def _load_product_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load product data organized by skin type."""
        return {
            "dry": [
                {
                    "name": "Hydrating Facial Cleanser",
                    "brand": "CeraVe",
                    "price": "14.99",
                    "currency": "USD",
                    "link": "https://www.cerave.com/skincare/cleansers/hydrating-facial-cleanser",
                    "imageUrl": "https://via.placeholder.com/300x300?text=CeraVe+Cleanser",
                    "description": "Gentle non-foaming cleanser that removes dirt and makeup while maintaining moisture barrier",
                    "forSkinType": ["Dry", "Normal"],
                    "targetGender": "All",
                    "ingredients": ["Ceramides", "Hyaluronic Acid", "MVE Technology"]
                },
                {
                    "name": "Daily Moisturizing Lotion",
                    "brand": "CeraVe",
                    "price": "19.99",
                    "currency": "USD",
                    "link": "https://www.cerave.com/skincare/moisturizers/daily-moisturizing-lotion",
                    "imageUrl": "https://via.placeholder.com/300x300?text=CeraVe+Moisturizer",
                    "description": "Lightweight, oil-free moisturizer with hyaluronic acid and ceramides",
                    "forSkinType": ["Dry", "Normal"],
                    "targetGender": "All",
                    "ingredients": ["Ceramides", "Hyaluronic Acid", "Dimethicone"]
                },
                {
                    "name": "Hyaluronic Acid Serum",
                    "brand": "The Ordinary",
                    "price": "8.90",
                    "currency": "USD",
                    "link": "https://theordinary.com/en-us/hyaluronic-acid-2-b5-serum-100436.html",
                    "imageUrl": "https://via.placeholder.com/300x300?text=TO+HA+Serum",
                    "description": "Hydration support formula with multiple weights of hyaluronic acid",
                    "forSkinType": ["Dry", "All"],
                    "targetGender": "All",
                    "ingredients": ["Hyaluronic Acid", "Vitamin B5", "Sodium Hyaluronate"]
                }
            ],
            "oily": [
                {
                    "name": "Foaming Facial Cleanser",
                    "brand": "CeraVe",
                    "price": "14.99",
                    "currency": "USD",
                    "link": "https://www.cerave.com/skincare/cleansers/foaming-facial-cleanser",
                    "imageUrl": "https://via.placeholder.com/300x300?text=CeraVe+Foaming",
                    "description": "Foaming gel cleanser for normal to oily skin that removes excess oil",
                    "forSkinType": ["Oily", "Combination"],
                    "targetGender": "All",
                    "ingredients": ["Ceramides", "Niacinamide", "Hyaluronic Acid"]
                },
                {
                    "name": "Niacinamide 10% + Zinc 1%",
                    "brand": "The Ordinary",
                    "price": "6.50",
                    "currency": "USD",
                    "link": "https://theordinary.com/en-us/niacinamide-10-zinc-1-serum-100436.html",
                    "imageUrl": "https://via.placeholder.com/300x300?text=TO+Niacinamide",
                    "description": "High-strength vitamin formula to reduce sebum production and minimize pores",
                    "forSkinType": ["Oily", "Combination"],
                    "targetGender": "All",
                    "ingredients": ["Niacinamide", "Zinc PCA"]
                },
                {
                    "name": "Oil-Free Acne Face Wash",
                    "brand": "Neutrogena",
                    "price": "9.99",
                    "currency": "USD",
                    "link": "https://www.neutrogena.com/products/skincare/oil-free-acne-fighting-face-wash",
                    "imageUrl": "https://via.placeholder.com/300x300?text=Neutrogena+Acne",
                    "description": "Maximum-strength salicylic acid acne treatment for clearer skin",
                    "forSkinType": ["Oily", "Acne-Prone"],
                    "targetGender": "All",
                    "forSkinIssues": ["Acne"],
                    "ingredients": ["Salicylic Acid"]
                }
            ],
            "combination": [
                {
                    "name": "Toleriane Purifying Foaming Cleanser",
                    "brand": "La Roche-Posay",
                    "price": "16.99",
                    "currency": "USD",
                    "link": "https://www.laroche-posay.us/our-products/face/face-wash/toleriane-purifying-foaming-facial-wash",
                    "imageUrl": "https://via.placeholder.com/300x300?text=LRP+Cleanser",
                    "description": "Gentle foaming face wash that removes excess oil while respecting skin's pH",
                    "forSkinType": ["Combination", "Normal"],
                    "targetGender": "All",
                    "ingredients": ["La Roche-Posay Thermal Spring Water", "Coco-Betaine"]
                },
                {
                    "name": "Effaclar Duo Acne Treatment",
                    "brand": "La Roche-Posay",
                    "price": "32.99",
                    "currency": "USD",
                    "link": "https://www.laroche-posay.us/our-products/acne-oily-skin/spot-treatment/effaclar-duo-acne-treatment",
                    "imageUrl": "https://via.placeholder.com/300x300?text=LRP+Effaclar",
                    "description": "Dual action acne treatment that targets spots and visible imperfections",
                    "forSkinType": ["Combination", "Oily"],
                    "forSkinIssues": ["Acne", "Pores"],
                    "targetGender": "All",
                    "ingredients": ["Benzoyl Peroxide", "Lipo-Hydroxy Acid"]
                }
            ],
            "normal": [
                {
                    "name": "Gentle Skin Cleanser",
                    "brand": "Cetaphil",
                    "price": "14.99",
                    "currency": "USD",
                    "link": "https://www.cetaphil.com/us/cleansers/gentle-skin-cleanser",
                    "imageUrl": "https://via.placeholder.com/300x300?text=Cetaphil+Cleanser",
                    "description": "Mild, non-irritating formula cleanses skin without stripping moisture",
                    "forSkinType": ["Normal", "Dry", "Sensitive"],
                    "targetGender": "All",
                    "ingredients": ["Glycerin", "Cetyl Alcohol", "Propylene Glycol"]
                },
                {
                    "name": "Daily Facial Moisturizer SPF 30",
                    "brand": "Cetaphil", 
                    "price": "18.99",
                    "currency": "USD",
                    "link": "https://www.cetaphil.com/us/moisturizers/daily-facial-moisturizer-with-sunscreen",
                    "imageUrl": "https://via.placeholder.com/300x300?text=Cetaphil+SPF",
                    "description": "Lightweight daily moisturizer with broad spectrum sun protection",
                    "forSkinType": ["Normal", "Combination"],
                    "targetGender": "All",
                    "ingredients": ["Zinc Oxide", "Octinoxate", "Glycerin"]
                }
            ],
            "sensitive": [
                {
                    "name": "Ultra Gentle Hydrating Cleanser",
                    "brand": "Neutrogena",
                    "price": "11.99",
                    "currency": "USD",
                    "link": "https://www.neutrogena.com/products/skincare/ultra-gentle-hydrating-cleanser",
                    "imageUrl": "https://via.placeholder.com/300x300?text=Neutrogena+Gentle",
                    "description": "Creamy, soap-free formula cleanses without irritation",
                    "forSkinType": ["Sensitive", "Dry"],
                    "targetGender": "All",
                    "ingredients": ["Polyglyceryl-4 Caprate", "Ultra-mild cleansers"]
                },
                {
                    "name": "Toleriane Double Repair Face Moisturizer",
                    "brand": "La Roche-Posay",
                    "price": "20.99",
                    "currency": "USD",
                    "link": "https://www.laroche-posay.us/our-products/face/face-moisturizer/toleriane-double-repair-face-moisturizer",
                    "imageUrl": "https://via.placeholder.com/300x300?text=LRP+Toleriane",
                    "description": "Oil-free moisturizer with ceramides and niacinamide to restore skin barrier",
                    "forSkinType": ["Sensitive", "Normal"],
                    "targetGender": "All",
                    "ingredients": ["Ceramide-3", "Niacinamide", "Thermal Spring Water"]
                }
            ]
        }
    
    def get_products(
        self,
        skin_type: str,
        skin_issues: List[str] = None,
        gender: str = "All",
        age_group: str = None,
        max_products: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get product recommendations based on criteria.
        
        Args:
            skin_type: Target skin type.
            skin_issues: List of skin issues to address.
            gender: Target gender.
            age_group: Target age group.
            max_products: Maximum number of products to return.
            
        Returns:
            List of matching products.
        """
        skin_issues = skin_issues or []
        skin_type_key = skin_type.lower()
        
        # Get products for the skin type
        type_products = self.products.get(skin_type_key, self.products.get("normal", []))
        
        # Filter by gender if specified
        if gender and gender != "All":
            type_products = [
                p for p in type_products 
                if p.get("targetGender") in ["All", gender]
            ]
        
        # Prioritize products that address specific skin issues
        if skin_issues:
            issue_products = []
            general_products = []
            
            for product in type_products:
                product_issues = product.get("forSkinIssues", [])
                if any(issue.capitalize() in product_issues for issue in skin_issues):
                    issue_products.append(product)
                else:
                    general_products.append(product)
            
            # Return issue-specific products first, then general ones
            all_products = issue_products + general_products
        else:
            all_products = type_products
        
        return all_products[:max_products]
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Get all products in the database.
        
        Returns:
            List of all products.
        """
        all_products = []
        for skin_type_products in self.products.values():
            all_products.extend(skin_type_products)
        return all_products
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """
        Search products by name, brand, or description.
        
        Args:
            query: Search query.
            
        Returns:
            List of matching products.
        """
        query_lower = query.lower()
        matching_products = []
        
        for product in self.get_all_products():
            if (query_lower in product.get("name", "").lower() or
                query_lower in product.get("brand", "").lower() or
                query_lower in product.get("description", "").lower()):
                matching_products.append(product)
        
        return matching_products
    
    def get_products_by_ingredient(self, ingredient: str) -> List[Dict[str, Any]]:
        """
        Get products containing a specific ingredient.
        
        Args:
            ingredient: Ingredient to search for.
            
        Returns:
            List of products containing the ingredient.
        """
        ingredient_lower = ingredient.lower()
        matching_products = []
        
        for product in self.get_all_products():
            product_ingredients = product.get("ingredients", [])
            if any(ingredient_lower in ing.lower() for ing in product_ingredients):
                matching_products.append(product)
        
        return matching_products
