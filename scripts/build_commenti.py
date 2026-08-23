#!/usr/bin/env python3
"""Build site/data/commenti/{Inferno,Purgatorio,Paradiso}.json from PD commentaries."""
from __future__ import annotations

import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from collections import defaultdict

ROOT = Path("/Users/g.borghi/ICT/dante-fuzzy")
PD = ROOT / "commenti-pd"
OUT = ROOT / "site/data/commenti"
OUT.mkdir(parents=True, exist_ok=True)

AUTHORS = {
    "tozer": {
        "name": "H. F. Tozer",
        "work": "An English Commentary on Dante’s Divina Commedia",
        "year": 1901,
        "lang": "en",
    },
    "scartazzini": {
        "name": "G. A. Scartazzini",
        "work": "La Divina Commedia commentata",
        "year": 1874,
        "lang": "it",
    },
    "longfellow": {
        "name": "H. W. Longfellow",
        "work": "The Divine Comedy (Notes)",
        "year": 1867,
        "lang": "en",
    },
    "tommaseo": {
        "name": "Niccolò Tommaseo",
        "work": "Commedia con ragionamenti e note",
        "year": 1865,
        "lang": "it",
    },
    "torraca": {
        "name": "Francesco Torraca",
        "work": "La Divina Commedia nuovamente commentata",
        "year": 1905,
        "lang": "it",
    },
    "campi": {
        "name": "Giuseppe Campi",
        "work": "La Divina Commedia ridotta a miglior lezione",
        "year": 1888,
        "lang": "it",
    },
    "bianchi": {
        "name": "Brunone Bianchi",
        "work": "La Commedia di Dante Alighieri",
        "year": 1857,
        "lang": "it",
    },
    "fraticelli": {
        "name": "Pietro Fraticelli",
        "work": "La Divina Commedia col comento",
        "year": 1881,
        "lang": "it",
    },
}

