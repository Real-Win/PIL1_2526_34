from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, jsonify
)
from flask_login import (
    login_user, logout_user,
    login_required, current_user
)
from app import db
from app.models import User, DemandeMentorat
from app.matching import calculer_match, get_top_mentors, get_top_mentores
from app.securite import inscrire_etudiant, verifier_connexion


# ===== MATCHING BLUEPRINT =====
matching_bp = Blueprint("matching", __name__)


@matching_bp.route("/match/<int:mentore_id>/<int:mentor_id>")
@login_required
def match(mentore_id, mentor_id):
    mentore = User.query.get_or_404(mentore_id)
    mentor  = User.query.get_or_404(mentor_id)
    score   = calculer_match(mentore, mentor)
    return jsonify({"score": score, "bon_match": score >= 60})


# ------------------------------------------------------------------
# TOP 3  —  adapté au rôle demandé via paramètre ?cherche=mentor|mentore
# ------------------------------------------------------------------
@matching_bp.route("/top3/<int:user_id>")
@login_required
def top3(user_id):
    """
    ?cherche=mentor   → l'user est mentoré, cherche les meilleurs mentors
    ?cherche=mentore  → l'user est mentor,  cherche les meilleurs mentorés
    Sans paramètre    → comportement selon le rôle de l'user
    """
    user       = User.query.get_or_404(user_id)
    cherche    = request.args.get("cherche", "").strip()
    autres     = User.query.filter(User.id != user_id).all()

    # Détermine ce qu'on cherche si non précisé
    if not cherche:
        if user.role == "mentor":
            cherche = "mentore"
        else:
            cherche = "mentor"

    if cherche == "mentore":
        result = get_top_mentores(user, autres)
    else:
        result = get_top_mentors(user, autres)

    return jsonify(result)


# ------------------------------------------------------------------
# API PROFIL UTILISATEUR  —  utilisée par le JS de matching.html
# ------------------------------------------------------------------
@matching_bp.route("/api/user/<int:user_id>")
@login_required
def api_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id":      user.id,
        "nom":     user.nom,
        "prenom":  user.prenom,
        "filiere": user.filiere,
        "role":    user.role,
        "niveau":  user.niveau,
        "bio":     user.bio or ""
    })


# ===== AUTH BLUEPRINT =====
auth_bp = Blueprint("auth", __name__)


# ------------------------------------------------------------------
# PAGE D'ACCUEIL  /
# ------------------------------------------------------------------
@auth_bp.route("/")
def accueil():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return render_template("accueil.html")


# ------------------------------------------------------------------
# DASHBOARD  /dashboard
# ------------------------------------------------------------------
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    autres_users = User.query.filter(User.id != current_user.id).all()

    top_mentors   = []
    top_mentores  = []

    # Si l'user peut être mentoré → on lui propose des mentors
    if current_user.role in ("etudiant", "mentore", "les_deux"):
        for item in get_top_mentors(current_user, autres_users):
            mentor = User.query.get(item["mentor_id"])
            if mentor:
                top_mentors.append({"user": mentor, "score": item["score"]})

    # Si l'user est mentor → on lui propose des mentorés
    if current_user.role in ("mentor", "les_deux"):
        for item in get_top_mentores(current_user, autres_users):
            mentore = User.query.get(item["mentore_id"])
            if mentore:
                top_mentores.append({"user": mentore, "score": item["score"]})

    demandes = DemandeMentorat.query.filter_by(
        etudiant_id=current_user.id
    ).order_by(DemandeMentorat.date_demande.desc()).limit(5).all()

    messages_recents = current_user.messages_recus[-5:] \
        if current_user.messages_recus else []

    return render_template(
        "dashboard.html",
        user=current_user,
        top_mentors=top_mentors,
        top_mentores=top_mentores,
        demandes=demandes,
        messages_recents=messages_recents
    )


# ------------------------------------------------------------------
# INSCRIPTION  /inscription
# ------------------------------------------------------------------
@auth_bp.route("/inscription", methods=["GET", "POST"])
def inscription():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        success, message = inscrire_etudiant(
            nom          = request.form.get("nom"),
            prenom       = request.form.get("prenom"),
            email        = request.form.get("email"),
            telephone    = request.form.get("telephone"),
            filiere      = request.form.get("filiere"),
            role         = request.form.get("role", "etudiant"),
            mot_de_passe = request.form.get("mot_de_passe")
        )
        if success:
            flash("Inscription réussie ! Connecte-toi maintenant.", "success")
            return redirect(url_for("auth.connexion"))
        flash(message, "danger")

    return render_template("inscription.html")


# ------------------------------------------------------------------
# CONNEXION  /connexion
# ------------------------------------------------------------------
@auth_bp.route("/connexion", methods=["GET", "POST"])
def connexion():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        user, message = verifier_connexion(
            request.form.get("email"),
            request.form.get("mot_de_passe")
        )
        if user:
            login_user(user, remember=True)
            flash("Connexion réussie !", "success")
            return redirect(url_for("auth.dashboard"))
        flash(message, "danger")

    return render_template("connexion.html")


# ------------------------------------------------------------------
# DÉCONNEXION  /deconnexion
# ------------------------------------------------------------------
@auth_bp.route("/deconnexion")
@login_required
def deconnexion():
    logout_user()
    flash("Tu as été déconnecté.", "info")
    return redirect(url_for("auth.connexion"))


