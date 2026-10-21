#!/usr/bin/env python3
"""Liest die gepflegten Inhalte aus _source/daten/*.csv.

Die CSV-Dateien sind die Quelle für Module (Beschreibungen, Preise, Lektionen),
Fachgebiete, Kursangebot und Veranstaltungskalender. Format (Excel-tauglich):
Semikolon als Trenner, UTF-8, Listen innerhalb einer Zelle mit « | » getrennt,
Ja/Nein-Spalten mit „ja“ oder leer, Datum als TT.MM.JJJJ.

Die Build-Skripte erzeugen daraus die deutschen Seiten. FR/IT kommen aus den
Sprachspalten derselben Zeile: csv_triples() liefert dafür (DE, FR, IT)-Einträge
für die Übersetzungstabelle – fehlt eine Übersetzung, bleibt der deutsche Text
stehen und der Build meldet die Lücke.
"""
import csv, datetime, html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATEN = ROOT / "daten"
SPRACHEN = ("de", "fr", "it")

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
# Ortsnamen, die in FR/IT anders heissen (Rest bleibt als Eigenname stehen)
ORTE = {"Zürich": ("Zurich", "Zurigo"), "Bern": ("Berne", "Berna"), "Zug": ("Zoug", "Zugo"),
        "Basel": ("Bâle", "Basilea"), "Luzern": ("Lucerne", "Lucerna")}
TYPEN = ("Unterricht", "Kurs", "Prüfung", "Anlass", "Frist", "Highlight")

_luecken = []          # fehlende FR/IT-Übersetzungen, vom Build gemeldet


def esc(s):
    return html.escape(s, quote=False)


def lesen(name):
    """Liest eine CSV-Datei als Liste von dicts (leere Zeilen werden übersprungen)."""
    pfad = DATEN / name
    text = pfad.read_text(encoding="utf-8-sig")
    trenner = ";" if text.split("\n", 1)[0].count(";") >= text.split("\n", 1)[0].count(",") else ","
    zeilen = []
    for nr, z in enumerate(csv.DictReader(text.splitlines(), delimiter=trenner), start=2):
        z = {k.strip(): (v or "").strip() for k, v in z.items() if k}
        if any(z.values()):
            z["_zeile"] = f"{name}:{nr}"
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


def sprachen(z, feld, wo, ist_liste=False):
    """{de, fr, it} eines Feldes; fehlende Übersetzungen fallen auf DE zurück."""
    de = z.get(f"{feld}_de", "")
    out = {"de": liste(de) if ist_liste else de}
    for lang in ("fr", "it"):
        v = z.get(f"{feld}_{lang}", "")
        if ist_liste:
            v = liste(v)
            if len(v) != len(out["de"]):
                if out["de"]:
                    _luecken.append(f"{wo}: {feld}_{lang} hat {len(v)} statt {len(out['de'])} Einträge")
                v = out["de"]
        elif de and not v:
            _luecken.append(f"{wo}: {feld}_{lang} fehlt")
            v = de
        out[lang] = v
    return out


# ------------------------------------------------------------------ Formatierung
def chf(betrag):
    n = int(re.sub(r"[^\d]", "", betrag) or 0)
    return "CHF " + f"{n:,}".replace(",", "'")


def zeit_text(zeit, lang):
    if not zeit:
        return ""
    if zeit.lower() in ("ganztägig", "ganztags"):
        return {"de": "Ganztägig", "fr": "Toute la journée", "it": "Intera giornata"}[lang]
    zeit = re.sub(r"\s*[–-]\s*", " – ", zeit)
    if lang == "de":
        return zeit + " Uhr"
    if lang == "fr":
        return re.sub(r"(\d{1,2}):(\d{2})", r"\1h\2", zeit)
    return zeit


def ort_text(ort, lang):
    if lang == "de":
        return ort
    i = 0 if lang == "fr" else 1
    for de, uebers in ORTE.items():
        ort = re.sub(rf"\b{de}\b", uebers[i], ort)
    return ort


def spanne_kurz(von, bis, lang):
    """28.–30.10.2026 bzw. 28.10.–2.11.2026 (FR/IT ohne Punkt nach dem Tag)."""
    p = "." if lang == "de" else ""
    if bis.month == von.month and bis.year == von.year:
        return f"{von.day}{p}–{bis.day}.{bis.month:02}.{bis.year}"
    return f"{von.day}.{von.month:02}{p}–{bis.day}.{bis.month:02}.{bis.year}"


