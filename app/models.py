from app import db , login_manager
from flask_login import UserMixin
from datetime import datetime
from datetime import date
from datetime import time


class users(UserMixin , db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer , primary_key = True)
    nom = db.Column(db.String(50) , nullable = False)
    prenom = db.Column(db.String(50) , nullable = False)
    email = db.Column(db.String(120), unique = True , nullable = False)
    telephone = db.Column(db.String(20), unique = True , nullable = False)
    filiere = db.Column(db.String(100) , nullable = False) 
    role = db.Column(db.String(20) , nullable = False , default = 'étudiant') 
    password_hash = db.Column(db.String(255) , nullable = False)
    date_inscription = db.Column(db.DateTime , default = datetime.now)
    photo_profil =db.Column(db.String(255) , default = "default.jpg")
    bio = db.Column(db.Text , nullable = True)

class disponibilites(db.Model):
    __tablename__ = "disponibilites"
    id = db.column(db.Integer , primary_key = True)
    user_id = db.Column(db.Integer , db.ForeignKey("users.id") , nullable = False , ondelete = 'CASCADE')
    jour_semaine = db.Column(db.String(15) , nullable = False)
    heure_debut = db.Column(db.Time , nullable = False)
    heure_fin = db.Column(db.Time , nullable = False)
    unique_creneau_mentor = db.UniqueConstraint('user_id' , 'jour_semaine' , 'heure_debut' , 'heure_fin')

class demandes_mentorat(db.Model):
    __tablename__ = "demandes_mentorat"
    id = db.column(db.Integer , primary_key = True)
    etudiant_id = db.Column( db.Integer , db.ForeignKey(users.id) , ondelete = 'CASCADE')
    mentor_id = db.Column(db.Integer , db.ForeignKey(users.id) , ondelete = 'CASCADE')
    sujet_aide = db.Column(db.Text , nullable = False)
    statut = db.Column(db.String(20) , nullable = False , default = 'En attente') 
    date_demande = db.Column(db.DateTime , default = datetime.now)

class Session(db.Model):
    __tablename__ = "sessions"
    id = db.column(db.Integer , primary_key = True)
    demande_id = db.Column(db.Integer , db.ForeignKey(demandes_mentorat.id) , ondelete = 'CASCADE')
    date_session = db.Column(db.Date , nullable = False)
    heure_debut = db.Column(db.Time , nullable = False)
    heure_fin = db.Column(db.Time , nullable = False)
    lien_virtuel = db.Column(db.String(255))
    notes = db.Column(db.Text)

class competences(db.Model): 
    id = db.column(db.Integer , primary_key = True)
    nom = db.Column(db.String(100) , nllable = False , unique = True)

class user_competences(db.Model): 
    user_id = db.Column(db.Integer , db.ForeignKey(users.id , ondelete = 'CASCADE'))
    competence_id = db.Column(db.Integer , db.ForeignKey(competences.id) , ondelete = 'CASCADE')
    niveau = db.Column(db.String(20) , default = 'Debutant')

class messages(db.Model):
    id = db.column(db.Integer , primary_key = True)
    sender_id = db.Column(db.Integer , db.ForeignKey(users.id) , ondelete = 'CASCADE')
    receiver_id = db.Column(db.Integer , db.ForeignKey(users.id) , ondelete = 'CASCADE')
    contenu = db.Column(db.Text , nullable = False)
    lu = db.Column(db.Boolean , default = False)
    date_envoi = db.Column(db.DateTime , default = datetime.now)
    
    @login_manager.user_loader
    def load_user(user_id):
        return users.query.get(int(user_id))
    
    
=======
from app import db

from flask_login import UserMixin


# =========================
# UTILISATEURS
# =========================

class User(UserMixin,db.Model):


    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)
    telephone = db.Column(db.String(20), unique=True, nullable=False)

    filiere = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default="etudiant")

    password_hash = db.Column(db.String(255), nullable=False)

    photo_profil = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    date_inscription = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    # Relations

    competences = db.relationship(
        "Competence",
        secondary="user_competences",
        lazy="joined"
    )

    disponibilites = db.relationship(
        "Disponibilite",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    demandes_envoyees = db.relationship(
        "DemandeMentorat",
        foreign_keys="DemandeMentorat.etudiant_id",
        backref="etudiant",
        lazy=True
    )

    demandes_recues = db.relationship(
        "DemandeMentorat",
        foreign_keys="DemandeMentorat.mentor_id",
        backref="mentor",
        lazy=True
    )

    messages_envoyes = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        backref="expediteur",
        lazy=True
    )

    messages_recus = db.relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        backref="destinataire",
        lazy=True
    )


# =========================
# COMPÉTENCES
# =========================
class Competence(db.Model):
    __tablename__ = "competences"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)


# =========================
# RELATION USER - COMPÉTENCES
# =========================
class UserCompetence(db.Model):
    __tablename__ = "user_competences"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True
    )

    competence_id = db.Column(
        db.Integer,
        db.ForeignKey("competences.id"),
        primary_key=True
    )

    niveau = db.Column(
        db.String(20),
        default="debutant"
    )


# =========================
# DISPONIBILITÉS
# =========================
class Disponibilite(db.Model):
    __tablename__ = "disponibilites"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    jour_semaine = db.Column(
        db.String(15),
        nullable=False
    )

    heure_debut = db.Column(
        db.Time,
        nullable=False
    )

    heure_fin = db.Column(
        db.Time,
        nullable=False
    )


# =========================
# DEMANDES DE MENTORAT
# =========================
class DemandeMentorat(db.Model):
    __tablename__ = "demandes_mentorat"

    id = db.Column(db.Integer, primary_key=True)

    etudiant_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    mentor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    sujet = db.Column(
        db.Text,
        nullable=False
    )

    statut = db.Column(
        db.String(20),
        default="en_attente"
    )

    score_compatibilite = db.Column(
        db.Float,
        default=0
    )

    date_demande = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    sessions = db.relationship(
        "SessionMentorat",
        backref="demande",
        lazy=True,
        cascade="all, delete-orphan"
    )


# =========================
# SESSIONS
# =========================
class SessionMentorat(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)

    demande_id = db.Column(
        db.Integer,
        db.ForeignKey("demandes_mentorat.id"),
        nullable=False
    )

    date_session = db.Column(
        db.Date,
        nullable=False
    )

    heure_debut = db.Column(
        db.Time,
        nullable=False
    )

    heure_fin = db.Column(
        db.Time,
        nullable=False
    )

    lien_visio = db.Column(
        db.String(255)
    )

    notes = db.Column(
        db.Text
    )


# =========================
# MESSAGES
# =========================
class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    contenu = db.Column(
        db.Text,
        nullable=False
    )

    lu = db.Column(
        db.Boolean,
        default=False
    )

    date_envoi = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )
