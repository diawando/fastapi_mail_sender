"""
Configuration settings for the email module.
"""
import os
from pydantic_settings import BaseSettings
from pydantic import EmailStr, field_validator
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
    
    @field_validator('MAIL_RECIPIENTS_CONTACT')
    @classmethod
    def parse_recipients(cls, v: str) -> List[str]:
        # Convertit la chaîne en liste d'emails
        if not v:
            return []
        # Nettoie les espaces et split par les virgules
        return [email.strip() for email in v.split(',')]
    
    # === TEMPLATES ===
    # Dossier contenant les modèles HTML d'emails (relatif au dossier Emails)
    MAIL_TEMPLATES_DIR: str = "templates"
    
    @field_validator('MAIL_TEMPLATES_DIR')
    @classmethod
    def validate_template_dir(cls, v: str) -> str:
        """Valide et crée le dossier templates si nécessaire"""
        # Si c'est un chemin relatif, le rendre absolu
        if not os.path.isabs(v):
            # Utiliser le dossier Emails comme base (où se trouve ce fichier)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            v = os.path.join(base_dir, v)
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(v):
            os.makedirs(v, exist_ok=True)
            print(f"Dossier templates créé: {v}")
        
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instance singleton pour utilisation dans l'application
email_settings = EmailSettings()
        