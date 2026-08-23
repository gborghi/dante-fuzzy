#!/usr/bin/env python3
"""Guided TF-IDF clustering: 10 literary themes of the Comedy."""
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path("/Users/g.borghi/ICT/dante-fuzzy")
rows = json.loads((ROOT / "data/terzine.json").read_text())

SEEDS = [
    {
        "id": "topic_0",
        "title": "Narrazione e dialogo",
        "synth": "Il <strong>tessuto</strong> del poema: dialogo con la guida, racconto, transizioni. Terzine non dominate da un tema lessicale unico.",
        "seed": "",
    },
    {
        "id": "topic_1",
        "title": "Amore e lussuria",
        "synth": "<strong>Amore</strong> folle e amore ordinato: <strong>Francesca</strong>, Paolo, Venere, disio. Dal turbine infernale alla fiamma del Purgatorio fino a Beatrice.",
        "seed": "amore amor lussuria francesca paolo disio bacio folle venere",
    },
    {
        "id": "topic_2",
        "title": "Firenze, politica, esilio",
        "synth": "<strong>Firenze</strong>, fazioni, papi e impero. Profezie di <strong>esilio</strong>, Cacciaguida, Farinata, la città corrotta e la missione di dire il vero.",
        "seed": "fiorenza firenze esilio parte guelfi ghibellini papa impero cacciaguida farinata cittade toscana",
    },
    {
        "id": "topic_3",
        "title": "Frode e consiglio",
        "synth": "<strong>Malebolge</strong>: inganno, lingua, fiamma. <strong>Ulisse</strong> e il folle volo, Guido da Montefeltro, consiglieri fraudolenti.",
        "seed": "frode ulisse diomede montefeltro consiglio fiamma malebolge inganno lingua folle volo canoscenza",
    },
    {
        "id": "topic_4",
        "title": "Pena e contrapasso",
        "synth": "La <strong>pena</strong> rispecchia la colpa: <strong>fuoco</strong>, ghiaccio, fango, vento, sepolcri. Il <strong>contrapasso</strong> come giustizia visibile.",
        "seed": "pena contrapasso foco fuoco ghiaccio gelo stige fango pioggia sepolcro vermi cerbero minosse",
    },
    {
        "id": "topic_5",
        "title": "Luce e visione",
        "synth": "<strong>Luce</strong>, raggio, stelle, viso. Dalla paura notturna alla <strong>visione</strong> dell’Empireo: vedere come forma della beatitudine.",
        "seed": "luce lume raggio splendore stelle stella viso occhi vedere imperio empireo candida rosa",
    },
    {
        "id": "topic_6",
        "title": "Libero arbitrio e natura",
        "synth": "<strong>Libero arbitrio</strong>, volontà, cielo che influisce ma non costringe. Natura, merto e responsabilità (Marco Lombardo, Beatrice).",
        "seed": "libero arbitrio volere volonta natura cielo influsso merto liberta velle marco lombardo",
    },
    {
        "id": "topic_7",
        "title": "Fede, Dio, teologia",
        "synth": "<strong>Fede</strong>, speranza, carità, <strong>Dio</strong>, Chiesa, santi. Esami di Pietro, Giacomo, Giovanni; grazia e rivelazione.",
        "seed": "fede dio cristo chiesa grazia santo pietro maria carita speranza teologia grazia beatitudine",
    },
    {
        "id": "topic_8",
        "title": "Poesia, fama, maestri",
        "synth": "<strong>Poesia</strong> e <strong>fama</strong>: Virgilio maestro, bello stilo, dolce stil novo, Bonagiunta, Guinizzelli. Come l’uomo s’etterna.",
        "seed": "poeta poesia fama maestro virgilio stilo canto musa bonagiunta guinizelli brunetto onore",
    },
    {
        "id": "topic_9",
        "title": "Violenza, ira, sangue",
        "synth": "<strong>Violenza</strong> e <strong>ira</strong>: Flegetonte, sangue, guerra, superbia armata. Da Capaneo e i violenti fino alle cornici dell’ira.",
        "seed": "violenza ira sangue guerra spada flegetonte centauri capaneo attila superbia orgoglio",
    },
]


def fold(s):
    s = (s or "").lower().replace("’", "'")
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


texts = []
meta = []
for r in rows:
    texts.append(fold(r.get("text") or ""))
    meta.append({
        "cantica": r["volume"],
        "canto": int(r["canto"]),
        "tercet": int(r["tercet"]),
        "text": r.get("text") or "",
    })

vec = TfidfVectorizer(min_df=4, max_df=0.5, ngram_range=(1, 2), max_features=8000)
X = vec.fit_transform(texts)
S = vec.transform([fold(s["seed"]) if s["seed"] else "xyznonword" for s in SEEDS])
sim = cosine_similarity(X, S)
# topic 0 is residual: ignore its seed column
sim[:, 0] = -1
assign = sim.argmax(axis=1)
strength = sim.max(axis=1)
assign[strength < 0.05] = 0
strength[assign == 0] = 0.0

vocab = np.array(vec.get_feature_names_out())
# distinctive unigrams per cluster via mean tfidf
topics = []
for k, seed in enumerate(SEEDS):
    idx = np.where(assign == k)[0]
    cantiche = Counter(meta[i]["cantica"] for i in idx)
    if len(idx):
        mean = np.asarray(X[idx].mean(axis=0)).ravel()
        # downweight seed-generic by preferring cluster-specific
        top = mean.argsort()[::-1]
        words = []
        for i in top:
            w = vocab[i]
            if " " in w:
                continue
            if len(w) < 4:
                continue
            if w in {"come", "quel", "quella", "quando", "cosi", "perche", "disse", "ogne", "altra", "altro", "tutti", "tutte"}:
                continue
            words.append(w)
            if len(words) >= 8:
                break
        order = idx[np.argsort(strength[idx])[::-1]]
    else:
        words = seed["seed"].split()[:8]
        order = []
    samples = []
    seen = set()
    for i in order:
        m = meta[i]
        key = (m["cantica"], m["canto"])
        if key in seen and len(samples) >= 3:
            continue
        seen.add(key)
        samples.append({
            "cantica": m["cantica"],
            "canto": m["canto"],
            "tercet": m["tercet"],
            "text": m["text"],
            "weight": float(round(float(strength[i]), 3)),
        })
        if len(samples) >= 6:
            break
    topics.append({
        "id": seed["id"],
        "num": k,
        "title": seed["title"],
        "synth": seed["synth"],
        "label": seed["title"],
        "n": int(len(idx)),
        "words": words,
        "cantiche": {
            "Inferno": int(cantiche.get("Inferno", 0)),
            "Purgatorio": int(cantiche.get("Purgatorio", 0)),
            "Paradiso": int(cantiche.get("Paradiso", 0)),
        },
        "samples": samples,
    })

out = {"method": "guided-tfidf-cosine", "k": 10, "topics": topics}
dest = ROOT / "site/data/topics.json"
dest.write_text(json.dumps(out, ensure_ascii=False))
print("topics", [(t["id"], t["n"], t["title"], t["words"][:5]) for t in topics])
print("bytes", dest.stat().st_size, "assigned", int((assign >= 0).sum()))
