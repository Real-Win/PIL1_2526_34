from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, jsonify
)
from flask_login import (
    login_user, logout_user,
    login_required, current_user
)
from app import db
from app.models import (Competence, UserCompetence, UserLacune, Lacune,
                         Disponibilite, User, DemandeMentorat)
from app.matching import calculer_match, get_top_mentors, get_top_mentores
from app.securite import inscrire_etudiant, verifier_connexion, demander_reinitialisation, reinitialiser_mot_de_passe


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
# TOP 3
# ------------------------------------------------------------------
@matching_bp.route("/top3/<int:user_id>")
@login_required
def top3(user_id):
    user    = User.query.get_or_404(user_id)
    cherche = request.args.get("cherche", "").strip()
    autres  = User.query.filter(User.id != user_id).all()

    if not cherche:
        cherche = "mentore" if user.role == "mentor" else "mentor"

    if cherche == "mentore":
        result = get_top_mentores(user, autres)
    else:
        result = get_top_mentors(user, autres)

    return jsonify(result)


# ------------------------------------------------------------------
# API PROFIL UTILISATEUR
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

    top_mentors  = []
    top_mentores = []

    if current_user.role in ("etudiant", "mentore", "les_deux"):
        for item in get_top_mentors(current_user, autres_users):
            mentor = User.query.get(item["mentor_id"])
            if mentor:
                top_mentors.append({"user": mentor, "score": item["score"]})

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
            niveau       = request.form.get("niveau", "L1"),
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
# PROFIL (son propre profil)  /profil
# ------------------------------------------------------------------
@auth_bp.route("/profil", methods=["GET"])
@login_required
def profil():
    return render_template("profil.html", profil=current_user, demande_existante=None)


# ------------------------------------------------------------------
# MODIFICATION PROFIL  /profil/modifier
# ------------------------------------------------------------------
@auth_bp.route("/profil/modifier", methods=["GET", "POST"])
@login_required
def profil_modifier():
    if request.method == "POST":
        from app.models import Competence, UserCompetence, Disponibilite, Lacune, UserLacune
        from datetime import datetime

        current_user.nom     = request.form.get("nom",     current_user.nom)
        current_user.prenom  = request.form.get("prenom",  current_user.prenom)
        current_user.filiere = request.form.get("filiere", current_user.filiere)
        current_user.niveau  = request.form.get("niveau",  current_user.niveau)
        current_user.role    = request.form.get("role",    current_user.role)
        current_user.bio     = request.form.get("bio",     current_user.bio)

        competences_raw = request.form.get("competences", "").strip()
        lacunes_raw     = request.form.get("lacunes", "").strip()

        UserLacune.query.filter_by(user_id=current_user.id).delete()
        if lacunes_raw:
            for nom_lacune in [l.strip().lower() for l in lacunes_raw.split(",") if l.strip()]:
                lacune = Lacune.query.filter_by(nom=nom_lacune).first()
                if not lacune:
                    lacune = Lacune(nom=nom_lacune)
                    db.session.add(lacune)
                    db.session.flush()
                db.session.add(UserLacune(user_id=current_user.id, lacune_id=lacune.id))

        UserCompetence.query.filter_by(user_id=current_user.id).delete()
        if competences_raw:
            for nom_comp in [c.strip().lower() for c in competences_raw.split(",") if c.strip()]:
                comp = Competence.query.filter_by(nom=nom_comp).first()
                if not comp:
                    comp = Competence(nom=nom_comp)
                    db.session.add(comp)
                    db.session.flush()
                db.session.add(UserCompetence(user_id=current_user.id, competence_id=comp.id))

        jours        = request.form.getlist("jours[]")
        heures_debut = request.form.getlist("heures_debut[]")
        heures_fin   = request.form.getlist("heures_fin[]")

        Disponibilite.query.filter_by(user_id=current_user.id).delete()
        for jour, debut, fin in zip(jours, heures_debut, heures_fin):
            if jour and debut and fin:
                db.session.add(Disponibilite(
                    user_id      = current_user.id,
                    jour_semaine = jour,
                    heure_debut  = datetime.strptime(debut, "%H:%M").time(),
                    heure_fin    = datetime.strptime(fin,   "%H:%M").time()
                ))

        db.session.commit()
        flash("Profil mis à jour avec succès.", "success")
        return redirect(url_for("auth.profil"))

    return render_template("profil_edit.html", user=current_user)


