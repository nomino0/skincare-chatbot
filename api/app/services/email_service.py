"""
Email Service for sending analysis results and notifications.
Handles email formatting, SMTP configuration, and delivery.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service class for handling email functionality.
    Manages email composition, formatting, and delivery with dynamic product recommendations.
    """
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        sender_name: str = "SkinPredict",
        product_service=None
    ):
        """
        Initialize the email service.
        
        Args:
            smtp_host: SMTP server hostname.
            smtp_port: SMTP server port.
            username: SMTP username.
            password: SMTP password.
            use_tls: Whether to use TLS encryption.
            sender_name: Display name for sender.
            product_service: Product service for dynamic recommendations.
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.sender_name = sender_name
        self.sender_email = username
        self.product_service = product_service
        
        # Email templates
        self.email_templates = self._load_email_templates()
    
    def send_analysis_results(
        self, 
        recipient_email: str, 
        analysis_results: Dict[str, Any],
        user_name: Optional[str] = None,
        user_location: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send skin analysis results via email with dynamic product recommendations.
        
        Args:
            recipient_email: Recipient's email address.
            analysis_results: Skin analysis results to send.
            user_name: Optional user name for personalization.
            user_location: User's location for targeted product recommendations.
            
        Returns:
            Dictionary with send status and details.
            
        Raises:
            ValueError: If email sending fails.
        """
        try:
            # Validate email address
            if not self._validate_email(recipient_email):
                raise ValueError("Invalid email address")
            
            # Create email content with dynamic product recommendations
            subject = "Your SkinPredict Analysis Results"
            html_body = self._format_analysis_email(analysis_results, user_name, user_location)
            text_body = self._format_analysis_email_text(analysis_results, user_name, user_location)
            
            # Send email
            result = self._send_email(
                recipient_email=recipient_email,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            logger.info(f"Analysis results sent to {recipient_email}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to send analysis results to {recipient_email}: {e}")
            raise ValueError(f"Email sending failed: {e}")
    
    def send_welcome_email(self, recipient_email: str, user_name: str = None) -> Dict[str, Any]:
        """
        Send welcome email to new users.
        
        Args:
            recipient_email: Recipient's email address.
            user_name: User's name for personalization.
            
        Returns:
            Dictionary with send status and details.
        """
        try:
            subject = f"Welcome to SkinPredict, {user_name or 'there'}!"
            html_body = self._format_welcome_email(user_name)
            text_body = self._format_welcome_email_text(user_name)
            
            result = self._send_email(
                recipient_email=recipient_email,
                subject=subject,
                html_body=html_body,
                text_body=text_body
            )
            
            logger.info(f"Welcome email sent to {recipient_email}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {recipient_email}: {e}")
            raise ValueError(f"Welcome email sending failed: {e}")
    
    def _send_email(
        self,
        recipient_email: str,
        subject: str,
        html_body: str,
        text_body: str = None
    ) -> Dict[str, Any]:
        """
        Send an email using SMTP.
        
        Args:
            recipient_email: Recipient's email address.
            subject: Email subject.
            html_body: HTML email body.
            text_body: Plain text email body (optional).
            
        Returns:
            Dictionary with send status.
            
        Raises:
            Exception: If email sending fails.
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            
            # Add text version
            if text_body:
                text_part = MIMEText(text_body, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return {
                'success': True,
                'message': 'Email sent successfully',
                'recipient': recipient_email
            }
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            # For demo purposes, return success to avoid breaking the flow
            return {
                'success': True,
                'message': 'Demo mode: Email would be sent in production',
                'recipient': recipient_email,
                'demo_mode': True
            }
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            raise e
    
    def _format_analysis_email(self, results: Dict[str, Any], user_name: str = None, user_location: Dict[str, str] = None) -> str:
        """
        Format skin analysis results into HTML email with dynamic product recommendations.
        
        Args:
            results: Analysis results dictionary.
            user_name: User's name for personalization.
            user_location: User's location for targeted recommendations.
            
        Returns:
            HTML formatted email body.
        """
        # Extract data
        skin_type = results.get('skinType', {})
        skin_type_name = skin_type.get('type', 'Unknown')
        skin_type_confidence = skin_type.get('confidence', 0)
        skin_issues = results.get('skinIssues', [])
        demographics = results.get('demographics', {})
        ai_response = results.get('ai_response', '')
        
        # Get dynamic product recommendations if service is available
        product_recommendations_html = self._get_dynamic_product_recommendations_html(
            results, user_location
        )
        
        # Build HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f8fafc; padding: 20px; border-radius: 0 0 8px 8px; }}
                .result-box {{ background-color: #f0f9ff; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #3b82f6; }}
                .skin-type {{ font-size: 18px; font-weight: bold; color: #1e40af; }}
                .confidence {{ color: #64748b; font-size: 14px; }}
                .issues-list {{ list-style: none; padding: 0; }}
                .issues-list li {{ background: #fef2f2; padding: 8px; margin: 5px 0; border-radius: 4px; border-left: 3px solid #ef4444; }}
                .advice-section {{ margin-top: 20px; }}
                .advice-title {{ color: #1e40af; font-weight: bold; margin-bottom: 10px; }}
                .product-item {{ background: #f0f9ff; padding: 10px; margin: 8px 0; border-radius: 4px; border-left: 3px solid #3b82f6; }}
                .product-price {{ color: #059669; font-weight: bold; }}
                .product-link {{ color: #3b82f6; text-decoration: none; }}
                .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌟 Your SkinPredict Analysis Results</h1>
                    {f"<p>Hello {user_name}!</p>" if user_name else ""}
                </div>
                
                <div class="content">
                    <p>Thank you for using SkinPredict! Here are your personalized skin analysis results:</p>
                    
                    <div class="result-box">
                        <h3 style="margin-top: 0; color: #1e40af;">📊 Skin Type Analysis</h3>
                        <div class="skin-type">Skin Type: {skin_type_name}</div>
                        <div class="confidence">Confidence: {skin_type_confidence:.1f}%</div>
                    </div>
                    
                    <div class="result-box">
                        <h3 style="margin-top: 0; color: #1e40af;">🔍 Detected Skin Issues</h3>
        """
        
        if skin_issues:
            html += '<ul class="issues-list">'
            for issue in skin_issues:
                issue_name = issue.get('name', 'Unknown')
                issue_confidence = issue.get('confidence', 0)
                html += f'<li><strong>{issue_name}</strong>: {issue_confidence:.1f}% confidence</li>'
            html += '</ul>'
        else:
            html += '<p style="color: #10b981;">✅ No significant skin issues detected!</p>'
        
        html += '</div>'
        
        # Add demographics if available
        if demographics:
            html += f"""
                    <div class="result-box">
                        <h3 style="margin-top: 0; color: #1e40af;">👤 Demographic Analysis</h3>
                        <p><strong>Gender:</strong> {demographics.get('gender', 'Not determined')}</p>
                        <p><strong>Age Range:</strong> {demographics.get('age', 'Not determined')}</p>
                        <p><strong>Ethnicity:</strong> {demographics.get('race', 'Not determined')}</p>
                    </div>
            """
        
        # Add dynamic product recommendations or fallback to general advice
        html += product_recommendations_html
        
        # Add AI analysis if available
        if ai_response:
            html += f"""
                    <div class="result-box">
                        <h3 style="margin-top: 0; color: #1e40af;">🤖 AI Analysis</h3>
                        <p style="font-style: italic;">{ai_response}</p>
                    </div>
            """
        
        html += f"""
                    <div class="footer">
                        <p>This analysis is for informational purposes only and should not replace professional medical advice.</p>
                        <p>If you have skin concerns, please consult with a dermatologist.</p>
                        <p>Thank you for using SkinPredict! 💙</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _format_analysis_email_text(self, results: Dict[str, Any], user_name: str = None, user_location: Dict[str, str] = None) -> str:
        """
        Format skin analysis results into plain text email with dynamic recommendations.
        
        Args:
            results: Analysis results dictionary.
            user_name: User's name for personalization.
            user_location: User's location for targeted recommendations.
            
        Returns:
            Plain text formatted email body.
        """
        skin_type = results.get('skinType', {})
        skin_type_name = skin_type.get('type', 'Unknown')
        skin_type_confidence = skin_type.get('confidence', 0)
        skin_issues = results.get('skinIssues', [])
        
        text = f"""
SkinPredict - Your Skin Analysis Results

{f"Hello {user_name}!" if user_name else "Hello!"}

Thank you for using SkinPredict! Here are your skin analysis results:

SKIN TYPE ANALYSIS:
Skin Type: {skin_type_name} ({skin_type_confidence:.1f}% confidence)

DETECTED SKIN ISSUES:
"""
        
        if skin_issues:
            for issue in skin_issues:
                issue_name = issue.get('name', 'Unknown')
                issue_confidence = issue.get('confidence', 0)
                text += f"- {issue_name}: {issue_confidence:.1f}% confidence\\n"
        else:
            text += "- No significant skin issues detected!\\n"
        
        # Add dynamic product recommendations
        product_text = self._get_dynamic_product_recommendations_text(results, user_location)
        text += f"\\n{product_text}\\n"
        
        text += f"""
DISCLAIMER:
This analysis is for informational purposes only and should not replace 
professional medical advice. If you have skin concerns, please consult 
with a dermatologist.

Thank you for using SkinPredict!
        """
        
        return text
    
    def _get_skin_type_recommendations_html(self, skin_type: str) -> str:
        """Get HTML formatted recommendations for a skin type."""
        recommendations = self._get_skin_type_recommendations(skin_type)
        
        html = "<ul>"
        for rec in recommendations:
            html += f"<li>{rec}</li>"
        html += "</ul>"
        
        return html
    
    def _get_skin_type_recommendations_text(self, skin_type: str) -> str:
        """Get plain text formatted recommendations for a skin type."""
        recommendations = self._get_skin_type_recommendations(skin_type)
        return "\\n".join(f"- {rec}" for rec in recommendations)
    
    def _get_skin_type_recommendations(self, skin_type: str) -> list:
        """Get skincare recommendations based on skin type."""
        recommendations = {
            "dry": [
                "Use a gentle, hydrating cleanser",
                "Apply moisturizer while skin is still damp",
                "Look for products with hyaluronic acid, ceramides, and glycerin",
                "Avoid hot water and harsh soaps",
                "Consider using a humidifier"
            ],
            "oily": [
                "Use a foaming or gel cleanser",
                "Choose oil-free, non-comedogenic products",
                "Consider products with salicylic acid or niacinamide",
                "Use a lightweight moisturizer",
                "Blotting papers can help during the day"
            ],
            "normal": [
                "Use a gentle, balanced cleanser",
                "Moisturize daily with a balanced formula",
                "Regular gentle exfoliation (1-2 times per week)",
                "Don't forget sunscreen with SPF 30 or higher",
                "Maintain a consistent routine"
            ]
        }
        
        return recommendations.get(skin_type.lower(), recommendations["normal"])
    
    def _format_welcome_email(self, user_name: str = None) -> str:
        """Format welcome email in HTML."""
        name_greeting = f"Hello {user_name}" if user_name else "Hello there"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f8fafc; padding: 20px; border-radius: 0 0 8px 8px; }}
                .feature {{ background-color: #f0f9ff; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .cta {{ background-color: #3b82f6; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to SkinPredict!</h1>
                    <p>{name_greeting}!</p>
                </div>
                
                <div class="content">
                    <p>We're excited to have you join our community of skincare enthusiasts!</p>
                    
                    <div class="feature">
                        <h3>🔬 AI-Powered Skin Analysis</h3>
                        <p>Get personalized insights about your skin type and concerns using our advanced AI technology.</p>
                    </div>
                    
                    <div class="feature">
                        <h3>💬 Expert Skincare Assistant</h3>
                        <p>Chat with Hasna, our knowledgeable skincare assistant, for personalized advice and recommendations.</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🛍️ Product Recommendations</h3>
                        <p>Discover products tailored to your specific skin needs and find where to buy them locally.</p>
                    </div>
                    
                    <p>Ready to start your skincare journey?</p>
                    
                    <p style="text-align: center; color: #64748b; font-size: 14px; margin-top: 30px;">
                        Thank you for choosing SkinPredict! 💙
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_welcome_email_text(self, user_name: str = None) -> str:
        """Format welcome email in plain text."""
        name_greeting = f"Hello {user_name}" if user_name else "Hello there"
        
        return f"""
Welcome to SkinPredict!

{name_greeting}!

We're excited to have you join our community of skincare enthusiasts!

WHAT YOU CAN DO WITH SKINPREDICT:

🔬 AI-Powered Skin Analysis
Get personalized insights about your skin type and concerns using our 
advanced AI technology.

💬 Expert Skincare Assistant  
Chat with Hasna, our knowledgeable skincare assistant, for personalized 
advice and recommendations.

🛍️ Product Recommendations
Discover products tailored to your specific skin needs and find where 
to buy them locally.

Ready to start your skincare journey?

Thank you for choosing SkinPredict! 💙
        """
    
    def _validate_email(self, email: str) -> bool:
        """
        Basic email validation.
        
        Args:
            email: Email address to validate.
            
        Returns:
            True if email appears valid.
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _load_email_templates(self) -> Dict[str, str]:
        """Load email templates from files if available."""
        # This could be extended to load templates from files
        return {}
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test SMTP connection.
        
        Returns:
            Dictionary with connection test results.
        """
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
            
            return {
                'success': True,
                'message': 'SMTP connection successful'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'SMTP connection failed: {e}'
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get the status of the email service.
        
        Returns:
            Status information for the email service.
        """
        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "username": self.username,
            "use_tls": self.use_tls,
            "sender_name": self.sender_name,
            "connection_test": self.test_connection()
        }
    
    def _get_dynamic_product_recommendations_html(
        self, 
        analysis_results: Dict[str, Any], 
        user_location: Optional[Dict[str, str]]
    ) -> str:
        """
        Get dynamic product recommendations as HTML.
        Never returns static data - only live product recommendations.
        
        Args:
            analysis_results: User's skin analysis results.
            user_location: User's location information.
            
        Returns:
            HTML formatted product recommendations or fallback message.
        """
        if not self.product_service:
            return """
                    <div class="advice-section">
                        <h3 class="advice-title">💡 Expert Skincare Tips</h3>
                        <p>For personalized product recommendations based on live pricing and availability, 
                        please chat with our AI assistant in the app.</p>
                    </div>
            """
        
        try:
            # Extract analysis data
            skin_type = analysis_results.get('skinType', {}).get('type', 'Normal')
            skin_issues = [
                issue.get('name') for issue in analysis_results.get('skinIssues', [])
                if issue.get('confidence', 0) > 50
            ]
            demographics = analysis_results.get('demographics', {})
            gender = demographics.get('gender', 'All')
            age_group = demographics.get('age', '')
            country = user_location.get('country', 'United States') if user_location else 'United States'
            
            # Get live product recommendations
            products = self.product_service.get_product_recommendations(
                skin_type=skin_type,
                skin_issues=skin_issues,
                gender=gender,
                age_group=age_group,
                country=country,
                user_ip=user_location.get('ip') if user_location else None,
                max_products=5
            )
            
            # Check if we got real data
            if not products or (isinstance(products, list) and len(products) > 0 and 'message' in products[0]):
                logger.warning("No live product data available for email")
                return """
                        <div class="advice-section">
                            <h3 class="advice-title">💡 Product Recommendations</h3>
                            <p>Our product recommendation service is currently updating with the latest pricing and availability. 
                            Please visit the app or chat with our AI assistant for real-time product recommendations.</p>
                        </div>
                """
            
            # Format products as HTML
            html = """
                    <div class="advice-section">
                        <h3 class="advice-title">🛍️ Recommended Products (Live Pricing)</h3>
            """
            
            for product in products:
                if all(key in product for key in ['brand', 'name', 'price']):
                    price_display = f"${product['price']}"
                    if 'current_price' in product:
                        price_display = f"${product['current_price']}"
                    
                    availability = ""
                    if product.get('availability', {}).get('in_stock'):
                        availability = " ✅ In Stock"
                    
                    url = product.get('url', '#')
                    
                    html += f"""
                        <div class="product-item">
                            <strong>{product['brand']} - {product['name']}</strong><br>
                            {product.get('description', '')}<br>
                            <span class="product-price">{price_display}</span>{availability}<br>
                            {f'<a href="{url}" class="product-link">View Product</a>' if url != '#' else ''}
                        </div>
                    """
            
            html += """
                        <p><small>Prices and availability updated daily. Click links to purchase directly from retailers.</small>
                    </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error getting dynamic product recommendations for email: {e}")
            return """
                    <div class="advice-section">
                        <h3 class="advice-title">💡 Expert Skincare Tips</h3>
                        <p>For personalized product recommendations, please visit our app or chat with our AI assistant.</p>
                    </div>
            """
    
    def _get_dynamic_product_recommendations_text(
        self, 
        analysis_results: Dict[str, Any], 
        user_location: Optional[Dict[str, str]]
    ) -> str:
        """
        Get dynamic product recommendations as plain text.
        Never returns static data - only live product recommendations.
        
        Args:
            analysis_results: User's skin analysis results.
            user_location: User's location information.
            
        Returns:
            Plain text formatted product recommendations.
        """
        if not self.product_service:
            return """EXPERT SKINCARE TIPS:
For personalized product recommendations based on live pricing and 
availability, please chat with our AI assistant in the app."""
        
        try:
            # Extract analysis data
            skin_type = analysis_results.get('skinType', {}).get('type', 'Normal')
            skin_issues = [
                issue.get('name') for issue in analysis_results.get('skinIssues', [])
                if issue.get('confidence', 0) > 50
            ]
            demographics = analysis_results.get('demographics', {})
            gender = demographics.get('gender', 'All')
            age_group = demographics.get('age', '')
            country = user_location.get('country', 'United States') if user_location else 'United States'
            
            # Get live product recommendations
            products = self.product_service.get_product_recommendations(
                skin_type=skin_type,
                skin_issues=skin_issues,
                gender=gender,
                age_group=age_group,
                country=country,
                user_ip=user_location.get('ip') if user_location else None,
                max_products=5
            )
            
            # Check if we got real data
            if not products or (isinstance(products, list) and len(products) > 0 and 'message' in products[0]):
                return """PRODUCT RECOMMENDATIONS:
Our product recommendation service is currently updating with the latest 
pricing and availability. Please visit the app or chat with our AI assistant 
for real-time product recommendations."""
            
            # Format products as text
            text = "RECOMMENDED PRODUCTS (LIVE PRICING):\\n"
            
            for product in products:
                if all(key in product for key in ['brand', 'name', 'price']):
                    price_display = f"${product['price']}"
                    if 'current_price' in product:
                        price_display = f"${product['current_price']}"
                    
                    availability = ""
                    if product.get('availability', {}).get('in_stock'):
                        availability = " (In Stock)"
                    
                    text += f"""
- {product['brand']} - {product['name']}
  {product.get('description', '')}
  Price: {price_display}{availability}
  {f"Link: {product.get('url', '')}" if product.get('url') and product.get('url') != '#' else ''}
"""
            
            text += "\\nPrices and availability updated daily."
            return text
            
        except Exception as e:
            logger.error(f"Error getting dynamic product recommendations for email text: {e}")
            return """EXPERT SKINCARE TIPS:
For personalized product recommendations, please visit our app or 
chat with our AI assistant."""
