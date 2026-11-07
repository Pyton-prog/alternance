"""Récupère de vraies offres d'alternance via l'API France Travail et écrit data/offers.json."""
import json, os, re, time, unicodedata, urllib.parse, urllib.request

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
API = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
PER = 40  # offres max par requête (API : 150 max)

def nrm(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()

def token():
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": os.environ["FT_CLIENT_ID"],
        "client_secret": os.environ["FT_CLIENT_SECRET"],
        "scope": "api_offresdemploiv2 o2dsoffre",
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=data), timeout=30) as r:
        return json.load(r)["access_token"]

def get(url, tok):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            b = r.read()
            return json.loads(b) if b else {}
    except Exception as e:
        print("erreur:", e)
        return {}

doms = json.load(open("domains.json", encoding="utf-8"))
SK = {}
for d in doms:
    for s in d["s"]:
        SK[s.split("|")[0]] = [
            re.compile(r"(?<![a-z0-9+#])" + re.escape(nrm(k)) + r"(?![a-z0-9+#])") for k in s.split("|")
        ]

tok = token()
offers = {}
for d in doms:
    for q in d["q"]:
        for nature in ("E2", "E3"):  # E2 apprentissage, E3 professionnalisation
            url = API + "?" + urllib.parse.urlencode(
                {"motsCles": q, "natureContrat": nature, "range": f"0-{PER - 1}"})
            for o in get(url, tok).get("resultats", []):
                if o["id"] in offers:
                    continue
                txt = nrm(o.get("intitule", "") + " " + o.get("description", ""))
                skills = [k for k, res in SK.items() if any(r.search(txt) for r in res)]
                for c in o.get("competences", [])[:6]:
                    lib = c.get("libelle", "").strip()
                    if lib and lib not in skills:
                        skills.append(lib)
                offers[o["id"]] = {
                    "id": o["id"], "g": d["id"], "t": o.get("intitule", ""),
                    "c": o.get("entreprise", {}).get("nom", ""),
                    "l": o.get("lieuTravail", {}).get("libelle", ""),
                    "d": o.get("dateCreation", "")[:10],
                    "u": o.get("origineOffre", {}).get("urlOrigine")
                         or "https://candidat.francetravail.fr/offres/recherche/detail/" + o["id"],
                    "x": " ".join(o.get("description", "").split())[:200],
                    "s": skills[:12],
                }
            time.sleep(0.3)
    print(d["n"], len(offers))

os.makedirs("data", exist_ok=True)
with open("data/offers.json", "w", encoding="utf-8") as f:
    json.dump({"updated": time.strftime("%Y-%m-%d"), "offers": list(offers.values())},
              f, ensure_ascii=False, separators=(",", ":"))
print(len(offers), "offres enregistrées")
