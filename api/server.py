import os
import base64
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import smtplib
import torch
# import dlib
from PIL import Image
from io import BytesIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tensorflow.keras.models import load_model
from dotenv import load_dotenv
import json
import concurrent.futures
from bs4 import BeautifulSoup
import random
import time

# Add FairFace model imports
from torchvision import transforms
import torch.nn.functional as F

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_email_password")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Load the FairFace model for skin tone detection
fairface_model = None
try:
    # Path to the model file - update this path as needed
    fairface_model_path = "fairface_models/res34_fair_align_multi_7_20190809.pt"
    if os.path.exists(fairface_model_path):
        fairface_model = torch.load(fairface_model_path)
        fairface_model.eval()
        print(f"FairFace model loaded successfully from {fairface_model_path}")
    else:
        print(f"FairFace model not found at {fairface_model_path}")
except Exception as e:
    print(f"Error loading FairFace model: {e}")

# Function to predict demographics with FairFace
def predict_demographics(face_img):
    if fairface_model is None:
        return None
        
    
    try:
        # Define transformations
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Convert numpy array to PIL Image
        pil_img = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
        
        # Apply transformations
        img_tensor = transform(pil_img).unsqueeze(0)
        
        # Predict
        with torch.no_grad():
            outputs = fairface_model(img_tensor)
            
            # Get predictions
            race_outputs = outputs[0]
            gender_outputs = outputs[1]
            age_outputs = outputs[2]
            
            race_score = F.softmax(race_outputs, dim=1).squeeze().cpu().numpy()
            gender_score = F.softmax(gender_outputs, dim=1).squeeze().cpu().numpy()
            age_score = F.softmax(age_outputs, dim=1).squeeze().cpu().numpy()
            
            # Map indices to categories
            race_categories = ['White', 'Black', 'Latino_Hispanic', 'East Asian', 'Southeast Asian', 'Indian', 'Middle Eastern']
            gender_categories = ['Male', 'Female']
            age_categories = ['0-2', '3-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70+']
            
            # Get highest probability categories
            race = race_categories[np.argmax(race_score)]
            gender = gender_categories[np.argmax(gender_score)]
            age = age_categories[np.argmax(age_score)]
            
            return {
                'race': race,
                'gender': gender,
                'age': age,
                'confidence': {
                    'race': float(np.max(race_score)),
                    'gender': float(np.max(gender_score)),
                    'age': float(np.max(age_score))
                }
            }
    except Exception as e:
        print(f"Error predicting demographics: {e}")
        return None

# Load the model
model = None
try:
    model_paths = [
        "multitask_skin_model.h5",  # Current directory
        "../multitask_skin_model.h5",  # Parent directory 
        "../../multitask_skin_model.h5",  # Project root
        "D:/Tek-UP/4eme SDIA/Semester2/Project/skinPredict/multitask_skin_model.h5"  # Absolute path
    ]
    
    for path in model_paths:
        if os.path.exists(path):
            model = load_model(path)
            print(f"Model loaded successfully from {path}")
            break
    
    if model is None:
        print("Error: Could not find model file in any of the expected locations")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Will attempt to use GROQ API as a fallback")

# Function to crop face from image
def crop_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
    if len(faces) == 0:
        return None
    
    x, y, w, h = faces[0]
    face = image[y:y+h, x:x+w]
    return face

