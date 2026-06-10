from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app import db, socketio
from app.models import Message, User, DemandeMentorat
from datetime import datetime

messagerie_bp = Blueprint("messagerie", __name__)


@messagerie_bp.route("/messages")
@login_required
def messages():
    contact_ids = set()

    # Tous les IDs avec qui on a échangé des messages
    messages_envoyes = Message.query.filter_by(sender_id=current_user.id).all()
    messages_recus   = Message.query.filter_by(receiver_id=current_user.id).all()
    for msg in messages_envoyes:
        contact_ids.add(msg.receiver_id)
    for msg in messages_recus:
        contact_ids.add(msg.sender_id)

    # Toutes les demandes acceptées (peu importe qui a envoyé)
    demandes_acc = DemandeMentorat.query.filter(
        DemandeMentorat.statut == "acceptee",
        db.or_(
            DemandeMentorat.etudiant_id == current_user.id,
            DemandeMentorat.mentor_id   == current_user.id
        )
    ).all()
    for d in demandes_acc:
        autre_id = d.mentor_id if d.etudiant_id == current_user.id else d.etudiant_id
        contact_ids.add(autre_id)

    # On retire l'utilisateur lui-même
    contact_ids.discard(current_user.id)

    # Récupérer les objets User
    contacts = [User.query.get(cid) for cid in contact_ids if User.query.get(cid)]

    # Trier par date du dernier message (plus récent en premier)
    def dernier_message_date(contact):
        msg = Message.query.filter(
            db.or_(
                db.and_(Message.sender_id == current_user.id,   Message.receiver_id == contact.id),
                db.and_(Message.sender_id == contact.id,         Message.receiver_id == current_user.id)
            )
        ).order_by(Message.date_envoi.desc()).first()
        return msg.date_envoi if msg else datetime.min

    contacts.sort(key=dernier_message_date, reverse=True)

    # Auto-ouvrir depuis ?contact=ID
    contact_id = request.args.get("contact", type=int)
    contact_ouverture = None
    if contact_id and contact_id != current_user.id:
        contact_ouverture = User.query.get(contact_id)
        # S'assurer qu'il est dans la liste (cas où pas encore de message)
        if contact_ouverture and contact_ouverture not in contacts:
            contacts.insert(0, contact_ouverture)

    return render_template(
        "messages.html",
        contacts=contacts,
        contact_ouverture=contact_ouverture
    )


@messagerie_bp.route("/api/messages/<int:contact_id>")
@login_required
def get_messages(contact_id):
    msgs = Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == current_user.id,   Message.receiver_id == contact_id),
            db.and_(Message.sender_id == contact_id,         Message.receiver_id == current_user.id)
        )
    ).order_by(Message.date_envoi.asc()).all()
    return jsonify([{
        "id":       m.id,
        "contenu":  m.contenu,
        "heure":    m.date_envoi.strftime("%H:%M") if m.date_envoi else "",
        "est_moi":  m.sender_id == current_user.id
    } for m in msgs])


@socketio.on("rejoindre_salle")
def rejoindre_salle(data):
    ids  = sorted([int(data["user_id"]), int(data["contact_id"])])
    salle = f"salle_{ids[0]}_{ids[1]}"
    join_room(salle)


@socketio.on("rejoindre_salle_perso")
def rejoindre_salle_perso(data):
    user_id = int(data["user_id"])
    join_room(f"perso_{user_id}")


@socketio.on("nouveau_message")
def gerer_message(data):
    sender_id   = int(data.get("sender_id"))
    receiver_id = int(data.get("receiver_id"))
    contenu     = data.get("contenu", "").strip()
    if not contenu:
        return

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
        "id":        msg.id,
        "pseudo":    pseudo,
        "msg":       contenu,
        "date":      msg.date_envoi.strftime("%H:%M"),
        "sender_id": sender_id
    }, room=salle)

    emit("nouveau_message_notif", {
        "pseudo":      pseudo,
        "msg":         contenu,
        "receiver_id": receiver_id,
        "sender_id":   sender_id
    }, room=f"perso_{receiver_id}")


@socketio.on("quitter_salle")
def quitter_salle(data):
    ids   = sorted([int(data["user_id"]), int(data["contact_id"])])
    salle = f"salle_{ids[0]}_{ids[1]}"
    leave_room(salle)