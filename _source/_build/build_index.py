#!/usr/bin/env python3
"""Erzeugt assets/search-index.json aus den fertigen HTML-Seiten.

Jeder Abschnitt (section mit Überschrift) wird zu einem Eintrag mit Titel,
Fliesstext, Zielseite und – falls vorhanden – Ankersprung. Der Chat-Bot
durchsucht diesen Index clientseitig; es verlässt kein Text die Website.
"""
import json, re, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = {
    "index.html": "Startseite",
    "fachausweis.html": "Eidg. Fachausweis",
    "weiterbildung.html": "Weiterbildung",
    "veranstaltungen.html": "Veranstaltungen",
    "ueber-uns.html": "Über uns",
    "anmeldung.html": "Anmeldung",
    "kontakt.html": "Kontakt",
    "datenschutz.html": "Datenschutz",
}

def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def sections(page_html):
    # Innerhalb <section ...> ... </section> arbeiten
    out = []
    for sec in re.findall(r"<section\b[^>]*>.*?</section>", page_html, flags=re.S):
        m_id = re.search(r'id="([^"]+)"', sec.split(">", 1)[0])
        anchor = m_id.group(1) if m_id else ""
        h = re.search(r"<h[12][^>]*>(.*?)</h[12]>", sec, flags=re.S)
        title = strip_tags(h.group(1)) if h else ""
        # Text: alle Absätze, Listen, Karten, Steps
        body_parts = re.findall(r"<(?:p|li|span)\b[^>]*>(.*?)</(?:p|li|span)>", sec, flags=re.S)
        body = strip_tags(" ".join(body_parts))
        if not title and not body:
            continue
        out.append({"title": title, "text": body, "anchor": anchor})
    return out

index = []
for fname, label in PAGES.items():
    fp = ROOT / fname
    if not fp.exists():
        continue
    doc = fp.read_text(encoding="utf-8")
    # Header/Footer wegschneiden, damit die Navigation nicht jeden Treffer verwässert
    body = doc
    if "<!-- ================================================================== HERO -->" in doc:
        body = doc[doc.index("<!-- ================================================================== HERO -->"):]
    elif '<section class="hero"' in doc:
        body = doc[doc.index('<section class="hero"'):]
    if "<!-- ================================================================ FOOTER -->" in body:
        body = body[:body.index("<!-- ================================================================ FOOTER -->")]

    for sec in sections(body):
        if len(sec["title"]) + len(sec["text"]) < 12:
            continue
        url = fname + ("#" + sec["anchor"] if sec["anchor"] else "")
        index.append({
            "page": label,
            "url": url,
            "title": sec["title"] or label,
            "text": sec["text"][:900],
        })

out = ROOT / "assets" / "search-index.json"
out.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(index)} Abschnitte indexiert -> {out.relative_to(ROOT)}")
