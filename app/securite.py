from app import db, bcrypt
from app.models import User, PasswordResetToken
import secrets
import requests
from datetime import datetime, timedelta
import os


def inscrire_etudiant(nom, prenom, email, telephone, filiere, niveau, role, mot_de_passe):
    try:
        existing = User.query.filter(
            (User.email == email) | (User.telephone == telephone)
        ).first()
        if existing:
            return False, "Email ou téléphone déjà utilisé."
        password_hash = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')
        user = User(nom=nom, prenom=prenom, email=email, telephone=telephone,
                    filiere=filiere, niveau=niveau, role=role, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return True, "Inscription réussie !"
    except Exception as e:
        db.session.rollback()
        return False, f"Erreur lors de l'inscription : {e}"


def verifier_connexion(email, mot_de_passe_saisi):
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            return None, "Aucun utilisateur trouvé avec cet email."
        if bcrypt.check_password_hash(user.password_hash, mot_de_passe_saisi):
            return user, "Connexion réussie !"
        return None, "Mot de passe incorrect."
    except Exception as e:
        return None, f"Erreur lors de la connexion : {e}"


def envoyer_email_api(destinataire, sujet, contenu_html):
    try:
        api_key = os.environ.get("BREVO_SMTP_PASSWORD")
        if not api_key:
            print("❌ Clé API Brevo manquante.")
            return False

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        data = {
            "sender": {"name": "MentorLink", "email": "ae3c1a001@smtp-brevo.com"},
            "to": [{"email": destinataire, "name": destinataire}],
            "subject": sujet,
            "htmlContent": contenu_html
        }
        print(f"📧 Envoi email à {destinataire}...")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        if response.status_code == 201:
            print(f"✅ Email envoyé à {destinataire}")
            return True
        print(f"❌ Brevo erreur {response.status_code}: {response.text}")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Brevo.")
        return False
    except Exception as e:
        print(f"❌ Erreur email: {e}")
        return False


def demander_reinitialisation(email):
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            # Message vague pour sécurité
            return True, "Si cet email est enregistré, un lien vous a été envoyé (vérifiez vos spams)."

        # Invalider les anciens tokens
        PasswordResetToken.query.filter_by(user_id=user.id, utilise=False).delete()
        db.session.flush()

        token = secrets.token_urlsafe(32)
        record = PasswordResetToken(
            token=token,
            user_id=user.id,
            expiration=datetime.utcnow() + timedelta(hours=24),
            utilise=False
        )
        db.session.add(record)
        db.session.commit()

        site_url = os.environ.get("SITE_URL", "https://rising-minds-mentorlink.onrender.com")
        lien = f"{site_url}/reinitialisation/{token}"

        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="font-family:sans-serif;background:#f8fafc;padding:40px 0;">
  <div style="max-width:520px;margin:auto;background:#fff;border-radius:16px;
              padding:40px;border:1px solid #e2e8f0;">
    <h2 style="color:#1e293b;margin:0 0 8px">Réinitialisation de mot de passe</h2>
    <p style="color:#64748b;margin:0 0 24px">Bonjour <strong>{user.prenom} {user.nom}</strong>,</p>
    <p style="color:#475569">Vous avez demandé à réinitialiser votre mot de passe MentorLink.</p>
    <div style="text-align:center;margin:32px 0">
      <a href="{lien}"
         style="background:#2563eb;color:#fff;padding:14px 32px;border-radius:10px;
                text-decoration:none;font-weight:600;font-size:15px;display:inline-block">
        Réinitialiser mon mot de passe
      </a>
    </div>
    <p style="color:#94a3b8;font-size:13px">Ou copiez ce lien :<br>
      <a href="{lien}" style="color:#2563eb;word-break:break-all">{lien}</a>
    </p>
    <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0">
    <p style="color:#94a3b8;font-size:12px">
      Ce lien est valable <strong>24 heures</strong>.<br>
      Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.
    </p>
    <p style="color:#94a3b8;font-size:12px;margin-bottom:0">L'équipe MentorLink — IFRI</p>
  </div>
</body></html>"""

        ok = envoyer_email_api(email, "Réinitialisation de votre mot de passe MentorLink", html)
        if ok:
            return True, "Un email de réinitialisation vous a été envoyé (pensez à vérifier vos spams)."
        return False, "L'email n'a pas pu être envoyé. Vérifiez la configuration Brevo."

    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur demande réinit: {e}")
        return False, "Erreur interne. Veuillez réessayer."


def reinitialiser_mot_de_passe(token, nouveau_mot_de_passe):
    try:
        record = PasswordResetToken.query.filter_by(token=token, utilise=False).first()
        if not record:
            return False, "Ce lien est invalide ou a déjà été utilisé."
        if datetime.utcnow() > record.expiration:
            db.session.delete(record)
            db.session.commit()
            return False, "Ce lien a expiré. Veuillez refaire une demande."
        user = User.query.get(record.user_id)
        if not user:
            return False, "Utilisateur introuvable."
        user.password_hash = bcrypt.generate_password_hash(nouveau_mot_de_passe).decode('utf-8')
        record.utilise = True
        db.session.commit()
        return True, "Mot de passe réinitialisé avec succès !"
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur réinit: {e}")
        return False, "Erreur lors de la réinitialisation."