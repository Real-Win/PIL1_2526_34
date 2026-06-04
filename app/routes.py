from flask import Blueprint, jsonify, request
from app.matching import calculer_match, get_top_mentors

matching_bp = Blueprint("matching", __name__)


@matching_bp.route("/match", methods=["POST"])
def match():
    data = request.json

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

    mentore = data["mentore"]
    mentors = data["mentors"]

    result = get_top_mentors(mentore, mentors)

    return jsonify(result)