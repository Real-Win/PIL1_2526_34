from app import db, bcrypt
from app.models import User
import secrets
import requests
from datetime import datetime, timedelta
import os

# Dictionnaire pour stocker les tokens de réinitialisation
reset_tokens = {}


def inscrire_etudiant(nom, prenom, email, telephone, filiere, niveau, role, mot_de_passe):
    """Inscrit un nouvel utilisateur"""
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter(
            (User.email == email) | (User.telephone == telephone)
        ).first()
        if existing_user:
            return False, "Email ou téléphone déjà utilisé."

        # Hacher le mot de passe
        password_hash = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

        # Créer l'utilisateur
        user = User(
            nom=nom, prenom=prenom, email=email, telephone=telephone,
            filiere=filiere, niveau=niveau, role=role, password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()
        return True, "Inscription réussie !"
    except Exception as e:
        db.session.rollback()
        return False, f"Erreur lors de l'inscription : {e}"


def verifier_connexion(email, mot_de_passe_saisi):
    """Vérifie les identifiants de connexion"""
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            return None, "Aucun utilisateur trouvé avec cet email."

        if bcrypt.check_password_hash(user.password_hash, mot_de_passe_saisi):
            return user, "Connexion réussie !"
        else:
            return None, "Mot de passe incorrect."
    except Exception as e:
        return None, f"Erreur lors de la connexion : {e}"


def envoyer_email_api(destinataire, sujet, contenu_html):
    """
    Envoie un email via l'API Brevo.
    C'est la méthode qui fonctionne le mieux sur Render.
    """
    try:
        # Ta clé API (stockée dans les variables d'environnement)
        api_key = os.environ.get("BREVO_SMTP_PASSWORD")
        if not api_key:
            print("❌ La clé API Brevo n'est pas configurée sur Render.")
            return False

        # Configuration de la requête pour l'API Brevo
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        
        # Contenu de l'email
        data = {
            "sender": {
                "name": "MentorLink",
                "email": "ae3c1a001@smtp-brevo.com"  # Email fourni par Brevo
            },
            "to": [{"email": destinataire, "name": destinataire}],
            "subject": sujet,
            "htmlContent": contenu_html
        }

        # Envoyer la requête à Brevo
        print(f"📧 Tentative d'envoi d'email à {destinataire}...")
        response = requests.post(url, json=data, headers=headers, timeout=30)

        # Vérifier si l'envoi a réussi
        if response.status_code == 201:
            print(f"✅ Email envoyé avec succès à {destinataire}")
            return True
        else:
            print(f"❌ L'API Brevo a retourné une erreur: {response.status_code}")
            print(f"   Détails: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ La requête à l'API Brevo a expiré.")
        return False
    except Exception as e:
        print(f"❌ Une erreur inattendue s'est produite : {e}")
        return False


def demander_reinitialisation(email):
    """
    Génère un token et envoie un email de réinitialisation à l'utilisateur.
    """
    print(f"🔐 Début de la demande de réinitialisation pour : {email}")
    try:
        # 1. Vérifier si l'email existe dans notre base de données
        user = User.query.filter_by(email=email).first()
        if not user:
            return False, "Aucun compte n'est associé à cette adresse email."

        # 2. Générer un token unique et sécurisé
        token = secrets.token_urlsafe(32)
        # On le stocke en mémoire avec une durée de vie de 24h
        reset_tokens[token] = {
            "user_id": user.id,
            "expiration": datetime.utcnow() + timedelta(hours=24)
        }

        # 3. Construire le lien de réinitialisation
        site_url = os.environ.get("SITE_URL", "https://rising-minds-mentorlink.onrender.com")
        lien_reset = f"{site_url}/reinitialisation/{token}"
        print(f"🔗 Lien de réinitialisation généré : {lien_reset}")

        # 4. Préparer le contenu HTML de l'email
        contenu_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: sans-serif;">
            <h1>Réinitialisation MentorLink</h1>
            <p>Bonjour {user.prenom} {user.nom},</p>
            <p>Vous avez demandé à réinitialiser votre mot de passe.</p>
            <p>
                <a href="{lien_reset}" style="background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Cliquez ici pour réinitialiser votre mot de passe
                </a>
            </p>
            <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :</p>
            <p>{lien_reset}</p>
            <p>Ce lien est valable 24 heures.</p>
            <p>Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.</p>
            <hr>
            <p>L'équipe MentorLink</p>
        </body>
        </html>
        """

        # 5. Envoyer l'email via l'API Brevo
        email_envoye = envoyer_email_api(email, "Réinitialisation de votre mot de passe MentorLink", contenu_html)

        if email_envoye:
            return True, "Un email de réinitialisation vient de vous être envoyé (pensez à vérifier vos spams)."
        else:
            return False, "L'email n'a pas pu être envoyé. Veuillez réessayer plus tard."

    except Exception as e:
        print(f"❌ Erreur inattendue dans la demande de réinitialisation : {e}")
        return False, "Une erreur interne est survenue. Veuillez réessayer."


def reinitialiser_mot_de_passe(token, nouveau_mot_de_passe):
    """Réinitialise le mot de passe si le token est valide"""
    try:
        # Vérifier si le token existe
        token_data = reset_tokens.get(token)
        if not token_data:
            return False, "Le lien est invalide ou a déjà été utilisé."

        # Vérifier si le token a expiré
        if datetime.utcnow() > token_data["expiration"]:
            # Supprimer le token expiré
            del reset_tokens[token]
            return False, "Ce lien a expiré. Veuillez refaire une demande."

        # Récupérer l'utilisateur correspondant
        user = User.query.get(token_data["user_id"])
        if not user:
            return False, "Utilisateur non trouvé."

        # Mettre à jour le mot de passe
        nouveau_hash = bcrypt.generate_password_hash(nouveau_mot_de_passe).decode('utf-8')
        user.password_hash = nouveau_hash
        db.session.commit()

        # Supprimer le token utilisé
        del reset_tokens[token]
        return True, "Votre mot de passe a été réinitialisé avec succès !"

    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation : {e}")
        return False, "Une erreur est survenue. Veuillez réessayer."