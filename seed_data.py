"""
seed_data.py — Script d'insertion de 21 profils de démonstration
Placer ce fichier à la RACINE du projet (même niveau que run.py)
Exécuter : python seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db, bcrypt
from app.models import (User, Competence, UserCompetence,
                        Lacune, UserLacune, Disponibilite)
from datetime import time

app = create_app()

# ─────────────────────────────────────────────
#  DONNÉES DES 21 PROFILS
# ─────────────────────────────────────────────
profils = [

  # ── MENTORS ─────────────────────────────────
  {
    "nom": "KOSSOU", "prenom": "Arnaud",
    "email": "arnaud.kossou@ifri.uac.bj", "telephone": "22997110001",
    "filiere": "IA", "niveau": "M2", "role": "mentor",
    "mot_de_passe": "ifri2026",
    "bio": "Passionné par le Machine Learning et la vision par ordinateur. J'ai travaillé sur plusieurs projets de classification d'images.",
    "competences": ["machine learning", "python", "tensorflow", "opencv", "sql"],
    "lacunes": [],
    "dispos": [("Lundi", "08:00", "12:00"), ("Mercredi", "14:00", "18:00")]
  },
  {
    "nom": "AGOSSOU", "prenom": "Mariette",
    "email": "mariette.agossou@ifri.uac.bj", "telephone": "22997110002",
    "filiere": "GL", "niveau": "M2", "role": "mentor",
    "mot_de_passe": "ifri2026",
    "bio": "Développeuse fullstack avec 3 ans d'expérience. Spécialisée en React et Django.",
    "competences": ["react", "django", "javascript", "git", "docker"],
    "lacunes": [],
    "dispos": [("Mardi", "10:00", "14:00"), ("Jeudi", "16:00", "19:00")]
  },
  {
    "nom": "HOUNTON", "prenom": "Florent",
    "email": "florent.hounton@ifri.uac.bj", "telephone": "22997110003",
    "filiere": "SI", "niveau": "M1", "role": "mentor",
    "mot_de_passe": "ifri2026",
    "bio": "Expert en cybersécurité offensive et défensive. CTF player actif.",
    "competences": ["cybersécurité", "linux", "python", "réseaux", "cryptographie"],
    "lacunes": [],
    "dispos": [("Vendredi", "09:00", "13:00"), ("Samedi", "10:00", "14:00")]
  },
  {
    "nom": "DOSSOU", "prenom": "Brice",
    "email": "brice.dossou@ifri.uac.bj", "telephone": "22997110004",
    "filiere": "SEIOT", "niveau": "M2", "role": "mentor",
    "mot_de_passe": "ifri2026",
    "bio": "Ingénieur embarqué. Je travaille sur des projets Arduino et Raspberry Pi depuis 4 ans.",
    "competences": ["arduino", "raspberry pi", "c", "python", "mqtt"],
    "lacunes": [],
    "dispos": [("Lundi", "14:00", "18:00"), ("Mercredi", "08:00", "12:00")]
  },
  {
    "nom": "ADANDE", "prenom": "Cynthia",
    "email": "cynthia.adande@ifri.uac.bj", "telephone": "22997110005",
    "filiere": "IM", "niveau": "M1", "role": "mentor",
    "mot_de_passe": "ifri2026",
    "bio": "Designeuse UI/UX et développeuse front. Passionnée par l'expérience utilisateur.",
    "competences": ["figma", "html", "css", "javascript", "wordpress"],
    "lacunes": [],
    "dispos": [("Jeudi", "09:00", "13:00"), ("Vendredi", "14:00", "17:00")]
  },
  {
    "nom": "GBESSI", "prenom": "Wilfried",
    "email": "wilfried.gbessi@ifri.uac.bj", "telephone": "22997110006",
    "filiere": "IA", "niveau": "M1", "role": "mentor",
    "mot_de_passe": "ifri2026",
    "bio": "Spécialiste NLP et traitement du langage naturel. Je fais de la recherche sur les LLMs.",
    "competences": ["nlp", "python", "transformers", "pytorch", "sql"],
    "lacunes": [],
    "dispos": [("Mardi", "08:00", "12:00"), ("Samedi", "14:00", "18:00")]
  },
  {
    "nom": "SOGLO", "prenom": "Elodie",
    "email": "elodie.soglo@ifri.uac.bj", "telephone": "22997110007",
    "filiere": "GL", "niveau": "M1", "role": "mentor",
    "mot_de_passe": "ifri2026",
    "bio": "Développeuse mobile Flutter et React Native. J'ai publié 2 apps sur le Play Store.",
    "competences": ["flutter", "dart", "react native", "firebase", "git"],
    "lacunes": [],
    "dispos": [("Lundi", "10:00", "14:00"), ("Jeudi", "08:00", "12:00")]
  },

  # ── MENTORÉS ────────────────────────────────
  {
    "nom": "AHOUNOU", "prenom": "Kévin",
    "email": "kevin.ahounou@ifri.uac.bj", "telephone": "22997110008",
    "filiere": "IA", "niveau": "L3", "role": "mentore",
    "mot_de_passe": "ifri2026",
    "bio": "Étudiant en L3 IA. J'ai du mal avec les réseaux de neurones et le calcul matriciel.",
    "competences": ["python", "sql"],
    "lacunes": ["machine learning", "tensorflow", "mathématiques"],
    "dispos": [("Lundi", "08:00", "12:00"), ("Mardi", "14:00", "17:00")]
  },
  {
    "nom": "BIOTCHO", "prenom": "Sandra",
    "email": "sandra.biotcho@ifri.uac.bj", "telephone": "22997110009",
    "filiere": "GL", "niveau": "L2", "role": "mentore",
    "mot_de_passe": "ifri2026",
    "bio": "Je débute en développement web et j'ai du mal avec JavaScript et les frameworks.",
    "competences": ["html", "css"],
    "lacunes": ["javascript", "react", "git"],
    "dispos": [("Mardi", "10:00", "14:00"), ("Mercredi", "16:00", "19:00")]
  },
  {
    "nom": "CAPO", "prenom": "Dimitri",
    "email": "dimitri.capo@ifri.uac.bj", "telephone": "22997110010",
    "filiere": "SI", "niveau": "L3", "role": "mentore",
    "mot_de_passe": "ifri2026",
    "bio": "Je veux me spécialiser en sécurité mais j'ai des lacunes en réseaux et Linux.",
    "competences": ["python", "algorithmique"],
    "lacunes": ["réseaux", "linux", "cryptographie"],
    "dispos": [("Vendredi", "09:00", "13:00"), ("Samedi", "10:00", "14:00")]
  },
  {
    "nom": "DANGNIVO", "prenom": "Précieux",
    "email": "precieux.dangnivo@ifri.uac.bj", "telephone": "22997110011",
    "filiere": "SEIOT", "niveau": "L3", "role": "mentore",
    "mot_de_passe": "ifri2026",
    "bio": "Je veux apprendre l'embarqué mais je pars de zéro sur Arduino et le C.",
    "competences": ["python"],
    "lacunes": ["arduino", "c", "raspberry pi"],
    "dispos": [("Lundi", "14:00", "18:00"), ("Jeudi", "09:00", "13:00")]
  },
  {
    "nom": "ELEGBE", "prenom": "Faustine",
    "email": "faustine.elegbe@ifri.uac.bj", "telephone": "22997110012",
    "filiere": "IM", "niveau": "L2", "role": "mentore",
    "mot_de_passe": "ifri2026",
    "bio": "Étudiante en L2 IM. Je veux apprendre le design UI et le CSS avancé.",
    "competences": ["html"],
    "lacunes": ["css", "figma", "javascript"],
    "dispos": [("Jeudi", "09:00", "13:00"), ("Vendredi", "14:00", "17:00")]
  },
  {
    "nom": "FAGNON", "prenom": "Rodrigue",
    "email": "rodrigue.fagnon@ifri.uac.bj", "telephone": "22997110013",
    "filiere": "IA", "niveau": "L2", "role": "mentore",
    "mot_de_passe": "ifri2026",
    "bio": "Passionné par l'IA mais j'ai du mal avec Python et les maths.",
    "competences": ["algorithmique"],
    "lacunes": ["python", "machine learning", "sql"],
    "dispos": [("Mardi", "08:00", "12:00"), ("Samedi", "10:00", "14:00")]
  },

  # ── LES DEUX (mentor ET mentoré) ─────────────
  {
    "nom": "GBAGUIDI", "prenom": "Jean",
    "email": "jean.gbaguidi@ifri.uac.bj", "telephone": "22997110014",
    "filiere": "GL", "niveau": "L3", "role": "les_deux",
    "mot_de_passe": "ifri2026",
    "bio": "Fort en algorithmique et Python, je cherche de l'aide en React. Je peux aider en algo.",
    "competences": ["python", "algorithmique", "sql"],
    "lacunes": ["react", "docker"],
    "dispos": [("Lundi", "08:00", "12:00"), ("Mercredi", "14:00", "18:00")]
  },
  {
    "nom": "HOUNKPATIN", "prenom": "Ines",
    "email": "ines.hounkpatin@ifri.uac.bj", "telephone": "22997110015",
    "filiere": "IA", "niveau": "L3", "role": "les_deux",
    "mot_de_passe": "ifri2026",
    "bio": "Je maîtrise le Python et SQL. Je cherche de l'aide sur TensorFlow et le Deep Learning.",
    "competences": ["python", "sql", "pandas"],
    "lacunes": ["tensorflow", "deep learning"],
    "dispos": [("Mardi", "14:00", "18:00"), ("Jeudi", "08:00", "12:00")]
  },
  {
    "nom": "IGBE", "prenom": "Cyrille",
    "email": "cyrille.igbe@ifri.uac.bj", "telephone": "22997110016",
    "filiere": "SI", "niveau": "L3", "role": "les_deux",
    "mot_de_passe": "ifri2026",
    "bio": "Je peux aider sur Linux et les réseaux basiques. J'ai besoin d'aide en cryptographie.",
    "competences": ["linux", "réseaux", "python"],
    "lacunes": ["cryptographie", "cybersécurité"],
    "dispos": [("Vendredi", "09:00", "13:00"), ("Samedi", "14:00", "18:00")]
  },
  {
    "nom": "JOHNSON", "prenom": "Axel",
    "email": "axel.johnson@ifri.uac.bj", "telephone": "22997110017",
    "filiere": "IM", "niveau": "L3", "role": "les_deux",
    "mot_de_passe": "ifri2026",
    "bio": "Bon en HTML/CSS/JS. Je cherche de l'aide sur les frameworks backend comme Django.",
    "competences": ["html", "css", "javascript"],
    "lacunes": ["django", "python", "sql"],
    "dispos": [("Lundi", "14:00", "18:00"), ("Mercredi", "10:00", "14:00")]
  },
  {
    "nom": "KEDE", "prenom": "Laeticia",
    "email": "laeticia.kede@ifri.uac.bj", "telephone": "22997110018",
    "filiere": "SEIOT", "niveau": "L3", "role": "les_deux",
    "mot_de_passe": "ifri2026",
    "bio": "Je maîtrise C et Arduino. Je cherche de l'aide sur MQTT et la communication IoT.",
    "competences": ["c", "arduino", "python"],
    "lacunes": ["mqtt", "raspberry pi"],
    "dispos": [("Mardi", "10:00", "14:00"), ("Vendredi", "14:00", "18:00")]
  },
  {
    "nom": "LOKOSSOU", "prenom": "Maxime",
    "email": "maxime.lokossou@ifri.uac.bj", "telephone": "22997110019",
    "filiere": "GL", "niveau": "M1", "role": "les_deux",
    "mot_de_passe": "ifri2026",
    "bio": "Expert Django et Python. Je cherche à m'améliorer sur Flutter et le mobile.",
    "competences": ["django", "python", "sql", "git"],
    "lacunes": ["flutter", "dart", "react native"],
    "dispos": [("Jeudi", "14:00", "18:00"), ("Samedi", "09:00", "13:00")]
  },
  {
    "nom": "MOUSSE", "prenom": "Déborah",
    "email": "deborah.mousse@ifri.uac.bj", "telephone": "22997110020",
    "filiere": "IA", "niveau": "M1", "role": "les_deux",
    "mot_de_passe": "ifri2026",
    "bio": "Je travaille sur des projets NLP. Je peux aider en Python/ML mais je cherche de l'aide en vision.",
    "competences": ["python", "nlp", "machine learning", "sql"],
    "lacunes": ["opencv", "vision par ordinateur"],
    "dispos": [("Lundi", "10:00", "14:00"), ("Mercredi", "08:00", "12:00")]
  },
  {
    "nom": "NAHUM", "prenom": "Théophile",
    "email": "theophile.nahum@ifri.uac.bj", "telephone": "22997110021",
    "filiere": "SI", "niveau": "M1", "role": "les_deux",
    "mot_de_passe": "ifri2026",
    "bio": "Bon en cryptographie et réseaux. Je cherche de l'aide sur les outils de pentest.",
    "competences": ["cryptographie", "réseaux", "python", "linux"],
    "lacunes": ["pentest", "cybersécurité offensive"],
    "dispos": [("Mardi", "09:00", "13:00"), ("Jeudi", "14:00", "18:00")]
  },
]


# ─────────────────────────────────────────────
#  INSERTION EN BASE
# ─────────────────────────────────────────────
def seed():
    with app.app_context():

        print("🗑️  Nettoyage des anciennes données de démo...")
        # Supprimer uniquement les users de démo (email @ifri.uac.bj)
        demo_users = User.query.filter(User.email.like('%@ifri.uac.bj')).all()
        for u in demo_users:
            db.session.delete(u)
        db.session.commit()

        print("👤 Insertion des 21 profils...\n")

        for p in profils:
            # Créer l'utilisateur
            password_hash = bcrypt.generate_password_hash(
                p["mot_de_passe"]
            ).decode('utf-8')

            user = User(
                nom=p["nom"], prenom=p["prenom"],
                email=p["email"], telephone=p["telephone"],
                filiere=p["filiere"], niveau=p["niveau"],
                role=p["role"], password_hash=password_hash,
                bio=p["bio"]
            )
            db.session.add(user)
            db.session.flush()  # pour avoir l'ID

            # Compétences
            for nom_comp in p["competences"]:
                comp = Competence.query.filter_by(nom=nom_comp).first()
                if not comp:
                    comp = Competence(nom=nom_comp)
                    db.session.add(comp)
                    db.session.flush()
                db.session.add(
                    UserCompetence(user_id=user.id, competence_id=comp.id)
                )

            # Lacunes
            for nom_lacune in p["lacunes"]:
                lacune = Lacune.query.filter_by(nom=nom_lacune).first()
                if not lacune:
                    lacune = Lacune(nom=nom_lacune)
                    db.session.add(lacune)
                    db.session.flush()
                db.session.add(
                    UserLacune(user_id=user.id, lacune_id=lacune.id)
                )

            # Disponibilités
            for jour, debut, fin in p["dispos"]:
                db.session.add(Disponibilite(
                    user_id=user.id,
                    jour_semaine=jour,
                    heure_debut=time(*map(int, debut.split(":"))),
                    heure_fin=time(*map(int, fin.split(":")))
                ))

            print(f"  ✅ {p['prenom']} {p['nom']} ({p['filiere']} {p['niveau']} — {p['role']})")

        db.session.commit()
        print("\n🎉 21 profils insérés avec succès !\n")

        # Afficher les identifiants
        print("=" * 60)
        print("  IDENTIFIANTS DE CONNEXION")
        print("=" * 60)
        print(f"  {'Nom':<20} {'Email':<35} {'MDP'}")
        print("-" * 60)
        for p in profils:
            nom_complet = f"{p['prenom']} {p['nom']}"
            print(f"  {nom_complet:<20} {p['email']:<35} {p['mot_de_passe']}")
        print("=" * 60)
        print("\n  Tous les mots de passe : ifri2026")
        print("=" * 60)


if __name__ == "__main__":
    seed()