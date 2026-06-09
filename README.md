# IFRI_MentorLink

## 📌 Présentation du projet

IFRI_MentorLink est une application web de mise en relation entre étudiants de l'IFRI (Université d'Abomey-Calavi) dans un contexte de mentorat académique et professionnel.

L'application permet aux étudiants de créer un profil, de renseigner leurs compétences et disponibilités, puis d'être mis en relation grâce à un système de matching intelligent.

---

## 🎯 Objectifs du projet

Ce projet vise à :

* Mettre en pratique les notions de :

  * Développement Web
  * Base de Données
  * Génie Logiciel
  * Sécurité Informatique
  * Intelligence Artificielle
  * Programmation Python
* Développer une application web complète client-serveur
* Travailler en équipe avec Git et GitHub
* Répondre à un besoin réel des étudiants de l'IFRI

---

## ⚙️ Fonctionnalités principales

### 👤 Gestion des utilisateurs

* Inscription sécurisée
* Connexion sécurisée
* Gestion du profil utilisateur
* Modification des informations personnelles

### 🧠 Système de Matching

* Recherche de mentors et mentorés
* Calcul automatique de compatibilité
* Prise en compte :

  * des compétences
  * de la filière
  * des disponibilités
* Suggestions automatiques de mentors

### 💬 Messagerie

* Communication entre mentor et mentoré
* Historique des échanges
* Organisation des sessions de mentorat

---

## 🏗️ Technologies utilisées

### Backend

* Python 3
* Flask
* SQLAlchemy
* Flask-Login
* Flask-Bcrypt

### Frontend

* HTML5
* Tailwind CSS
* JavaScript

### Base de données

* SQLite

### Versioning

* Git
* GitHub

---

## 📁 Structure du projet

```text
IFRI_MentorLink/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── matching.py
│   ├── securite.py
│   ├── templates/
│   └── static/
│
├── config.py
├── run.py
├── requirements.txt
├── README.md
└── mentorlink.db
```

---

## 🚀 Installation et exécution

### 1. Cloner le projet

```bash
git clone https://github.com/Real-Win/IFRI_MentorLink.git
cd IFRI_MentorLink
```

### 2. Créer un environnement virtuel

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / Mac

```bash
python3 -m venv venv
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

### 5. Ouvrir dans le navigateur

God Win FADONOUGBO — Responsable du groupe 34 : RISING MINDS
Projet académique IFRI - 2025-2026
Université d’Abomey-Calavi

```text
http://127.0.0.1:5000/connexion
```

---

## 🗄️ Base de données

L'application utilise SQLite.

Aucune installation de MySQL n'est nécessaire.

Au premier lancement, les tables sont créées automatiquement.

Le fichier de base de données est :

```text
mentorlink.db
```

---

## 👥 Membres du groupe 34 – RISING MINDS

| Nom et prénom        | Filière               | Responsabilité                                |
| -------------------- | --------------------- | --------------------------------------------- |
| FADONOUGBO God Win   | IA                    | Algorithme de matching + Coordination         |
| MONNOUKOUN Hironde   | Génie Logiciel        | Backend Flask + API                           |
| NOUGBOGNONHOU Mariel | Sécurité Informatique | Authentification + Sécurité + Base de données |
| SALIOU Samuel Exaucé | SE&IoT                | Messagerie et communication                   |
| BOUKOH Jean-Marc     | Internet & Multimédia | Interface utilisateur                         |

---

## 📚 Projet académique

Université d'Abomey-Calavi (UAC)

Institut de Formation et de Recherche en Informatique (IFRI)

Année académique 2025 - 2026

---

## 📄 Licence

Projet réalisé dans le cadre des enseignements de l'IFRI.
Usage académique uniquement.