from datetime import datetime

SEUIL_MATCH = 60


# ═══════════════════════════════════════════════════════════
#  SCORE ENTRE DEUX UTILISATEURS (matching par profil)
# ═══════════════════════════════════════════════════════════

# -------------------------
# COMPÉTENCES (sur 50)
# -------------------------
def calculer_score_competences(mentore, mentor):
    competences_mentore = {c.nom.strip().lower() for c in mentore.competences}
    competences_mentor  = {c.nom.strip().lower() for c in mentor.competences}

    if not competences_mentore:
        return 0

    communes = competences_mentore & competences_mentor
    return (len(communes) / len(competences_mentore)) * 50


# -------------------------
# OVERLAP HEURES (utilitaire)
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
# -----------------------------------------------------------
def get_top_mentors(mentore, liste_users):
    resultats = []

    for user in liste_users:
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
# -----------------------------------------------------------
def get_top_mentores(mentor, liste_users):
    resultats = []

    for user in liste_users:
        if user.role == "mentor":
            continue
        score = calculer_match(user, mentor)
        resultats.append({
            "mentore_id": user.id,
            "score":      score
        })

    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats[:3]


# ═══════════════════════════════════════════════════════════
#  SCORE ENTRE DEUX PUBLICATIONS (offres / demandes)
# ═══════════════════════════════════════════════════════════

def _parser_disponibilites(dispos_str):
    """
    Parse une chaîne "Lundi 14:00-17:00, Jeudi 10:00-12:00"
    Retourne une liste de dicts {jour, debut, fin, raw}
    """
    if not dispos_str:
        return []

    result = []
    for creneau in dispos_str.split(','):
        creneau = creneau.strip()
        parts   = creneau.split(' ')
        if len(parts) >= 2:
            jour   = parts[0]
            heures = parts[1].split('-')
            if len(heures) == 2:
                result.append({
                    'jour':  jour,
                    'debut': heures[0].strip(),
                    'fin':   heures[1].strip(),
                    'raw':   creneau
                })
    return result


def calculer_score_offre_demande(pub1, pub2):
    """
    Score de compatibilité entre deux publications (offre ↔ demande).
    Score sur 100 :
      - Matières communes   : 50 pts
      - Format compatible   : 20 pts
      - Disponibilités communes : 30 pts
    """
    score = 0

    # Matières communes (50 pts)
    m1 = {m.strip().lower() for m in pub1.matieres.split(',') if m.strip()}
    m2 = {m.strip().lower() for m in pub2.matieres.split(',') if m.strip()}
    communes = m1 & m2
    if m1:
        score += (len(communes) / len(m1)) * 50

    # Format compatible (20 pts)
    if pub1.format and pub2.format:
        if pub1.format == pub2.format:
            score += 20
        elif pub1.format == 'les_deux' or pub2.format == 'les_deux':
            score += 15

    # Disponibilités communes (30 pts)
    d1 = _parser_disponibilites(pub1.disponibilites)
    d2 = _parser_disponibilites(pub2.disponibilites)

    if d1 and d2:
        for c1 in d1:
            for c2 in d2:
                if c1['jour'].lower() == c2['jour'].lower():
                    debut = max(c1['debut'], c2['debut'])
                    fin   = min(c1['fin'],   c2['fin'])
                    if debut < fin:
                        score += 30
                        break
            else:
                continue
            break

    return round(score, 2)


def get_meilleures_correspondances(ma_pub, autres_pubs):
    """
    Trouve les 3 meilleures publications compatibles avec ma_pub.
    Retourne une liste de dicts :
      - publication       : objet OffreDemande
      - auteur            : objet User
      - score             : float
      - matieres_communes : list[str]
      - dispos_communes   : list[str]
    """
    resultats = []

    for pub in autres_pubs:
        score = calculer_score_offre_demande(ma_pub, pub)

        m1 = {m.strip().lower() for m in ma_pub.matieres.split(',') if m.strip()}
        m2 = {m.strip().lower() for m in pub.matieres.split(',')    if m.strip()}
        matieres_communes = sorted(m1 & m2)

        d1 = _parser_disponibilites(ma_pub.disponibilites)
        d2 = _parser_disponibilites(pub.disponibilites)
        dispos_communes = []
        for c1 in d1:
            for c2 in d2:
                if c1['jour'].lower() == c2['jour'].lower():
                    debut = max(c1['debut'], c2['debut'])
                    fin   = min(c1['fin'],   c2['fin'])
                    if debut < fin:
                        dispos_communes.append(f"{c1['jour']} {debut}–{fin}")

        resultats.append({
            "publication":       pub,
            "auteur":            pub.auteur,
            "score":             score,
            "matieres_communes": matieres_communes,
            "dispos_communes":   dispos_communes
        })

    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats[:3]
