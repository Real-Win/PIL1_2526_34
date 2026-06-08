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
    
    