-- ============================================================
--  IFRI MentorLink — Schéma de la base de données
--  Groupe 34 · PIL1 2025-2026
--  Compatible : MySQL 8+ / MariaDB 10.6+
-- ============================================================

-- Suppression dans l'ordre inverse des dépendances
DROP TABLE IF EXISTS offres_demandes;
DROP TABLE IF EXISTS user_lacunes;
DROP TABLE IF EXISTS lacunes;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS user_competences;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS demandes_mentorat;
DROP TABLE IF EXISTS disponibilites;
DROP TABLE IF EXISTS competences;
DROP TABLE IF EXISTS users;

-- ──────────────────────────────────────────────────────────
--  UTILISATEURS
-- ──────────────────────────────────────────────────────────
CREATE TABLE users (
    id               INT           NOT NULL AUTO_INCREMENT,
    nom              VARCHAR(50)   NOT NULL,
    prenom           VARCHAR(50)   NOT NULL,
    email            VARCHAR(100)  NOT NULL,
    telephone        VARCHAR(20)   NOT NULL,
    filiere          VARCHAR(100)  NOT NULL,
    niveau           VARCHAR(10)   NOT NULL DEFAULT 'L1',
    role             VARCHAR(20)   NOT NULL DEFAULT 'etudiant',
    password_hash    VARCHAR(255)  NOT NULL,
    photo_profil     VARCHAR(255)  DEFAULT NULL,
    bio              TEXT          DEFAULT NULL,
    date_inscription DATETIME      DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_email     (email),
    UNIQUE KEY uq_telephone (telephone)
);

-- ──────────────────────────────────────────────────────────
--  COMPÉTENCES
-- ──────────────────────────────────────────────────────────
CREATE TABLE competences (
    id  INT          NOT NULL AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uq_competence_nom (nom)
);

-- ──────────────────────────────────────────────────────────
--  LIAISON USER ↔ COMPÉTENCES
-- ──────────────────────────────────────────────────────────
CREATE TABLE user_competences (
    user_id       INT         NOT NULL,
    competence_id INT         NOT NULL,
    niveau        VARCHAR(20) NOT NULL DEFAULT 'debutant',

    PRIMARY KEY (user_id, competence_id),
    CONSTRAINT fk_uc_user       FOREIGN KEY (user_id)       REFERENCES users(id)       ON DELETE CASCADE,
    CONSTRAINT fk_uc_competence FOREIGN KEY (competence_id) REFERENCES competences(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────────────
--  LACUNES
-- ──────────────────────────────────────────────────────────
CREATE TABLE lacunes (
    id  INT          NOT NULL AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,

    PRIMARY KEY (id),
    UNIQUE KEY uq_lacune_nom (nom)
);

-- ──────────────────────────────────────────────────────────
--  LIAISON USER ↔ LACUNES
-- ──────────────────────────────────────────────────────────
CREATE TABLE user_lacunes (
    user_id   INT NOT NULL,
    lacune_id INT NOT NULL,

    PRIMARY KEY (user_id, lacune_id),
    CONSTRAINT fk_ul_user   FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
    CONSTRAINT fk_ul_lacune FOREIGN KEY (lacune_id) REFERENCES lacunes(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────────────
--  DISPONIBILITÉS
--  jour_semaine : Lundi | Mardi | Mercredi | Jeudi | Vendredi | Samedi | Dimanche
-- ──────────────────────────────────────────────────────────
CREATE TABLE disponibilites (
    id           INT         NOT NULL AUTO_INCREMENT,
    user_id      INT         NOT NULL,
    jour_semaine VARCHAR(15) NOT NULL,
    heure_debut  TIME        NOT NULL,
    heure_fin    TIME        NOT NULL,

    PRIMARY KEY (id),
    CONSTRAINT fk_dispo_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_creneau UNIQUE (user_id, jour_semaine, heure_debut, heure_fin)
);

-- ──────────────────────────────────────────────────────────
--  DEMANDES DE MENTORAT
-- ──────────────────────────────────────────────────────────
CREATE TABLE demandes_mentorat (
    id                  INT         NOT NULL AUTO_INCREMENT,
    etudiant_id         INT         NOT NULL,
    mentor_id           INT         NOT NULL,
    sujet               TEXT        NOT NULL,
    statut              VARCHAR(20) NOT NULL DEFAULT 'en_attente',
    score_compatibilite FLOAT                DEFAULT 0,
    date_demande        DATETIME             DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT fk_dm_etudiant FOREIGN KEY (etudiant_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_dm_mentor   FOREIGN KEY (mentor_id)   REFERENCES users(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────────────
--  SESSIONS DE MENTORAT
-- ──────────────────────────────────────────────────────────
CREATE TABLE sessions (
    id           INT          NOT NULL AUTO_INCREMENT,
    demande_id   INT          NOT NULL,
    date_session DATE         NOT NULL,
    heure_debut  TIME         NOT NULL,
    heure_fin    TIME         NOT NULL,
    lien_visio   VARCHAR(255) DEFAULT NULL,
    notes        TEXT         DEFAULT NULL,

    PRIMARY KEY (id),
    CONSTRAINT fk_session_demande FOREIGN KEY (demande_id) REFERENCES demandes_mentorat(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────────────
--  MESSAGES
-- ──────────────────────────────────────────────────────────
CREATE TABLE messages (
    id          INT      NOT NULL AUTO_INCREMENT,
    sender_id   INT      NOT NULL,
    receiver_id INT      NOT NULL,
    contenu     TEXT     NOT NULL,
    lu          BOOLEAN  NOT NULL DEFAULT FALSE,
    date_envoi  DATETIME          DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT fk_msg_sender   FOREIGN KEY (sender_id)   REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_msg_receiver FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────────────
--  OFFRES / DEMANDES DE MENTORAT (publications matching)
--  type    : 'offre' (mentor propose) | 'demande' (mentoré cherche)
--  statut  : 'active' | 'pourvue' | 'archivee'
--  format  : 'ligne'  | 'presentiel' | 'les_deux'
-- ──────────────────────────────────────────────────────────
CREATE TABLE offres_demandes (
    id             INT          NOT NULL AUTO_INCREMENT,
    user_id        INT          NOT NULL,
    type           VARCHAR(10)  NOT NULL,
    matieres       TEXT         NOT NULL,
    disponibilites TEXT         DEFAULT NULL,
    format         VARCHAR(20)  DEFAULT NULL,
    statut         VARCHAR(20)  NOT NULL DEFAULT 'active',
    date_creation  DATETIME     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT fk_od_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
