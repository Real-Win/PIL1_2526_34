from app import db, bcrypt
from app.models import User
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import traceback

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


def envoyer_email_smtp(destinataire, sujet, contenu_html):
    """Envoie un email via SMTP Brevo avec logs détaillés"""
    try:
        print("📧 [1/6] Début de l'envoi d'email...")
        
        smtp_user = os.environ.get("BREVO_SMTP_USER")
        smtp_password = os.environ.get("BREVO_SMTP_PASSWORD")
        EMAIL_EXPEDITEUR = os.environ.get("BREVO_SMTP_USER")  # Utilise l'email SMTP comme expéditeur
        
        print(f"📧 [2/6] SMTP User configuré: {smtp_user is not None}")
        print(f"📧 [3/6] SMTP Password configuré: {smtp_password is not None}")
        
        if not smtp_user or not smtp_password:
            print("❌ [ERREUR] Identifiants SMTP non configurés")
            return False
        
        smtp_server = "smtp-relay.brevo.com"
        smtp_port = 587
        
        print(f"📧 [4/6] Connexion à {smtp_server}:{smtp_port}...")
        
        msg = MIMEMultipart()
        msg["From"] = EMAIL_EXPEDITEUR
        msg["To"] = destinataire
        msg["Subject"] = sujet
        msg.attach(MIMEText(contenu_html, "html"))
        
        # Connexion et envoi
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(True)  # Affiche toute la communication SMTP
        server.starttls()
        print(f"📧 [5/6] Tentative de login...")
        server.login(smtp_user, smtp_password)
        print(f"📧 [6/6] Login réussi, envoi du message...")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email envoyé à {destinataire}")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR DETAILLEE: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def demander_reinitialisation(email):
    try:
        print(f"🔐 Demande de réinitialisation pour: {email}")
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return False, "Aucun compte associé à cet email."
        
        print(f"🔐 Utilisateur trouvé: {user.prenom} {user.nom}")
        
        token = secrets.token_urlsafe(32)
        reset_tokens[token] = {
            "user_id": user.id, 
            "expiration": datetime.utcnow() + timedelta(hours=24)
        }
        
        site_url = os.environ.get("SITE_URL", "http://localhost:5000")
        lien_reset = f"{site_url}/reinitialisation/{token}"
        
        print(f"🔐 Lien généré: {lien_reset}")
        
        contenu_html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #1e3a5f; color: white; padding: 20px; text-align: center;">
                    <h1>MentorLink</h1>
                    <p>Réinitialisation de votre mot de passe</p>
                </div>
                <div style="padding: 20px;">
                    <p>Bonjour <strong>{user.prenom} {user.nom}</strong>,</p>
                    <p>Cliquez sur le lien ci-dessous :</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{lien_reset}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px;">Réinitialiser</a>
                    </div>
                    <p><a href="{lien_reset}">{lien_reset}</a></p>
                    <p>Ce lien expire dans 24 heures.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        print(f"🔐 Envoi de l'email...")
        resultat = envoyer_email_smtp(email, "Réinitialisation de votre mot de passe", contenu_html)
        
        if resultat:
            print(f"✅ Email envoyé avec succès à {email}")
            return True, "Un email de réinitialisation a été envoyé à votre adresse."
        else:
            print(f"❌ Échec de l'envoi d'email")
            return False, "Erreur lors de l'envoi de l'email. Veuillez réessayer."
            
    except Exception as e:
        print(f"❌ Exception dans demander_reinitialisation: {e}")
        traceback.print_exc()
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