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
from app.matching import calculer_match, get_top_mentors
from app.securite import inscrire_etudiant, verifier_connexion


# ===== MATCHING BLUEPRINT =====
matching_bp = Blueprint("matching", __name__)


@matching_bp.route("/match/<int:mentore_id>/<int:mentor_id>")
@login_required
def match(mentore_id, mentor_id):
    mentore = User.query.get_or_404(mentore_id)
    mentor  = User.query.get_or_404(mentor_id)

    score = calculer_match(mentore, mentor)

    return jsonify({
        "score":     score,
        "bon_match": score >= 60
    })


@matching_bp.route("/top3/<int:mentore_id>")
@login_required
def top3(mentore_id):
    mentore = User.query.get_or_404(mentore_id)

    # Tous les mentors sauf le mentoré lui-même
    mentors = User.query.filter(
        User.id != mentore_id
    ).all()

    result = get_top_mentors(mentore, mentors)
    return jsonify(result)


# ===== AUTH BLUEPRINT =====
auth_bp = Blueprint("auth", __name__)


# ------------------------------------------------------------------
# PAGE D'ACCUEIL  /
# ------------------------------------------------------------------
@auth_bp.route("/")
def accueil():
    """
    Page d'accueil publique.
    Si l'utilisateur est déjà connecté → dashboard.
    Sinon → page de présentation de MentorLink.
    """
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return render_template("accueil.html")


# ------------------------------------------------------------------
# DASHBOARD  /dashboard
# ------------------------------------------------------------------
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Tableau de bord affiché après connexion.
    - Top 3 mentors compatibles avec l'utilisateur connecté
    - Ses demandes de mentorat envoyées
    - Ses derniers messages reçus
    """
    # Top 3 mentors pour l'utilisateur connecté
    autres_users = User.query.filter(
        User.id != current_user.id
    ).all()

    top_mentors_ids = get_top_mentors(current_user, autres_users)

    # Récupère les objets User correspondants (pour afficher nom/prénom)
    top_mentors = []
    for item in top_mentors_ids:
        mentor = User.query.get(item["mentor_id"])
        if mentor:
            top_mentors.append({
                "user":  mentor,
                "score": item["score"]
            })

    # Demandes de mentorat envoyées par l'utilisateur connecté
    demandes = DemandeMentorat.query.filter_by(
        etudiant_id=current_user.id
    ).order_by(DemandeMentorat.date_demande.desc()).limit(5).all()

    # Derniers messages reçus
    messages_recents = current_user.messages_recus[-5:] \
        if current_user.messages_recus else []

    return render_template(
        "dashboard.html",
        top_mentors=top_mentors,
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
            nom        = request.form.get("nom"),
            prenom     = request.form.get("prenom"),
            email      = request.form.get("email"),
            telephone  = request.form.get("telephone"),
            filiere    = request.form.get("filiere"),
            role       = request.form.get("role", "etudiant"),
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
        current_user.bio = request.form.get("bio")
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
    """Affiche la page de matching (frontend)."""
    return render_template("matching.html")


# ------------------------------------------------------------------
# CRÉER UNE DEMANDE DE MENTORAT  /demande/<mentor_id>
# ------------------------------------------------------------------
@auth_bp.route("/demande/<int:mentor_id>", methods=["POST"])
@login_required
def creer_demande(mentor_id):
    """L'utilisateur connecté envoie une demande au mentor choisi."""
    mentor = User.query.get_or_404(mentor_id)
    sujet  = request.form.get("sujet", "").strip()

    if not sujet:
        flash("Le sujet de la demande ne peut pas être vide.", "danger")
        return redirect(url_for("auth.dashboard"))

    # Vérifie qu'une demande identique n'existe pas déjà
    existante = DemandeMentorat.query.filter_by(
        etudiant_id = current_user.id,
        mentor_id   = mentor.id
    ).first()

    if existante:
        flash("Tu as déjà envoyé une demande à ce mentor.", "warning")
        return redirect(url_for("auth.dashboard"))

    demande = DemandeMentorat(
        etudiant_id = current_user.id,
        mentor_id   = mentor.id,
        sujet       = sujet
    )
    db.session.add(demande)
    db.session.commit()

    flash(f"Demande envoyée à {mentor.prenom} {mentor.nom} !", "success")
    return redirect(url_for("auth.dashboard"))


# ------------------------------------------------------------------
# LISTE DES DEMANDES  /demandes
# ------------------------------------------------------------------
@auth_bp.route("/demandes")
@login_required
def demandes():
    """Liste des demandes envoyées par l'utilisateur connecté."""
    mes_demandes = DemandeMentorat.query.filter_by(
        etudiant_id=current_user.id
    ).order_by(DemandeMentorat.date_demande.desc()).all()

    return render_template("demandes.html", demandes=mes_demandes)


# ------------------------------------------------------------------
# MESSAGES  /messages
# ------------------------------------------------------------------
@auth_bp.route("/messages")
@login_required
def messages():
    messages_recus = current_user.messages_recus
    return render_template("messages.html", messages=messages_recus)