# ------------------------------------------------------------------
# PROFIL  /profil
# ------------------------------------------------------------------
@auth_bp.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    if request.method == "POST":
        from app.models import Competence, UserCompetence, Disponibilite
        from datetime import datetime

        current_user.nom     = request.form.get("nom",     current_user.nom)
        current_user.prenom  = request.form.get("prenom",  current_user.prenom)
        current_user.filiere = request.form.get("filiere", current_user.filiere)
        current_user.niveau  = request.form.get("niveau",  current_user.niveau)
        current_user.role    = request.form.get("role",    current_user.role)
        current_user.bio     = request.form.get("bio",     current_user.bio)

        # Compétences
        competences_raw = request.form.get("competences", "").strip()
        if competences_raw:
            UserCompetence.query.filter_by(user_id=current_user.id).delete()
            for nom_comp in [c.strip().lower() for c in competences_raw.split(",") if c.strip()]:
                comp = Competence.query.filter_by(nom=nom_comp).first()
                if not comp:
                    comp = Competence(nom=nom_comp)
                    db.session.add(comp)
                    db.session.flush()
                lien = UserCompetence(user_id=current_user.id, competence_id=comp.id)
                db.session.add(lien)

        # Disponibilités
        jours        = request.form.getlist("jours[]")
        heures_debut = request.form.getlist("heures_debut[]")
        heures_fin   = request.form.getlist("heures_fin[]")
        if jours:
            Disponibilite.query.filter_by(user_id=current_user.id).delete()
            for jour, h_debut, h_fin in zip(jours, heures_debut, heures_fin):
                if jour and h_debut and h_fin:
                    dispo = Disponibilite(
                        user_id      = current_user.id,
                        jour_semaine = jour,
                        heure_debut  = datetime.strptime(h_debut, "%H:%M").time(),
                        heure_fin    = datetime.strptime(h_fin,   "%H:%M").time()
                    )
                    db.session.add(dispo)

        db.session.commit()
        flash("Profil mis à jour !", "success")
        return redirect(url_for("auth.profil"))

    return render_template("profil.html", user=current_user)


# ------------------------------------------------------------------
# PAGE MATCHING  /matching
# ------------------------------------------------------------------
@auth_bp.route("/matching")
@login_required
def matching_page():
    return render_template("matching.html", user=current_user)


# ------------------------------------------------------------------
# CRÉER UNE DEMANDE DE MENTORAT  /demande/<cible_id>
# Fonctionne dans les deux sens : mentoré → mentor  ET  mentor → mentoré
# ------------------------------------------------------------------
@auth_bp.route("/demande/<int:cible_id>", methods=["POST"])
@login_required
def creer_demande(cible_id):
    cible = User.query.get_or_404(cible_id)
    sujet = request.form.get("sujet", "").strip()

    if not sujet:
        flash("Le sujet de la demande ne peut pas être vide.", "danger")
        return redirect(url_for("auth.matching_page"))

    # Détermine qui est mentor et qui est mentoré selon les rôles
    # Si current_user est mentor et cible est mentoré → current_user propose son aide
    if current_user.role in ("mentor", "les_deux") and cible.role not in ("mentor",):
        etudiant_id = cible.id
        mentor_id   = current_user.id
    else:
        # Cas classique : current_user (mentoré) demande à cible (mentor)
        etudiant_id = current_user.id
        mentor_id   = cible.id

    # Vérifie qu'une demande identique n'existe pas déjà
    existante = DemandeMentorat.query.filter_by(
        etudiant_id=etudiant_id,
        mentor_id=mentor_id
    ).first()

    if existante:
        flash("Une demande existe déjà entre ces deux personnes.", "warning")
        return redirect(url_for("auth.matching_page"))

    demande = DemandeMentorat(
        etudiant_id=etudiant_id,
        mentor_id=mentor_id,
        sujet=sujet
    )
    db.session.add(demande)
    db.session.commit()

    flash(f"Demande envoyée à {cible.prenom} {cible.nom} !", "success")
    return redirect(url_for("auth.demandes"))


# ------------------------------------------------------------------
# CHANGER LE STATUT D'UNE DEMANDE  /demande/<id>/statut
# Utilisé par demandes.html (boutons Accepter / Refuser)
# ------------------------------------------------------------------
@auth_bp.route("/demande/<int:demande_id>/statut", methods=["POST"])
@login_required
def changer_statut_demande(demande_id):
    demande = DemandeMentorat.query.get_or_404(demande_id)

    # Seul le mentor concerné peut changer le statut
    if demande.mentor_id != current_user.id:
        flash("Action non autorisée.", "danger")
        return redirect(url_for("auth.demandes"))

    nouveau_statut = request.form.get("statut", "").strip()
    if nouveau_statut not in ("acceptee", "refusee"):
        flash("Statut invalide.", "danger")
        return redirect(url_for("auth.demandes"))

    demande.statut = nouveau_statut
    db.session.commit()

    msg = "Demande acceptée ✓" if nouveau_statut == "acceptee" else "Demande refusée."
    flash(msg, "success" if nouveau_statut == "acceptee" else "info")
    return redirect(url_for("auth.demandes"))


# ------------------------------------------------------------------
# LISTE DES DEMANDES  /demandes
# Envoyées ET reçues (pour le template avec onglets)
# ------------------------------------------------------------------
@auth_bp.route("/demandes")
@login_required
def demandes():
    demandes_envoyees = DemandeMentorat.query.filter_by(
        etudiant_id=current_user.id
    ).order_by(DemandeMentorat.date_demande.desc()).all()

    demandes_recues = DemandeMentorat.query.filter_by(
        mentor_id=current_user.id
    ).order_by(DemandeMentorat.date_demande.desc()).all()

    return render_template(
        "demandes.html",
        demandes_envoyees=demandes_envoyees,
        demandes_recues=demandes_recues
    )


# ------------------------------------------------------------------
# MESSAGES  /messages
# ------------------------------------------------------------------
@auth_bp.route("/messages")
@login_required
def messages():
    messages_recus = current_user.messages_recus
    return render_template("messages.html", messages=messages_recus)
