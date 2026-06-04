from datetime import datetime

SEUIL_MATCH = 60


def calculer_score_competences(faiblesses_mentore, forces_mentor):
    n = len(faiblesses_mentore)
    if n == 0:
        return 0

    K = len(set(faiblesses_mentore) & set(forces_mentor))
    return (K / n) * 50


def overlap(debut1, fin1, debut2, fin2):
    debut = max(debut1, debut2)
    fin = min(fin1, fin2)

    if debut >= fin:
        return 0

    return (fin - debut).seconds


def calculer_score_disponibilite(dispo_mentore, dispo_mentor):
    meilleur_score = 0

    for jour_m, hdm, hfm in dispo_mentore:
        for jour_M, hdM, hfM in dispo_mentor:

            if jour_m != jour_M:
                continue

            hdm = datetime.strptime(hdm, "%H:%M")
            hfm = datetime.strptime(hfm, "%H:%M")
            hdM = datetime.strptime(hdM, "%H:%M")
            hfM = datetime.strptime(hfM, "%H:%M")

            chevauchement = overlap(hdm, hfm, hdM, hfM)

            if chevauchement > 0:
                duree_mentore = (hfm - hdm).seconds
                score = (chevauchement / duree_mentore) * 30

                if score > meilleur_score:
                    meilleur_score = score

    return meilleur_score


def calculer_match(mentore, mentor):
    score_comp = calculer_score_competences(
        mentore["faiblesses"],
        mentor["forces"]
    )

    score_time = calculer_score_disponibilite(
        mentore["disponibilites"],
        mentor["disponibilites"]
    )

    return score_comp + score_time + 20


def quality_match(mentore, mentor):
    score = calculer_match(mentore, mentor)

    return {
        "score": score,
        "bon_match": score >= SEUIL_MATCH
    }


def get_top_mentors(mentore, liste_mentors):
    resultats = []

    for mentor in liste_mentors:
        score = calculer_match(mentore, mentor)
        resultats.append({
            "mentor": mentor,
            "score": score
        })

    resultats.sort(key=lambda x: x["score"], reverse=True)

    return resultats[:3]