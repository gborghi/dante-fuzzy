#!/usr/bin/env python3
"""Build site/data/elementi.json: characters, themes, vices, virtues,
commandments, and later authors — each locus resolved against the tercet text."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path("/Users/g.borghi/ICT/dante-fuzzy")
TERZ = json.loads((ROOT / "data/terzine.json").read_text())


def fold(s: str) -> str:
    s = (s or "").lower().replace("’", "'").replace("`", "'")
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


INDEX = []
for row in TERZ:
    INDEX.append({
        "cantica": row["volume"],
        "canto": int(row["canto"]),
        "tercet": int(row["tercet"]),
        "text": row.get("text") or "",
        "fold": fold(row.get("text") or ""),
        "id": row.get("Tercet_ID"),
    })


def find_rx(pattern: str, limit: int = 40) -> list[dict]:
    rx = re.compile(pattern, re.I)
    out = []
    for r in INDEX:
        if rx.search(r["fold"]):
            out.append(locus(r))
            if len(out) >= limit:
                break
    return out


def find_canto(cantica: str, canto: int, tercet: int | None = None) -> dict | None:
    for r in INDEX:
        if r["cantica"] == cantica and r["canto"] == canto:
            if tercet is None or r["tercet"] == tercet:
                return locus(r)
    return None


def locus(r: dict) -> dict:
    snip = re.sub(r"\s+", " ", r["text"]).strip()
    if len(snip) > 180:
        snip = snip[:177] + "…"
    return {
        "cantica": r["cantica"],
        "canto": r["canto"],
        "tercet": r["tercet"],
        "snippet": snip,
    }


def pin(*triples, fallback_rx=None, limit=12):
    """Prefer explicit (cantica, canto, tercet) pins; fill with regex hits."""
    seen = set()
    out = []
    for c, n, t in triples:
        loc = find_canto(c, n, t)
        if not loc:
            loc = find_canto(c, n, None)
        if loc:
            k = (loc["cantica"], loc["canto"], loc["tercet"])
            if k not in seen:
                seen.add(k)
                out.append(loc)
    if fallback_rx:
        for loc in find_rx(fallback_rx, limit=limit):
            k = (loc["cantica"], loc["canto"], loc["tercet"])
            if k not in seen:
                seen.add(k)
                out.append(loc)
    return out


# ── 7 vices (Purgatorio terraces) + Inferno circles ──────────
VIZI = [
    {
        "id": "lussuria",
        "name": "Lussuria",
        "luogo": "Inferno II cerchio; Purgatorio VII cornice",
        "comandamenti": ["VI"],
        "virtu_contraria": "castita",
        "pins": [("Inferno", 5, 1), ("Purgatorio", 25, 1), ("Purgatorio", 26, 1)],
        "rx": r"\blussur|\bfrancesca\b|\bpaolo\b|\bfolle amor",
    },
    {
        "id": "gola",
        "name": "Gola",
        "luogo": "Inferno III cerchio; Purgatorio VI cornice",
        "comandamenti": ["X"],
        "virtu_contraria": "temperanza",
        "pins": [("Inferno", 6, 1), ("Purgatorio", 23, 1), ("Purgatorio", 24, 1)],
        "rx": r"\bciacco\b|\bgola\b|\bghiott",
    },
    {
        "id": "avarizia",
        "name": "Avarizia e prodigalità",
        "luogo": "Inferno IV cerchio; Purgatorio V cornice",
        "comandamenti": ["VII", "X"],
        "virtu_contraria": "liberalita",
        "pins": [("Inferno", 7, 1), ("Purgatorio", 19, 1), ("Purgatorio", 20, 1)],
        "rx": r"\bavar|\bprodigal|\bpluto\b|\bpapa adrian",
    },
    {
        "id": "ira",
        "name": "Ira e accidia fangosa",
        "luogo": "Inferno V cerchio (Stige); Purgatorio III cornice",
        "comandamenti": ["V"],
        "virtu_contraria": "mansuetudine",
        "pins": [("Inferno", 7, 30), ("Inferno", 8, 1), ("Purgatorio", 15, 1), ("Purgatorio", 16, 1)],
        "rx": r"\bira\b|\birac|\bfilippo argenti|\bstige",
    },
    {
        "id": "accidia",
        "name": "Accidia",
        "luogo": "Purgatorio IV cornice; Inferno Stige (ignavi sommersi)",
        "comandamenti": ["III"],
        "virtu_contraria": "fortezza",
        "pins": [("Purgatorio", 17, 1), ("Purgatorio", 18, 1), ("Inferno", 3, 10)],
        "rx": r"\baccid|\bnegligent|\bpigr",
    },
    {
        "id": "eresia",
        "name": "Eresia",
        "luogo": "Inferno VI cerchio (sepolcri infuocati)",
        "comandamenti": ["I"],
        "virtu_contraria": "fede",
        "pins": [("Inferno", 9, 30), ("Inferno", 10, 1), ("Inferno", 11, 1)],
        "rx": r"\beresi|\bfarinata\b|\bepicur",
    },
    {
        "id": "violenza",
        "name": "Violenza",
        "luogo": "Inferno VII cerchio (Flegetonte, suicidi, sodomiti, usurai)",
        "comandamenti": ["V", "VII"],
        "virtu_contraria": "giustizia",
        "pins": [("Inferno", 12, 1), ("Inferno", 13, 1), ("Inferno", 15, 1)],
        "rx": r"\bviolenz|\bflegetonta|\bpier de la vigna|\bbrunetto",
    },
    {
        "id": "frode",
        "name": "Frode (Malebolge)",
        "luogo": "Inferno VIII cerchio",
        "comandamenti": ["VIII", "II", "VII"],
        "virtu_contraria": "verita",
        "pins": [("Inferno", 18, 1), ("Inferno", 26, 1), ("Inferno", 27, 1)],
        "rx": r"\bmalebolg|\bulisse\b|\bdiomede|\bguido da montefeltro",
    },
    {
        "id": "tradimento",
        "name": "Tradimento (Cocito)",
        "luogo": "Inferno IX cerchio",
        "comandamenti": ["V", "VIII"],
        "virtu_contraria": "fedelta",
        "pins": [("Inferno", 32, 1), ("Inferno", 33, 1), ("Inferno", 34, 1)],
        "rx": r"\bcocito|\bugolin|\bruggeri|\blucifero|\bgiuda\b|\bbruto\b|\bcassio",
    },
    {
        "id": "superbia",
        "name": "Superbia",
        "luogo": "Purgatorio I cornice",
        "comandamenti": ["I"],
        "virtu_contraria": "umilta",
        "pins": [("Purgatorio", 10, 1), ("Purgatorio", 11, 1), ("Purgatorio", 12, 1)],
        "rx": r"\bsuperbi|\bumilta|\boderisi|\bomberto aldobrandeschi",
    },
    {
        "id": "invidia",
        "name": "Invidia",
        "luogo": "Purgatorio II cornice",
        "comandamenti": ["X"],
        "virtu_contraria": "carita",
        "pins": [("Purgatorio", 13, 1), ("Purgatorio", 14, 1)],
        "rx": r"\binvidi|\bsapia\b",
    },
]

VIRTU = [
    {
        "id": "fede",
        "name": "Fede",
        "luogo": "Paradiso XXIV (esame di san Pietro)",
        "comandamenti": ["I"],
        "pins": [("Paradiso", 24, 1)],
        "rx": r"\bfede\b|\bsan pietro|\bpietro\b",
    },
    {
        "id": "speranza",
        "name": "Speranza",
        "luogo": "Paradiso XXV (esame di san Giacomo)",
        "comandamenti": ["I"],
        "pins": [("Paradiso", 25, 1)],
        "rx": r"\bsperanza\b|\bgiacomo\b",
    },
    {
        "id": "carita",
        "name": "Carità",
        "luogo": "Paradiso XXVI (esame di san Giovanni); contrario dell'invidia",
        "comandamenti": ["I", "X"],
        "pins": [("Paradiso", 26, 1), ("Purgatorio", 15, 1)],
        "rx": r"\bcarita\b|\bcarità|\bamor che move",
    },
    {
        "id": "umilta",
        "name": "Umiltà",
        "luogo": "Purgatorio I cornice (esempi: Maria, Davide, Traiano)",
        "comandamenti": ["I"],
        "pins": [("Purgatorio", 10, 10)],
        "rx": r"\bumil",
    },
    {
        "id": "giustizia",
        "name": "Giustizia",
        "luogo": "Paradiso VI (Giustiniano); cielo di Giove (aquila)",
        "comandamenti": ["V", "VII", "VIII"],
        "pins": [("Paradiso", 6, 1), ("Paradiso", 18, 1), ("Paradiso", 19, 1)],
        "rx": r"\bgiustiz|\bgiustiniano|\baquila",
    },
    {
        "id": "temperanza",
        "name": "Temperanza",
        "luogo": "Purgatorio VI cornice; Paradiso cielo del Sole",
        "comandamenti": ["VI", "X"],
        "pins": [("Purgatorio", 22, 1), ("Paradiso", 10, 1)],
        "rx": r"\btemperan|\bfren",
    },
    {
        "id": "prudenza",
        "name": "Prudenza / sapienza",
        "luogo": "Virgilio come guida; Paradiso cielo del Sole (Sapienza)",
        "comandamenti": ["I"],
        "pins": [("Inferno", 1, 27), ("Paradiso", 10, 1), ("Paradiso", 11, 1)],
        "rx": r"\bvirtute e canoscenza|\bsapienz|\bthomas\b|\btommaso",
    },
    {
        "id": "fortezza",
        "name": "Fortezza",
        "luogo": "Contrario dell'accidia; Cacciaguida (croce di Marte)",
        "comandamenti": ["III"],
        "pins": [("Paradiso", 15, 1), ("Paradiso", 17, 1)],
        "rx": r"\bcacciaguida|\bmarte\b",
    },
    {
        "id": "castita",
        "name": "Castità / amore ordinato",
        "luogo": "Purgatorio VII cornice; Beatrice; cielo di Venere purificato",
        "comandamenti": ["VI"],
        "pins": [("Purgatorio", 27, 1), ("Purgatorio", 30, 1), ("Paradiso", 8, 1)],
        "rx": r"\bbeatrice\b|\bcastit|\bvenere",
    },
    {
        "id": "speranza_beatrice",
        "name": "Beatitudine / visione",
        "luogo": "Paradiso XXXIII (visione finale)",
        "comandamenti": ["I"],
        "pins": [("Paradiso", 33, 1), ("Paradiso", 33, 40)],
        "rx": r"\bl'amor che move il sole|\bultima salute|\bveder voleva",
    },
]

COMANDAMENTI = [
    {"n": 1, "name": "Non avrai altro Dio", "vizi": ["eresia", "superbia"], "virtu": ["fede", "umilta"]},
    {"n": 2, "name": "Non nominare il nome di Dio invano", "vizi": ["frode"], "virtu": ["verita"]},
    {"n": 3, "name": "Ricordati del sabato / culto", "vizi": ["accidia"], "virtu": ["fortezza"]},
    {"n": 4, "name": "Onora il padre e la madre", "vizi": ["tradimento"], "virtu": ["fedelta"]},
    {"n": 5, "name": "Non uccidere", "vizi": ["violenza", "ira", "tradimento"], "virtu": ["giustizia", "mansuetudine"]},
    {"n": 6, "name": "Non commettere adulterio", "vizi": ["lussuria"], "virtu": ["castita"]},
    {"n": 7, "name": "Non rubare", "vizi": ["avarizia", "frode", "violenza"], "virtu": ["liberalita", "giustizia"]},
    {"n": 8, "name": "Non dire falsa testimonianza", "vizi": ["frode", "tradimento"], "virtu": ["verita"]},
    {"n": 9, "name": "Non desiderare la donna d'altri", "vizi": ["lussuria", "invidia"], "virtu": ["castita", "carita"]},
    {"n": 10, "name": "Non desiderare la roba d'altri", "vizi": ["avarizia", "invidia", "gola"], "virtu": ["temperanza", "carita"]},
]

PERSONAGGI = [
    {"id": "dante", "name": "Dante pellegrino", "vizi": [], "virtu": ["fede", "speranza", "carita"],
     "comandamenti": [], "rx": r"\bio dante\b|\bbiagioni", "pins": [("Inferno", 1, 1), ("Purgatorio", 30, 18), ("Paradiso", 33, 46)]},
    {"id": "virgilio", "name": "Virgilio", "vizi": [], "virtu": ["prudenza"],
     "comandamenti": [], "rx": r"\bvirgilio\b|\bmaro\b", "pins": [("Inferno", 1, 22), ("Purgatorio", 30, 15)]},
    {"id": "beatrice", "name": "Beatrice", "vizi": [], "virtu": ["fede", "carita", "castita", "speranza"],
     "comandamenti": [], "rx": r"\bbeatrice\b|\bbeatrice", "pins": [("Inferno", 2, 17), ("Purgatorio", 30, 11), ("Paradiso", 1, 16)]},
    {"id": "caronte", "name": "Caronte", "vizi": [], "virtu": [], "comandamenti": [],
     "rx": r"\bcaron", "pins": [("Inferno", 3, 28)]},
    {"id": "francesca", "name": "Francesca da Rimini", "vizi": ["lussuria"], "virtu": [],
     "comandamenti": ["VI", "IX"], "rx": r"\bfrancesca\b", "pins": [("Inferno", 5, 24)]},
    {"id": "paolo", "name": "Paolo Malatesta", "vizi": ["lussuria"], "virtu": [],
     "comandamenti": ["VI", "IX"], "rx": r"\bpaolo\b", "pins": [("Inferno", 5, 34)]},
    {"id": "ciacco", "name": "Ciacco", "vizi": ["gola"], "virtu": [],
     "comandamenti": ["X"], "rx": r"\bciacco\b", "pins": [("Inferno", 6, 14)]},
    {"id": "filippo-argenti", "name": "Filippo Argenti", "vizi": ["ira"], "virtu": [],
     "comandamenti": ["V"], "rx": r"\bargenti\b|\bfilippo argenti", "pins": [("Inferno", 8, 11)]},
    {"id": "farinata", "name": "Farinata degli Uberti", "vizi": ["eresia", "superbia"], "virtu": [],
     "comandamenti": ["I"], "rx": r"\bfarinata\b", "pins": [("Inferno", 10, 8)]},
    {"id": "cavalcante", "name": "Cavalcante de' Cavalcanti", "vizi": ["eresia"], "virtu": [],
     "comandamenti": ["I"], "rx": r"\bcavalcante\b|\bguido vostro", "pins": [("Inferno", 10, 17)]},
    {"id": "pier", "name": "Pier della Vigna", "vizi": ["violenza"], "virtu": [],
     "comandamenti": ["V"], "rx": r"\bpier de la vigna|\bpiero\b", "pins": [("Inferno", 13, 10)]},
    {"id": "capaneo", "name": "Capaneo", "vizi": ["violenza", "superbia"], "virtu": [],
     "comandamenti": ["I", "V"], "rx": r"\bcapaneo\b", "pins": [("Inferno", 14, 14)]},
    {"id": "brunetto", "name": "Brunetto Latini", "vizi": ["violenza"], "virtu": ["prudenza"],
     "comandamenti": [], "rx": r"\bbrunetto\b", "pins": [("Inferno", 15, 10)]},
    {"id": "ulisse", "name": "Ulisse", "vizi": ["frode"], "virtu": ["prudenza"],
     "comandamenti": ["VIII"], "rx": r"\bulisse\b|\bodisseo", "pins": [("Inferno", 26, 19), ("Paradiso", 27, 28)]},
    {"id": "diomede", "name": "Diomede", "vizi": ["frode"], "virtu": [],
     "comandamenti": ["VIII"], "rx": r"\bdiomede\b", "pins": [("Inferno", 26, 19)]},
    {"id": "guido-mf", "name": "Guido da Montefeltro", "vizi": ["frode"], "virtu": [],
     "comandamenti": ["II", "VIII"], "rx": r"\bmontefeltro\b|\bguido\b", "pins": [("Inferno", 27, 19)]},
    {"id": "ugolino", "name": "Conte Ugolino", "vizi": ["tradimento"], "virtu": [],
     "comandamenti": ["V", "VIII"], "rx": r"\bugolin", "pins": [("Inferno", 33, 1)]},
    {"id": "ruggieri", "name": "Arcivescovo Ruggieri", "vizi": ["tradimento"], "virtu": [],
     "comandamenti": ["V"], "rx": r"\bruggeri\b", "pins": [("Inferno", 33, 4)]},
    {"id": "lucifero", "name": "Lucifero / Dite", "vizi": ["tradimento", "superbia"], "virtu": [],
     "comandamenti": ["I", "V"], "rx": r"\blucifer|\bimperator del doloroso regno|\bdite\b", "pins": [("Inferno", 34, 10)]},
    {"id": "giuda", "name": "Giuda Iscariota", "vizi": ["tradimento"], "virtu": [],
     "comandamenti": ["V", "VIII"], "rx": r"\bgiuda\b", "pins": [("Inferno", 34, 20)]},
    {"id": "cato", "name": "Catone uticense", "vizi": [], "virtu": ["giustizia", "fortezza"],
     "comandamenti": [], "rx": r"\bcaton", "pins": [("Purgatorio", 1, 10)]},
    {"id": "casella", "name": "Casella", "vizi": ["accidia"], "virtu": [],
     "comandamenti": ["III"], "rx": r"\bcasella\b", "pins": [("Purgatorio", 2, 25)]},
    {"id": "manfredi", "name": "Manfredi", "vizi": ["accidia"], "virtu": ["speranza"],
     "comandamenti": [], "rx": r"\bmanfredi\b", "pins": [("Purgatorio", 3, 34)]},
    {"id": "sordello", "name": "Sordello", "vizi": [], "virtu": ["giustizia"],
     "comandamenti": [], "rx": r"\bsordel", "pins": [("Purgatorio", 6, 20)]},
    {"id": "stazio", "name": "Stazio", "vizi": ["avarizia"], "virtu": ["prudenza"],
     "comandamenti": ["VII"], "rx": r"\bstazio\b", "pins": [("Purgatorio", 21, 20)]},
    {"id": "forese", "name": "Forese Donati", "vizi": ["gola"], "virtu": [],
     "comandamenti": ["X"], "rx": r"\bforese\b", "pins": [("Purgatorio", 23, 14)]},
    {"id": "bonagiunta", "name": "Bonagiunta Orbicciani", "vizi": ["gola"], "virtu": [],
     "comandamenti": [], "rx": r"\bbonagiunta\b", "pins": [("Purgatorio", 24, 7)]},
    {"id": "guinizelli", "name": "Guido Guinizzelli", "vizi": ["lussuria"], "virtu": ["castita"],
     "comandamenti": ["VI"], "rx": r"\bguiniz|\bguinizz", "pins": [("Purgatorio", 26, 25)]},
    {"id": "arseni", "name": "Arnaut Daniel", "vizi": ["lussuria"], "virtu": [],
     "comandamenti": ["VI"], "rx": r"\barnaut\b|\barnaldo", "pins": [("Purgatorio", 26, 46)]},
    {"id": "matelda", "name": "Matelda", "vizi": [], "virtu": ["castita", "carita"],
     "comandamenti": [], "rx": r"\bmatelda\b", "pins": [("Purgatorio", 28, 13)]},
    {"id": "piccarda", "name": "Piccarda Donati", "vizi": [], "virtu": ["fede", "umilta"],
     "comandamenti": [], "rx": r"\bpiccarda\b", "pins": [("Paradiso", 3, 13)]},
    {"id": "giustiniano", "name": "Giustiniano", "vizi": [], "virtu": ["giustizia"],
     "comandamenti": ["V", "VII"], "rx": r"\bgiustinian", "pins": [("Paradiso", 6, 1)]},
    {"id": "carlos", "name": "Carlo Martello", "vizi": [], "virtu": ["carita"],
     "comandamenti": [], "rx": r"\bcarlo\b", "pins": [("Paradiso", 8, 10)]},
    {"id": "tommaso", "name": "Tommaso d'Aquino", "vizi": [], "virtu": ["prudenza", "fede"],
     "comandamenti": ["I"], "rx": r"\btommaso\b|\bthomas\b", "pins": [("Paradiso", 10, 25)]},
    {"id": "bonaventura", "name": "Bonaventura", "vizi": [], "virtu": ["prudenza", "carita"],
     "comandamenti": ["I"], "rx": r"\bbonaventura\b", "pins": [("Paradiso", 12, 37)]},
    {"id": "cacciaguida", "name": "Cacciaguida", "vizi": [], "virtu": ["fortezza", "giustizia"],
     "comandamenti": [], "rx": r"\bcacciaguida\b", "pins": [("Paradiso", 15, 25)]},
    {"id": "cacciaguida-esilio", "name": "Cacciaguida (profezia d'esilio)", "vizi": [], "virtu": ["fortezza"],
     "comandamenti": [], "rx": r"\b tu lascerai ogne cosa diletta", "pins": [("Paradiso", 17, 13)]},
    {"id": "ripheus", "name": "Rifeo troiano", "vizi": [], "virtu": ["giustizia", "fede"],
     "comandamenti": ["I"], "rx": r"\brifeo\b|\bripheus", "pins": [("Paradiso", 20, 20)]},
    {"id": "pietro", "name": "San Pietro", "vizi": [], "virtu": ["fede"],
     "comandamenti": ["I"], "rx": r"\bpietro\b", "pins": [("Paradiso", 24, 10)]},
    {"id": "bernardo", "name": "San Bernardo", "vizi": [], "virtu": ["carita", "speranza"],
     "comandamenti": ["I"], "rx": r"\bbernard", "pins": [("Paradiso", 31, 16)]},
    {"id": "maria", "name": "Maria", "vizi": [], "virtu": ["umilta", "carita", "castita"],
     "comandamenti": [], "rx": r"\bmaria\b|\bvergine madre", "pins": [("Purgatorio", 10, 12), ("Paradiso", 33, 1)]},
]

TEMI = [
    {"id": "libero-arbitrio", "name": "Libero arbitrio",
     "pins": [("Purgatorio", 16, 18), ("Purgatorio", 18, 13), ("Paradiso", 5, 7)],
     "rx": r"\blibero arbitrio|\blibertà|\blibero voler"},
    {"id": "amore", "name": "Amore (folle / ordinato)",
     "pins": [("Inferno", 5, 34), ("Purgatorio", 17, 25), ("Paradiso", 33, 46)],
     "rx": r"\bamor che a nullo amato|\bamor che move|\bamore\b"},
    {"id": "giustizia-divina", "name": "Giustizia divina e contrapasso",
     "pins": [("Inferno", 28, 46), ("Paradiso", 19, 13)],
     "rx": r"\bcontrapasso|\bgiustizia\b"},
    {"id": "lingua", "name": "Lingua, fama, poesia",
     "pins": [("Inferno", 4, 25), ("Purgatorio", 24, 16), ("Paradiso", 17, 30)],
     "rx": r"\bdolce stil|\bfama\b|\bvolgare"},
    {"id": "politica", "name": "Impero, Chiesa, Firenze",
     "pins": [("Purgatorio", 6, 22), ("Paradiso", 6, 1), ("Paradiso", 16, 1)],
     "rx": r"\bfiorenza|\bimpero\b|\bchiesa\b"},
    {"id": "esilio", "name": "Esilio e profezia",
     "pins": [("Inferno", 10, 25), ("Inferno", 15, 20), ("Paradiso", 17, 13)],
     "rx": r"\besilio|\b tu lascerai ogne cosa diletta"},
    {"id": "conoscenza", "name": "Conoscenza e suoi limiti",
     "pins": [("Inferno", 26, 38), ("Paradiso", 4, 13), ("Paradiso", 21, 25)],
     "rx": r"\bvirtute e canoscenza|\bfolle volo|\bsapienza"},
    {"id": "beatitudine", "name": "Visione e beatitudine",
     "pins": [("Paradiso", 30, 1), ("Paradiso", 33, 40)],
     "rx": r"\bcandida rosa|\bultima salute|\bveder voleva"},
    {"id": "fortuna", "name": "Fortuna",
     "pins": [("Inferno", 7, 22)],
     "rx": r"\bfortuna\b"},
    {"id": "tempo", "name": "Tempo, memoria, oblio",
     "pins": [("Purgatorio", 28, 40), ("Purgatorio", 33, 31), ("Paradiso", 17, 30)],
     "rx": r"\blete\b|\beunoe|\bmemoria"},
]

# Later authors: established citations only.
POSTERIORI = [
    {
        "author": "Giovanni Boccaccio",
        "work": "Esposizioni sopra la Comedìa / Trattatello in laude di Dante",
        "year": "c. 1355–1373",
        "what": "Prima lettura pubblica fiorentina e vita di Dante; fissa il canone biografico.",
        "locus": [("Inferno", 1, 1)],
        "url": "https://it.wikipedia.org/wiki/Esposizioni_sopra_la_Comedia_di_Dante",
    },
    {
        "author": "Geoffrey Chaucer",
        "work": "The House of Fame / Troilus and Criseyde",
        "year": "c. 1379–1385",
        "what": "Riprende l'aquila e la struttura visionaria; Troilo legge Paolo e Francesca.",
        "locus": [("Inferno", 5, 34)],
        "url": "https://www.gutenberg.org/ebooks/257",
    },
    {
        "author": "John Milton",
        "work": "Paradise Lost",
        "year": "1667",
        "what": "Satana e l'inferno miltoniano dialogano col Lucifero dantesco e col volo di Ulisse.",
        "locus": [("Inferno", 26, 38), ("Inferno", 34, 10)],
        "url": "https://www.gutenberg.org/ebooks/26",
    },
    {
        "author": "T. S. Eliot",
        "work": "The Love Song of J. Alfred Prufrock",
        "year": "1915",
        "what": "Epigrafe da Guido da Montefeltro: «S'io credesse che mia risposta fosse / a persona che mai tornasse al mondo…».",
        "locus": [("Inferno", 27, 20)],
        "url": "https://www.poetryfoundation.org/poetrymagazine/poems/44212/the-love-song-of-j-alfred-prufrock",
    },
    {
        "author": "T. S. Eliot",
        "work": "The Waste Land",
        "year": "1922",
        "what": "«I had not thought death had undone so many» (Inf. III); chiusura «Poi s'ascose nel foco che gli affina» (Purg. XXVI, Arnaut).",
        "locus": [("Inferno", 3, 19), ("Purgatorio", 26, 46)],
        "url": "https://www.gutenberg.org/ebooks/1321",
    },
    {
        "author": "T. S. Eliot",
        "work": "Little Gidding (Four Quartets)",
        "year": "1942",
        "what": "L'incontro col «compound ghost» ricalca Brunetto (Inf. XV) e il maestro che insegna «come l'uom s'etterna».",
        "locus": [("Inferno", 15, 26)],
        "url": "https://en.wikipedia.org/wiki/Little_Gidding_(poem)",
    },
    {
        "author": "Osip Mandel'štam",
        "work": "Conversazione su Dante",
        "year": "1933",
        "what": "Saggio sulla Commedia come organismo metrico e politico; legge Inferno come macchina della storia.",
        "locus": [("Inferno", 1, 1)],
        "url": "https://it.wikipedia.org/wiki/Osip_%C4%96mil%27evi%C4%8D_Mandel%27%C5%A1tam",
    },
    {
        "author": "Primo Levi",
        "work": "Se questo è un uomo — Il canto di Ulisse",
        "year": "1947",
        "what": "Nel Lager insegna Inf. XXVI a Jean: «Considerate la vostra semenza…» come resistenza della memoria.",
        "locus": [("Inferno", 26, 38)],
        "url": "https://it.wikipedia.org/wiki/Se_questo_%C3%A8_un_uomo",
    },
    {
        "author": "Jorge Luis Borges",
        "work": "Nueve ensayos dantescos / El Aleph",
        "year": "1949–1982",
        "what": "Saggi su Ulisse, sul falso problema di Ugolino, su Beatrice; l'Aleph come parodia della visione del XXXIII Paradiso.",
        "locus": [("Inferno", 26, 38), ("Inferno", 33, 1), ("Paradiso", 33, 40)],
        "url": "https://es.wikipedia.org/wiki/Nueve_ensayos_dantesco",
    },
    {
        "author": "Samuel Beckett",
        "work": "The Lost Ones / Waiting for Godot",
        "year": "1950–1970",
        "what": "Belacqua (Purg. IV) diventa figura dell'attesa; l'inferno come spazio cilindrico chiuso.",
        "locus": [("Purgatorio", 4, 30)],
        "url": "https://en.wikipedia.org/wiki/Belacqua",
    },
    {
        "author": "Eugenio Montale",
        "work": "Ossi di seppia / La bufera",
        "year": "1925–1956",
        "what": "Dantismi lessicali e la figura della donna-salvezza (Clizia) in dialogo con Beatrice.",
        "locus": [("Purgatorio", 30, 11), ("Paradiso", 23, 1)],
        "url": "https://it.wikipedia.org/wiki/Eugenio_Montale",
    },
    {
        "author": "Pier Paolo Pasolini",
        "work": "La Divina Mimesis",
        "year": "1975",
        "what": "Riscrivere l'Inferno nel presente italiano: il pellegrino è un intellettuale in crisi.",
        "locus": [("Inferno", 1, 1)],
        "url": "https://it.wikipedia.org/wiki/La_Divina_Mimesis",
    },
    {
        "author": "Seamus Heaney",
        "work": "Seeing Things / Ugolino (Field Work)",
        "year": "1979–1991",
        "what": "Traduce Ugolino e usa il contrapasso per l'Irlanda del conflitto.",
        "locus": [("Inferno", 33, 1)],
        "url": "https://www.poetryfoundation.org/poets/seamus-heaney",
    },
    {
        "author": "Derek Walcott",
        "work": "Omeros",
        "year": "1990",
        "what": "Epica caraibica con guida dantesca e discesa tra i morti.",
        "locus": [("Inferno", 1, 22)],
        "url": "https://www.poetryfoundation.org/poets/derek-walcott",
    },
    {
        "author": "Claudia Rankine / poets of the afterlife",
        "work": "citazioni contemporanee del Limbo e degli ignavi",
        "year": "XX–XXI sec.",
        "what": "Il III dell'Inferno (ignavi, «gran rifiuto») resta il luogo più citato per l'indifferenza politica.",
        "locus": [("Inferno", 3, 10)],
        "url": "https://it.wikipedia.org/wiki/Inferno_-_Canto_terzo",
    },
    {
        "author": "Erich Auerbach",
        "work": "Mimesis / Studi su Dante",
        "year": "1929–1946",
        "what": "Farinata e Cavalcante come nascita del realismo moderno (figura e destino).",
        "locus": [("Inferno", 10, 8)],
        "url": "https://it.wikipedia.org/wiki/Mimesis._Il_realismo_nella_letteratura_occidentale",
    },
    {
        "author": "Giacomo Leopardi",
        "work": "Zibaldone / Operette",
        "year": "1817–1832",
        "what": "Citazioni e giudizio sul «poetico» dantesco; la selva come figura della noia e della natura.",
        "locus": [("Inferno", 1, 1)],
        "url": "https://it.wikisource.org/wiki/Zibaldone_di_pensieri",
    },
    {
        "author": "Ugo Foscolo",
        "work": "Dei sepolcri / Discorso sul testo della Commedia",
        "year": "1807–1825",
        "what": "Dante come padre della nazione letteraria; edizione e discorso sul poema.",
        "locus": [("Inferno", 4, 25)],
        "url": "https://it.wikisource.org/wiki/Dei_sepolcri",
    },
]


def pack_vizio(v):
    pins = pin(*v["pins"], fallback_rx=v.get("rx"), limit=10)
    return {
        "id": v["id"],
        "name": v["name"],
        "luogo": v["luogo"],
        "comandamenti": v.get("comandamenti", []),
        "virtu_contraria": v.get("virtu_contraria"),
        "luoghi": pins,
    }


def pack_virtu(v):
    return {
        "id": v["id"],
        "name": v["name"],
        "luogo": v["luogo"],
        "comandamenti": v.get("comandamenti", []),
        "luoghi": pin(*v["pins"], fallback_rx=v.get("rx"), limit=8),
    }


def pack_personaggio(p):
    return {
        "id": p["id"],
        "name": p["name"],
        "vizi": p.get("vizi", []),
        "virtu": p.get("virtu", []),
        "comandamenti": p.get("comandamenti", []),
        "luoghi": pin(*p.get("pins", ()), fallback_rx=p.get("rx"), limit=14),
    }


def pack_tema(t):
    return {
        "id": t["id"],
        "name": t["name"],
        "luoghi": pin(*t["pins"], fallback_rx=t.get("rx"), limit=10),
    }


def pack_comando(c, vizi_by_id, pers):
    roman = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
             6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X"}[c["n"]]
    vice_ids = set(c.get("vizi") or [])
    virt_ids = set(c.get("virtu") or [])
    violatori, osservanti = [], []
    for p in pers:
        # violator = has a vice tied to this commandment (or explicit decalogue mark + vice)
        if vice_ids & set(p.get("vizi") or []):
            violatori.append({"id": p["id"], "name": p["name"]})
        elif virt_ids & set(p.get("virtu") or []):
            osservanti.append({"id": p["id"], "name": p["name"]})
    luoghi_v, luoghi_o = [], []
    for vid in c.get("vizi", []):
        luoghi_v.extend(vizi_by_id.get(vid, {}).get("luoghi", [])[:3])
    for p in pers:
        if virt_ids & set(p.get("virtu") or []):
            luoghi_o.extend((p.get("luoghi") or [])[:2])

    def uniq(seq):
        seen, out = set(), []
        for loc in seq:
            k = (loc["cantica"], loc["canto"], loc["tercet"])
            if k not in seen:
                seen.add(k)
                out.append(loc)
        return out

    return {
        "n": c["n"],
        "roman": roman,
        "name": c["name"],
        "vizi": c.get("vizi", []),
        "virtu": c.get("virtu", []),
        "violatori": violatori,
        "osservanti": osservanti,
        "luoghi_violazione": uniq(luoghi_v)[:12],
        "luoghi_osservanza": uniq(luoghi_o)[:12],
        "luoghi": uniq(luoghi_v)[:12],
    }


def pack_post(p):
    locs = []
    for triple in p["locus"]:
        loc = find_canto(*triple) or find_canto(triple[0], triple[1], None)
        if loc:
            locs.append(loc)
    return {
        "author": p["author"],
        "work": p["work"],
        "year": p["year"],
        "what": p["what"],
        "url": p.get("url"),
        "luoghi": locs,
    }


def main():
    vizi = [pack_vizio(v) for v in VIZI]
    vizi_by_id = {v["id"]: v for v in vizi}
    virtu = [pack_virtu(v) for v in VIRTU]
    pers = [pack_personaggio(p) for p in PERSONAGGI]
    # drop empty personaggi
    pers = [p for p in pers if p["luoghi"]]
    temi = [pack_tema(t) for t in TEMI]
    cmds = [pack_comando(c, vizi_by_id, pers) for c in COMANDAMENTI]
    post = [pack_post(p) for p in POSTERIORI]

    # invert: virtue -> personaggi
    for v in virtu:
        v["personaggi"] = [{"id": p["id"], "name": p["name"]}
                           for p in pers if v["id"] in p.get("virtu", [])]
    for v in vizi:
        v["personaggi"] = [{"id": p["id"], "name": p["name"]}
                           for p in pers if v["id"] in p.get("vizi", [])]

    out = {
        "personaggi": sorted(pers, key=lambda x: x["name"]),
        "temi": temi,
        "vizi": vizi,
        "virtu": virtu,
        "comandamenti": cmds,
        "posteriori": post,
    }
    dest = ROOT / "site/data/elementi.json"
    dest.write_text(json.dumps(out, ensure_ascii=False))
    print("personaggi", len(out["personaggi"]))
    print("temi", len(out["temi"]))
    print("vizi", len(out["vizi"]))
    print("virtu", len(out["virtu"]))
    print("comandamenti", len(out["comandamenti"]))
    print("posteriori", len(out["posteriori"]))
    print("bytes", dest.stat().st_size)
    empty = [p["name"] for p in pers if not p["luoghi"]]
    print("empty chars", empty)


if __name__ == "__main__":
    main()
