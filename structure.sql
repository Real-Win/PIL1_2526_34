DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS demandes_mentorat CASCADE;
DROP TABLE IF EXISTS disponibilites CASCADE;
DROP TABLE IF EXISTS users CASCADE;

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
