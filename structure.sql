DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS demandes_mentorat CASCADE;
DROP TABLE IF EXISTS disponibilites CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS competences CASCADE;
DROP TABLE IF EXISTS disponibilites CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS user_competences CASCADE;
DROP TABLE IF EXISTS messages CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    telephone VARCHAR(20) NOT NULL UNIQUE,
    filiere VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'etudiant',
    password_hash VARCHAR(255) NOT NULL,
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    photo_profil VARCHAR(255),
    bio TEXT,
);

CREATE TABLE disponibilites (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jour_semaine VARCHAR(15) NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    CONSTRAINT unique_creneau_mentor UNIQUE(user_id, jour_semaine, heure_debut, heure_fin)
);

CREATE TABLE demandes_mentorat (
    id SERIAL PRIMARY KEY,
    etudiant_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mentor_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sujet_aide TEXT NOT NULL,         
    statut VARCHAR(20) NOT NULL DEFAULT 'en_attente',
    date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    demande_id INT NOT NULL REFERENCES demandes_mentorat(id) ON DELETE CASCADE,
    date_session DATE NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    lien_virtuel VARCHAR(255),        
    notes TEXT                        
);

CREATE TABLE competences (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE user_competences (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    competence_id INT REFERENCES competences(id) ON DELETE CASCADE,
    niveau VARCHAR(20) DEFAULT 'debutant',

    PRIMARY KEY (user_id, competence_id)
);

CREATE TABLE user_competences (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    competence_id INT REFERENCES competences(id) ON DELETE CASCADE,
    niveau VARCHAR(20) DEFAULT 'debutant',

    PRIMARY KEY (user_id, competence_id)
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,

    sender_id INT REFERENCES users(id) ON DELETE CASCADE,
    receiver_id INT REFERENCES users(id) ON DELETE CASCADE,

    contenu TEXT NOT NULL,
    lu BOOLEAN DEFAULT FALSE,

    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
