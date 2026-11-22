import html
import json
import random
import re
import urllib.parse
import urllib.request

API_URL = "https://fr.wikiquote.org/w/api.php"
HEADERS = {"User-Agent": "MonProjetCitationsFilms/1.0 (contact@exemple.fr)"}

# Catégories principales de films sur fr.wikiquote.org
CATEGORIES_FILMS = [
    "Catégorie:Film français",
    "Catégorie:Film américain",
]


def appel_api(params):
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{API_URL}?{query}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read().decode("utf-8"))


def nettoyer_html(texte_html):
    texte = re.sub(r"<br\s*/?>", "\n", texte_html)
    texte = re.sub(r"<[^>]+>", " ", texte)
    texte = html.unescape(texte)
    lignes = [re.sub(r"\s+", " ", l).strip() for l in texte.splitlines()]
    return "\n".join(l for l in lignes if l)


def extraire_realisateur(raw_html):
    # Nettoie les balises pour lire le texte d'introduction de la page
    texte_intro = re.sub(r"<[^>]+>", " ", raw_html)
    texte_intro = html.unescape(texte_intro)
    texte_intro = re.sub(r"\s+", " ", texte_intro)

    # Cherche les formulations classiques sur Wikiquote FR :
    # "réalisé par ...", "film de ...", "Réalisation : ..."
    patterns = [
        r"réalisé par\s+([A-ZÀ-Ÿ][a-zà-ÿ'-]+(?:\s+(?:de|du|van|von|le|la|des|[A-ZÀ-Ÿ][a-zà-ÿ'-]+)){1,3})",
        r"Réalisation\s*:\s*([A-ZÀ-Ÿ][a-zà-ÿ'-]+(?:\s+(?:de|du|van|von|le|la|des|[A-ZÀ-Ÿ][a-zà-ÿ'-]+)){1,3})",
        r"film [^,.()]+? de\s+([A-ZÀ-Ÿ][a-zà-ÿ'-]+(?:\s+(?:de|du|van|von|le|la|des|[A-ZÀ-Ÿ][a-zà-ÿ'-]+)){1,3})",
    ]

    for pattern in patterns:
        match = re.search(pattern, texte_intro)
        if match:
            return match.group(1).strip(" ,.;:")

    return "Réalisateur non renseigné"


def extraire_infos_film(titre):
    data = appel_api({
        "action": "parse",
        "page": titre,
        "prop": "text",
        "format": "json"
    })
    raw_html = data.get("parse", {}).get("text", {}).get("*", "")

    # 1. Extraction des citations
    blocs = re.findall(r'<div class="citation"[^>]*>(.*?)</div>', raw_html, flags=re.S)
    citations = [nettoyer_html(b) for b in blocs if len(nettoyer_html(b)) > 10]

    if not citations:
        return None

    # 2. Extraction du réalisateur
    realisateur = extraire_realisateur(raw_html)

    # Nettoie le titre (enlève "(film)" s'il est présent dans le titre Wiki)
    titre_propre = re.sub(r"\s*\(film[^)]*\)", "", titre).strip()

    return {
        "film": titre_propre,
        "realisateur": realisateur,
        "replique": random.choice(citations),
    }


def replique_film_aleatoire():
    while True:
        categorie = random.choice(CATEGORIES_FILMS)
        data = appel_api({
            "action": "query",
            "list": "categorymembers",
            "cmtitle": categorie,
            "cmtype": "page",      # Exclut les sous-catégories
            "cmlimit": 500,        # Récupère jusqu'à 500 films de la catégorie
            "format": "json"
        })

        pages = data.get("query", {}).get("categorymembers", [])
        if not pages:
            continue

        film_choisi = random.choice(pages)["title"]
        infos = extraire_infos_film(film_choisi)

        if infos:
            return infos

def renvoieDeDonnee():
	resultat = replique_film_aleatoire()
	while resultat['realisateur']=="Réalisateur non renseigné":
		resultat = replique_film_aleatoire()
	return resultat
if __name__ == "__main__":
    resultat = renvoieDeDonnee()
    	
    print(f"« {resultat['replique']} »")
    print(f"— {resultat['film']} (réalisé par {resultat['realisateur']})")