# ------------------------------------------------------------------
# PROFIL PUBLIC  /profil/<user_id>  — lecture seule
# ------------------------------------------------------------------
@auth_bp.route("/profil/<int:user_id>")
@login_required
def profil_public(user_id):
    profil = User.query.get_or_404(user_id)

    if profil.id == current_user.id:
        return redirect(url_for("auth.profil"))

    demande_existante = DemandeMentorat.query.filter(
        db.or_(
            db.and_(
                DemandeMentorat.etudiant_id == current_user.id,
                DemandeMentorat.mentor_id   == profil.id
            ),
            db.and_(
                DemandeMentorat.etudiant_id == profil.id,
                DemandeMentorat.mentor_id   == current_user.id
            )
        )
    ).first()

    return render_template(
        "profil.html",
        profil=profil,
        demande_existante=demande_existante
    )


# ------------------------------------------------------------------
# PAGE MATCHING  /matching
# ------------------------------------------------------------------
@auth_bp.route("/matching")
@login_required
def matching_page():
    return render_template("matching.html", user=current_user)


# ------------------------------------------------------------------
# CRÉER UNE DEMANDE DE MENTORAT  /demande/<cible_id>
# ------------------------------------------------------------------
@auth_bp.route("/demande/<int:cible_id>", methods=["POST"])
@login_required
def creer_demande(cible_id):
    cible = User.query.get_or_404(cible_id)
    sujet = request.form.get("sujet", "").strip()

    if not sujet:
        flash("Le sujet de la demande ne peut pas être vide.", "danger")
        return redirect(url_for("auth.matching_page"))

    if current_user.role in ("mentor", "les_deux") and cible.role not in ("mentor",):
        etudiant_id = cible.id
        mentor_id   = current_user.id
    else:
        etudiant_id = current_user.id
        mentor_id   = cible.id

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
# ------------------------------------------------------------------
@auth_bp.route("/demande/<int:demande_id>/statut", methods=["POST"])
@login_required
def changer_statut_demande(demande_id):
    demande = DemandeMentorat.query.get_or_404(demande_id)

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


# ⭐⭐⭐ NOUVEAU : RÉINITIALISATION MOT DE PASSE ⭐⭐⭐

# ------------------------------------------------------------------
# DEMANDE DE RÉINITIALISATION  /reinitialisation
# ------------------------------------------------------------------
@auth_bp.route("/reinitialisation", methods=["GET", "POST"])
def demande_reinitialisation():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        if email:
            success, message = demander_reinitialisation(email)
            flash(message, "success" if success else "danger")
            if success:
                return redirect(url_for("auth.connexion"))
        else:
            flash("Veuillez entrer votre adresse email.", "danger")

    return render_template("reinitialisation.html")


# ------------------------------------------------------------------
# NOUVEAU MOT DE PASSE  /reinitialisation/<token>
# ------------------------------------------------------------------
@auth_bp.route("/reinitialisation/<token>", methods=["GET", "POST"])
def nouveau_mot_de_passe(token):
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        mot_de_passe = request.form.get("mot_de_passe")
        confirmation = request.form.get("confirmation")

        if not mot_de_passe or len(mot_de_passe) < 6:
            flash("Le mot de passe doit contenir au moins 6 caractères.", "danger")
        elif mot_de_passe != confirmation:
            flash("Les mots de passe ne correspondent pas.", "danger")
        else:
            success, message = reinitialiser_mot_de_passe(token, mot_de_passe)
            flash(message, "success" if success else "danger")
            if success:
                return redirect(url_for("auth.connexion"))

    return render_template("nouveau_mot_de_passe.html", token=token)