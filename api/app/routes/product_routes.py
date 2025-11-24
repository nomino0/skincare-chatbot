"""
Product routes for product recommendations and store locations.
"""

import logging
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

product_bp = Blueprint('product', __name__)


@product_bp.route('/product-recommendations', methods=['GET'])
def product_recommendations():
    """
    Get product recommendations based on skin analysis.
    
    Query parameters:
    - skinType: User's skin type
    - skinIssues: Comma-separated list of skin issues
    - gender: User's gender
    - ageGroup: User's age group
    - country: User's country
    """
    try:
        # Get query parameters
        skin_type = request.args.get('skinType', 'Normal')
        skin_issues_str = request.args.get('skinIssues', '')
        skin_issues = [issue.strip() for issue in skin_issues_str.split(',') if issue.strip()]
        gender = request.args.get('gender', 'All')
        age_group = request.args.get('ageGroup', '')
        country = request.args.get('country', 'United States')
        
        logger.info(f"Getting product recommendations for: {skin_type} skin, issues: {skin_issues}")
        
        # Get product service
        product_service = current_app.services['product_service']
        
        # Get recommendations
        products = product_service.get_product_recommendations(
            skin_type=skin_type,
            skin_issues=skin_issues,
            gender=gender,
            age_group=age_group,
            country=country
        )
        
        return jsonify(products)
        
    except Exception as e:
        logger.error(f"Error getting product recommendations: {e}")
        return jsonify({'error': 'Failed to get product recommendations'}), 500


@product_bp.route('/find-dermatologists', methods=['GET'])
def find_dermatologists():
    """
    Find nearby dermatologists using Google Places API.
    
    Query parameters:
    - lat: Latitude
    - lng: Longitude
    """
    try:
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        
        if not lat or not lng:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Get product service for store finding functionality
        product_service = current_app.services['product_service']
        
        # Find nearby stores (dermatologists would be similar functionality)
        stores = product_service.find_nearby_stores(
            latitude=float(lat),
            longitude=float(lng),
            product_type="dermatologist"
        )
        
        return jsonify(stores)
        
    except ValueError as e:
        logger.error(f"Invalid coordinates: {e}")
        return jsonify({'error': 'Invalid coordinates provided'}), 400
    except Exception as e:
        logger.error(f"Error finding dermatologists: {e}")
        return jsonify({'error': 'Failed to find dermatologists'}), 500


@product_bp.route('/nearby-stores', methods=['GET'])
def nearby_stores():
    """
    Find nearby stores that sell skincare products.
    
    Query parameters:
    - lat: Latitude
    - lng: Longitude
    - radius: Search radius in meters (default: 5000)
    - product_type: Type of products (default: skincare)
    """
    try:
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        radius = int(request.args.get('radius', 5000))
        product_type = request.args.get('product_type', 'skincare')
        
        if not lat or not lng:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Get product service
        product_service = current_app.services['product_service']
        
        # Find nearby stores
        stores = product_service.find_nearby_stores(
            latitude=float(lat),
            longitude=float(lng),
            radius=radius,
            product_type=product_type
        )
        
        return jsonify(stores)
        
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        return jsonify({'error': 'Invalid parameters provided'}), 400
    except Exception as e:
        logger.error(f"Error finding nearby stores: {e}")
        return jsonify({'error': 'Failed to find nearby stores'}), 500


@product_bp.route('/nearby-products', methods=['GET'])
def nearby_products():
    """
    Get product recommendations with nearby store locations.
    
    Query parameters:
    - lat: Latitude
    - lng: Longitude
    - skinType: User's skin type
    - skinIssues: Comma-separated list of skin issues
    - gender: User's gender
    - ageGroup: User's age group
    - radius: Search radius for stores (default: 5000)
    """
    try:
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        skin_type = request.args.get('skinType', 'Normal')
        skin_issues_str = request.args.get('skinIssues', '')
        skin_issues = [issue.strip() for issue in skin_issues_str.split(',') if issue.strip()]
        gender = request.args.get('gender', 'All')
        age_group = request.args.get('ageGroup', '')
        radius = int(request.args.get('radius', 5000))
        
        if not lat or not lng:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Get product service
        product_service = current_app.services['product_service']
        
        # Get products with nearby stores
        result = product_service.find_nearby_products(
            latitude=float(lat),
            longitude=float(lng),
            skin_type=skin_type,
            skin_issues=skin_issues,
            gender=gender,
            age_group=age_group,
            radius=radius
        )
        
        return jsonify(result)
        
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        return jsonify({'error': 'Invalid parameters provided'}), 400
    except Exception as e:
        logger.error(f"Error finding nearby products: {e}")
        return jsonify({'error': 'Failed to find nearby products'}), 500
