from Emails.router import router
from Emails.service import email_service
from Emails.config_email import email_settings

__all__ = [
    "router", 
    "email_service", 
    "email_settings"
]

__version__ = "1.0.0"
__author__ = "Petit Coeur Technologie"