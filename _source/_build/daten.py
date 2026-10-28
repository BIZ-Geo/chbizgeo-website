#!/usr/bin/env python3
"""Liest die gepflegten Inhalte einer Sprachregion aus _source/daten/<region>/*.csv.

Je Region (de = Deutschschweiz, fr = Romandie, it = Ticino) gibt es einen Ordner mit
module.csv, fachgebiete.csv, kursangebot.csv und veranstaltungen.csv – jeweils nur in
der Sprache der Region. Format (Excel-tauglich): Semikolon als Trenner, UTF-8, Listen
innerhalb einer Zelle mit « | » getrennt, Ja/Nein-Spalten mit „ja“ oder leer, Datum
als TT.MM.JJJJ.

Welche Region gebaut wird, bestimmt die Umgebungsvariable BIZGEO_REGION (gesetzt von
build_regions.py, Standard „de“). Die Build-Skripte setzen die Texte der Region direkt
ein; die festen Seitentexte übersetzt build_regions.py anschliessend über
translate_data.py.
"""
import csv, datetime, html, os, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGION = os.environ.get("BIZGEO_REGION", "de")
DATEN = ROOT / "daten" / REGION

MONATE = {
    "de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
           "September", "Oktober", "November", "Dezember"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"],
    "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
           "settembre", "ottobre", "novembre", "dicembre"],
}
MONATE_KURZ = {
    "de": ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
    "fr": ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.",
           "nov.", "déc."],
    "it": ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"],
}

# Kurze Textbausteine, die die Build-Skripte mit den CSV-Inhalten kombinieren
TEXT = {
    "modul": {"de": "Modul", "fr": "Module", "it": "Modulo"},
    "eyecatcher": {"de": "Eyecatcher", "fr": "Visuel", "it": "Immagine guida"},
    "eyecatcher_modul": {"de": "Eyecatcher Modul", "fr": "Visuel module", "it": "Immagine guida modulo"},
    "lektionen": {"de": "Lektionen", "fr": "leçons", "it": "lezioni"},
    "kurs": {"de": "Kurs", "fr": "Cours", "it": "Corso"},
    "einzelkurs": {"de": "Einzelkurs", "fr": "Cours individuel", "it": "Corso singolo"},
    "partner": {"de": "Partner", "fr": "Partenaire", "it": "Partner"},
    "naechste": {"de": "Nächste Termine:", "fr": "Prochaines dates :", "it": "Prossime date:"},
    "und": {"de": "und", "fr": "et", "it": "e"},
    "ganztaegig": {"de": "Ganztägig", "fr": "Toute la journée", "it": "Intera giornata"},
    "keine_termine": {"de": "Aktuell sind keine Termine eingetragen.",
                      "fr": "Aucune date n'est inscrite pour le moment.",
                      "it": "Al momento non ci sono date in programma."},
    "keine_highlights": {"de": "Aktuell sind keine Highlights geplant.",
                         "fr": "Aucun temps fort n'est prévu pour le moment.",
                         "it": "Al momento non sono previsti highlight."},
    "keine_kurse": {"de": "Aktuell sind keine Kurse ausgeschrieben.",
                    "fr": "Aucun cours n'est programmé pour le moment.",
                    "it": "Al momento non ci sono corsi in programma."},
    "basismodul_im": {"de": "Basismodul im Lehrgang Geomatiktechnik bei BIZ Geo.",
                      "fr": "module de base du cursus en technique de la géomatique chez BIZ Geo.",
                      "it": "modulo di base del ciclo di formazione in tecnica della geomatica presso BIZ Geo."},
    "wahlmodul_im": {"de": "Wahlmodul im Lehrgang Geomatiktechnik bei BIZ Geo.",
                     "fr": "module à option du cursus en technique de la géomatique chez BIZ Geo.",
                     "it": "modulo a scelta del ciclo di formazione in tecnica della geomatica presso BIZ Geo."},
}

