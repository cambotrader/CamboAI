"""
📧 EMAIL SERVICE - PROFESSIONAL NOTIFICATIONS
Comprehensive email service for user notifications, alerts, and security
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import os
from datetime import datetime
import asyncio
import logging
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader
import aiosmtplib

logger = logging.getLogger(__name__)

@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    from_email: str
    from_name: str
    use_tls: bool = True

@dataclass
class EmailTemplate:
    name: str
    subject: str
    html_content: str
    text_content: str

class EmailService:
    """Professional email service with templates and async sending"""
    
    def __init__(self):
        self.config = self._load_config()
        self.templates = self._load_templates()
        
    def _load_config(self) -> EmailConfig:
        """Load email configuration from environment"""
        
        return EmailConfig(
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME", "your-email@gmail.com"),
            password=os.getenv("SMTP_PASSWORD", "your-app-password"),
            from_email=os.getenv("FROM_EMAIL", "noreply@camboai.com"),
            from_name=os.getenv("FROM_NAME", "CamboAI Trading Platform"),
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        )
    
    def _load_templates(self) -> Dict[str, EmailTemplate]:
        """Load email templates"""
        
        return {
            "verification": EmailTemplate(
                name="Email Verification",
                subject="Verify Your CamboAI Account",
                html_content="""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <img src="https://camboai.com/logo.png" alt="CamboAI" style="height: 60px;">
                        <h1 style="color: #007AFF; margin-top: 20px;">Welcome to CamboAI!</h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 12px; margin-bottom: 30px;">
                        <h2 style="color: #333; margin-bottom: 20px;">Hi {first_name},</h2>
                        <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                            Thank you for joining CamboAI, the next-generation AI-powered trading platform. 
                            To complete your registration and start trading, please verify your email address.
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://app.camboai.com/verify-email/{token}" 
                               style="background: #007AFF; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
                                Verify Email Address
                            </a>
                        </div>
                        
                        <p style="color: #666; font-size: 14px; margin-top: 20px;">
                            Or copy and paste this link in your browser:<br>
                            <a href="https://app.camboai.com/verify-email/{token}">https://app.camboai.com/verify-email/{token}</a>
                        </p>
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h3 style="color: #22c55e; margin-bottom: 15px;">🎯 What's Next?</h3>
                        <ul style="color: #666; line-height: 1.8;">
                            <li>Complete your profile setup</li>
                            <li>Explore our demo trading environment</li>
                            <li>Access AI-powered market insights</li>
                            <li>Join our professional trading community</li>
                        </ul>
                    </div>
                    
                    <div style="border-top: 1px solid #eee; padding-top: 20px; color: #888; font-size: 12px; text-align: center;">
                        <p>This email was sent to {email}. If you didn't create an account, please ignore this email.</p>
                        <p>© 2024 CamboAI. All rights reserved.</p>
                    </div>
                </div>
                """,
                text_content="""
                Welcome to CamboAI!
                
                Hi {first_name},
                
                Thank you for joining CamboAI, the next-generation AI-powered trading platform.
                To complete your registration, please verify your email address by clicking the link below:
                
                https://app.camboai.com/verify-email/{token}
                
                What's next:
                - Complete your profile setup
                - Explore our demo trading environment  
                - Access AI-powered market insights
                - Join our professional trading community
                
                If you didn't create an account, please ignore this email.
                
                Best regards,
                The CamboAI Team
                """
            ),
            
            "password_reset": EmailTemplate(
                name="Password Reset",
                subject="Reset Your CamboAI Password",
                html_content="""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <img src="https://camboai.com/logo.png" alt="CamboAI" style="height: 60px;">
                        <h1 style="color: #007AFF; margin-top: 20px;">Password Reset Request</h1>
                    </div>
                    
                    <div style="background: #fff8dc; border-left: 4px solid #ffa500; padding: 20px; margin-bottom: 30px;">
                        <h3 style="color: #e67e22; margin-bottom: 10px;">🔒 Security Notice</h3>
                        <p style="color: #666; margin: 0;">
                            A password reset was requested for your CamboAI account. If this wasn't you, please ignore this email.
                        </p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 12px; margin-bottom: 30px;">
                        <h2 style="color: #333; margin-bottom: 20px;">Hi {first_name},</h2>
                        <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                            To reset your password, click the button below. This link will expire in 30 minutes for security reasons.
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://app.camboai.com/reset-password/{token}" 
                               style="background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
                                Reset Password
                            </a>
                        </div>
                        
                        <p style="color: #666; font-size: 14px; margin-top: 20px;">
                            Or copy and paste this link in your browser:<br>
                            <a href="https://app.camboai.com/reset-password/{token}">https://app.camboai.com/reset-password/{token}</a>
                        </p>
                    </div>
                    
                    <div style="background: #ffe6e6; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
                        <h3 style="color: #dc3545; margin-bottom: 15px;">🛡️ Security Tips</h3>
                        <ul style="color: #666; line-height: 1.8;">
                            <li>Use a strong, unique password</li>
                            <li>Enable two-factor authentication</li>
                            <li>Never share your login credentials</li>
                            <li>Log out from shared computers</li>
                        </ul>
                    </div>
                    
                    <div style="border-top: 1px solid #eee; padding-top: 20px; color: #888; font-size: 12px; text-align: center;">
                        <p>If you need help, contact our support team at support@camboai.com</p>
                        <p>© 2024 CamboAI. All rights reserved.</p>
                    </div>
                </div>
                """,
                text_content="""
                Password Reset Request
                
                Hi {first_name},
                
                A password reset was requested for your CamboAI account.
                To reset your password, click the link below (expires in 30 minutes):
                
                https://app.camboai.com/reset-password/{token}
                
                If you didn't request this reset, please ignore this email.
                
                Security Tips:
                - Use a strong, unique password
                - Enable two-factor authentication
                - Never share your login credentials
                
                Need help? Contact support@camboai.com
                
                Best regards,
                The CamboAI Team
                """
            ),
            
            "trade_notification": EmailTemplate(
                name="Trade Notification",
                subject="Trade Executed - {symbol}",
                html_content="""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <img src="https://camboai.com/logo.png" alt="CamboAI" style="height: 60px;">
                        <h1 style="color: #007AFF; margin-top: 20px;">Trade Confirmation</h1>
                    </div>
                    
                    <div style="background: #f0f8ff; border-left: 4px solid #007AFF; padding: 25px; margin-bottom: 30px;">
                        <h2 style="color: #007AFF; margin-bottom: 15px;">📊 Trade Executed Successfully</h2>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;">
                            <div>
                                <strong style="color: #333;">Symbol:</strong> {symbol}<br>
                                <strong style="color: #333;">Action:</strong> {action}<br>
                                <strong style="color: #333;">Quantity:</strong> {quantity}
                            </div>
                            <div>
                                <strong style="color: #333;">Price:</strong> ${price}<br>
                                <strong style="color: #333;">Total:</strong> ${total}<br>
                                <strong style="color: #333;">Time:</strong> {time}
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #333;">Order Details</h3>
                        <p style="color: #666; margin: 10px 0;">Order ID: {order_id}</p>
                        <p style="color: #666; margin: 10px 0;">Account: {account}</p>
                        <p style="color: #666; margin: 10px 0;">Commission: ${commission}</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://app.camboai.com/portfolio" 
                           style="background: #007AFF; color: white; padding: 12px 25px; text-decoration: none; border-radius: 8px; display: inline-block;">
                            View Portfolio
                        </a>
                    </div>
                    
                    <div style="border-top: 1px solid #eee; padding-top: 20px; color: #888; font-size: 12px; text-align: center;">
                        <p>© 2024 CamboAI. All rights reserved.</p>
                    </div>
                </div>
                """,
                text_content="""
                Trade Confirmation
                
                Your trade has been executed successfully:
                
                Symbol: {symbol}
                Action: {action}
                Quantity: {quantity}
                Price: ${price}
                Total: ${total}
                Time: {time}
                
                Order Details:
                Order ID: {order_id}
                Account: {account}
                Commission: ${commission}
                
                View your portfolio: https://app.camboai.com/portfolio
                
                Best regards,
                The CamboAI Team
                """
            ),
            
            "security_alert": EmailTemplate(
                name="Security Alert",
                subject="🚨 Security Alert - {alert_type}",
                html_content="""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #dc3545; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
                        <h1 style="margin: 0;">🚨 Security Alert</h1>
                        <p style="margin: 10px 0 0 0; font-size: 18px;">{alert_type}</p>
                    </div>
                    
                    <div style="background: #fff; border: 2px solid #dc3545; border-top: none; padding: 30px; border-radius: 0 0 8px 8px;">
                        <h2 style="color: #dc3545; margin-bottom: 20px;">Alert Details</h2>
                        <div style="background: #ffebee; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                            <p style="color: #333; margin-bottom: 10px;"><strong>Time:</strong> {timestamp}</p>
                            <p style="color: #333; margin-bottom: 10px;"><strong>IP Address:</strong> {ip_address}</p>
                            <p style="color: #333; margin-bottom: 10px;"><strong>Location:</strong> {location}</p>
                            <p style="color: #333; margin: 0;"><strong>Details:</strong> {details}</p>
                        </div>
                        
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                            <h3 style="color: #1976d2; margin-bottom: 15px;">🛡️ Immediate Actions</h3>
                            <ul style="color: #333; line-height: 1.8; margin: 0; padding-left: 20px;">
                                <li>Review your recent account activity</li>
                                <li>Change your password if you suspect unauthorized access</li>
                                <li>Enable two-factor authentication if not already enabled</li>
                                <li>Contact support if you need assistance</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin-bottom: 25px;">
                            <a href="https://app.camboai.com/security" 
                               style="background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; margin-right: 15px;">
                                Review Security
                            </a>
                            <a href="mailto:security@camboai.com" 
                               style="background: #6c757d; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
                                Contact Support
                            </a>
                        </div>
                        
                        <div style="border-top: 1px solid #eee; padding-top: 20px; color: #666; font-size: 14px;">
                            <p><strong>Note:</strong> This is an automated security notification. If this activity was authorized by you, no further action is needed.</p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; color: #888; font-size: 12px;">
                        <p>© 2024 CamboAI. All rights reserved.</p>
                    </div>
                </div>
                """,
                text_content="""
                🚨 SECURITY ALERT - {alert_type}
                
                We detected potentially suspicious activity on your CamboAI account.
                
                Alert Details:
                Time: {timestamp}
                IP Address: {ip_address}
                Location: {location}
                Details: {details}
                
                Immediate Actions:
                1. Review your recent account activity
                2. Change your password if you suspect unauthorized access
                3. Enable two-factor authentication if not already enabled
                4. Contact security@camboai.com if you need assistance
                
                Security Dashboard: https://app.camboai.com/security
                
                If this activity was authorized by you, no further action is needed.
                
                CamboAI Security Team
                """
            )
        }
    
    async def send_email_async(self, to_email: str, subject: str, 
                              html_content: str, text_content: str = None) -> bool:
        """Send email asynchronously"""
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.config.from_name} <{self.config.from_email}>"
            message["To"] = to_email
            
            # Add text part
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.config.smtp_server,
                port=self.config.smtp_port,
                start_tls=self.config.use_tls,
                username=self.config.username,
                password=self.config.password,
            )
            
            logger.info(f"📧 Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def send_email_sync(self, to_email: str, subject: str, 
                       html_content: str, text_content: str = None) -> bool:
        """Send email synchronously"""
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.config.from_name} <{self.config.from_email}>"
            message["To"] = to_email
            
            # Add text part
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Create SMTP session
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.username, self.config.password)
                server.send_message(message)
            
            logger.info(f"📧 Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    async def send_template_email(self, template_name: str, to_email: str, 
                                 variables: Dict[str, Any]) -> bool:
        """Send templated email"""
        
        if template_name not in self.templates:
            logger.error(f"❌ Email template '{template_name}' not found")
            return False
        
        template = self.templates[template_name]
        
        try:
            # Format template content
            html_content = template.html_content.format(**variables)
            text_content = template.text_content.format(**variables)
            subject = template.subject.format(**variables)
            
            # Send email
            return await self.send_email_async(to_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"❌ Failed to send template email '{template_name}': {e}")
            return False
    
    async def send_bulk_email(self, emails: List[str], subject: str,
                             html_content: str, text_content: str = None,
                             batch_size: int = 50) -> Dict[str, Any]:
        """Send bulk email with rate limiting"""
        
        sent_count = 0
        failed_count = 0
        failed_emails = []
        
        # Process in batches
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            
            # Send batch concurrently
            tasks = [
                self.send_email_async(email, subject, html_content, text_content)
                for email in batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count results
            for j, result in enumerate(results):
                if isinstance(result, Exception) or not result:
                    failed_count += 1
                    failed_emails.append(batch[j])
                else:
                    sent_count += 1
            
            # Rate limiting between batches
            if i + batch_size < len(emails):
                await asyncio.sleep(1)  # 1 second delay
        
        return {
            "total_emails": len(emails),
            "sent_count": sent_count,
            "failed_count": failed_count,
            "failed_emails": failed_emails,
            "success_rate": (sent_count / len(emails)) * 100 if emails else 0
        }

# Global email service instance
email_service = EmailService()

# Convenience functions for common email types

async def send_verification_email(email: str, first_name: str, token: str) -> bool:
    """Send email verification email"""
    
    return await email_service.send_template_email(
        "verification",
        email,
        {
            "first_name": first_name,
            "email": email,
            "token": token
        }
    )

async def send_password_reset_email(email: str, first_name: str, token: str) -> bool:
    """Send password reset email"""
    
    return await email_service.send_template_email(
        "password_reset",
        email,
        {
            "first_name": first_name,
            "token": token
        }
    )

async def send_trade_notification(email: str, trade_data: Dict[str, Any]) -> bool:
    """Send trade execution notification"""
    
    return await email_service.send_template_email(
        "trade_notification",
        email,
        trade_data
    )

async def send_security_alert(email: str, alert_data: Dict[str, Any]) -> bool:
    """Send security alert email"""
    
    return await email_service.send_template_email(
        "security_alert",
        email,
        alert_data
    )

# Email validation utilities

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_email_provider(email: str) -> str:
    """Get email provider domain"""
    try:
        return email.split('@')[1].lower()
    except:
        return "unknown"

# Email analytics (for tracking opens, clicks, etc.)
class EmailAnalytics:
    """Track email analytics"""
    
    def __init__(self):
        self.email_stats = {
            "sent": 0,
            "delivered": 0,
            "opened": 0,
            "clicked": 0,
            "bounced": 0,
            "complained": 0
        }
    
    def track_sent(self, email_id: str):
        """Track email sent"""
        self.email_stats["sent"] += 1
    
    def track_delivered(self, email_id: str):
        """Track email delivered"""
        self.email_stats["delivered"] += 1
    
    def track_opened(self, email_id: str):
        """Track email opened"""
        self.email_stats["opened"] += 1
    
    def track_clicked(self, email_id: str, link_url: str):
        """Track link clicked"""
        self.email_stats["clicked"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get email statistics"""
        total_sent = max(self.email_stats["sent"], 1)
        
        return {
            **self.email_stats,
            "delivery_rate": (self.email_stats["delivered"] / total_sent) * 100,
            "open_rate": (self.email_stats["opened"] / max(self.email_stats["delivered"], 1)) * 100,
            "click_rate": (self.email_stats["clicked"] / max(self.email_stats["opened"], 1)) * 100
        }

# Global analytics instance
email_analytics = EmailAnalytics()

# Export main components
__all__ = [
    'email_service', 'email_analytics',
    'send_verification_email', 'send_password_reset_email',
    'send_trade_notification', 'send_security_alert',
    'validate_email', 'get_email_provider'
]