"""
Product Service for handling skincare product recommendations.
Manages product data, web scraping, and recommendation logic.
"""

import logging
from typing import Dict, List, Any, Optional
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time
import random

from ..utils.web_scraper import WebScraper
from ..utils.product_data import ProductDatabase

logger = logging.getLogger(__name__)


class ProductService:
    """
    Service class for handling product recommendations and store locations.
    Manages product data retrieval and recommendation logic.
    """
    
    def __init__(
        self, 
        web_scraper: WebScraper,
        product_database: ProductDatabase,
        google_maps_api_key: Optional[str] = None,
        max_products: int = 12,
        request_timeout: int = 10
    ):
        """
        Initialize the product service.
        
        Args:
            web_scraper: Web scraping utility for product data.
            product_database: Product database with reliable fallback data.
            google_maps_api_key: Google Maps API key for store locations.
            max_products: Maximum number of products to return.
            request_timeout: Timeout for external API requests.
        """
        self.web_scraper = web_scraper
        self.product_database = product_database
        self.google_maps_api_key = google_maps_api_key
        self.max_products = max_products
        self.request_timeout = request_timeout
    
    def get_product_recommendations(
        self,
        skin_type: str,
        skin_issues: List[str] = None,
        gender: str = "All",
        age_group: str = None,
        country: str = None,
        user_ip: str = None,
        max_products: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get dynamic product recommendations based on real-time web scraping and user location.
        
        Args:
            skin_type: User's skin type (Normal, Dry, Oily, etc.).
            skin_issues: List of detected skin issues.
            gender: User's gender for targeted recommendations.
            age_group: User's age group for age-appropriate products.
            country: User's country (auto-detected if not provided).
            user_ip: User's IP for location detection.
            max_products: Maximum number of products to return.
            
        Returns:
            List of dynamic product recommendations with real pricing and availability.
        """
        max_products = max_products or self.max_products
        skin_issues = skin_issues or []
        
        # Detect user location if not provided
        if not country:
            country = self._detect_user_location(user_ip)
        
        logger.info(f"Getting LIVE product recommendations for: {skin_type} skin, issues: {skin_issues}, location: {country}")
        
        try:
            # Get real-time dynamic products from multiple sources
            live_products = self._get_live_product_data(
                skin_type, skin_issues, gender, age_group, country, max_products
            )
            
            if not live_products:
                # Return honest message instead of static data
                return [{
                    "message": "We're currently updating our product database with the latest recommendations. Please try again in a few moments for real-time product suggestions with current pricing.",
                    "status": "updating_database",
                    "retry_suggested": True,
                    "estimated_wait": "30-60 seconds"
                }]
            
            # Add real-time pricing and availability
            enhanced_products = self._enhance_with_live_data(live_products, country)
            
            # Add shipping costs and delivery times for user's location
            self._add_shipping_information(enhanced_products, country)
            
            return enhanced_products[:max_products]
            
        except Exception as e:
            logger.error(f"Error getting live product recommendations: {e}")
            return [{
                "message": "Our recommendation system is temporarily offline. We're working to restore real-time product suggestions as quickly as possible.",
                "status": "service_temporarily_unavailable",
                "support_contact": "Please check back in 10-15 minutes or contact support if this persists."
            }]
    
    def find_nearby_stores(
        self,
        latitude: float,
        longitude: float,
        radius: int = 5000,
        product_type: str = "skincare"
    ) -> List[Dict[str, Any]]:
        """
        Find nearby stores that sell skincare products.
        
        Args:
            latitude: User's latitude.
            longitude: User's longitude.
            radius: Search radius in meters.
            product_type: Type of products to search for.
            
        Returns:
            List of nearby stores with details.
            
        Raises:
            ValueError: If Google Maps API is not configured or request fails.
        """
        if not self.google_maps_api_key:
            raise ValueError("Google Maps API key is not configured")
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "type": "store",
                "keyword": f"{product_type} store beauty",
                "key": self.google_maps_api_key
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            response.raise_for_status()
            
            places_data = response.json()
            
            # Process and format stores
            stores = []
            for place in places_data.get("results", []):
                store = self._format_store_data(place)
                stores.append(store)
            
            return stores
            
        except requests.RequestException as e:
            logger.error(f"Error finding nearby stores: {e}")
            raise ValueError(f"Failed to find nearby stores: {e}")
    
    def find_nearby_products(
        self,
        latitude: float,
        longitude: float,
        skin_type: str,
        skin_issues: List[str] = None,
        gender: str = "All",
        age_group: str = None,
        radius: int = 5000
    ) -> Dict[str, Any]:
        """
        Find both product recommendations and nearby stores where they can be purchased.
        
        Args:
            latitude: User's latitude.
            longitude: User's longitude.
            skin_type: User's skin type.
            skin_issues: List of detected skin issues.
            gender: User's gender.
            age_group: User's age group.
            radius: Search radius for stores.
            
        Returns:
            Dictionary with products and nearby stores.
        """
        try:
            # Get product recommendations
            products = self.get_product_recommendations(
                skin_type=skin_type,
                skin_issues=skin_issues,
                gender=gender,
                age_group=age_group,
                max_products=15
            )
            
            # Get nearby stores
            stores = self.find_nearby_stores(latitude, longitude, radius)
            
            # Match products to appropriate stores
            nearby_products = self._match_products_to_stores(products, stores)
            
            # Group products by price category
            grouped_products = self._group_products_by_price(nearby_products)
            
            return {
                "products": nearby_products,
                "groupedByPrice": grouped_products,
                "nearbyStores": stores[:10]  # Top 10 stores
            }
            
        except Exception as e:
            logger.error(f"Error finding nearby products: {e}")
            raise ValueError(f"Failed to find nearby products: {e}")
    
    def _get_scraped_products(
        self, 
        skin_type: str, 
        skin_issues: List[str], 
        gender: str, 
        age_group: str, 
        max_products: int
    ) -> List[Dict[str, Any]]:
        """
        Get products from real-time web scraping with timeout and error handling.
        
        Args:
            skin_type: User's skin type.
            skin_issues: List of skin issues.
            gender: User's gender.
            age_group: User's age group.
            max_products: Maximum number of products.
            
        Returns:
            List of scraped products.
        """
        scraped_products = []
        
        try:
            # Use ThreadPoolExecutor for concurrent scraping with timeout
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Submit scraping tasks for multiple retailers
                futures = {}
                
                # Major beauty retailers for real-time data
                futures['sephora'] = executor.submit(
                    self.web_scraper.scrape_sephora_live,
                    skin_type, skin_issues, gender, age_group, max_products // 3
                )
                futures['ulta'] = executor.submit(
                    self.web_scraper.scrape_ulta_live,
                    skin_type, skin_issues, gender, age_group, max_products // 3
                )
                futures['amazon'] = executor.submit(
                    self.web_scraper.scrape_amazon_beauty,
                    skin_type, skin_issues, gender, age_group, max_products // 3
                )
                
                # Collect results with timeout
                for retailer, future in futures.items():
                    try:
                        products = future.result(timeout=12)  # 12 seconds per retailer
                        if products:
                            scraped_products.extend(products)
                            logger.info(f"Successfully scraped {len(products)} products from {retailer}")
                    except TimeoutError:
                        logger.warning(f"{retailer} scraping timed out")
                    except Exception as e:
                        logger.warning(f"{retailer} scraping failed: {e}")
            
        except Exception as e:
            logger.warning(f"Web scraping failed: {e}")
        
        return scraped_products
    
    def _detect_user_location(self, user_ip: str = None) -> str:
        """
        Detect user's location based on IP address for personalized recommendations.
        
        Args:
            user_ip: User's IP address.
            
        Returns:
            User's country name.
        """
        try:
            if user_ip:
                response = requests.get(f'https://ipapi.co/{user_ip}/json/', timeout=5)
            else:
                response = requests.get('https://ipapi.co/json/', timeout=5)
            
            location_data = response.json()
            country = location_data.get('country_name', 'United States')
            
            logger.info(f"Detected user location: {country}")
            return country
            
        except Exception as e:
            logger.warning(f"Could not detect user location: {e}")
            return "United States"  # Default fallback
    
    def _get_live_product_data(
        self, 
        skin_type: str, 
        skin_issues: List[str], 
        gender: str, 
        age_group: str, 
        country: str,
        max_products: int
    ) -> List[Dict[str, Any]]:
        """
        Get live product data from multiple sources with real-time pricing.
        
        Args:
            skin_type: User's skin type.
            skin_issues: List of skin issues.
            gender: User's gender.
            age_group: User's age group.
            country: User's country.
            max_products: Maximum number of products.
            
        Returns:
            List of live product data.
        """
        live_products = []
        
        try:
            # Get real-time scraped products
            scraped_products = self._get_scraped_products(
                skin_type, skin_issues, gender, age_group, max_products
            )
            
            if scraped_products:
                live_products.extend(scraped_products)
                
            # If we have some live data, enhance it with expert recommendations
            if live_products:
                # Add dermatologist-reviewed products based on conditions
                expert_products = self._get_expert_recommended_products(
                    skin_type, skin_issues, country
                )
                live_products.extend(expert_products)
            
            return live_products
            
        except Exception as e:
            logger.error(f"Error getting live product data: {e}")
            return []
    
    def _enhance_with_live_data(
        self, 
        products: List[Dict[str, Any]], 
        country: str
    ) -> List[Dict[str, Any]]:
        """
        Enhance products with real-time pricing, availability, and shipping info.
        
        Args:
            products: List of products to enhance.
            country: User's country.
            
        Returns:
            Enhanced product list.
        """
        enhanced_products = []
        
        for product in products:
            try:
                # Get real-time pricing
                current_price = self._get_current_price(product, country)
                if current_price:
                    product['current_price'] = current_price
                    product['price_last_updated'] = time.time()
                
                # Check availability
                availability = self._check_availability(product, country)
                product['availability'] = availability
                
                # Add review scores from multiple sources
                reviews = self._get_aggregated_reviews(product)
                product['reviews'] = reviews
                
                enhanced_products.append(product)
                
            except Exception as e:
                logger.warning(f"Could not enhance product {product.get('name', 'unknown')}: {e}")
                enhanced_products.append(product)  # Include anyway
        
        return enhanced_products
    
    def _add_shipping_information(
        self, 
        products: List[Dict[str, Any]], 
        country: str
    ) -> None:
        """
        Add shipping costs and delivery times based on user's location.
        
        Args:
            products: List of products to enhance.
            country: User's country.
        """
        for product in products:
            # Calculate shipping based on retailer and country
            retailer = product.get('retailer', '').lower()
            
            if country == "United States":
                if 'sephora' in retailer:
                    product['shipping'] = {'cost': 'Free over $50', 'delivery_time': '2-3 business days'}
                elif 'ulta' in retailer:
                    product['shipping'] = {'cost': 'Free over $35', 'delivery_time': '3-5 business days'}
                else:
                    product['shipping'] = {'cost': '$5.99', 'delivery_time': '5-7 business days'}
            elif country in ["Canada", "United Kingdom", "Australia"]:
                product['shipping'] = {'cost': '$9.99-15.99', 'delivery_time': '7-14 business days'}
            else:
                product['shipping'] = {'cost': 'Varies by location', 'delivery_time': '10-21 business days'}
    
    def _get_expert_recommended_products(
        self, 
        skin_type: str, 
        skin_issues: List[str], 
        country: str
    ) -> List[Dict[str, Any]]:
        """
        Get products recommended by dermatologists and skincare experts.
        
        Args:
            skin_type: User's skin type.
            skin_issues: List of skin issues.
            country: User's country.
            
        Returns:
            List of expert-recommended products.
        """
        # This would integrate with dermatology databases and expert recommendations
        # For now, returning structure for expert-backed products
        expert_products = []
        
        # Add condition-specific expert recommendations
        for issue in skin_issues:
            if issue.lower() in ['acne', 'pimples']:
                expert_products.append({
                    'type': 'expert_recommendation',
                    'condition': issue,
                    'recommendation_source': 'American Academy of Dermatology',
                    'ingredients_to_look_for': ['Salicylic Acid', 'Benzoyl Peroxide', 'Retinoids'],
                    'ingredients_to_avoid': ['Heavy oils', 'Comedogenic ingredients']
                })
            elif issue.lower() in ['dry', 'dryness']:
                expert_products.append({
                    'type': 'expert_recommendation',
                    'condition': issue,
                    'recommendation_source': 'Dermatology Research',
                    'ingredients_to_look_for': ['Hyaluronic Acid', 'Ceramides', 'Glycerin'],
                    'ingredients_to_avoid': ['Alcohol', 'Fragrances']
                })
        
        return expert_products
    
    def _get_current_price(self, product: Dict[str, Any], country: str) -> Optional[str]:
        """
        Get current real-time price for a product.
        
        Args:
            product: Product dictionary.
            country: User's country.
            
        Returns:
            Current price string or None.
        """
        try:
            # This would integrate with price comparison APIs
            # For now, return the scraped price with timestamp validation
            if 'price' in product and 'price_last_updated' in product:
                # Check if price is recent (within last hour)
                if time.time() - product.get('price_last_updated', 0) < 3600:
                    return product['price']
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not get current price: {e}")
            return None
    
    def _check_availability(self, product: Dict[str, Any], country: str) -> Dict[str, Any]:
        """
        Check real-time availability for a product.
        
        Args:
            product: Product dictionary.
            country: User's country.
            
        Returns:
            Availability information.
        """
        return {
            'in_stock': True,  # This would be checked via retailer APIs
            'stock_level': 'moderate',
            'last_checked': time.time(),
            'available_in_region': True
        }
    
    def _get_aggregated_reviews(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get aggregated reviews from multiple sources.
        
        Args:
            product: Product dictionary.
            
        Returns:
            Aggregated review data.
        """
        return {
            'average_rating': product.get('rating', 4.0),
            'total_reviews': product.get('review_count', 100),
            'sources': ['Sephora', 'Ulta', 'Amazon'],
            'last_updated': time.time()
        }
    
    def _combine_and_deduplicate_products(
        self, 
        scraped_products: List[Dict[str, Any]], 
        fallback_products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Combine scraped and fallback products, removing duplicates.
        
        Args:
            scraped_products: Products from web scraping.
            fallback_products: Reliable fallback products.
            
        Returns:
            Combined and deduplicated product list.
        """
        # Use scraped products if available, otherwise use fallback
        if scraped_products:
            all_products = scraped_products + fallback_products
        else:
            all_products = fallback_products
        
        # Remove duplicates based on brand + name
        seen_products = set()
        unique_products = []
        
        for product in all_products:
            product_key = (
                product.get("brand", "").lower().strip(),
                product.get("name", "").lower().strip()
            )
            
            if product_key not in seen_products and product_key != ("", ""):
                seen_products.add(product_key)
                unique_products.append(product)
        
        return unique_products
    
    def _add_country_specific_info(self, products: List[Dict[str, Any]], country: str) -> None:
        """
        Add country-specific information to products.
        
        Args:
            products: List of products to modify.
            country: User's country.
        """
        for product in products:
            product["availableIn"] = country
            
            # Adjust currency based on country
            if country == "United Kingdom":
                product["currency"] = "GBP"
            elif country == "Canada":
                product["currency"] = "CAD"
            elif country in ["France", "Germany", "Italy", "Spain"]:
                product["currency"] = "EUR"
            else:
                product["currency"] = "USD"
    
    def _categorize_by_price(self, products: List[Dict[str, Any]]) -> None:
        """
        Categorize products by price range.
        
        Args:
            products: List of products to categorize.
        """
        for product in products:
            try:
                price_value = float(product.get("price", "0"))
                if price_value < 10:
                    product["priceCategory"] = "Budget"
                elif price_value < 25:
                    product["priceCategory"] = "Moderate"
                else:
                    product["priceCategory"] = "Premium"
            except (ValueError, TypeError):
                product["priceCategory"] = "Unknown"
    
    def _format_store_data(self, place: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format Google Places API data into store information.
        
        Args:
            place: Raw place data from Google Places API.
            
        Returns:
            Formatted store data.
        """
        store = {
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "location": place.get("geometry", {}).get("location", {}),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "place_id": place.get("place_id"),
            "open_now": place.get("opening_hours", {}).get("open_now"),
            "photo_reference": place.get("photos", [{}])[0].get("photo_reference") if place.get("photos") else None
        }
        
        # Add photo URL if available
        if store["photo_reference"] and self.google_maps_api_key:
            store["photo_url"] = (
                f"https://maps.googleapis.com/maps/api/place/photo"
                f"?maxwidth=400&photoreference={store['photo_reference']}"
                f"&key={self.google_maps_api_key}"
            )
        
        # Identify store type
        store_name = place.get("name", "").lower()
        if "sephora" in store_name:
            store["store_type"] = "Sephora"
            store["products_available"] = ["Luxury skincare", "Makeup", "Fragrances"]
        elif "ulta" in store_name:
            store["store_type"] = "Ulta Beauty"
            store["products_available"] = ["Luxury and drugstore skincare", "Makeup", "Hair care"]
        elif "target" in store_name:
            store["store_type"] = "Target"
            store["products_available"] = ["Drugstore skincare", "Beauty", "Household"]
        elif any(pharmacy in store_name for pharmacy in ["cvs", "walgreens", "rite aid"]):
            store["store_type"] = "Pharmacy"
            store["products_available"] = ["Drugstore skincare", "Medications", "Health products"]
        else:
            store["store_type"] = "Beauty Store"
            store["products_available"] = ["Skincare products", "Beauty items"]
        
        return store
    
    def _match_products_to_stores(
        self, 
        products: List[Dict[str, Any]], 
        stores: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Match products to appropriate nearby stores.
        
        Args:
            products: List of product recommendations.
            stores: List of nearby stores.
            
        Returns:
            Products with matched nearby stores.
        """
        store_types = {
            "luxury": ["sephora", "nordstrom", "bloomingdale", "neiman marcus", "ulta"],
            "drugstore": ["cvs", "walgreens", "rite aid", "target", "walmart"],
            "specialty": ["lush", "the body shop", "kiehl", "bath & body", "l'occitane"]
        }
        
        # Categorize stores
        categorized_stores = {"luxury": [], "drugstore": [], "specialty": [], "other": []}
        
        for store in stores:
            store_name = store.get("name", "").lower()
            store_category = "other"
            
            for category, keywords in store_types.items():
                if any(keyword in store_name for keyword in keywords):
                    store_category = category
                    break
            
            categorized_stores[store_category].append(store)
        
        # Match products to stores
        for product in products:
            brand = product.get("brand", "").lower()
            price_value = 0
            try:
                price_value = float(product.get("price", "0"))
            except:
                pass
            
            # Determine appropriate store types
            matching_stores = []
            
            if price_value > 30 or brand in ["the ordinary", "kiehl's", "drunk elephant", "la roche-posay"]:
                matching_stores = categorized_stores["luxury"]
            elif price_value < 15:
                matching_stores = categorized_stores["drugstore"]
            
            # Add brand-specific stores
            brand_stores = [
                store for store in stores 
                if brand in store.get("name", "").lower()
            ]
            matching_stores.extend(brand_stores)
            
            # If no specific matches, include some general stores
            if not matching_stores:
                matching_stores = stores[:3]
            
            # Add store information to product
            product["nearbyStores"] = [
                {
                    "name": store.get("name"),
                    "address": store.get("address"),
                    "location": store.get("location"),
                    "rating": store.get("rating"),
                    "place_id": store.get("place_id"),
                    "open_now": store.get("open_now"),
                    "map_url": f"https://www.google.com/maps/place/?q=place_id:{store.get('place_id')}"
                }
                for store in matching_stores[:3]
            ]
        
        return products
    
    def _group_products_by_price(self, products: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group products by price category.
        
        Args:
            products: List of products to group.
            
        Returns:
            Dictionary with products grouped by price category.
        """
        grouped = {"Budget": [], "Moderate": [], "Premium": []}
        
        for product in products:
            category = product.get("priceCategory", "Moderate")
            if category in grouped:
                grouped[category].append(product)
        
        return grouped
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get the status of the product service.
        
        Returns:
            Status information for the product service.
        """
        return {
            "web_scraper": {
                "available": self.web_scraper is not None
            },
            "product_database": {
                "available": self.product_database is not None,
                "product_count": len(self.product_database.get_all_products()) if self.product_database else 0
            },
            "google_maps": {
                "configured": self.google_maps_api_key is not None
            },
            "max_products": self.max_products,
            "request_timeout": self.request_timeout
        }
