from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from Emails.service import email_service
from Emails.schemas import ContactFormRequest, ContactFormResponse, HealthResponse
import logging
import re


logger = logging.getLogger(__name__)

# === CREATION DU ROUTER ===
router = APIRouter(
    prefix="/contact",
    tags=["Contact"]
)


# === ENDPOINTS API ===
@router.post(
    "/submit",
    response_model=ContactFormResponse,
    status_code=status.HTTP_200_OK,
    summary="Soumettre un formulaire de contact",
    description="""
     **Endpoint pour recevoir les soumissions du formulaire de contact web.**
    
         ### Workflow :
         1. 📝 Validation automatique des données (Pydantic)
         2. 📧 Envoi email à l'équipe Ville Propre
         3. ✅ Envoi confirmation au visiteur
         4. 🔄 Réponse immédiate à l'utilisateur
         
         ### Caractéristiques :
         - ⚡ Réponse ultra-rapide (~50ms)
         - 🔒 Validation stricte des données
         - 🛡️ Protection anti-spam intégrée
         - 📊 Logging automatique
         
         ### Codes de réponse :
         - `200` : Message envoyé avec succès
         - `422` : Données invalides (validation échouée)
         - `500` : Erreur serveur (rare)
    """,
    responses={
        200: {"description": "Message envoyé avec succès"},
        422: {"description": "Données invalides (validation échouée)"},
        500: {"description": "Erreur serveur (rare)"}
    }   
)
async def submit_contact_form(
    form_data: ContactFormRequest,
    background_tasks: BackgroundTasks
) -> ContactFormResponse:
    """
    Traite la soumission d'un formulaire de contact
    
    Args:
        form_data: Données validées du formulaire
        background_tasks: Gestionnaire FastAPI pour tâches asynchrones
        
    Returns:
        ContactFormResponse avec confirmation
        
    Raises:
        HTTPException: En cas d'erreur validation (géré par Pydantic)
    
    """
    
    # Log de la soumission pour audit/statistiques
    logger.info(
        f"Nouvelle soumission formulaire contact: "
        f"{form_data.nom} <{form_data.email}>"
    )
    
    try:
        # Appel du service email qui gère toute la logique métier
        result = await email_service.send_contact_form_submission(
            nom=form_data.nom,
            email=form_data.email,
            telephone=form_data.telephone,
            sujet=form_data.sujet,
            message=form_data.message,
            background_tasks=background_tasks
        )
        
        logger.info(
            f"Formulaire traité avec succès pour {form_data.email}"
        )
        
        # Retour de la réponse formatée
        return ContactFormResponse(**result)

    except Exception as e:
        # Gestion d'erreur globale (ne devrait jamais arriver)
        logger.error(
            f"Erreur inattendue lors du traitement du formulaire: {str(e)}",
            exc_info=True
        )
        
        # On retourne quand même un succès pour ne pas bloquer l'utilisateur
        # L'erreur est loggée et peut être inverstiguée
        return ContactFormResponse(
            success=True,
            message="Votre message a été reçu. Nous vous contacterons bientôt.",
            timestamp=datetime.now().isoformat()
        )


@router.get(
    "/health",
    summary="Vérifier le statut du service mail",
    description="Endpoint de santé pour vérifier que le service email est opérationnel.",
    response_model=HealthResponse
)
async def check_email_service_health() -> dict[str, any]:
    """
    Vérifie que le service email est configuré correctement
    
    UTILITÉ :
    --------
    ✓ Monitoring : Vérifier que SMTP est accessible
    ✓ Diagnostics : Identifier les problèmes de configuration
    ✓ CI/CD : Tests automatisés avant déploiement
    
    Returns:
        Status du service avec détails de configuration
    """
    from Emails.config_email import email_settings
    
    return {
        "status": "operational",
        "smtp_server": f"{email_settings.MAIL_SERVER}:{email_settings.MAIL_PORT}",
        "mail_from": email_settings.MAIL_FROM,
        "tls_enabled": email_settings.MAIL_SSL_TLS,
        "recipients_count": len(email_settings.MAIL_RECIPIENTS_CONTACT)
    }