# Typ-Spalte: die Begriffe dürfen in der Sprache der Region stehen; intern gilt der deutsche Name
# (das Etikett auf der Website übersetzt translate_data.py)
TYPEN = {
    "Unterricht": ("unterricht", "enseignement", "lezione", "lezioni"),
    "Kurs": ("kurs", "cours", "corso"),
    "Prüfung": ("prüfung", "pruefung", "examen", "esame"),
    "Anlass": ("anlass", "événement", "evenement", "evento"),
    "Frist": ("frist", "délai", "delai", "scadenza"),
    "Highlight": ("highlight", "temps fort"),
}


def t(schluessel):
    """Textbaustein in der Sprache der Region."""
    return TEXT[schluessel][REGION]


def esc(s):
    return html.escape(s, quote=False)


def lesen(name):
    """Liest eine CSV-Datei der Region als Liste von dicts (leere Zeilen werden übersprungen)."""
    pfad = DATEN / name
    if not pfad.exists():
        raise SystemExit(f"Datei fehlt: daten/{REGION}/{name}")
    text = pfad.read_text(encoding="utf-8-sig")
    kopf = text.split("\n", 1)[0]
    trenner = ";" if kopf.count(";") >= kopf.count(",") else ","
    zeilen = []
    for nr, z in enumerate(csv.DictReader(text.splitlines(), delimiter=trenner), start=2):
        z = {k.strip(): (v or "").strip() for k, v in z.items() if k}
        if any(z.values()):
            z["_zeile"] = f"daten/{REGION}/{name}:{nr}"
            zeilen.append(z)
    return zeilen


def liste(wert):
    return [x.strip() for x in wert.split("|") if x.strip()] if wert else []


def ja(wert):
    return wert.strip().lower() in ("ja", "x", "1", "true", "oui", "si", "sì")


