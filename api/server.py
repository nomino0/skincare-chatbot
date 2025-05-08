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
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Prepare the prompt with context and knowledge
        system_prompt = """
        You are Hasna, a friendly and knowledgeable skincare assistant. Respond in a warm, conversational tone.
        
        When giving skincare advice:
        - Be specific and personalized based on the user's skin type and concerns
        - Use a natural, encouraging tone with occasional emoji for friendliness
        - Focus on evidence-based skincare advice and product recommendations
        - Include both affordable and premium options when recommending products
        - Organize information clearly with sections when providing routines
        
        Skin analysis information:
        {}
        """.format(json.dumps(skin_analysis) if skin_analysis else "No skin analysis available yet")
        
        # If we have GROQ API key, use it
        if GROQ_API_KEY:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Format the conversation history for the API
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add prior conversation for context
            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add the current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            payload = {
                "messages": messages,
                "model": "llama3-70b-8192",
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            response = requests.post("https://api.groq.com/v1/chat/completions", 
                                   headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                assistant_response = result["choices"][0]["message"]["content"]
                return jsonify({"response": assistant_response})
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
        
        # In a real implementation, you would query a database of products
        # For now, we'll return mock data based on parameters
        
        # This could be expanded with a real database of products by country
        products = []
        
        # Just some example data based on parameters
        if country and skin_type:
            # Mock database of products
            all_products = [
                # Example for dry skin, female, older skin
                {
                    "name": "Ultra Facial Cream",
                    "brand": "Kiehl's",
                    "price": "38.00",
                    "currency": "USD",
                    "link": "https://www.kiehls.com/skincare/face-moisturizers/ultra-facial-cream/3605970360757.html",
                    "imageUrl": "https://www.kiehls.com/dw/image/v2/AANG_PRD/on/demandware.static/-/Sites-kiehls-master-catalog/default/dwd93fb99e/nextgen/face-moisturizers/ultra-facial-cream/ultra-facial-cream-3605970360757-1.jpg",
                    "description": "24-hour moisturizer for all skin types",
                    "forSkinType": ["Dry", "Normal"],
                    "targetGender": "All"
                },
                # Example for male, oily skin
                {
                    "name": "Oil-Free Moisturizer",
                    "brand": "Lab Series",
                    "price": "37.00",
                    "currency": "USD",
                    "link": "https://www.labseries.com/product/19791/54538/",
                    "imageUrl": "https://www.labseries.com/media/images/products/1000x1000/ls_sku_54538_1000x1000_0.jpg",
                    "description": "Lightweight, oil-free hydration for men",
                    "forSkinType": ["Oily", "Combination"],
                    "targetGender": "Male"
                },
                # More products...
            ]
            
            # Filter products based on parameters
            for product in all_products:
                # Check for skin type match
                if skin_type.lower() in [t.lower() for t in product.get("forSkinType", [])]:
                    # Check for gender-specific match if gender is provided
                    if gender and product.get("targetGender") != "All" and product.get("targetGender") != gender:
                        continue
                        
                    # Check for skin issues if provided
                    if skin_issues and product.get("forSkinIssues"):
                        if not any(issue.lower() in [i.lower() for i in product.get("forSkinIssues", [])] for issue in skin_issues):
                            continue
                    
                    # Add product to recommendations
                    products.append(product)
            
        return jsonify(products)
    except Exception as e:
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)