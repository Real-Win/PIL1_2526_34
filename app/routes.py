from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.matching import calculer_match, get_top_mentors
from app.securite import inscrire_etudiant, verifier_connexion
# ===== MATCHING BLUEPRINT =====
matching_bp = Blueprint("matching", __name__)

@matching_bp.route("/match", methods=["POST"])
def match():
    data = request.json

    mentore = data.get("mentore")
    mentor = data.get("mentor")

    if not mentore or not mentor:
        return jsonify({"error": "Donnees manquantes"}), 400

    mentore = data["mentore"]
    mentor = data["mentor"]

    score = calculer_match(mentore, mentor)

    return jsonify({
        "score": score,
        "bon_match": score >= 60
    })


@matching_bp.route("/top3", methods=["POST"])
def top3():
    data = request.json
    mentore = data.get("mentore")
    mentors = data.get("mentors")

    if not mentore or not mentors:
        return jsonify({"error": "Donnees manquantes"}), 400
    mentore = data["mentore"]
    mentors = data["mentors"]

    result = get_top_mentors(mentore, mentors)

    return jsonify(result)


# ===== AUTHENTIFICATION BLUEPRINT =====
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/inscription", methods=["GET", "POST"])
def inscription():
    if current_user.is_authenticated:
        return redirect(url_for("auth.profil"))
    
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        telephone = request.form.get("telephone")
        filiere = request.form.get("filiere")
        role = request.form.get("role", "etudiant")
        mot_de_passe = request.form.get("mot_de_passe")
        
        success, message = inscrire_etudiant(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            filiere=filiere,
            role=role,
            mot_de_passe=mot_de_passe
        )
        
        if success:
            flash("Inscription reussie ! Veuillez vous connecter.", "success")
            return redirect(url_for("auth.connexion"))
        else:
            flash(message, "danger")
    
    return render_template("inscription.html")


@auth_bp.route("/connexion", methods=["GET", "POST"])
def connexion():
    if current_user.is_authenticated:
        return redirect(url_for("auth.profil"))
    
    if request.method == "POST":
        email = request.form.get("email")
        mot_de_passe = request.form.get("mot_de_passe")
        
        user, message = verifier_connexion(email, mot_de_passe)
        
        if user:
            login_user(user, remember=True)
            flash("Connexion reussie !", "success")
            return redirect(url_for("auth.profil"))
        else:
            flash(message, "danger")
    
    return render_template("connexion.html")


@auth_bp.route("/deconnexion", methods=["GET"])
@login_required
def deconnexion():
    logout_user()
    flash("Vous avez ete deconnecte.", "info")
    return redirect(url_for("auth.connexion"))


@auth_bp.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    if request.method == "POST":
        # Modification du profil
        current_user.bio = request.form.get("bio")
        
        db.session.commit()
        flash("Profil mis a jour !", "success")
        return redirect(url_for("auth.profil"))
    
    return render_template("profil.html", user=current_user)


@auth_bp.route("/messages", methods=["GET"])
@login_required
def messages():
    """Affiche les messages recus"""
    messages_recus = current_user.messages_recus
    return render_template("messages.html", messages=messages_recus)


@auth_bp.route("/matching", methods=["GET"])
@login_required
def matching_page():
    """Page du systeme de matching"""
    return render_template("matching.html")
