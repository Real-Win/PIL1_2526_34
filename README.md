# Rising Minds — MentorLink

## 🌐 Application en ligne

👉 **[https://rising-minds-mentorlink.onrender.com](https://rising-minds-mentorlink.onrender.com)**

---

## 📌 Présentation du projet

Rising Minds MentorLink est une application web de mise en relation entre étudiants de l'IFRI (Université d'Abomey-Calavi) dans un contexte de mentorat académique et professionnel.

Chaque utilisateur peut créer un profil (compétences, filière, disponibilités), publier ou rechercher des offres de mentorat, et être automatiquement mis en relation avec d'autres utilisateurs grâce à un système de matching intelligent.

---

## 🎯 Objectifs du projet

Ce projet vise à :

- Mettre en pratique les notions de :
  - Algorithmique
  - Développement web
  - Base de données (SQL / algèbre relationnelle)
  - Programmation Python
- Développer une application web complète (client-serveur)
- Travailler en équipe avec Git et outils collaboratifs
- Concevoir une solution réelle à un problème académique

---

## ⚙️ Fonctionnalités principales

### 1. Gestion des utilisateurs
- Inscription / connexion
- Gestion de profil (filière, compétences, disponibilité)
- Modification des informations personnelles

### 2. Système de mentorat (matching)
- Recherche de mentors **et** de mentorés (matching bidirectionnel)
- Algorithme de compatibilité basé sur :
  - Compétences communes
  - Filière
  - Disponibilités
- Suggestions automatiques des 3 meilleurs profils compatibles
- Envoi de demandes de mentorat avec sujet
- Acceptation / refus des demandes reçues

### 3. Messagerie temps réel
- Chat instantané entre utilisateurs (Flask-SocketIO)
- Indicateur "en train d'écrire"
- Historique des conversations

---

## 🏗️ Architecture du projet

- **Frontend** : HTML / CSS / JavaScript (Tailwind CSS + Vue.js)
- **Backend** : Python — Flask
- **Temps réel** : Flask-SocketIO
- **Base de données** : MySQL (PostgreSQL sur Render)
- **Déploiement** : Render
- **Versioning** : Git + GitHub

---

## 📁 Structure du projet

```
IFRI_MentorLink/
│
├── app/
│   ├── __init__.py
│   ├── models.py             # Modèles SQLAlchemy
│   ├── routes.py             # Routes auth + matching + demandes
│   ├── routes_messagerie.py  # Routes messagerie + SocketIO
│   ├── matching.py           # Algorithme de matching
│   ├── securite.py           # Inscription / connexion
│   ├── static/               # CSS, JS, images
│   └── templates/            # HTML Jinja2
│
├── config.py                 # Configuration de l'application
├── run.py                    # Point d'entrée du serveur
├── requirements.txt          # Dépendances Python
├── runtime.txt               # Version Python pour Render
├── .gitignore
└── README.md
```

---

## 🚀 Installation et exécution en local

### 1. Cloner le projet

```bash
git clone https://github.com/Real-Win/PIL1_2526_34.git
cd PIL1_2526_34
```

### 2. Activer l'environnement virtuel

```bash
# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer l'application

```bash
python run.py
```

---

## 👥 Équipe — Groupe 34 : RISING MINDS

| Nom | Filière | Rôle |
|-----|---------|------|
| God Win FADONOUGBO | Intelligence Artificielle | Chef de groupe + Algorithme de matching |
| MONNOUKOUN Hironde | Génie Logiciel | Backend Flask / Routes |
| NOUGBOGNONHOUN Mariel | Sécurité Informatique | Auth / Sécurité / Base de données |
| BOUKOH Jean-Marc | Internet et Multimédia | Frontend |
| SALIOU Samuel Exaucé | Systèmes Embarqués & IoT | Messagerie temps réel |

---

*Projet académique IFRI — 2025-2026 — Université d'Abomey-Calavi*
