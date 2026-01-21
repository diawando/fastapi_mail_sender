"""
Configuration settings for the email module.
"""

from pydantic_settings import BaseSettings
from pydantic import EmailStr, validator
from typing import List


class EmailSettings(BaseSettings):
    """
    Configuration centralisée pour l'envoi d'emails

    Pydantic valide automatiquement que toutes les variables 
    d'environnement requises sont présentes au démarrage
    """
    
    # === CONFIGURATION SERVEUR SMTP ===
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str 
    
    # === OPTIONS DE CONNEXION ===
    
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    
    # === VALIDATION EMAIL ===
    # Active la vérification du format email
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    
    # ==== DESTINATAIRES INTERNES ===
    # Emails qui recevront les soumissions de formulaires
    MAIL_RECIPIENTS_CONTACT: str
    
    @validator('MAIL_RECIPIENTS_CONTACT')
    @classmethod
    def parse_recipients(cls, v: str) -> List[str]:
        # Convertit la chaîne en liste d'emails
        if not v:
            return []
        # Nettoie les espaces et split par les virgules
        return [email.strip() for email in v.split(',')]
    
    # === TEMPLATES ===
    # Dossier contenant les modèles HTML d'emails
    MAIL_TEMPLATES_DIR: str = "Email/templates"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instance singleton pour utilisation dans l'application
email_settings = EmailSettings()
        