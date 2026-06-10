from app import db, bcrypt
from app.models import User
import secrets
import requests
from datetime import datetime, timedelta
import os
import json

reset_tokens = {}


def inscrire_etudiant(nom, prenom, email, telephone, filiere, niveau, role, mot_de_passe):
    try:
        existing_user = User.query.filter(
            (User.email == email) | (User.telephone == telephone)
        ).first()
        if existing_user:
            return False, "Email ou téléphone déjà utilisé."
        password_hash = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')
        user = User(
            nom=nom, prenom=prenom, email=email, telephone=telephone,
            filiere=filiere, niveau=niveau, role=role, password_hash=password_hash
        )
        db.session.add(user)
        db.session.commit()
        return True, "Inscription réussie !"
    except Exception as e:
        db.session.rollback()
        return False, f"Erreur inscription : {e}"


def verifier_connexion(email, mot_de_passe_saisi):
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            return None, "Aucun utilisateur trouvé avec cet email."
        if bcrypt.check_password_hash(user.password_hash, mot_de_passe_saisi):
            return user, "Connexion réussie !"
        else:
            return None, "Mot de passe incorrect."
    except Exception as e:
        return None, f"Erreur connexion : {e}"


def envoyer_email_brevo_api(destinataire, sujet, contenu_html):
    """Envoie un email via l'API Brevo (port 443 - toujours ouvert)"""
    try:
        api_key = os.environ.get("BREVO_SMTP_PASSWORD")  # La clé API Brevo
        
        if not api_key:
            print("❌ Clé API Brevo non configurée")
            return False
        
        url = "https://api.brevo.com/v3/smtp/email"
        
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        
        data = {
            "sender": {
                "name": "MentorLink",
                "email": "ae3c1a001@smtp-brevo.com"  # Email expéditeur
            },
            "to": [
                {
                    "email": destinataire,
                    "name": destinataire
                }
            ],
            "subject": sujet,
            "htmlContent": contenu_html
        }
        
        print(f"📧 Envoi via API à {destinataire}...")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 201:
            print(f"✅ Email envoyé à {destinataire}")
            return True
        else:
            print(f"❌ API erreur: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False


def demander_reinitialisation(email):
    try:
        print(f"🔐 Demande de réinitialisation pour: {email}")
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return False, "Aucun compte associé à cet email."
        
        token = secrets.token_urlsafe(32)
        reset_tokens[token] = {
            "user_id": user.id, 
            "expiration": datetime.utcnow() + timedelta(hours=24)
        }
        
        site_url = os.environ.get("SITE_URL", "http://localhost:5000")
        lien_reset = f"{site_url}/reinitialisation/{token}"
        
        contenu_html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f0f4f8;">
                <div style="background-color: #1e3a5f; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0;">🔐 MentorLink</h1>
                    <p style="margin: 5px 0 0;">IFRI - Université d'Abomey-Calavi</p>
                </div>
                <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px;">
                    <p>Bonjour <strong>{user.prenom} {user.nom}</strong>,</p>
                    
                    <p>Vous avez demandé à réinitialiser votre mot de passe.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{lien_reset}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block;">
                            🔑 Réinitialiser mon mot de passe
                        </a>
                    </div>
                    
                    <p>Ou copiez ce lien : <a href="{lien_reset}">{lien_reset}</a></p>
                    
                    <p><strong>⚠️ Ce lien expire dans 24 heures.</strong></p>
                    
                    <hr style="margin: 20px 0;">
                    
                    <p style="font-size: 12px; color: #666;">L'équipe MentorLink - IFRI</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        resultat = envoyer_email_brevo_api(email, "🔐 Réinitialisation de votre mot de passe", contenu_html)
        
        if resultat:
            return True, "Un email de réinitialisation a été envoyé (vérifiez vos spams)."
        else:
            return False, "Erreur lors de l'envoi de l'email. Veuillez réessayer."
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, f"Erreur: {e}"


def reinitialiser_mot_de_passe(token, nouveau_mot_de_passe):
    try:
        token_data = reset_tokens.get(token)
        if not token_data:
            return False, "Lien invalide ou expiré."
        if datetime.utcnow() > token_data["expiration"]:
            del reset_tokens[token]
            return False, "Le lien a expiré."
        user = User.query.get(token_data["user_id"])
        if not user:
            return False, "Utilisateur introuvable."
        user.password_hash = bcrypt.generate_password_hash(nouveau_mot_de_passe).decode('utf-8')
        db.session.commit()
        del reset_tokens[token]
        return True, "Mot de passe réinitialisé avec succès !"
    except Exception as e:
        return False, f"Erreur: {e}"