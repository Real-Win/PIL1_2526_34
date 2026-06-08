from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app import db, socketio
from app.models import Message, User
from datetime import datetime

# Blueprint (pas de Flask() ici — on réutilise l'app principale)
messagerie_bp = Blueprint("messagerie", __name__)


# ------------------------------------------------------------------
# PAGE DE MESSAGERIE  /messages
# ------------------------------------------------------------------
@messagerie_bp.route("/messages")
@login_required
def messages():
    """
    Affiche l'historique des messages reçus ET envoyés
    par l'utilisateur connecté.
    """
    # Tous les messages impliquant l'utilisateur connecté
    historique = Message.query.filter(
        (Message.sender_id   == current_user.id) |
        (Message.receiver_id == current_user.id)
    ).order_by(Message.date_envoi.asc()).all()

    # Liste des utilisateurs avec qui on peut discuter
    autres_users = User.query.filter(
        User.id != current_user.id
    ).all()

    return render_template(
        "messages.html",
        historique=historique,
        autres_users=autres_users
    )


# ------------------------------------------------------------------
# ÉVÉNEMENTS SOCKET.IO
# ------------------------------------------------------------------

@socketio.on("rejoindre_salle")
def rejoindre_salle(data):
    """
    L'utilisateur rejoint une salle de discussion privée.
    La salle est nommée avec les deux IDs triés pour être unique.
    Exemple : salle_2_5 pour les users 2 et 5.
    """
    user_id     = data.get("user_id")
    contact_id  = data.get("contact_id")

    # Nom de salle unique et symétrique
    ids  = sorted([int(user_id), int(contact_id)])
    salle = f"salle_{ids[0]}_{ids[1]}"

    join_room(salle)
    emit("statut", {"msg": "Connecté à la salle."}, room=salle)


@socketio.on("nouveau_message")
def gerer_message(data):
    """
    Reçoit un message, le sauvegarde en base,
    et le diffuse dans la salle correspondante.
    """
    sender_id   = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    contenu     = data.get("contenu", "").strip()

    if not contenu:
        return

    # Sauvegarde en base de données
    msg = Message(
        sender_id   = sender_id,
        receiver_id = receiver_id,
        contenu     = contenu,
        date_envoi  = datetime.utcnow(),
        lu          = False
    )
    db.session.add(msg)
    db.session.commit()

    # Récupère le nom de l'expéditeur
    expediteur = User.query.get(sender_id)
    pseudo     = f"{expediteur.prenom} {expediteur.nom}" if expediteur else "Inconnu"

    # Diffuse dans la bonne salle
    ids   = sorted([int(sender_id), int(receiver_id)])
    salle = f"salle_{ids[0]}_{ids[1]}"

    emit("diffusion_message", {
        "pseudo":     pseudo,
        "msg":        contenu,
        "date":       msg.date_envoi.strftime("%H:%M"),
        "sender_id":  sender_id
    }, room=salle)


@socketio.on("quitter_salle")
def quitter_salle(data):
    user_id    = data.get("user_id")
    contact_id = data.get("contact_id")

    ids   = sorted([int(user_id), int(contact_id)])
    salle = f"salle_{ids[0]}_{ids[1]}"

    leave_room(salle)