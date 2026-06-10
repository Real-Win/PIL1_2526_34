from app import db, bcrypt
from app.models import User

def inscrire_etudiant(nom, prenom, email, telephone, filiere, niveau, role, mot_de_passe):
    try:
        existing = User.query.filter(
            (User.email == email) | (User.telephone == telephone)
        ).first()
        if existing:
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
        return None, "Mot de passe incorrect."
    except Exception as e:
        return None, f"Erreur connexion : {e}"