def datum_lang(von, bis, lang):
    """27. November 2026 / 28.–30. Oktober 2026 (DE) bzw. 27 novembre 2026 (FR/IT)."""
    p = "." if lang == "de" else ""
    m = MONATE[lang]
    if not bis or bis == von:
        return f"{von.day}{p} {m[von.month - 1]} {von.year}"
    if bis.month == von.month:
        return f"{von.day}{p}–{bis.day}{p} {m[bis.month - 1]} {bis.year}"
    return f"{von.day}{p} {m[von.month - 1]} – {bis.day}{p} {m[bis.month - 1]} {bis.year}"


def termine_liste(daten, lang):
    """22.10., 28.10. und 3.12.2026"""
    p = "." if lang == "de" else ""
    und = {"de": "und", "fr": "et", "it": "e"}[lang]
    teile = [f"{d.day}.{d.month}{p}" for d in daten[:-1]]
    letzt = f"{daten[-1].day}.{daten[-1].month}.{daten[-1].year}"
    return letzt if not teile else ", ".join(teile) + f" {und} " + letzt


# ------------------------------------------------------------------ Datensätze
def module():
    """Module in Dateireihenfolge, als dict im Format von build_modules.MODULES."""
    out = {}
    for z in lesen("module.csv"):
        wo = z["_zeile"]
        code = z["code"].upper()
        art = z["art"].lower()
        kind = "basis" if art.startswith("basis") else "wahl"
        m = {
            "code": code, "kind": kind,
            "titel": sprachen(z, "titel", wo),
            "lead": sprachen(z, "kurzbeschreibung", wo),
            "outcomes": sprachen(z, "kompetenzen", wo, ist_liste=True),
            "voraussetzungen": sprachen(z, "voraussetzungen", wo, ist_liste=True),
            "kurse": sprachen(z, "kurse", wo, ist_liste=True),
            "lektionen": f"{z['lektionen']} Lektionen" if z.get("lektionen") else "",
            "kosten": chf(z["kosten_chf"]) if z.get("kosten_chf") else "",
        }
        m["title"] = m["titel"]["de"]
        out[code.lower()] = m
    return out


def fachgebiete():
    kurse = {}
    for z in lesen("kursangebot.csv"):
        kurse.setdefault(z["fachgebiet"], []).append(sprachen(z, "kurs", z["_zeile"]))
    out = []
    for z in lesen("fachgebiete.csv"):
        wo = z["_zeile"]
        out.append({"id": z["id"], "titel": sprachen(z, "titel", wo),
                    "beschreibung": sprachen(z, "beschreibung", wo), "kurse": kurse.pop(z["id"], [])})
    for rest in kurse:
        raise SystemExit(f"kursangebot.csv: Fachgebiet «{rest}» fehlt in fachgebiete.csv")
    return out


def veranstaltungen(ab=None):
    """Kommende Veranstaltungen (ab heute), nach Datum sortiert."""
    ab = ab or datetime.date.today()
    out = []
    for z in lesen("veranstaltungen.csv"):
        wo = z["_zeile"]
        von, bis = datum(z["datum"], wo), datum(z.get("bis", ""), wo)
        if (bis or von) < ab:
            continue
        typ = z.get("typ", "") or "Anlass"
        if typ not in TYPEN:
            raise SystemExit(f"{wo}: Typ «{typ}» unbekannt – erlaubt: {', '.join(TYPEN)}")
        e = {"von": von, "bis": bis if bis and bis != von else None, "typ": typ,
             "klasse": z.get("klasse", ""), "modul": z.get("modul", "").upper(),
             "partner": z.get("partner", ""),
             "startseite": ja(z.get("startseite", "")), "highlight": ja(z.get("highlight", "")),
             "titel": sprachen(z, "titel", wo), "text": sprachen(z, "text", wo)}
        e["meta"] = {}
        e["ort"] = {lang: ort_text(z.get("ort", ""), lang) for lang in SPRACHEN}
        for lang in SPRACHEN:
            vorne = spanne_kurz(von, e["bis"], lang) if e["bis"] else zeit_text(z.get("zeit", ""), lang)
            e["meta"][lang] = " · ".join(x for x in (vorne, e["ort"][lang]) if x)
        e["datum_lang"] = {lang: datum_lang(von, e["bis"], lang) for lang in SPRACHEN}
        out.append(e)
    return sorted(out, key=lambda e: (e["von"], e["titel"]["de"]))


