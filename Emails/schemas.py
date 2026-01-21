from pydantic import BaseModel, EmailStr, Field, validator
from typing import Dict, Any
import re


# === SCHEMAS DE VALIDATION ===
class ContactFormRequest(BaseModel):
    """
    Schéma Pydantic Pour valider les données du formulaire de contact
    
    EXEMPLE D'UTILISATION :
    ----------------------
    {
      "nom": "Mamadou Diallo",
      "email": "mamadou@example.com",
      "telephone": "+224621234567",
      "sujet": "Question sur les tarifs",
      "message": "Je souhaite connaître vos tarifs..."
    }
    """
    
    nom: str = Field(
        ..., 
        min_length=2,
        max_length=100,
        description="Nom complet du visiteur",
        example="Mamadou DIALLO"
    )
    email: EmailStr = Field(
        ...,
        description="Adresse email du visiteur",
        example="mamadou@example.com"
    )
    telephone: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Numéro de téléphone (format international recommandé)",
        example="+224600000000"
    )
    sujet: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Sujet du message",
        example="Demande d'information sur les services"
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Contenu du message",
        example="Je souhaiterais obtenir plus d'information sur ..."
    )
    
    @validator('telephone')
    def validate_phone_format(cls, v):
        """
        Validateur personnalisé pour le numéro de téléphone
        
        VALIDATION:
        ----------
        - Accepte les formats internationaux (+224...)
        - Accepte les formats locaux (621...)
        - Retire les espaces et caractères spéciaux
        """
        # Nettoyer le numéro (retirer espaces, tirets, parenthèses)
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        
        # Vérifier qu'il ne reste que des chiffres et éventuellement un +
        if not re.match(r'^\+?\d{8,15}$', cleaned):
            raise ValueError(
                "Format de téléphone invalide. "
                "Utilisez un format international (+224...) ou local (621..)"
            )
        
        return cleaned
    
    @validator('message')
    def sanitize_message(cls, v):
        """
        Nettoie le message pour éviter les injections HTML/Script
        """
        # Retirer les balises HTML potentiellement dangereuses
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Scripts
            r'<iframe[^>]*>.*?</iframe>',  # IFrames
            r'javascript:',                 # URLs JavaScript
            r'on\w+\s*=',                  # Événements inline (onclick, etc.)   
        ]
        
        cleaned = v
        for pattern in dangerous_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        return cleaned.strip()
    
    class Config:
        """Configuration du modèle Pydantic"""
        # Génère des exemples dans la doc Swagger 
        json_schema_extra = {
            "example": {
                "nom": "Mamadou Diallo",
                "email": "mamadou@example.com",
                "telephone": "+224621234567",
                "sujet": "Demande d'information",
                "message": "Bonjour, je souhaiterais en savoir plus sur vos services."
            }
        }


class ContactFormResponse(BaseModel):
    """
    Schéma de réponse après soumission du formulaire
    
    STRUCTURE :
    ----------
    {
      "success": true,
      "message": "Votre message a été envoyé...",
      "timestamp": "2025-01-20T14:30:00"
    }
    """
    success: bool = Field(
        ...,
        description="Indique si la soumission a réussi"
    )
    message: str = Field(
        ...,
        description="Message de confirmation ou d'erreur"
    )
    timestamp: str = Field(
        ...,
        description="Horodatage de la soumission (ISO 8601)"
    )


class HealthResponse(BaseModel):
    status: str
    smtp_server: str = None
    mail_from: str = None
    tls_enabled: bool = None
    recipients_count: int = None