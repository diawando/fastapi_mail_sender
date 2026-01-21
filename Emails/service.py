"""Service d'envoi d'emails
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi import BackgroundTasks
from typing import List, Dict, Any
from Emails.config_email import email_settings
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from pathlib import Path
import logging


# Configuration du logger pour tracer les emails envoyés
logger = logging.getLogger(__name__)


# === CONFIGURATION JINJA2 ===


# Créer l'environnement Jinja2 pour le rendu des templates
jinja_env = Environment(
    # FileSystemLoader : charge les templates depuis le système de fichiers
    loader=FileSystemLoader(email_settings.MAIL_TEMPLATES_DIR),
    
    # Autoescape : protège automatiquement contre les injections XSS
    # en échappant les caractères HTML dangereux
    autoescape=select_autoescape(['html', 'xml']),
    
    # Trim blocks : retire les espaces inutiles dans les blocs Jinja
    trim_blocks=True,
    
    # Lstrip blocks : retire les espaces au début des lignes
    lstrip_blocks=True
)


# === CONFIGURATION CONNEXION SMTP ===
# Cette configuration est créée une fois au démarrage de l'application
mail_config = ConnectionConfig(
    MAIL_USERNAME=email_settings.MAIL_USERNAME,
    MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
    MAIL_FROM=email_settings.MAIL_FROM,
    MAIL_PORT=email_settings.MAIL_PORT,
    MAIL_SERVER=email_settings.MAIL_SERVER,
    MAIL_STARTTLS=email_settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=email_settings.USE_CREDENTIALS,
    VALIDATE_CERTS=email_settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=email_settings.MAIL_TEMPLATES_DIR
)


class EmailService:
    """
        Service centralisé pour l'envoi d'emails
        
        PATTERN UTILISE : Service Layer Pattern
        ---------------------------------------
        Sépare la logique métier (envoi email) de la logique de présentation
    """
    def __init__(self):
        """
        Initialise le service avec la configuration SMTP
        
        FastMail est un client qui gère :
        - La connexion au serveur SMTP
        - Le formatage des emails
        - La gestion des erreurs de connexion
        """
        self.fast_mail = FastMail(mail_config)
        
    async def send_contact_form_submission(
        self,
        nom: str,
        email: str,
        telephone: str,
        sujet: str,
        message: str,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """
        Envoie un email de soumission de formulaire de contact
        à l'équipe interne
        
        Utilise les templates HTML pour formater l'email
        
        WORKFLOW :
        ----------
        1. Prépare les données pour les templates
        2. Génère les emails HTML à partir des templates Jinja2
        3. Envoie les deux emails en arrière-plan
        4. Retourne un statut de succès
        
        Args:
            nom (str): Nom du contact
            email (str): Email du contact
            telephone (str): Téléphone du contact
            sujet (str): Sujet du message
            message (str): Contenu du message
            background_tasks (BackgroundTasks): Tâches en arrière-plan de FastAPI
            
        Returns:
            Dict avec status et message de confirmation
        """
        
        # Date/heure actuelle formatée
        date_reception = datetime.now().strftime("%d/%m/%Y à %H:%M")
        
        # === PREPARATION DES DONNEES POUR LES TEMPLATES ===
        # Ces variables seront disponibles dans les templates Jinja2
        template_data = {
            'nom': nom,
            'email': email,
            'telephone': telephone,
            'sujet': sujet,
            'message': message,
            'date_reception': date_reception
        }
        
        # === EMAIL POUR l'EQUIPE (Notification interne) ===
        internal_email_body = self._render_template(
            'notification_interne.html',
            template_data
        )
        
        internal_message = MessageSchema(
            subject=f"Nouveau message: {sujet}",
            recipients=email_settings.MAIL_RECIPIENTS_CONTACT,
            body=internal_email_body,
            subtype=MessageType.html
        )
        
        # === EMAIL POUR LE VISITEUR (Confirmation) === 
        visitor_email_body = self._render_template(
            'confirmation_visiteur.html',
            template_data
        )
        
        visitor_message = MessageSchema(
            subject=" Votre message a bien été reçu - Ville Propre",
            recipients=[email],
            body=visitor_email_body,
            subtype=MessageType.html
        )

        # === ENVOI ASYNCHRONE EN ARRIÈRE-PLAN ===
        # Les emails sont ajoutés à une queue de tâches en arrière-plan
        background_tasks.add_task(
            self._send_email_with_logging,
            internal_message,
            "notification interne"
        )
        
        background_tasks.add_task(
            self._send_email_with_logging,
            visitor_message,
            "confirmation visiteur"
        )
        
        logger.info(
            f"Emails programmés pour envoi - Contact: {nom} <{email}>"
        )
        
        return {
            "success": True,
            "message": "Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    
    def _render_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Génère le HTML à partir d'un template Jinja2
        
        C'est la méthode clé qui remplace les anciennes méthodes
        _format_internal_notification et _format_visitor_confirmation
        
        FONCTIONNEMENT :
        ---------------
        1. Charge le template depuis Email/templates/
        2. Injecte les variables du contexte dans le template
        3. Retourne le HTML final généré
        
        Args:
            template_name: Nom du fichier template (ex: "notification_interne.html")
            context: Dictionnaire de variables à passer au template
            
        Returns:
            HTML généré à partir du template
        """
        try: 
            # Charger le template
            template = jinja_env.get_template(template_name)
            
            # Générer le HTML en injectant les variables
            html = template.render(**context)
            
            logger.debug(f"Template '{template_name}' rendu avec succès.")
            
            return html
        
        except Exception as e:
            logger.error(
                f"Erreur lors du rendu du template '{template_name}': {str(e)}",
                exc_info=True
            )
            
            # En cas d'erreur, retourner un HTML minimal de secours
            return self._fallback_html(context)
    
    def _fallback_html(self, context: Dict[str, Any]) -> str:
        """
        HTML de secours en cas d'erreur de rendu du template
        
        POURQUOI UN FALLBACK ?
        ---------------------
        Si le template Jinja2 a une erreur (syntaxe, fichier manquant, etc.),
        on ne veut pas que l'email échoue complètement. On envoie donc
        un HTML minimal mais fonctionnel.
        
        Args:
            context: Données à afficher
            
        Returns:
            HTML simple avec les données de base
        """
        return f""" 
                <!DOCTYPE html>
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Nouveau Message de Contact</h2>
                    <p><strong>Nom :</strong> {context.get('nom', 'N/A')}</p>
                    <p><strong>Email :</strong> {context.get('email', 'N/A')}</p>
                    <p><strong>Téléphone :</strong> {context.get('telephone', 'N/A')}</p>
                    <p><strong>Sujet :</strong> {context.get('sujet', 'N/A')}</p>
                    <p><strong>Message :</strong></p>
                    <pre>{context.get('message', 'N/A')}</pre>
                </body>
                </html>
            """
        
    async def _send_email_with_logging(
        self,
        message: MessageSchema,
        email_type: str
    ):
        """
        Envoie un email avec d'erreurs et logging
        
        Args:
            message: Le message à envoyer
            email_type: Type d'email pour les logs ("notification interne", etc.)
        """
        try: 
            await self.fast_mail.send_message(message)
            logger.info(f"Email envoyé avec succès: {email_type}")
            
        except Exception as e:
            # Ne pas faire échouer l'application pour une erreur email
            # Juste logguer l'erreur pour investigation
            logger.error(f"Erreur envoi email ({email_type}): {str(e)}",
                         exc_info=True)


# === INSTANCE SINGLETON ===
email_service = EmailService()

    
    