def highlights(events):
    """Je Titel eine Kachel; mehrere Termine desselben Anlasses werden zusammengefasst."""
    gruppen = {}
    for e in events:
        if e["highlight"]:
            gruppen.setdefault(e["titel"]["de"], []).append(e)
    out = []
    for gruppe in gruppen.values():
        e = gruppe[0]
        if len(gruppe) == 1:
            wann = {l: " · ".join(x for x in (e["datum_lang"][l], e["ort"][l]) if x) for l in SPRACHEN}
        else:
            vor = {"de": "Nächste Termine:", "fr": "Prochaines dates :", "it": "Prossime date:"}
            wann = {l: f"{vor[l]} {termine_liste([g['von'] for g in gruppe], l)}" for l in SPRACHEN}
        out.append({**e, "wann": wann, "mehrfach": len(gruppe) > 1})
    return out


# ------------------------------------------------------------------ Übersetzung
def _tripel(de, fr, it):
    return (esc(de), esc(fr), esc(it))


def csv_triples():
    """(DE, FR, IT) für alle Texte, die die Build-Skripte aus den CSV-Dateien erzeugen."""
    t = []
    for m in module().values():
        c, ti = m["code"], m["titel"]
        t.append(_tripel(ti["de"], ti["fr"], ti["it"]))
        t.append(_tripel(f"Modul {c} – {ti['de']}", f"Module {c} – {ti['fr']}", f"Modulo {c} – {ti['it']}"))
        t.append(_tripel(f"Modul {c} – {ti['de']} – BIZ Geo", f"Module {c} – {ti['fr']} – BIZ Geo",
                         f"Modulo {c} – {ti['it']} – BIZ Geo"))
        t.append(_tripel(f"Eyecatcher Modul {c} – {ti['de']}", f"Visuel module {c} – {ti['fr']}",
                         f"Immagine guida modulo {c} – {ti['it']}"))
        if m["kind"] == "basis":
            art = ("Basismodul", "module de base", "modulo di base")
        else:
            art = ("Wahlmodul", "module à option", "modulo a scelta")
        t.append(_tripel(f"Modul {c} {ti['de']} – {art[0]} im Lehrgang Geomatiktechnik bei BIZ Geo.",
                         f"Module {c} {ti['fr']} – {art[1]} du cursus en technique de la géomatique chez BIZ Geo.",
                         f"Modulo {c} {ti['it']} – {art[2]} del ciclo di formazione in tecnica della geomatica presso BIZ Geo."))
        t.append(_tripel(m["lead"]["de"], m["lead"]["fr"], m["lead"]["it"]))
        for feld in ("outcomes", "voraussetzungen", "kurse"):
            t += [_tripel(*x) for x in zip(m[feld]["de"], m[feld]["fr"], m[feld]["it"])]
        if m["lektionen"]:
            n = m["lektionen"].split()[0]
            t.append((f"{n} Lektionen", f"{n} leçons", f"{n} lezioni"))
    for f in fachgebiete():
        t.append(_tripel(f["titel"]["de"], f["titel"]["fr"], f["titel"]["it"]))
        t.append(_tripel(f["beschreibung"]["de"], f["beschreibung"]["fr"], f["beschreibung"]["it"]))
        t += [_tripel(k["de"], k["fr"], k["it"]) for k in f["kurse"]]
    events = veranstaltungen()
    t += list(zip(MONATE_KURZ["de"], MONATE_KURZ["fr"], MONATE_KURZ["it"]))
    for e in events:
        for feld in ("titel", "text", "meta", "datum_lang"):
            t.append(_tripel(e[feld]["de"], e[feld]["fr"], e[feld]["it"]))
        t.append(_tripel(*(" · ".join(x for x in (e["datum_lang"][l], e["ort"][l]) if x) for l in SPRACHEN)))
        if e["klasse"]:
            t.append(_tripel(f"Kurs {e['klasse']}", f"Cours {e['klasse']}", f"Corso {e['klasse']}"))
        modul = e["modul"] or "S2"
        t.append(_tripel(f"Eyecatcher {modul} – {e['titel']['de']}", f"Visuel {modul} – {e['titel']['fr']}",
                         f"Immagine guida {modul} – {e['titel']['it']}"))
    for h in highlights(events):
        t.append(_tripel(h["wann"]["de"], h["wann"]["fr"], h["wann"]["it"]))
        if h["partner"]:
            t.append(_tripel(f"Partner · {h['partner']}", f"Partenaire · {h['partner']}",
                             f"Partner · {h['partner']}"))
    return [x for x in t if x[0] and (x[1] != x[0] or x[2] != x[0])]


def luecken():
    return sorted(set(_luecken))