def datum(wert, wo):
    """Akzeptiert 22.10.2026, 22.10.26, 2026-10-22 (Excel speichert je nach Einstellung anders)."""
    if not wert:
        return None
    for f in ("%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.datetime.strptime(wert, f).date()
        except ValueError:
            pass
    raise SystemExit(f"Ungültiges Datum «{wert}» in {wo} – erwartet TT.MM.JJJJ")


# ------------------------------------------------------------------ Formatierung
def chf(betrag):
    n = int(re.sub(r"[^\d]", "", betrag) or 0)
    return "CHF " + f"{n:,}".replace(",", "'")


def zeit_text(zeit):
    if not zeit:
        return ""
    if zeit.lower() in ("ganztägig", "ganztags", "toute la journée", "intera giornata"):
        return t("ganztaegig")
    zeit = re.sub(r"\s*[–-]\s*", " – ", zeit)
    if REGION == "de":
        return zeit + " Uhr"
    if REGION == "fr":
        return re.sub(r"(\d{1,2}):(\d{2})", r"\1h\2", zeit)
    return zeit


def spanne_kurz(von, bis):
    """28.–30.10.2026 bzw. 28.10.–2.11.2026 (FR/IT ohne Punkt nach dem Tag)."""
    p = "." if REGION == "de" else ""
    if bis.month == von.month and bis.year == von.year:
        return f"{von.day}{p}–{bis.day}.{bis.month:02}.{bis.year}"
    return f"{von.day}.{von.month:02}{p}–{bis.day}.{bis.month:02}.{bis.year}"


def datum_lang(von, bis):
    """27. November 2026 / 28.–30. Oktober 2026 (DE) bzw. 27 novembre 2026 (FR/IT)."""
    p = "." if REGION == "de" else ""
    m = MONATE[REGION]
    if not bis or bis == von:
        return f"{von.day}{p} {m[von.month - 1]} {von.year}"
    if bis.month == von.month:
        return f"{von.day}{p}–{bis.day}{p} {m[bis.month - 1]} {bis.year}"
    return f"{von.day}{p} {m[von.month - 1]} – {bis.day}{p} {m[bis.month - 1]} {bis.year}"


def termine_liste(daten):
    """22.10., 28.10. und 3.12.2026"""
    p = "." if REGION == "de" else ""
    teile = [f"{d.day}.{d.month}{p}" for d in daten[:-1]]
    letzt = f"{daten[-1].day}.{daten[-1].month}.{daten[-1].year}"
    return letzt if not teile else ", ".join(teile) + f" {t('und')} " + letzt


# ------------------------------------------------------------------ Datensätze
def module():
    """Module in Dateireihenfolge: {key: {code, kind, title, lead, outcomes, …}}."""
    out = {}
    for z in lesen("module.csv"):
        code = z["code"].upper()
        art = z["art"].lower()
        kind = "basis" if ("basis" in art or "base" in art) else "wahl"
        out[code.lower()] = {
            "code": code, "kind": kind,
            "title": z["titel"],
            "lead": z.get("kurzbeschreibung", ""),
            "outcomes": liste(z.get("kompetenzen", "")),
            "voraussetzungen": liste(z.get("voraussetzungen", "")),
            "kurse": liste(z.get("kurse", "")),
            "lektionen": f"{z['lektionen']} {t('lektionen')}" if z.get("lektionen") else "",
            "kosten": chf(z["kosten_chf"]) if z.get("kosten_chf") else "",
        }
    return out


def fachgebiete():
    kurse = {}
    for z in lesen("kursangebot.csv"):
        kurse.setdefault(z["fachgebiet"], []).append(z["kurs"])
    out = []
    for z in lesen("fachgebiete.csv"):
        out.append({"id": z["id"], "titel": z["titel"], "beschreibung": z["beschreibung"],
                    "kurse": kurse.pop(z["id"], [])})
    for rest in kurse:
        raise SystemExit(f"daten/{REGION}/kursangebot.csv: Fachgebiet «{rest}» fehlt in fachgebiete.csv")
    return out


def typ_normal(wert, wo):
    w = (wert or "Anlass").strip().lower()
    for name, varianten in TYPEN.items():
        if w in varianten:
            return name
    raise SystemExit(f"{wo}: Typ «{wert}» unbekannt – erlaubt: " +
                     ", ".join(v for vs in TYPEN.values() for v in vs))


def veranstaltungen(ab=None):
    """Kommende Veranstaltungen (ab heute), nach Datum sortiert."""
    ab = ab or datetime.date.today()
    out = []
    for z in lesen("veranstaltungen.csv"):
        wo = z["_zeile"]
        von, bis = datum(z["datum"], wo), datum(z.get("bis", ""), wo)
        if (bis or von) < ab:
            continue
        bis = bis if bis and bis != von else None
        ort = z.get("ort", "")
        vorne = spanne_kurz(von, bis) if bis else zeit_text(z.get("zeit", ""))
        out.append({
            "von": von, "bis": bis, "typ": typ_normal(z.get("typ", ""), wo),
            "klasse": z.get("klasse", ""), "modul": z.get("modul", "").upper(),
            "partner": z.get("partner", ""), "ort": ort,
            "startseite": ja(z.get("startseite", "")), "highlight": ja(z.get("highlight", "")),
            "titel": z["titel"], "text": z.get("text", ""),
            "meta": " · ".join(x for x in (vorne, ort) if x),
            "datum_lang": datum_lang(von, bis),
        })
    return sorted(out, key=lambda e: (e["von"], e["titel"]))


def highlights(events):
    """Je Titel eine Kachel; mehrere Termine desselben Anlasses werden zusammengefasst."""
    gruppen = {}
    for e in events:
        if e["highlight"]:
            gruppen.setdefault(e["titel"], []).append(e)
    out = []
    for gruppe in gruppen.values():
        e = gruppe[0]
        if len(gruppe) == 1:
            wann = " · ".join(x for x in (e["datum_lang"], e["ort"]) if x)
        else:
            wann = f"{t('naechste')} {termine_liste([g['von'] for g in gruppe])}"
        out.append({**e, "wann": wann, "mehrfach": len(gruppe) > 1,
                    "startseite": any(g["startseite"] for g in gruppe)})
    return out


def zusammenfassung():
    """Kurzer Überblick für die Build-Ausgabe."""
    return (f"{len(module())} Module, {sum(len(f['kurse']) for f in fachgebiete())} Kurse, "
            f"{len(veranstaltungen())} kommende Termine")
