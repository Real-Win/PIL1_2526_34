from datetime import datetime

SEUIL_MATCH = 60


# -------------------------
# COMPÉTENCES (sur 50)
# -------------------------
def calculer_score_competences(mentore, mentor):
    """
    Compare les compétences du mentoré avec celles du mentor.
    Le mentoré cherche un mentor qui MAÎTRISE ce qu'il ne maîtrise pas.
    Donc on compare : compétences du mentoré VS compétences du mentor.
    """
    competences_mentore = {c.nom.strip().lower() for c in mentore.competences}
    competences_mentor  = {c.nom.strip().lower() for c in mentor.competences}

    if not competences_mentore:
        return 0

    communes = competences_mentore & competences_mentor
    return (len(communes) / len(competences_mentore)) * 50


# -------------------------
# OVERLAP HEURES
# -------------------------
def overlap(debut1, fin1, debut2, fin2):
    debut = max(debut1, debut2)
    fin   = min(fin1,   fin2)

    if debut >= fin:
        return 0

    return (fin - debut).seconds


# -------------------------
# DISPONIBILITÉ (sur 30)
# -------------------------
def calculer_score_disponibilite(mentore, mentor):

    meilleur_score = 0

    for dispo_m in mentore.disponibilites:
        for dispo_M in mentor.disponibilites:

            if dispo_m.jour_semaine != dispo_M.jour_semaine:
                continue

            hdm = datetime.strptime(dispo_m.heure_debut.strftime("%H:%M"), "%H:%M")
            hfm = datetime.strptime(dispo_m.heure_fin.strftime("%H:%M"),   "%H:%M")
            hdM = datetime.strptime(dispo_M.heure_debut.strftime("%H:%M"), "%H:%M")
            hfM = datetime.strptime(dispo_M.heure_fin.strftime("%H:%M"),   "%H:%M")

            chevauchement = overlap(hdm, hfm, hdM, hfM)

            if chevauchement > 0:
                duree = (hfm - hdm).seconds
                if duree == 0:
                    continue
                score = (chevauchement / duree) * 30
                meilleur_score = max(meilleur_score, score)

    return meilleur_score


# -------------------------
# FILIÈRE (sur 20)
# -------------------------
def calculer_score_filiere(mentore, mentor):
    if mentore.filiere == mentor.filiere:
        return 20
    return 10


# -------------------------
# SCORE TOTAL
# -------------------------
def calculer_match(mentore, mentor):
    score_comp    = calculer_score_competences(mentore, mentor)
    score_dispo   = calculer_score_disponibilite(mentore, mentor)
    score_filiere = calculer_score_filiere(mentore, mentor)
    return round(score_comp + score_dispo + score_filiere, 2)


# -------------------------
# QUALITÉ MATCH
# -------------------------
def quality_match(mentore, mentor):
    score = calculer_match(mentore, mentor)
    return {
        "score":     score,
        "bon_match": score >= SEUIL_MATCH
    }


# -----------------------------------------------------------
# TOP 3 MENTORS  (l'utilisateur est mentoré → cherche mentor)
# On cherche parmi les users qui ont rôle mentor ou les_deux
# -----------------------------------------------------------
def get_top_mentors(mentore, liste_users):
    """
    Retourne les 3 meilleurs mentors pour un mentoré donné.
    liste_users : tous les users sauf mentore lui-même.
    On ne garde que ceux qui peuvent être mentors (role in ['mentor','les_deux']).
    """
    resultats = []

    for user in liste_users:
        # Seuls les vrais mentors peuvent être proposés
        if user.role not in ("mentor", "les_deux"):
            continue

        score = calculer_match(mentore, user)
        resultats.append({
            "mentor_id": user.id,
            "score":     score
        })

    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats[:3]


# -----------------------------------------------------------
# TOP 3 MENTORÉS  (l'utilisateur est mentor → cherche qui aider)
# On cherche parmi les users qui ont rôle mentore ou les_deux
# -----------------------------------------------------------
def get_top_mentores(mentor, liste_users):
    """
    Retourne les 3 meilleurs mentorés pour un mentor donné.
    liste_users : tous les users sauf mentor lui-même.
    On ne garde que ceux qui peuvent être mentorés (role in ['etudiant','mentore','les_deux']).
    """
    resultats = []

    for user in liste_users:
        # On exclut les purs mentors (ils ne cherchent pas à être mentorés)
        if user.role == "mentor":
            continue

        # Ici le score se calcule en considérant `user` comme le mentoré
        score = calculer_match(user, mentor)
        resultats.append({
            "mentore_id": user.id,
            "score":      score
        })

    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats[:3]