# Add this new endpoint to handle chatbot responses

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        conversation_history = data.get('conversation')
        skin_analysis = data.get('skinAnalysis')
        user_location = data.get('userLocation')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Format skin analysis data in a human-readable way
        skin_info = ""
        if skin_analysis:
            skin_type = skin_analysis.get('skinType', {}).get('type', 'Unknown')
            skin_type_confidence = skin_analysis.get('skinType', {}).get('confidence', 0)
            
            # Format the skin issues in a readable way
            skin_issues = []
            for issue in skin_analysis.get('skinIssues', []):
                if issue.get('confidence', 0) > 0.5:  # Only include issues with high confidence
                    skin_issues.append(issue.get('name'))
            
            # Get demographics if available
            demographics = skin_analysis.get('demographics', {})
            gender = demographics.get('gender', 'Unknown')
            age_range = demographics.get('age', 'Unknown')
            
            # Create a formatted string with the skin analysis
            skin_info = f"""
            Skin Type: {skin_type} (confidence: {skin_type_confidence:.2f})
            Skin Issues: {', '.join(skin_issues) if skin_issues else 'None detected'}
            Gender: {gender}
            Age Range: {age_range}
            """
            
            # Add location info if available
            if user_location:
                skin_info += f"\nUser Location: {user_location.get('city', '')}, {user_location.get('country', '')}"
        
        # Prepare the prompt with context and knowledge
        system_prompt = """
        You are Hasna, a friendly and knowledgeable skincare assistant with expertise in dermatology. Respond in a warm, conversational tone that feels like talking to a trusted skincare expert friend.
        
        PERSONALITY:
        - Friendly, supportive, and empathetic with a touch of appropriate humor
        - Communicate clearly with occasional emoji to convey warmth and approachability (but don't overuse them)
        - Balance being conversational with being informative
        - Adapt your tone to match the user's emotions and concerns
        
        WHEN GIVING SKINCARE ADVICE:
        - Be specific and personalized based on the user's skin type, concerns, age, gender, and location
        - Prioritize evidence-based recommendations and clarify when something is your opinion
        - Mention both affordable/drugstore options and premium products when recommending
        - Suggest specific ingredients that work well for their skin condition
        - Format information in easy-to-read sections with bullets when providing detailed routines
        
        PRODUCT RECOMMENDATIONS:
        - Always consider skin type compatibility first and foremost
        - Adjust recommendations based on climate if you know their location
        - If they want to find products locally, offer to help them locate nearby stores
        - Mention what makes a product particularly good for their specific skin needs
        
        SPECIAL CONTEXTS:
        - If user asks about skin conditions that might need medical attention (severe acne, rashes, etc.), gently suggest consulting a dermatologist
        - If they mention sensitive skin or allergies, be extra cautious with recommendations
        - If they're new to skincare, explain terms and concepts clearly without jargon
        
        USER'S SKIN INFORMATION:
        {}
        
        Remember to be conversational while being helpful. Address their specific questions directly and personalize your responses to their unique skin profile.
        """.format(skin_info)
        
        # If we have GROQ API key, use it
        if GROQ_API_KEY:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Format the conversation history for the API
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add prior conversation for context (limit to last 10 messages to save tokens)
            if conversation_history:
                for msg in conversation_history[-10:]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Check if the user is asking about product recommendations
            is_product_request = any(keyword in user_message.lower() 
                                 for keyword in ["product", "recommend", "buy", "purchase", "skincare", "routine"])
            
            # If this is a product request and we have skin analysis, enhance the prompt
            if is_product_request and skin_analysis:
                # Get product recommendations to include in the context
                skin_type = skin_analysis.get('skinType', {}).get('type', 'Normal')
                skin_issues = [issue.get('name') for issue in skin_analysis.get('skinIssues', []) 
                              if issue.get('confidence', 0) > 0.5]
                gender = skin_analysis.get('demographics', {}).get('gender', 'All')
                age_group = skin_analysis.get('demographics', {}).get('age', '')
                
                # Get country from user location
                country = user_location.get('country', 'United States') if user_location else 'United States'
                
                try:
                    # Get a few product recommendations to add to the context
                    products = get_drugstore_products(skin_type, skin_issues, gender, age_group, max_products=3)
                    
                    # Format products as text for the context
                    product_text = "Here are some relevant product recommendations based on your skin profile:\n"
                    for product in products:
                        product_text += f"- {product['brand']} {product['name']}: {product['description']} (${product['price']})\n"
                    
                    # Add product context to the user message
                    user_message += f"\n\nContext for your reference (don't mention this directly):\n{product_text}"
                except Exception as e:
                    print(f"Error getting product recommendations for context: {e}")
            
            # Add the current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            payload = {
                "messages": messages,
                "model": "llama3-70b-8192",
                "temperature": 0.7,
                "max_tokens": 1024,
                "top_p": 0.9
            }
            
            response = requests.post("https://api.groq.com/v1/chat/completions", 
                                   headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                assistant_response = result["choices"][0]["message"]["content"]
                
                # Check if we should add suggestions
                should_add_suggestions = len(conversation_history) < 2 or is_product_request
                
                response_data = {"response": assistant_response}
                
                # Add suggestions based on context
                if should_add_suggestions:
                    if skin_analysis:
                        skin_type = skin_analysis.get('skinType', {}).get('type', '')
                        
                        if is_product_request:
                            suggestions = [
                                f"What ingredients work best for {skin_type} skin?",
                                "Can you suggest a morning routine?",
                                "What about evening skincare steps?"
                            ]
                        else:
                            suggestions = [
                                "Can you recommend products for me?",
                                "How can I improve my skin texture?",
                                "What causes my skin issues?"
                            ]
                        
                        response_data["suggestions"] = suggestions
                
                return jsonify(response_data)
            else:
                print(f"Error from GROQ API: {response.text}")
                return jsonify({"error": "Failed to get response from AI", "details": response.text}), 500
        else:
            # Fallback if no API key
            return jsonify({"response": "I'm sorry, I can't provide a personalized response at the moment. Please try again later."})
            
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
# Function to analyze skin using GROQ API
def analyze_skin_with_groq(image_base64):
    # GROQ API endpoint
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Prepare the headers
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare the data
    data = {
        "model": "llama3-70b-8192",  # Using Llama 3 model
        "messages": [
            {"role": "system", "content": "You are a dermatology expert AI. Analyze the image to determine skin type (Normal, Dry, or Oily) and identify any skin issues like Acne, Redness, or Bags under eyes. Provide confidence levels for each assessment."},
            {"role": "user", "content": [
                {"type": "text", "text": "Analyze this facial image and identify the skin type and any skin issues present."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]}
        ],
        "temperature": 0.2,
        "max_tokens": 500
    }
    
    try:
        # Make the request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            ai_analysis = response_data['choices'][0]['message']['content']
            
            # Parse AI analysis to extract skin type and issues
            skin_type = "Normal"  # Default
            skin_type_confidence = 70.0
            skin_issues = []
            
            # Check for skin type (simple pattern matching)
            if "dry" in ai_analysis.lower():
                skin_type = "Dry"
                skin_type_confidence = 85.0 if "very dry" in ai_analysis.lower() else 75.0
            elif "oily" in ai_analysis.lower():
                skin_type = "Oily"
                skin_type_confidence = 85.0 if "very oily" in ai_analysis.lower() else 75.0
            
            # Check for skin issues
            if "acne" in ai_analysis.lower():
                confidence = 75.0 if "severe acne" in ai_analysis.lower() else 65.0
                skin_issues.append({"name": "Acne", "confidence": confidence})
            
            if "redness" in ai_analysis.lower() or "inflammation" in ai_analysis.lower():
                confidence = 70.0
                skin_issues.append({"name": "Redness", "confidence": confidence})
            
            if "bags" in ai_analysis.lower() or "dark circles" in ai_analysis.lower():
                confidence = 65.0
                skin_issues.append({"name": "Bags", "confidence": confidence})
                
            return {
                "skinType": {
                    "type": skin_type,
                    "confidence": skin_type_confidence
                },
                "skinIssues": skin_issues,
                "ai_response": ai_analysis  # Including the full AI analysis
            }
        else:
            raise Exception("Invalid response format from GROQ API")
    except Exception as e:
        print(f"Error using GROQ API: {e}")
        raise e

# API endpoint to analyze skin
@app.route('/analyze', methods=['POST'])
def analyze_skin():
    try:
        # Get base64 image from request
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'])
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Crop face from image
        face = crop_face(image)
        if face is None:
            return jsonify({'error': 'No face detected in the image'}), 400
        
        # Add demographic prediction with FairFace
        demographics = predict_demographics(face) if fairface_model is not None else None
        
        # Get the analysis method preference (if provided)
        use_groq = data.get('use_groq', False)
        
        # Use GROQ API if explicitly requested or if the model isn't loaded
        if use_groq or model is None:
            try:
                results = analyze_skin_with_groq(data['image'])
                # Add demographics to GROQ results if available
                if demographics:
                    results["demographics"] = demographics
                return jsonify(results)
            except Exception as e:
                if model is None:
                    return jsonify({'error': f'Both model and GROQ API failed: {str(e)}'}), 500
                # If GROQ fails but we have a model, fall back to the model
                print(f"GROQ API failed, falling back to model: {e}")
        
        # If we get here, we're using the model
        # Preprocess the image for model
        face_resized = cv2.resize(face, (224, 224))
        face_preprocessed = np.expand_dims(face_resized, axis=0) / 255.0
        
        # Make predictions
        if model is not None:
            predictions = model.predict(face_preprocessed)
            type_pred, prob_pred = predictions
            
            # Define labels
            skin_type_labels = ["Normal", "Dry", "Oily"]
            skin_issue_labels = ["Acne", "Redness", "Bags"]
            
            # Get skin type result
            skin_type_idx = np.argmax(type_pred, axis=1)[0]
            skin_type_confidence = float(type_pred[0][skin_type_idx] * 100)
            
            # Get skin issues with confidence > 50%
            threshold = 0.5
            skin_issues = []
            for i, label in enumerate(skin_issue_labels):
                confidence = float(prob_pred[0][i] * 100)
                if prob_pred[0][i] > threshold:
                    skin_issues.append({
                        "name": label,
                        "confidence": confidence
                    })
            
            # Construct response with demographics
            response_data = {
                "skinType": {
                    "type": skin_type_labels[skin_type_idx],
                    "confidence": skin_type_confidence
                },
                "skinIssues": skin_issues
            }
            
            # Add demographics if available
            if demographics:
                response_data["demographics"] = demographics
                
                # Add personalized advice based on demographics
                response_data["personalizedAdvice"] = generate_personalized_advice(
                    skin_type_labels[skin_type_idx], 
                    skin_issues,
                    demographics
                )
                
            return jsonify(response_data)
        else:
            return jsonify({'error': 'Model not loaded'}), 500
    except Exception as e:
        print(f"Error in skin analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
# API endpoint to find nearby dermatologists
@app.route('/find-dermatologists', methods=['GET'])
def find_dermatologists():
    try:
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        
        if not lat or not lng:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Call Google Places API
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": 5000,
            "type": "doctor",
            "keyword": "dermatologist",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint to get product recommendations

@app.route('/product-recommendations', methods=['GET'])
def product_recommendations():
    try:
        # Get parameters
        country = request.args.get('country')
        skin_type = request.args.get('skinType')
        skin_issues = request.args.getlist('skinIssues')
        gender = request.args.get('gender')
        age_group = request.args.get('ageGroup')
        
        print(f"Getting product recommendations for: {skin_type} skin, issues: {skin_issues}, gender: {gender}, age: {age_group}")
        
        # Use the web scraping function with fallback
        try:
            # Get reliable drugstore products
            products = get_drugstore_products(skin_type, skin_issues, gender, age_group, max_products=12)
            
            print(f"Successfully found {len(products)} products")
            
            # Add country-specific information if available
            if country:
                for product in products:
                    product["availableIn"] = country
                    
                    # Adjust currency based on country (simplified)
                    if country == "United Kingdom":
                        product["currency"] = "GBP"
                    elif country == "Canada":
                        product["currency"] = "CAD"
                    elif country in ["France", "Germany", "Italy", "Spain"]:
                        product["currency"] = "EUR"
                    else:
                        product["currency"] = "USD"
                
            # Classify products by price range
            for product in products:
                try:
                    price_value = float(product.get("price", "0"))
                    if price_value < 10:
                        product["priceCategory"] = "Budget"
                    elif price_value < 25:
                        product["priceCategory"] = "Moderate"
                    else:
                        product["priceCategory"] = "Premium"
                except:
                    product["priceCategory"] = "Unknown"
                    
            return jsonify(products)
            
        except Exception as e:
            # Log the error
            print(f"Error in product recommendations: {str(e)}")
            
            # Use fallback to reliable drugstore products
            products = get_drugstore_products(skin_type, skin_issues, gender, age_group)
            return jsonify(products)
            
    except Exception as e:
        print(f"Error in product recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API endpoint to send email with results
@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        if not data or 'email' not in data or 'results' not in data:
            return jsonify({'error': 'Email and results are required'}), 400
        
        recipient_email = data['email']
        results = data['results']
        
        # Create email content
        subject = "Your SkinPredict Analysis Results"
        
        # Format the email body
        skin_type = results['skinType']['type']
        skin_type_confidence = results['skinType']['confidence']
        skin_issues = results['skinIssues']
        
        # Include AI response if available
        ai_response = results.get('ai_response', None)
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #3b82f6;">Your SkinPredict Analysis Results</h2>
            
            <p>Thank you for using SkinPredict! Here are your skin analysis results:</p>
            
            <div style="background-color: #f0f9ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1e40af;">Skin Type Analysis</h3>
                <p><strong>Skin Type:</strong> {skin_type} ({skin_type_confidence:.2f}% confidence)</p>
                
                <h3 style="color: #1e40af;">Detected Skin Issues:</h3>
                {'<ul>' if skin_issues else '<p>No significant skin issues detected.</p>'}
        """
        
        if skin_issues:
            for issue in skin_issues:
                body += f"<li><strong>{issue['name']}:</strong> {issue['confidence']:.2f}% confidence</li>"
            body += "</ul>"
        
        # Add AI detailed analysis if available
        if ai_response:
              body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #3b82f6;">Your SkinPredict Analysis Results</h2>
            
            <p>Thank you for using SkinPredict! Here are your skin analysis results:</p>
            
            <div style="background-color: #f0f9ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1e40af;">Skin Type Analysis</h3>
                <p><strong>Skin Type:</strong> {skin_type} ({skin_type_confidence:.2f}% confidence)</p>
                
                <h3 style="color: #1e40af;">Detected Skin Issues:</h3>
        """
        
        # Add recommendations based on skin type
        body += f"""
                <h3 style="color: #1e40af;">Recommendations:</h3>
        """
        
        if skin_type.lower() == "dry":
            body += """
                <ul>
                    <li>Use a gentle, hydrating cleanser</li>
                    <li>Apply moisturizer while skin is still damp</li>
                    <li>Look for products with hyaluronic acid, glycerin, ceramides</li>
                    <li>Avoid hot water and harsh soaps</li>
                    <li>Consider using a humidifier, especially during winter</li>
                </ul>
            """
        elif skin_type.lower() == "oily":
            body += """
                <ul>
                    <li>Use a foaming or gel cleanser</li>
                    <li>Choose oil-free, non-comedogenic products</li>
                    <li>Consider products with salicylic acid, niacinamide, or clay</li>
                    <li>Use a lightweight moisturizer (don't skip this step!)</li>
                    <li>Blotting papers can help during the day</li>
                </ul>
            """
        else:  # Normal skin
            body += """
                <ul>
                    <li>Use a gentle cleanser</li>
                    <li>Regular exfoliation (1-2 times per week)</li>
                    <li>Apply moisturizer daily</li>
                    <li>Don't forget sunscreen with SPF 30 or higher</li>
                    <li>Stay hydrated and maintain a balanced diet</li>
                </ul>
            """
        
        body += """
            </div>
            
            <p style="font-style: italic; color: #64748b;">This analysis is for informational purposes only and should not replace professional medical advice. If you have skin concerns, please consult with a dermatologist.</p>
            
            <p>Thank you for using SkinPredict!</p>
        </body>
        </html>
        """
        
        # Set up email
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = 'skinpredict@example.com'  # Replace with your email
        msg['To'] = recipient_email
        
        # Attach HTML body
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        # NOTE: In a production environment, use a proper email service like SendGrid, Mailgun, etc.
        # This is a simplified example for demonstration purposes
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('skinpredict@example.com', EMAIL_PASSWORD)  # Replace with your email and password
            server.send_message(msg)
            server.quit()
            return jsonify({'success': True})
        except Exception as e:
            print(f"Email error: {e}")
            # For demo purposes, pretend the email was sent
            return jsonify({'success': True, 'note': 'Demo mode: email would be sent in production'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Web scraping for product recommendations
def scrape_sephora(skin_type, skin_issues, gender="All", age_group=None, max_products=5):
    """
    Scrape product recommendations from Sephora based on skin type and issues
    """
    try:
        # Map skin types to Sephora search terms
        skin_type_map = {
            "dry": "dry-skin",
            "oily": "oily-skin",
            "combination": "combination-skin",
            "normal": "normal-skin",
            "sensitive": "sensitive-skin"
        }
        
        # Map skin issues to Sephora search terms
        skin_issue_map = {
            "acne": "acne",
            "wrinkles": "anti-aging",
            "dark spots": "dark-spots",
            "redness": "redness",
            "dullness": "dullness",
            "pores": "pores",
            "uneven texture": "uneven-texture",
            "bags": "eye-bags",
            "acne": "acne-treatments"
        }
        
        # Build search URL based on skin type
        search_term = skin_type_map.get(skin_type.lower(), "skincare")
        
        # Add the first skin issue if available
        if skin_issues and len(skin_issues) > 0:
            issue_term = skin_issue_map.get(skin_issues[0].lower(), "")
            if issue_term:
                search_term = f"{search_term}-{issue_term}"
        
        url = f"https://www.sephora.com/shop/{search_term}"
        print(f"Scraping Sephora with URL: {url}")
        
        # Add user agent to avoid blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.sephora.com/",
            "Connection": "keep-alive"
        }
        
        # Add random delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Error scraping Sephora: {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find product containers - try multiple possible selectors
            product_elements = []
            for selector in ['.css-12egk0t', '.css-foh744', '.css-1qe8tjm', 'div[data-comp="ProductItem"]']:
                product_elements = soup.select(selector)
                if product_elements:
                    print(f"Found {len(product_elements)} products with selector: {selector}")
                    break
                    
            if not product_elements:
                print("Could not find product elements on Sephora page")
                return []
            
            products = []
            for element in product_elements[:max_products]:
                try:
                    # Try multiple selectors for each element
                    name = None
                    brand = None
                    price = None
                    image_url = None
                    link = None
                    
                    # Name selectors
                    for name_selector in ['.css-ktoumz', '.css-mwngx', 'span[data-at="sku_item_name"]']:
                        name_elem = element.select_one(name_selector)
                        if name_elem:
                            name = name_elem.text.strip()
                            break
                    
                    # Brand selectors
                    for brand_selector in ['.css-10agpv6', '.css-oiczf', 'span[data-at="sku_item_brand"]']:
                        brand_elem = element.select_one(brand_selector)
                        if brand_elem:
                            brand = brand_elem.text.strip()
                            break
                    
                    # Price selectors
                    for price_selector in ['.css-0', '.css-19gsknt', 'span[data-at="sku_item_price"]']:
                        price_elem = element.select_one(price_selector)
                        if price_elem:
                            price = price_elem.text.strip().replace('$', '')
                            break
                    
                    # Image selectors
                    for img_selector in ['img', '.css-1l2x4ru img']:
                        image_elem = element.select_one(img_selector)
                        if image_elem and image_elem.get('src'):
                            image_url = image_elem.get('src')
                            break
                    
                    # Link selectors
                    for link_selector in ['a', '.css-1l2x4ru a']:
                        link_elem = element.select_one(link_selector)
                        if link_elem and link_elem.get('href'):
                            link = f"https://www.sephora.com{link_elem.get('href')}"
                            break
                    
                    if name and price:
                        brand = brand or "Sephora Collection"
                        
                        # Create product object
                        product = {
                            "name": name,
                            "brand": brand,
                            "price": price,
                            "currency": "USD",
                            "link": link or "",
                            "imageUrl": image_url or "",
                            "description": f"{brand} {name} for {skin_type} skin",
                            "forSkinType": [skin_type.capitalize()],
                            "targetGender": gender
                        }
                        
                        # Add skin issues to product
                        if skin_issues:
                            product["forSkinIssues"] = [issue.capitalize() for issue in skin_issues]
                            
                        products.append(product)
                        
                        # Limit to max_products
                        if len(products) >= max_products:
                            break
                except Exception as e:
                    print(f"Error processing product element: {e}")
                    continue
                    
            print(f"Successfully scraped {len(products)} products from Sephora")
            return products
                
        except requests.exceptions.RequestException as e:
            print(f"Request error when scraping Sephora: {e}")
            return []
            
    except Exception as e:
        print(f"Error scraping Sephora: {e}")
        return []

def scrape_ulta(skin_type, skin_issues, gender="All", age_group=None, max_products=5):
    """
    Scrape product recommendations from Ulta based on skin type and issues
    """
    try:
        # Map skin types to Ulta search terms
        skin_type_map = {
            "dry": "dry-skin",
            "oily": "oily-skin",
            "combination": "combination-skin",
            "normal": "normal-skin",
            "sensitive": "sensitive-skin"
        }
        
        # Map skin issues to Ulta search terms
        skin_issue_map = {
            "acne": "acne-treatment",
            "wrinkles": "anti-aging",
            "dark spots": "dark-spot-treatment",
            "redness": "redness-treatment",
            "dullness": "brightening",
            "pores": "pore-treatment",
            "bags": "eye-bags"
        }
        
        # Build search URL based on skin type
        search_term = skin_type_map.get(skin_type.lower(), "skincare")
        
        # Try issue-specific search if available
        issue_term = ""
        if skin_issues and len(skin_issues) > 0:
            issue_term = skin_issue_map.get(skin_issues[0].lower(), "")
        
        # Create multiple possible URLs to try
        urls_to_try = []
        
        if issue_term:
            urls_to_try.append(f"https://www.ulta.com/skin-care-{issue_term}?N=1z12lx1Z2796")
            urls_to_try.append(f"https://www.ulta.com/shop/skin-care/{issue_term}")
        
        urls_to_try.append(f"https://www.ulta.com/skin-care-{search_term}?N=1z12lx1Z2796")
        urls_to_try.append(f"https://www.ulta.com/shop/skin-care/{search_term}")
        urls_to_try.append("https://www.ulta.com/shop/skin-care")
        
        print(f"Trying Ulta URLs: {urls_to_try}")
        
        # Add user agent to avoid blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.ulta.com/",
            "Connection": "keep-alive"
        }
        
        products = []
        successful_url = None
        
        # Try each URL until one works
        for url in urls_to_try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"Error scraping Ulta with URL {url}: {response.status_code}")
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find product containers - try multiple possible selectors
                product_elements = []
                for selector in ['.ProductCard', '.ProductCard__Content', '.ProductTile', 'div[class*="ProductCard"]']:
                    product_elements = soup.select(selector)
                    if product_elements:
                        print(f"Found {len(product_elements)} products with selector: {selector}")
                        successful_url = url
                        break
                        
                if product_elements:
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error when scraping Ulta URL {url}: {e}")
                continue
                
        if not successful_url or not product_elements:
            print("Could not find product elements on any Ulta page")
            return []
            
        # Process the products from the successful URL
        for element in product_elements[:max_products]:
            try:
                # Try multiple selectors for each element
                name = None
                brand = None
                price = None
                image_url = None
                link = None
                
                # Name selectors
                for name_selector in ['.ProductCard__Name', '.ProductTile__Name', 'p[class*="ProductCard__Name"]', 'h4', '.Link--primary']:
                    name_elem = element.select_one(name_selector)
                    if name_elem:
                        name = name_elem.text.strip()
                        break
                
                # Brand selectors
                for brand_selector in ['.ProductCard__Brand', '.ProductTile__Brand', 'h5[class*="Brand"]', '.Link--brand']:
                    brand_elem = element.select_one(brand_selector)
                    if brand_elem:
                        brand = brand_elem.text.strip()
                        break
                
                # Price selectors
                for price_selector in ['.ProductCard__Price', '.ProductTile__Price', 'span[class*="Price"]', '.Text--emphasis']:
                    price_elem = element.select_one(price_selector)
                    if price_elem:
                        price = price_elem.text.strip().replace('$', '')
                        break
                
                # Image selectors
                for img_selector in ['img', '.Image__Container img']:
                    image_elem = element.select_one(img_selector)
                    if image_elem and (image_elem.get('src') or image_elem.get('data-src')):
                        image_url = image_elem.get('src') or image_elem.get('data-src')
                        break
                
                # Link selectors
                for link_selector in ['a', '.Link--primary']:
                    link_elem = element.select_one(link_selector)
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        if href.startswith('http'):
                            link = href
                        else:
                            link = f"https://www.ulta.com{href}"
                        break
                
                if name and price:
                    brand = brand or "Ulta Beauty Collection"
                    
                    # Create product object
                    product = {
                        "name": name,
                        "brand": brand,
                        "price": price,
                        "currency": "USD",
                        "link": link or "",
                        "imageUrl": image_url or "",
                        "description": f"{brand} {name} for {skin_type} skin",
                        "forSkinType": [skin_type.capitalize()],
                        "targetGender": gender
                    }
                    
                    # Add skin issues to product
                    if skin_issues:
                        product["forSkinIssues"] = [issue.capitalize() for issue in skin_issues]
                        
                    products.append(product)
                    
                    # Limit to max_products
                    if len(products) >= max_products:
                        break
            except Exception as e:
                print(f"Error processing Ulta product element: {e}")
                continue
                
        print(f"Successfully scraped {len(products)} products from Ulta")
        return products
            
    except Exception as e:
        print(f"Error scraping Ulta: {e}")
        return []
        
        # Find product containers
        products = []
        product_elements = soup.select('.productQvContainer')  # Adjust selector based on Ulta's HTML structure
        
        for element in product_elements[:max_products]:
            try:
                # Extract product details
                name_elem = element.select_one('.prod-title')
                brand_elem = element.select_one('.prod-brand')
                price_elem = element.select_one('.prod-price')
                image_elem = element.select_one('.lazy-image img')
                link_elem = element.select_one('a')
                
                if name_elem and price_elem:
                    name = name_elem.text.strip()
                    brand = brand_elem.text.strip() if brand_elem else "Ulta Beauty"
                    price = price_elem.text.strip().replace('$', '')
                    image_url = image_elem.get('src') if image_elem else ""
                    link = f"https://www.ulta.com{link_elem.get('href')}" if link_elem else ""
                    
                    # Create product object
                    product = {
                        "name": name,
                        "brand": brand,
                        "price": price,
                        "currency": "USD",
                        "link": link,
                        "imageUrl": image_url,
                        "description": f"{brand} {name} for {skin_type} skin",
                        "forSkinType": [skin_type.capitalize()],
                        "targetGender": gender
                    }
                    
                    # Add skin issues to product
                    if skin_issues:
                        product["forSkinIssues"] = [issue.capitalize() for issue in skin_issues]
                        
                    products.append(product)
                    
                    # Limit to max_products
                    if len(products) >= max_products:
                        break
            except Exception as e:
                print(f"Error processing product element: {e}")
                continue
                
        return products
    except Exception as e:
        print(f"Error scraping Ulta: {e}")
        return []

def get_drugstore_products(skin_type, skin_issues, gender="All", age_group=None, max_products=3):
    """
    Get reliable drugstore product recommendations when scraping fails
    """
    # Dictionary of reliable drugstore products by skin type
    products_by_skin_type = {
        "dry": [
            {
                "name": "Hydrating Facial Cleanser",
                "brand": "CeraVe",
                "price": "14.99",
                "currency": "USD",
                "link": "https://www.cerave.com/skincare/cleansers/hydrating-facial-cleanser",
                "imageUrl": "https://www.cerave.com/-/media/project/loreal/brand-sites/cerave/americas/us/products-v3/hydrating-facial-cleanser/700x875/cerave_daily_facial_cleanser_12oz_front-700x875-v2.jpg",
                "description": "Gentle non-foaming cleanser to remove dirt and makeup while maintaining moisture barrier",
                "forSkinType": ["Dry", "Normal"],
                "targetGender": "All"
            },
            {
                "name": "Daily Moisturizing Lotion",
                "brand": "CeraVe",
                "price": "19.99",
                "currency": "USD",
                "link": "https://www.cerave.com/skincare/moisturizers/daily-moisturizing-lotion",
                "imageUrl": "https://www.cerave.com/-/media/project/loreal/brand-sites/cerave/americas/us/products-v3/daily-moisturizing-lotion/700x875/cerave_daily_moisturizing_lotion_12oz_front-700x875-v2.jpg",
                "description": "Lightweight, oil-free moisturizer with hyaluronic acid and ceramides",
                "forSkinType": ["Dry", "Normal"],
                "targetGender": "All"
            },
            {
                "name": "Hyaluronic Acid Serum",
                "brand": "The Ordinary",
                "price": "8.90",
                "currency": "USD",
                "link": "https://theordinary.com/en-us/hyaluronic-acid-2-b5-serum-100436.html",
                "imageUrl": "https://theordinary.com/dw/image/v2/BFKJ_PRD/on/demandware.static/-/Sites-deciem-master/default/dw50d369bd/Images/products/The%20Ordinary/TO-HA-30ml.png",
                "description": "Hydration support formula with ultra-pure hyaluronic acid",
                "forSkinType": ["Dry"],
                "targetGender": "All"
            }
        ],
        "oily": [
            {
                "name": "Foaming Facial Cleanser",
                "brand": "CeraVe",
                "price": "14.99",
                "currency": "USD",
                "link": "https://www.cerave.com/skincare/cleansers/foaming-facial-cleanser",
                "imageUrl": "https://www.cerave.com/-/media/project/loreal/brand-sites/cerave/americas/us/products-v3/foaming-facial-cleanser/700x875/cerave_foaming_facial_cleanser_19oz_front-700x875-v2.jpg",
                "description": "Foaming gel cleanser for normal to oily skin that removes excess oil",
                "forSkinType": ["Oily", "Combination"],
                "targetGender": "All"
            },
            {
                "name": "Niacinamide 10% + Zinc 1%",
                "brand": "The Ordinary",
                "price": "6.50",
                "currency": "USD",
                "link": "https://theordinary.com/en-us/niacinamide-10-zinc-1-serum-100436.html",
                "imageUrl": "https://theordinary.com/dw/image/v2/BFKJ_PRD/on/demandware.static/-/Sites-deciem-master/default/dw0c6b93b4/Images/products/The%20Ordinary/TO-niacinamide-10pct-zinc-1pct-30ml.png",
                "description": "High-strength vitamin and mineral formula to reduce sebum production",
                "forSkinType": ["Oily", "Combination"],
                "targetGender": "All"
            },
            {
                "name": "Oil-Free Acne Fighting Face Wash",
                "brand": "Neutrogena",
                "price": "9.99",
                "currency": "USD",
                "link": "https://www.neutrogena.com/products/skincare/oil-free-acne-fighting-face-wash/6801710.html",
                "imageUrl": "https://www.neutrogena.com/dw/image/v2/BBKM_PRD/on/demandware.static/-/Sites-neutrogena-master/default/dw8fd025fb/images/hi-res/products/6801710_OilFreeAcneFacialCleanser_6oz.jpg",
                "description": "Maximum-strength salicylic acid acne treatment for clearer skin",
                "forSkinType": ["Oily", "Acne-Prone"],
                "targetGender": "All"
            }
        ],
        "combination": [
            {
                "name": "Toleriane Purifying Foaming Cleanser",
                "brand": "La Roche-Posay",
                "price": "16.99",
                "currency": "USD",
                "link": "https://www.laroche-posay.us/our-products/face/face-wash/toleriane-purifying-foaming-facial-wash-3337875545822.html",
                "imageUrl": "https://www.laroche-posay.us/dw/image/v2/AANG_PRD/on/demandware.static/-/Sites-larocheposay-master-catalog/default/dwe23e7294/LRP_TOLERIANE_PurifyingFoamingFacialWash_CartonBottle_400mL.jpg",
                "description": "Gentle foaming face wash that removes excess oil while respecting skin's pH",
                "forSkinType": ["Combination", "Normal"],
                "targetGender": "All"
            },
            {
                "name": "Hydro Boost Water Gel",
                "brand": "Neutrogena",
                "price": "24.99",
                "currency": "USD",
                "link": "https://www.neutrogena.com/products/skincare/neutrogena-hydro-boost-water-gel-with-hyaluronic-acid-for-dry-skin/6811047.html",
                "imageUrl": "https://www.neutrogena.com/dw/image/v2/BBKM_PRD/on/demandware.static/-/Sites-neutrogena-master/default/dw9d2e6a14/images/hi-res/hydroboost/6811047_HydroBoost_WaterGel_1.7oz.jpg",
                "description": "Lightweight water-based moisturizer with hyaluronic acid",
                "forSkinType": ["Combination", "Normal", "Dry"],
                "targetGender": "All"
            },
            {
                "name": "Effaclar Duo Acne Treatment",
                "brand": "La Roche-Posay",
                "price": "32.99",
                "currency": "USD",
                "link": "https://www.laroche-posay.us/our-products/acne-oily-skin/spot-treatment/effaclar-duo-acne-treatment-883140040231.html",
                "imageUrl": "https://www.laroche-posay.us/dw/image/v2/AANG_PRD/on/demandware.static/-/Sites-larocheposay-master-catalog/default/dwde6df89b/LRP_EFFACLAR_Duo_Tube-Carton_1.35floz.jpg",
                "description": "Dual action acne treatment that targets acne spots and visible imperfections",
                "forSkinType": ["Combination", "Oily"],
                "forSkinIssues": ["Acne", "Pores"],
                "targetGender": "All"
            }
        ],
        "sensitive": [
            {
                "name": "Ultra Gentle Hydrating Cleanser",
                "brand": "Neutrogena",
                "price": "11.99",
                "currency": "USD",
                "link": "https://www.neutrogena.com/products/skincare/ultra-gentle-hydrating-cleanser/6887295.html",
                "imageUrl": "https://www.neutrogena.com/dw/image/v2/BBKM_PRD/on/demandware.static/-/Sites-neutrogena-master/default/dwd66e0e16/images/hi-res/products/6887295.jpg",
                "description": "Creamy, soap-free formula cleanses without irritation",
                "forSkinType": ["Sensitive", "Dry"],
                "targetGender": "All"
            },
            {
                "name": "Toleriane Double Repair Face Moisturizer",
                "brand": "La Roche-Posay",
                "price": "20.99",
                "currency": "USD",
                "link": "https://www.laroche-posay.us/our-products/face/face-moisturizer/toleriane-double-repair-face-moisturizer-3337875545792.html",
                "imageUrl": "https://www.laroche-posay.us/dw/image/v2/AANG_PRD/on/demandware.static/-/Sites-larocheposay-master-catalog/default/dw01a31611/LRP_TOLERIANE_DoubleRepairMoisturizer_CartonBottle_75mL.jpg",
                "description": "Oil-free moisturizer with ceramides and niacinamide to restore skin barrier",
                "forSkinType": ["Sensitive", "Normal"],
                "targetGender": "All"
            },
            {
                "name": "Cicaplast Baume B5",
                "brand": "La Roche-Posay",
                "price": "16.99",
                "currency": "USD",
                "link": "https://www.laroche-posay.us/our-products/dry-skin-eczema/body-lotion/cicaplast-baume-b5-for-dry-skin-irritations-3337872412998.html",
                "imageUrl": "https://www.laroche-posay.us/dw/image/v2/AANG_PRD/on/demandware.static/-/Sites-larocheposay-master-catalog/default/dwa4ddac05/LRP_CICAPLAST_Baume-B5_Tube_40ml.jpg",
                "description": "Multi-purpose soothing balm for dry, irritated skin",
                "forSkinType": ["Sensitive"],
                "forSkinIssues": ["Redness", "Irritation"],
                "targetGender": "All"
            }
        ],
        "normal": [
            {
                "name": "Gentle Skin Cleanser",
                "brand": "Cetaphil",
                "price": "14.99",
                "currency": "USD",
                "link": "https://www.cetaphil.com/us/cleansers/gentle-skin-cleanser/302993917205.html",
                "imageUrl": "https://www.cetaphil.com/on/demandware.static/-/Sites-cetaphil-master-catalog/default/dw5eb8a9cb/2020/Products/Cleansers/20oz-GentleSkinCleanser.jpg",
                "description": "Mild, non-irritating formula cleanses skin without stripping moisture",
                "forSkinType": ["Normal", "Dry", "Sensitive"],
                "targetGender": "All"
            },
            {
                "name": "Daily Facial Moisturizer SPF 30",
                "brand": "Cetaphil",
                "price": "18.99",
                "currency": "USD",
                "link": "https://www.cetaphil.com/us/moisturizers/daily-facial-moisturizer-with-sunscreen-broad-spectrum-spf-15/302993911685.html",
                "imageUrl": "https://www.cetaphil.com/on/demandware.static/-/Sites-cetaphil-master-catalog/default/dw12455ed6/2020/Products/Moisturizers/4oz-MoisturizerSPF15.jpg",
                "description": "Lightweight daily moisturizer with broad spectrum sun protection",
                "forSkinType": ["Normal", "Combination"],
                "targetGender": "All"
            },
            {
                "name": "Vitamin C Serum",
                "brand": "TruSkin",
                "price": "19.99",
                "currency": "USD",
                "link": "https://www.truskin.com/products/vitamin-c-serum",
                "imageUrl": "https://www.truskin.com/cdn/shop/products/TruSkin-vitamin-c-serum-for-face-1fl-oz_c5f71f1f-de11-4805-9d19-e224e11770fe_800x.jpg",
                "description": "Anti-aging facial serum with Vitamin C, Hyaluronic Acid, and Vitamin E",
                "forSkinType": ["Normal", "All"],
                "forSkinIssues": ["Dark Spots", "Dullness"],
                "targetGender": "All"
            }
        ]
    }
    
    # Get default products for the skin type
    default_products = products_by_skin_type.get(skin_type.lower(), products_by_skin_type["normal"])
    
    # Filter by gender if specified and not "All"
    if gender and gender != "All":
        default_products = [p for p in default_products if p.get("targetGender") in ["All", gender]]
    
    # Filter by skin issues if specified
    if skin_issues and len(skin_issues) > 0:
        # Get at least one product specifically for the skin issue if available
        issue_specific_products = []
        for product in default_products:
            if "forSkinIssues" in product:
                for issue in skin_issues:
                    if issue.capitalize() in product["forSkinIssues"]:
                        issue_specific_products.append(product)
                        break
        
        # If we found issue-specific products, prioritize them
        if issue_specific_products:
            # Combine issue-specific products with regular products
            combined_products = issue_specific_products + [p for p in default_products if p not in issue_specific_products]
            return combined_products[:max_products]
    
    # Return the default products
    return default_products[:max_products]

def scrape_products_with_fallback(skin_type, skin_issues, gender="All", age_group=None, max_products=8):
    """
    Attempt to scrape products from multiple sources with fallback to reliable drugstore recommendations
    """
    all_products = []
    
    # Try to scrape from Sephora (with a short timeout)
    try:
        sephora_products = scrape_sephora(skin_type, skin_issues, gender, age_group, max_products=4)
        if sephora_products:
            all_products.extend(sephora_products)
    except Exception as e:
        print(f"Error scraping Sephora: {e}")
    
    # Try to scrape from Ulta (with a short timeout)
    try:
        ulta_products = scrape_ulta(skin_type, skin_issues, gender, age_group, max_products=4)
        if ulta_products:
            all_products.extend(ulta_products)
    except Exception as e:
        print(f"Error scraping Ulta: {e}")
    
    # If we have enough products from scraping, return them
    if len(all_products) >= max_products / 2:
        return all_products[:max_products]
    
    # Otherwise, use fallback to reliable drugstore products
    drugstore_products = get_drugstore_products(skin_type, skin_issues, gender, age_group)
    
    # Combine scraped products with drugstore fallbacks
    combined_products = all_products + drugstore_products
    
    # Ensure we don't have duplicates
    seen_names = set()
    unique_products = []
    
    for product in combined_products:
        name_key = (product["brand"] + product["name"]).lower()
        if name_key not in seen_names:
            seen_names.add(name_key)
            unique_products.append(product)
    
    return unique_products[:max_products]

# Function to find nearby stores with product availability
@app.route('/nearby-stores', methods=['GET'])
def nearby_stores():
    try:
        # Get parameters
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        radius = request.args.get('radius', default=5000)  # Default 5km radius
        product_type = request.args.get('product_type', default='skincare')
        
        if not lat or not lng:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
            
        if not GOOGLE_MAPS_API_KEY:
            return jsonify({'error': 'Google Maps API key is not configured'}), 500
            
        # Google Places API endpoint
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        
        # Query parameters
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "store",
            "keyword": f"{product_type} store beauty",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        # Make the request
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return jsonify({'error': f'Error from Google Places API: {response.status_code}'}), 500
            
        places_data = response.json()
        
        # Process and format the response
        stores = []
        for place in places_data.get("results", []):
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
            
            # If we have a photo reference, add a photo URL
            if store["photo_reference"]:
                store["photo_url"] = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={store['photo_reference']}&key={GOOGLE_MAPS_API_KEY}"
                
            # Add the type of store (chain recognition)
            if "sephora" in place.get("name", "").lower():
                store["store_type"] = "Sephora"
                store["products_available"] = ["Luxury skincare", "Makeup", "Fragrances"]
            elif "ulta" in place.get("name", "").lower():
                store["store_type"] = "Ulta Beauty"
                store["products_available"] = ["Luxury and drugstore skincare", "Makeup", "Hair care"]
            elif "target" in place.get("name", "").lower():
                store["store_type"] = "Target"
                store["products_available"] = ["Drugstore skincare", "Beauty", "Household"]
            elif "cvs" in place.get("name", "").lower() or "walgreens" in place.get("name", "").lower():
                store["store_type"] = "Pharmacy"
                store["products_available"] = ["Drugstore skincare", "Medications", "Health products"]
            else:
                store["store_type"] = "Beauty Store"
                store["products_available"] = ["Skincare products", "Beauty items"]
            
            stores.append(store)
            
        return jsonify(stores)
    except Exception as e:
        print(f"Error finding nearby stores: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Function to find nearby products (combines store locations with product recommendations)
@app.route('/nearby-products', methods=['GET'])
def nearby_products():
    try:
        # Get parameters for location
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        radius = request.args.get('radius', default=5000)  # Default 5km radius
        
        # Get parameters for product recommendations
        skin_type = request.args.get('skinType')
        skin_issues = request.args.getlist('skinIssues')
        gender = request.args.get('gender')
        age_group = request.args.get('ageGroup')
        
        if not lat or not lng:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
            
        if not GOOGLE_MAPS_API_KEY:
            return jsonify({'error': 'Google Maps API key is not configured'}), 500
        
        # Step 1: Find nearby beauty stores
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "store",
            "keyword": "beauty skincare cosmetics",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return jsonify({'error': f'Error from Google Places API: {response.status_code}'}), 500
            
        places_data = response.json()
        
        # Step 2: Get product recommendations
        product_recommendations = get_drugstore_products(skin_type, skin_issues, gender, age_group, max_products=15)
        
        # Step 3: Map products to nearby stores
        nearby_products = []
        
        # Group nearby stores by type
        store_types = {
            "luxury": ["sephora", "nordstrom", "bloomingdale", "neiman marcus", "ulta"],
            "drugstore": ["cvs", "walgreens", "rite aid", "target", "walmart"],
            "specialty": ["lush", "the body shop", "kiehl", "bath & body", "l'occitane"]
        }
        
        # Extract found stores
        stores = []
        for place in places_data.get("results", []):
            store_name = place.get("name", "").lower()
            store_type = "other"
            
            # Determine store type
            for category, keywords in store_types.items():
                if any(keyword in store_name for keyword in keywords):
                    store_type = category
                    break
            
            stores.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "location": place.get("geometry", {}).get("location", {}),
                "rating": place.get("rating"),
                "place_id": place.get("place_id"),
                "type": store_type,
                "photo_reference": place.get("photos", [{}])[0].get("photo_reference") if place.get("photos") else None,
                "open_now": place.get("opening_hours", {}).get("open_now")
            })
        
        # For each product, find potential nearby stores where it might be available
        for product in product_recommendations:
            brand = product.get("brand", "").lower()
            price_value = 0
            try:
                price_value = float(product.get("price", "0"))
            except:
                pass
                
            # Determine price category
            if price_value < 10:
                product["priceCategory"] = "Budget"
            elif price_value < 25:
                product["priceCategory"] = "Moderate"
            else:
                product["priceCategory"] = "Premium"
            
            # Match products to appropriate store types
            matching_stores = []
            
            # Luxury brands typically at luxury stores
            if price_value > 30 or brand in ["the ordinary", "kiehl's", "drunk elephant", "la roche-posay"]:
                matching_stores = [s for s in stores if s.get("type") == "luxury"]
            # Budget products typically at drugstores
            elif price_value < 15:
                matching_stores = [s for s in stores if s.get("type") == "drugstore"]
            # Try to find specific brand stores
            brand_specific_stores = [s for s in stores if brand.lower() in s.get("name", "").lower()]
            if brand_specific_stores:
                matching_stores.extend(brand_specific_stores)
            
            # If no specific matches, include some general stores
            if not matching_stores:
                matching_stores = stores[:3]  # Just include a few options
            
            # Create nearby product entry
            product_entry = {
                **product,  # Include all product details
                "nearbyStores": [
                    {
                        "name": store.get("name"),
                        "address": store.get("address"),
                        "location": store.get("location"),
                        "rating": store.get("rating"),
                        "place_id": store.get("place_id"),
                        "open_now": store.get("open_now"),
                        "map_url": f"https://www.google.com/maps/place/?q=place_id:{store.get('place_id')}"
                    } for store in matching_stores[:3]  # Limit to 3 stores per product
                ]
            }
            
            # Add photo URL if available
            if matching_stores and matching_stores[0].get("photo_reference"):
                product_entry["storePhotoUrl"] = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={matching_stores[0]['photo_reference']}&key={GOOGLE_MAPS_API_KEY}"
            
            nearby_products.append(product_entry)
        
        # Group products by price category
        grouped_products = {
            "Budget": [],
            "Moderate": [],
            "Premium": []
        }
        
        for product in nearby_products:
            category = product.get("priceCategory", "Moderate")
            if category in grouped_products:
                grouped_products[category].append(product)
        
        return jsonify({
            "products": nearby_products,
            "groupedByPrice": grouped_products,
            "nearbyStores": stores[:10]  # Include top 10 nearby stores as context
        })
    except Exception as e:
        print(f"Error finding nearby products: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)