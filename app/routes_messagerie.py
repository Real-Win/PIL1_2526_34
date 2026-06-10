from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app import db, socketio
from app.models import Message, User
from datetime import datetime

messagerie_bp = Blueprint("messagerie", __name__)
@messagerie_bp.route("/test-lab")
def labo_test():
    # Cette route te permet d'ouvrir ton panel sans être bloqué par la sécurité
    return render_template("test_brut.html")


# ------------------------------------------------------------------
# PAGE MESSAGES  /messages 
# ------------------------------------------------------------------
@messagerie_bp.route("/messages")
@login_required
def messages():
    # 1. On récupère toujours tous les autres utilisateurs pour la recherche
    autres_users = User.query.filter(User.id != current_user.id).all()
    
    # 2. On récupère tous les messages triés du plus ancien au plus récent
    tous_les_messages = Message.query.filter(
        (Message.sender_id   == current_user.id) |
        (Message.receiver_id == current_user.id)
    ).order_by(Message.date_envoi.asc()).all()

    # 3. ALGORITHME DE FILTRAGE : Un dictionnaire pour écraser les doublons
    # La clé sera l'ID du contact, la valeur sera le dernier message
    derniers_messages_par_contact = {}

    for msg in tous_les_messages:
        # On détermine qui est le contact (l'autre personne)
        contact_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        
        # On stocke (ou on écrase avec le plus récent) le message pour ce contact
        derniers_messages_par_contact[contact_id] = msg

    # 4. On extrait les messages filtrés et on les trie du plus récent au plus ancien pour la liste
    historique_filtre = list(derniers_messages_par_contact.values())
    historique_filtre.sort(key=lambda x: x.date_envoi, reverse=True)

    return render_template(
        "messages.html",
        historique=historique_filtre,  # Cette liste contient maintenant 1 seule ligne par contact !
        autres_users=autres_users
    )

# ------------------------------------------------------------------
# API : historique d'une conversation  GET /api/messages/<id>
# ------------------------------------------------------------------
@messagerie_bp.route("/api/messages/<int:contact_id>")
@login_required
def get_messages(contact_id):
    """Retourne l'historique JSON entre l'utilisateur connecté et contact_id."""
    msgs = Message.query.filter(
        ((Message.sender_id   == current_user.id) & (Message.receiver_id == contact_id)) |
        ((Message.sender_id   == contact_id)       & (Message.receiver_id == current_user.id))
    ).order_by(Message.date_envoi.asc()).all()

    return jsonify([{
        "id":      m.id,
        "contenu": m.contenu,
        "heure":   m.date_envoi.strftime("%H:%M") if m.date_envoi else "",
        "est_moi": m.sender_id == current_user.id
    } for m in msgs])


# ------------------------------------------------------------------
# SOCKET.IO : rejoindre une salle privée
# ------------------------------------------------------------------
@socketio.on("rejoindre_salle")
def rejoindre_salle(data):
    ids   = sorted([int(data["user_id"]), int(data["contact_id"])])
    salle = f"salle_{ids[0]}_{ids[1]}"
    join_room(salle)


# ------------------------------------------------------------------
# SOCKET.IO : recevoir et diffuser un message
# ------------------------------------------------------------------
@socketio.on("nouveau_message")
def gerer_message(data):
    sender_id   = int(data.get("sender_id"))
    receiver_id = int(data.get("receiver_id"))
    contenu     = data.get("contenu", "").strip()

    if not contenu:
        return

    # Sauvegarde en base
    msg = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        contenu=contenu,
        date_envoi=datetime.utcnow(),
        lu=False
    )
    db.session.add(msg)
    db.session.commit()

    expediteur = User.query.get(sender_id)
    pseudo     = f"{expediteur.prenom} {expediteur.nom}" if expediteur else "Inconnu"

    ids   = sorted([sender_id, receiver_id])
    salle = f"salle_{ids[0]}_{ids[1]}"

    emit("diffusion_message", {
        "pseudo":     pseudo,
        "msg":        contenu,
        "date":       msg.date_envoi.strftime("%H:%M"),
        "sender_id":  sender_id
    }, room=salle)


@socketio.on("quitter_salle")
def quitter_salle(data):
    ids   = sorted([int(data["user_id"]), int(data["contact_id"])])
    salle = f"salle_{ids[0]}_{ids[1]}"
    leave_room(salle)
# ------------------------------------------------------------------
# SOCKET.IO : Gérer l'état "En train d'écrire"
# ------------------------------------------------------------------
@socketio.on("debut_ecriture")
def debut_ecriture(data):
    sender_id   = int(data.get("sender_id"))
    receiver_id = int(data.get("receiver_id"))
    
    ids   = sorted([sender_id, receiver_id])
    salle = f"salle_{ids[0]}_{ids[1]}"
    
    # On prévient l'autre utilisateur que le sender écrit
    emit("l_autre_ecrit", {"sender_id": sender_id, "statut": True}, room=salle, include_self=False)

@socketio.on("fin_ecriture")
def fin_ecriture(data):
    sender_id   = int(data.get("sender_id"))
    receiver_id = int(data.get("receiver_id"))
    
    ids   = sorted([sender_id, receiver_id])
    salle = f"salle_{ids[0]}_{ids[1]}"
    
    # On prévient l'autre utilisateur que le sender a arrêté d'écrire
    emit("l_autre_ecrit", {"sender_id": sender_id, "statut": False}, room=salle, include_self=False)