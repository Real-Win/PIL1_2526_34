
# IFRI_MentorLink

## 📌 Présentation du projet

IFRI_MentorLink est une application web de mise en relation entre étudiants de l’IFRI (Université d’Abomey-Calavi) dans un contexte de mentorat académique et professionnel.

Chaque utilisateur peut créer un profil (compétences, filière, disponibilités), publier ou rechercher des offres de mentorat, et être automatiquement mis en relation avec d’autres utilisateurs grâce à un système de matching intelligent.

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
- Recherche de mentors / mentorés
- Algorithme de compatibilité basé sur :
  - Compétences
  - Filière
  - Disponibilités
- Suggestions automatiques de correspondance

### 3. Messagerie
- Chat entre utilisateurs
- Organisation des sessions de mentorat

---

## 🏗️ Architecture du projet

- Frontend : HTML / CSS / JavaScript  
- Backend : Python (Flask ou autre framework)  
- Base de données : MySQL / SQLite  
- Versioning : Git + GitHub  

---

## 📁 Structure du projet
```
IFRI_MentorLink/
│
├── __pycache__
├── app/                # Code principal backend
├── config.py           # Configuration de l’application
├── run.py              # Point d’entrée du serveur
├── requirements.txt    # Dépendances Python
├── venv/               # Environnement virtuel (non versionné)
├── .gitignore          # Fichiers ignorés par Git
└── README.md
```

---

## 🚀 Installation et exécution

### 1. Cloner le projet

``bash
git clone https://github.com/Real-Win/IFRI_MentorLink.git
cd IFRI_MentorLink

### 2. Activer l’environnement virtuel
source venv/Scripts/activate

### 3. Installer les dépendances
pip install -r requirements.txt

### 4. Lancer l’application
python run.py

### ✍️ Auteur

God Win FADONOUGBO — Responsable du groupe 34 : RISING MINDS
Projet académique IFRI - 2025-2026
Université d’Abomey-Calavi
