from app import db, bcrypt
from app.models import User
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os

# Stockage temporaire des tokens de réinitialisation
reset_tokens = {}


# =========================
# INSCRIPTION UTILISATEUR
# =========================
def inscrire_etudiant(nom, prenom, email, telephone, filiere, niveau, role, mot_de_passe):

    try:
        # Vérifier si user existe déjà
        existing_user = User.query.filter(
            (User.email == email) | (User.telephone == telephone)
        ).first()

        if existing_user:
            return False, "Email ou téléphone déjà utilisé."

        # Hash du mot de passe
        password_hash = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

        # Création user
        user = User(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            filiere=filiere,
            niveau=niveau,
            role=role,
            password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()

        return True, "Inscription réussie !"

    except Exception as e:
        db.session.rollback()
        return False, f"Erreur inscription : {e}"


# =========================
# CONNEXION UTILISATEUR
# =========================
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


# =========================
# ENVOI D'EMAIL VIA SMTP BREVO
# =========================
def envoyer_email_smtp(destinataire, sujet, contenu_html):
    """Envoie un email via SMTP Brevo"""
    try:
        # Paramètres SMTP Brevo (ceux que tu as vus dans ton compte)
        smtp_server = "smtp-relay.brevo.com"
        smtp_port = 587
        smtp_user = "ae3c1a001@smtp-brevo.com"
        smtp_password = "hgWEKV0O6j8Yp2ZC"
        
        # Création du message
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = destinataire
        msg["Subject"] = sujet
        msg.attach(MIMEText(contenu_html, "html"))
        
        # Connexion et envoi
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Email envoyé à {destinataire}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        return False


# =========================
# DEMANDE DE RÉINITIALISATION
# =========================
def demander_reinitialisation(email):
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            return False, "Aucun compte associé à cet email."
        
        # Générer un token unique
        token = secrets.token_urlsafe(32)
        reset_tokens[token] = {
            "user_id": user.id, 
            "expiration": datetime.utcnow() + timedelta(hours=24)
        }
        
        # Récupère l'URL du site (depuis Render ou local)
        site_url = os.environ.get("SITE_URL", "http://localhost:5000")
        lien_reset = f"{site_url}/reinitialisation/{token}"
        
        # Contenu HTML de l'email
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
                    
                    <p>Vous avez demandé à réinitialiser votre mot de passe sur MentorLink.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{lien_reset}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block;">
                            🔑 Réinitialiser mon mot de passe
                        </a>
                    </div>
                    
                    <p>Ou copiez ce lien dans votre navigateur :</p>
                    <p style="background-color: #f0f4f8; padding: 10px; word-break: break-all;">
                        <a href="{lien_reset}" style="color: #2563eb;">{lien_reset}</a>
                    </p>
                    
                    <p><strong>⚠️ Ce lien expire dans 24 heures.</strong></p>
                    
                    <p>Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.</p>
                    
                    <hr style="margin: 20px 0;">
                    
                    <p style="font-size: 12px; color: #666;">Cordialement,<br>
                    <strong>L'équipe MentorLink</strong><br>
                    IFRI - Université d'Abomey-Calavi</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Envoi de l'email
        if envoyer_email_smtp(email, "🔐 Réinitialisation de votre mot de passe - MentorLink", contenu_html):
            return True, "Un email de réinitialisation a été envoyé à votre adresse."
        else:
            return False, "Erreur lors de l'envoi de l'email. Veuillez réessayer."
            
    except Exception as e:
        return False, f"Erreur: {e}"


# =========================
# RÉINITIALISATION MOT DE PASSE
# =========================
def reinitialiser_mot_de_passe(token, nouveau_mot_de_passe):
    try:
        token_data = reset_tokens.get(token)
        
        if not token_data:
            return False, "Lien invalide ou expiré."
        
        if datetime.utcnow() > token_data["expiration"]:
            del reset_tokens[token]
            return False, "Le lien de réinitialisation a expiré."
        
        user = User.query.get(token_data["user_id"])
        if not user:
            return False, "Utilisateur introuvable."
        
        # Mettre à jour le mot de passe
        user.password_hash = bcrypt.generate_password_hash(nouveau_mot_de_passe).decode('utf-8')
        db.session.commit()
        
        # Supprimer le token utilisé
        del reset_tokens[token]
        
        return True, "Mot de passe réinitialisé avec succès !"
        
    except Exception as e:
        return False, f"Erreur: {e}"