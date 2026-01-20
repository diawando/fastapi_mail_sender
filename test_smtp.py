import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# Configuration for the SMTP server
SMTP_SERVER = os.getenv('MAIL_SERVER')
SMTP_PORT = 587
EMAIL = os.getenv('MAIL_USERNAME')
PASSWORD = os.getenv('MAIL_PASSWORD')

try: 
    # Connexion au serveur SMTP
    print("Connection au serveur SMTP Hostinger....")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    
    # Activation TLS
    print("Activation TLS....")
    server.starttls()
    
    # Authentification
    print("Authentification....")
    server.login(EMAIL, PASSWORD)
    
    print(" Connexion reussie à Hostinger SMTP Server")
    
    # Test d'envoi
    msg = MIMEText("Test depuis Python")
    msg['Subject'] = 'Test Hostinger SMTP'
    msg['From'] = EMAIL
    msg['To'] = "abduldiawade777@gmail.com"
    
    server.send_message(msg)
    print("Email de test envoyé avec succès!")
    
    server.quit()

except Exception as e:
    print(f"Erreur : {str(e)}")
    