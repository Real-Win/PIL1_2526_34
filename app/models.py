from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    nom           = db.Column(db.String(50),  nullable=False)
    prenom        = db.Column(db.String(50),  nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    telephone     = db.Column(db.String(20),  unique=True, nullable=False)
    filiere       = db.Column(db.String(100), nullable=False)
    niveau        = db.Column(db.String(10),  default="L1")
    role          = db.Column(db.String(20),  default="etudiant")
    password_hash = db.Column(db.String(255), nullable=False)
    photo_profil  = db.Column(db.String(255), nullable=True)
    photo_couverture=db.Column(db.String(255), nullable=True)
    bio           = db.Column(db.Text,        nullable=True)
    date_inscription = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    competences   = db.relationship("Competence",   secondary="user_competences", lazy="joined")
    lacunes       = db.relationship("Lacune",        secondary="user_lacunes",     lazy="joined")
    disponibilites = db.relationship("Disponibilite", backref="user", lazy=True, cascade="all, delete-orphan")

    demandes_envoyees = db.relationship("DemandeMentorat", foreign_keys="DemandeMentorat.etudiant_id", backref="etudiant", lazy=True)
    demandes_recues   = db.relationship("DemandeMentorat", foreign_keys="DemandeMentorat.mentor_id",   backref="mentor",   lazy=True)
    messages_envoyes  = db.relationship("Message", foreign_keys="Message.sender_id",   backref="expediteur",  lazy=True)
    messages_recus    = db.relationship("Message", foreign_keys="Message.receiver_id", backref="destinataire", lazy=True)
    reset_tokens      = db.relationship("PasswordResetToken", backref="user", lazy=True, cascade="all, delete-orphan")


class Competence(db.Model):
    __tablename__ = "competences"
    id  = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)


class Lacune(db.Model):
    __tablename__ = "lacunes"
    id  = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)


class UserCompetence(db.Model):
    __tablename__ = "user_competences"
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"),       primary_key=True)
    competence_id = db.Column(db.Integer, db.ForeignKey("competences.id"), primary_key=True)
    niveau        = db.Column(db.String(20), default="debutant")


class UserLacune(db.Model):
    __tablename__ = "user_lacunes"
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"),    primary_key=True)
    lacune_id = db.Column(db.Integer, db.ForeignKey("lacunes.id"),  primary_key=True)


class Disponibilite(db.Model):
    __tablename__ = "disponibilites"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    jour_semaine = db.Column(db.String(15), nullable=False)
    heure_debut  = db.Column(db.Time, nullable=False)
    heure_fin    = db.Column(db.Time, nullable=False)


class DemandeMentorat(db.Model):
    __tablename__ = "demandes_mentorat"
    id                  = db.Column(db.Integer, primary_key=True)
    etudiant_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mentor_id           = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    sujet               = db.Column(db.Text,    nullable=False)
    statut              = db.Column(db.String(20), default="en_attente")
    score_compatibilite = db.Column(db.Float, default=0)
    date_demande        = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    sessions            = db.relationship("SessionMentorat", backref="demande", lazy=True, cascade="all, delete-orphan")


class SessionMentorat(db.Model):
    __tablename__ = "sessions"
    id           = db.Column(db.Integer, primary_key=True)
    demande_id   = db.Column(db.Integer, db.ForeignKey("demandes_mentorat.id"), nullable=False)
    date_session = db.Column(db.Date, nullable=False)
    heure_debut  = db.Column(db.Time, nullable=False)
    heure_fin    = db.Column(db.Time, nullable=False)
    lien_visio   = db.Column(db.String(255))
    notes        = db.Column(db.Text)


class Message(db.Model):
    __tablename__ = "messages"
    id          = db.Column(db.Integer, primary_key=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contenu     = db.Column(db.Text,    nullable=False)
    lu          = db.Column(db.Boolean, default=False)
    date_envoi  = db.Column(db.DateTime, server_default=db.func.current_timestamp())


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id         = db.Column(db.Integer, primary_key=True)
    token      = db.Column(db.String(120), unique=True, nullable=False, index=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)
    utilise    = db.Column(db.Boolean, default=False)