IT_ORD = {
    "PRIMO": 1, "SECONDO": 2, "TERZO": 3, "QUARTO": 4, "QUINTO": 5,
    "SESTO": 6, "SETTIMO": 7, "OTTAVO": 8, "NONO": 9, "DECIMO": 10,
    "UNDECIMO": 11, "UNDICESIMO": 11, "DECIMOPRIMO": 11,
    "DUODECIMO": 12, "DODICESIMO": 12, "DECIMOSECONDO": 12,
    "DECIMOTERZO": 13, "TREDICESIMO": 13,
    "DECIMOQUARTO": 14, "QUATTORDICESIMO": 14,
    "DECIMOQUINTO": 15, "QUINDICESIMO": 15,
    "DECIMOSESTO": 16, "SEDICESIMO": 16,
    "DECIMOSETTIMO": 17, "DICIASSETTESIMO": 17,
    "DECIMOTTAVO": 18, "DECIMOOTTAVO": 18, "DICIOTTESIMO": 18,
    "DECIMONONO": 19, "DICIANNOVESIMO": 19,
    "VENTESIMO": 20, "VENTESIMOPRIMO": 21, "VENTUNESIMO": 21,
    "VENTESIMOSECONDO": 22, "VENTIDUESIMO": 22,
    "VENTESIMOTERZO": 23, "VENTITREESIMO": 23,
    "VENTESIMOQUARTO": 24, "VENTIQUATTRESIMO": 24,
    "VENTESIMOQUINTO": 25, "VENTICINQUESIMO": 25,
    "VENTESIMOSESTO": 26, "VENTISEIESIMO": 26,
    "VENTESIMOSETTIMO": 27, "VENTISETTEESIMO": 27, "VENTISETTESIMO": 27,
    "VENTESIMOTTAVO": 28, "VENTOTTESIMO": 28,
    "VENTESIMONONO": 29, "VENTINOVESIMO": 29,
    "TRENTESIMO": 30, "TRENTESIMOPRIMO": 31, "TRENTUNESIMO": 31,
    "TRENTESIMOSECONDO": 32, "TRENTADUESIMO": 32,
    "TRENTESIMOTERZO": 33, "TRENTATREESIMO": 33,
    "TRENTESIMOQUARTO": 34, "TRENTAQUATTRESIMO": 34,
}

ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9,
    "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16,
    "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20, "XXI": 21, "XXII": 22,
    "XXIII": 23, "XXIV": 24, "XXV": 25, "XXVI": 26, "XXVII": 27, "XXVIII": 28,
    "XXIX": 29, "XXX": 30, "XXXI": 31, "XXXII": 32, "XXXIII": 33, "XXXIV": 34,
}


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self._skip:
            self._skip -= 1
        if tag in {"p", "div", "br", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if self._skip:
            return
        if data.strip():
            self.parts.append(data)


def html_text(raw: str) -> str:
    p = TextExtractor()
    try:
        p.feed(raw)
    except Exception:
        pass
    t = "".join(p.parts)
    t = re.sub(r"\s+\n", "\n", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t


def epub_concat(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if re.search(r"page_(\d+)\.html$", n)]
        def _pg(n):
            mm = re.search(r"page_(\d+)", n)
            return int(mm.group(1)) if mm else 0
        names.sort(key=_pg)
        chunks = []
        for n in names:
            raw = z.read(n).decode("utf-8", "replace")
            chunks.append(html_text(raw))
        return "\n".join(chunks)


def clean(s: str, limit=720) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"Page \d+\s*", "", s)
    s = s.replace(" ,", ",").replace(" .", ".")
    if len(s) > limit:
        s = s[: limit - 1].rsplit(" ", 1)[0] + "…"
    return s


def line_to_tercet(line: int) -> int:
    return max(1, (int(line) + 2) // 3)


def parse_line_spec(spec: str):
    spec = spec.replace("—", "-").replace("–", "-").replace(" ", "")
    nums = [int(x) for x in re.findall(r"\d+", spec)]
    if not nums:
        return []
    if len(nums) == 1:
        return [nums[0]]
    a, b = nums[0], nums[-1]
    if b < a:
        b = a
    if b - a > 40:
        return [a]
    return list(range(a, b + 1))


def add_note(store, cantica, canto, tercets, author, text, cite, canto_level=False):
    text = clean(text)
    if len(text) < 40:
        return
    key = f"{cantica}:{int(canto)}"
    rec = {"a": author, "t": text, "cite": cite}
    bucket = store[key]
    if canto_level or not tercets:
        bucket["canto"].append(rec)
        return
    for vv in tercets:
        tz = str(line_to_tercet(vv))
        bucket["tz"].setdefault(tz, []).append(rec)


# ── Tozer ──────────────────────────────────────────────
def parse_tozer():
    text = epub_concat(PD / "en/tozer_1901_english_commentary.epub")
    cantica = "Inferno"
    canto = 1
    store = defaultdict(lambda: {"canto": [], "tz": {}})
    # split on CANTO + roman or PURGATORIO/PARADISO headers
    parts = re.split(
        r"(?=(?:INFERNO|PURGATORIO|PARADISO)\s+CANTO\s+[IVX]+|CANTO\s+[IVX]+\b)",
        text,
    )
    header_re = re.compile(
        r"(?:(?P<cant>INFERNO|PURGATORIO|PARADISO)\s+)?CANTO\s+(?P<rom>[IVX]+)",
        re.I,
    )
    note_re = re.compile(
        r"(?m)^(?:(?P<spec>\d{1,3}(?:\s*[,.\-–—]\s*\d{1,3}){0,3})\s*[.:]\s+)(?P<body>.+?)(?=(?:^\d{1,3}(?:\s*[,.\-–—]\s*\d{1,3}){0,3}\s*[.:]\s+)|\Z)",
        re.S,
    )
    # Tozer notes are inline "4-6. text 7. text" not always at line start
    inline_re = re.compile(
        r"(?:(?<=\s)|(?<=^))(?P<spec>\d{1,3}(?:\s*[,.\-–—]\s*\d{1,3}){0,2})\s*\.\s+(?P<body>[A-Z“\"'].{20,}?)(?=(?:\s\d{1,3}(?:\s*[,.\-–—]\s*\d{1,3}){0,2}\s*\.\s+[A-Z“\"'])|\Z)",
        re.S,
    )
    for part in parts:
        hm = header_re.search(part[:400])
        if re.search(r"\bPURGATORIO\b", part[:500]):
            cantica = "Purgatorio"
        elif re.search(r"\bPARADISO\b", part[:500]) and not re.search(r"\bINFERNO\b", part[:200]):
            cantica = "Paradiso"
        if hm:
            if hm.group("cant"):
                cantica = hm.group("cant").title().replace("Purgatorio", "Purgatorio")
                if cantica.lower().startswith("purg"):
                    cantica = "Purgatorio"
                elif cantica.lower().startswith("par"):
                    cantica = "Paradiso"
                else:
                    cantica = "Inferno"
            canto = ROMAN.get(hm.group("rom").upper(), canto)
        arg = re.search(r"Argument\.?\s*[—–-]?\s*(.{80,900}?)(?=\d{1,3}[\s.\-]|\Z)", part, re.S)
        if arg:
            add_note(
                store, cantica, canto, [], "tozer", arg.group(1),
                f"Tozer 1901, {cantica} {canto} (Argument)",
                canto_level=True,
            )
        pref = re.search(r"Prefatory Note[^.]*\.\s*(.{80,900})", part, re.S)
        if pref:
            add_note(
                store, cantica, canto, [], "tozer", pref.group(1),
                f"Tozer 1901, {cantica} {canto} (Prefatory)",
                canto_level=True,
            )
        for m in inline_re.finditer(part):
            lines = parse_line_spec(m.group("spec"))
            if not lines:
                continue
            add_note(
                store, cantica, canto, lines, "tozer", m.group("body"),
                f"Tozer 1901, {cantica} {canto}, vv. {m.group('spec').replace(' ','')}",
            )
    return store


# ── Scartazzini ────────────────────────────────────────
def parse_scartazzini():
    files = [
        (PD / "it/scartazzini_1874_inferno.epub", "Inferno", 1874),
        (PD / "it/scartazzini_1875_purgatorio.epub", "Purgatorio", 1875),
        (None, "Paradiso", 1882),
    ]
    store = defaultdict(lambda: {"canto": [], "tz": {}})
    # Paradiso as txt
    texts = []
    if files[0][0].exists():
        texts.append((epub_concat(files[0][0]), "Inferno", 1874))
    if files[1][0].exists():
        texts.append((epub_concat(files[1][0]), "Purgatorio", 1875))
    par_txt = PD / "it/scartazzini_1882_paradiso.txt"
    if par_txt.exists():
        texts.append((par_txt.read_text(errors="replace"), "Paradiso", 1882))

    canto_head = re.compile(
        r"CANTO\s+([A-ZÀ]+|[IVX]+|\d{1,2})",
        re.I,
    )
    note_re = re.compile(
        r"(?:(?<=\n)|(?<=^)|(?<=\s))(?P<spec>\d{1,3}(?:\s*[-–—]\s*\d{1,3})?)\s*[.:—]\s+(?P<body>[A-ZÀ-Ú«\"'].{30,}?)(?=(?:\s\d{1,3}(?:\s*[-–—]\s*\d{1,3})?\s*[.:—]\s+[A-ZÀ-Ú«\"'])|\nCANTO\s+|\Z)",
        re.S,
    )
    for text, cantica, year in texts:
        text = text.replace("\f", "\n")
        chunks = canto_head.split(text)
        # split keeps delimiters: [pre, token, body, token, body...]
        i = 1
        while i + 1 < len(chunks):
            token, body = chunks[i], chunks[i + 1]
            token_u = token.strip().upper()
            if token_u in IT_ORD:
                canto = IT_ORD[token_u]
            elif token_u in ROMAN:
                canto = ROMAN[token_u]
            elif token_u.isdigit():
                canto = int(token_u)
            else:
                i += 2
                continue
            # first paragraph as argument if no leading verse number
            head = body[:800]
            if not re.match(r"\s*\d{1,3}\s*[.:]", head):
                para = re.split(r"\n\d{1,3}\s*[.:]", body, maxsplit=1)[0]
                add_note(
                    store, cantica, canto, [], "scartazzini", para,
                    f"Scartazzini {year}, {cantica} {canto}",
                    canto_level=True,
                )
            for m in note_re.finditer(body):
                lines = parse_line_spec(m.group("spec"))
                add_note(
                    store, cantica, canto, lines, "scartazzini", m.group("body"),
                    f"Scartazzini {year}, {cantica} {canto}, v. {m.group('spec').replace(' ','')}",
                )
            i += 2
    return store


# ── Longfellow notes (Wikisource HTML already saved) ──
def parse_longfellow():
    store = defaultdict(lambda: {"canto": [], "tz": {}})
    pages = [
        ("Inferno", "Divine_Comedy_(Longfellow_1867)/Volume_1/Notes",
         PD / "en/longfellow_notes_inferno.html"),
        ("Purgatorio", "Divine_Comedy_(Longfellow_1867)/Volume_2/Notes",
         PD / "en/longfellow_notes_purgatorio.html"),
        ("Paradiso", "Divine_Comedy_(Longfellow_1867)/Volume_3/Notes",
         PD / "en/longfellow_notes_paradiso.html"),
    ]
    import urllib.request
    canto_re = re.compile(r"(?:Canto|CANTO)\s+([IVX]+|\d{1,2})", re.I)
    note_re = re.compile(
        r"(?:(?<=\n)|(?<=^))(?P<spec>\d{1,3}(?:\s*[-–—]\s*\d{1,3})?)\s*[.:]\s+(?P<body>.+?)(?=(?:\n\d{1,3}(?:\s*[-–—]\s*\d{1,3})?\s*[.:]\s+)|\n(?:Canto|CANTO)\s+|\Z)",
        re.S,
    )
    for cantica, title, path in pages:
        text = ""
        try:
            url = (
                "https://en.wikisource.org/w/api.php?action=parse&page="
                + title.replace(" ", "_")
                + "&prop=wikitext&format=json"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "dante-fuzzy/1.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read().decode())
            text = (data.get("parse") or {}).get("wikitext", {}).get("*") or ""
        except Exception as e:
            print("  longfellow api fail", cantica, e)
        if len(text) < 2000 and path.exists():
            text = html_text(path.read_text(errors="replace"))
        chunks = canto_re.split(text)
        i = 1
        while i + 1 < len(chunks):
            token, body = chunks[i], chunks[i + 1]
            token_u = token.strip().upper()
            canto = ROMAN.get(token_u) or (int(token_u) if token_u.isdigit() else None)
            if not canto:
                i += 2
                continue
            if not re.match(r"\s*\d", body[:200]):
                para = re.split(r"\n\d{1,3}\s*[.:]", body, maxsplit=1)[0]
                add_note(
                    store, cantica, canto, [], "longfellow", para,
                    f"Longfellow 1867, Notes, {cantica} {canto}",
                    canto_level=True,
                )
            for nm in note_re.finditer(body):
                lines = parse_line_spec(nm.group("spec"))
                add_note(
                    store, cantica, canto, lines, "longfellow", nm.group("body"),
                    f"Longfellow 1867, Notes, {cantica} {canto}, v. {nm.group('spec').replace(' ','')}",
                )
            i += 2
    return store


# ── Tommaseo Inferno OCR (canto-level + rough verse) ──
def parse_verse_txt(path: Path, author: str, year: int, default_cantica: str | None):
    store = defaultdict(lambda: {"canto": [], "tz": {}})
    if not path.exists():
        return store
    text = path.read_text(errors="replace")
    text = text.replace("\f", "\n")
    # split keeping headers
    parts = re.split(r"(?m)(?=^[ \t]*CANTO\s+[A-ZÀIVX0-9]+\.?\s*$)", text)
    cantica = default_cantica or "Inferno"
    for part in parts:
        head = part[:400].upper()
        if re.search(r"\bPURGATORIO\b", head) or re.search(r"\bPURGATORIO\b", part[:1200]):
            cantica = "Purgatorio"
        elif re.search(r"\bPARADISO\b", head) or (
            default_cantica is None and re.search(r"\bPARADISO\b", part[:1200])
        ):
            if default_cantica is None:
                cantica = "Paradiso"
        hm = re.match(r"\s*CANTO\s+([A-ZÀ]+|[IVX]+|\d{1,2})\.?", part, re.I)
        if not hm:
            continue
        token = hm.group(1).strip().upper()
        if token in IT_ORD:
            canto = IT_ORD[token]
        elif token in ROMAN:
            canto = ROMAN[token]
        elif token.isdigit():
            canto = int(token)
        else:
            continue
        if canto < 1 or canto > 34:
            continue
        body = part[hm.end():]
        arg = re.search(
            r"ARGOMENTO\s*(.{80,900}?)(?=\n\s*\d{1,3}\s*[.:]|\nNel mezzo|\nPer correr|\nLa gloria|\Z)",
            body, re.S | re.I,
        )
        if arg:
            add_note(store, cantica, canto, [], author, arg.group(1),
                     f"{author.title()} {year}, {cantica} {canto} (argomento)", True)
        elif not re.match(r"\s*\d", body[:200]):
            para = re.split(r"\n\s*\d{1,3}\s*[.:\-]", body, maxsplit=1)[0]
            add_note(store, cantica, canto, [], author, para[:1100],
                     f"{author.title()} {year}, {cantica} {canto}", True)
        for nm in re.finditer(
            r"(?:(?<=\n)|(?<=^))\s*(?P<spec>\d{1,3}(?:\s*[-–—]\s*\d{1,3})?)\s*[.:]\s+(?P<body>.{40,900}?)(?=\n\s*\d{1,3}(?:\s*[-–—]\s*\d{1,3})?\s*[.:]|\Z)",
            body, re.S,
        ):
            add_note(
                store, cantica, canto, parse_line_spec(nm.group("spec")),
                author, nm.group("body"),
                f"{author.title()} {year}, {cantica} {canto}, v. {nm.group('spec').replace(' ','')}",
            )
    return store


def parse_tommaseo():
    store = defaultdict(lambda: {"canto": [], "tz": {}})
    path = PD / "it/tommaseo_1865_inferno.txt"
    if not path.exists():
        return store
    text = path.read_text(errors="replace")
    chunks = re.split(r"CANTO\s+([IVX]+|\d{1,2})\b", text)
    i = 1
    while i + 1 < len(chunks):
        token, body = chunks[i], chunks[i + 1]
        token_u = token.strip().upper()
        canto = ROMAN.get(token_u) or (int(token_u) if token_u.isdigit() else None)
        if not canto:
            i += 2
            continue
        # ragionamento: first 900 chars
        add_note(
            store, "Inferno", canto, [], "tommaseo", body[:1200],
            f"Tommaseo 1865, Inferno {canto}",
            canto_level=True,
        )
        for nm in re.finditer(
            r"(?:(?<=\n)|(?<=^))(?P<spec>\d{1,3})\s*[.:]\s+(?P<body>.{40,400}?)(?=\n\d{1,3}\s*[.:]|\Z)",
            body, re.S,
        ):
            add_note(
                store, "Inferno", canto, [int(nm.group("spec"))], "tommaseo",
                nm.group("body"),
                f"Tommaseo 1865, Inferno {canto}, v. {nm.group('spec')}",
            )
        i += 2
    return store


def merge(*stores):
    out = defaultdict(lambda: {"canto": [], "tz": {}})
    for st in stores:
        for k, v in st.items():
            out[k]["canto"].extend(v.get("canto") or [])
            for tz, notes in (v.get("tz") or {}).items():
                out[k]["tz"].setdefault(tz, []).extend(notes)
    # dedupe similar starts per author/tz
    for k, v in out.items():
        v["canto"] = _dedupe(v["canto"])[:8]
        for tz in list(v["tz"]):
            v["tz"][tz] = _dedupe(v["tz"][tz])[:12]
            if not v["tz"][tz]:
                del v["tz"][tz]
    return out


def _dedupe(notes):
    seen = set()
    by_a = {}
    for n in notes:
        sig = (n["a"], n["t"][:80])
        if sig in seen:
            continue
        seen.add(sig)
        by_a.setdefault(n["a"], []).append(n)
    out = []
    # keep up to 2 excerpts per author so later sources remain visible
    authors = list(by_a)
    for a in authors:
        out.extend(by_a[a][:2])
    return out


def main():
    print("parsing tozer…")
    t = parse_tozer()
    print("  keys", len(t))
    print("parsing scartazzini…")
    s = parse_scartazzini()
    print("  keys", len(s))
    print("parsing longfellow…")
    l = parse_longfellow()
    print("  keys", len(l))
    print("parsing tommaseo…")
    m = parse_tommaseo()
    print("  keys", len(m))
    extras = [
        parse_verse_txt(PD / "it/torraca_1905.txt", "torraca", 1905, None),
        parse_verse_txt(PD / "it/campi_1888_inferno.txt", "campi", 1888, "Inferno"),
        parse_verse_txt(PD / "it/campi_1891_purgatorio.txt", "campi", 1891, "Purgatorio"),
        parse_verse_txt(PD / "it/campi_1893_paradiso.txt", "campi", 1893, "Paradiso"),
        parse_verse_txt(PD / "it/bianchi_1857.txt", "bianchi", 1857, None),
        parse_verse_txt(PD / "it/fraticelli_1881.txt", "fraticelli", 1881, None),
    ]
    for i, e in enumerate(extras):
        print("  extra", i, "keys", len(e))
    alls = merge(t, s, l, m, *extras)
    by_c = {"Inferno": {}, "Purgatorio": {}, "Paradiso": {}}
    for k, v in alls.items():
        cant, canto = k.split(":")
        if cant not in by_c:
            continue
        by_c[cant][str(int(canto))] = v
    meta = {"authors": AUTHORS}
    for cant, data in by_c.items():
        payload = {"authors": AUTHORS, "canti": data}
        dest = OUT / f"{cant}.json"
        dest.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        n_tz = sum(len(x.get("tz") or {}) for x in data.values())
        print(cant, "canti", len(data), "terzine-con-note", n_tz, "bytes", dest.stat().st_size)


if __name__ == "__main__":
    main()
