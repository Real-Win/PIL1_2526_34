CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    telephone VARCHAR(20) NOT NULL UNIQUE,
    filiere VARCHAR(10) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    nom_matiere VARCHAR(100) NOT NULL UNIQUE,
);

CREATE TABLE user_mentors (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    skill_id INT REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY(user_id,skill_id)
);

CREATE TABLE user_mentees (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    skill_id INT REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY(user_id,skill_id)
);