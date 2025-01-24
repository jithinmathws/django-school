# Django imports for email handling and configuration
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from loguru import logger

def send_otp_email(email, otp):
    """
    Send a One-Time Password (OTP) email to the user for verification.
    
    Args:
        email (str): The recipient's email address
        otp (str): The generated OTP to be sent
        
    The email includes:
        - The OTP code
        - Expiry time information
        - Site name for branding
        
    Both HTML and plain text versions of the email are sent.
    Logs success or failure of email sending operation.
    """
    subject = _("Please verify your login")
    from_email = settings.DEFAULT_FROM_EMAIL
    recepient_list = [email]
    # Prepare context data for email template
    context = {
        "otp": otp,
        "expiry_time": settings.OTP_EXPIRY_TIME,
        "site_name": settings.SITE_NAME,
    }
    # Render both HTML and plain text versions
    html_email = render_to_string("emails/otp_email.html", context)
    plain_email = strip_tags(html_email)
    email = EmailMultiAlternatives(subject, plain_email, from_email, recepient_list)
    email.attach_alternative(html_email, "text/html")
    try:
        email.send()
        logger.info("OTP sent to %s", email)
    except Exception as e:
        logger.error(f"Failed to send OTP to {email}: Error: {str(e)}", exc_info=True)

def send_account_locked_email(self):
    """
    Send an email notification when a user's account is locked due to multiple failed login attempts.
    
    Args:
        self: The user instance whose account is locked
        
    The email includes:
        - User's full name
        - Account lockout duration
        - Site name for branding
        
    Both HTML and plain text versions of the email are sent.
    Logs success or failure of email sending operation.
    """
    subject = _("Account Locked")
    from_email = settings.DEFAULT_FROM_EMAIL
    recepient_list = [self.email]
    # Prepare context data for email template
    context = {
        "user": self,
        "lockout_duration": int(settings.LOCKOUT_DURATION.total_seconds() // 60),
        "site_name": settings.SITE_NAME,
    }
    # Render both HTML and plain text versions
    html_email = render_to_string("emails/account_locked.html", context)
    plain_email = strip_tags(html_email)
    email = EmailMultiAlternatives(subject, plain_email, from_email, recepient_list)
    email.attach_alternative(html_email, "text/html")
    try:
        email.send()
        logger.info("Account locked email sent to %s", self.email)
    except Exception as e:
        logger.error(f"Failed to send account locked email to {self.email}: Error: {str(e)}", exc_info=True)