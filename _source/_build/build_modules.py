#!/usr/bin/env python3
"""Erzeugt eine Detailseite pro Modul: modul-<key>.html

Vorlage + Daten getrennt (die Daten stehen unten in MODULES und stammen von der
alten Seite geo-education.ch). Künftig werden diese Felder aus der Kursdatenbank
gezogen – die Vorlage bleibt gleich, nur die Datenquelle wechselt.
"""
import html as _html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
index = (ROOT / "index.html").read_text(encoding="utf-8")

HEADER = index[index.index("<!-- ================================================================ HEADER -->"):
               index.index("<!-- ================================================================== HERO -->")]
FOOTER = index[index.index("<!-- ================================================================ FOOTER -->"):
               index.index('<script src="assets/site.js"></script>')]

HEAD = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} – BIZ Geo</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/png" sizes="256x256" href="assets/favicon.png">
<link rel="apple-touch-icon" href="assets/favicon.png">
<link rel="stylesheet" href="assets/styles.css">
<link rel="stylesheet" href="assets/chatbot.css">
</head>
<body>
"""
TAIL = ('<script src="assets/site.js"></script>\n'
        '<script src="assets/chatbot.js"></script>\n</body>\n</html>\n')


def esc(s):
    return _html.escape(s, quote=False)


def outcomes_html(items):
    if not items:
        return ""
    if len(items) == 1:
        return f'<p class="lead">{esc(items[0])}</p>'
    lis = "".join(f"<li>{esc(x)}</li>" for x in items)
    return f'<ul class="ul-check">{lis}</ul>'


def facts_html(m):
    facts = []
    if m.get("lektionen"):
        facts.append(("Unterrichtszeit", m["lektionen"]))
    if m.get("kosten"):
        facts.append(("Modulkosten", m["kosten"]))
    facts.append(("Kategorie", "Basismodul" if m["kind"] == "basis" else "Wahlmodul"))
    cells = "".join(
        f'<div class="mfact"><span class="mfact__label">{esc(l)}</span>'
        f'<b class="mfact__value">{esc(v)}</b></div>' for l, v in facts)
    return f'<div class="mfacts">{cells}</div>'


def block(title, inner):
    if not inner:
        return ""
    return (f'<section class="section section--tight">\n  <div class="wrap">\n'
            f'    <p class="eyebrow">{esc(title)}</p>\n{inner}\n  </div>\n</section>\n')


def voraussetzungen_html(m):
    v = m.get("voraussetzungen")
    if not v:
        return ""
    if isinstance(v, str):
        return f'<p class="lead">{esc(v)}</p>'
    if len(v) == 1:
        return f'<p class="lead">{esc(v[0])}</p>'
    return '<ul class="ul-check">' + "".join(f"<li>{esc(x)}</li>" for x in v) + "</ul>"


def kurse_html(m):
    k = m.get("kurse")
    if not k:
        return ""
    chips = "".join(f'<span class="chip">{esc(x)}</span>' for x in k)
    return f'<div class="chips">{chips}</div>'


def page(key, m):
    code = m["code"]
    kind = m["kind"]
    ey = code if kind == "basis" else code   # B*.png greige, S*.png navy (Originalfarbe)
    cat = "Basismodul" if kind == "basis" else "Wahlmodul"
    lead = m.get("lead") or ("Die Detailangaben zu diesem Modul werden aus der Kursdatenbank "
                             "ergänzt.")
    bp = "btn--solid" if kind == "basis" else "btn--primary"
    bs = "btn--outline" if kind == "basis" else "btn--ghost"
    body = f"""
<section class="section modul-banner modul-banner--{kind}">
  <div class="wrap">
    <p class="breadcrumb"><a href="index.html">Start</a> &nbsp;/&nbsp;
      <a href="fachausweis.html">Eidg. Fachausweis</a> &nbsp;/&nbsp; Modul {code}</p>
    <div class="modul-banner__inner">
      <div>
        <p class="eyebrow">{cat}</p>
        <h1>Modul {code} – {esc(m['title'])}</h1>
        <p class="lead">{esc(lead)}</p>
        <div class="hero__actions">
          <a class="btn {bp}" href="anmeldung.html">Kursdaten &amp; Anmeldung</a>
          <a class="btn {bs}" href="fachausweis.html">Zur Übersicht</a>
        </div>
      </div>
      <div class="modul-banner__art">
        <img src="assets/eyecatcher/{ey}.png" alt="Eyecatcher Modul {code} – {esc(m['title'])}">
      </div>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">{facts_html(m)}</div>
</section>
"""
    body += block("Ihre Kompetenzen nach der Modulprüfung", outcomes_html(m.get("outcomes", [])))
    body += block("Voraussetzungen", voraussetzungen_html(m))
    body += block("Enthaltene Kurse und Lernziele", kurse_html(m))
    body += """
<section class="section section--tight">
  <div class="wrap">
    <p class="note">Diese Angaben stammen aus dem bisherigen Kursverzeichnis und werden im
    Livebetrieb automatisch aus der Kursdatenbank gezogen (Termine, Kosten, Lernziele).</p>
    <div class="cta mt-2">
      <div><h2>Bereit für Modul {code}?</h2>
      <p style="margin:.4rem 0 0;opacity:.85">Nächste Kursdaten und Online-Anmeldung im Anmeldebereich.</p></div>
      <a class="btn btn--primary" href="anmeldung.html">Zur Anmeldung</a>
    </div>
  </div>
</section>
""".replace("{code}", code)

    doc = (HEAD.format(title=f"Modul {code} – {m['title']}",
                       desc=f"Modul {code} {m['title']} – {cat} im Lehrgang Geomatiktechnik bei BIZ Geo.")
           + HEADER + body + FOOTER + TAIL)
    (ROOT / f"modul-{key}.html").write_text(doc, encoding="utf-8")
    return f"modul-{key}.html"


# ------------------------------------------------------------------ Moduldaten
MODULES = {
 "b1": {"code": "B1", "kind": "basis", "title": "Persönliche Kompetenzen",
        "lead": "Persönliche Kompetenzen erfassen, Arbeitstechniken anwenden und Lernende "
                "fachgerecht ausbilden.",
        "outcomes": [
            "Sie sind befähigt, ihre persönlichen Kompetenzen zu erfassen und richtig einzuschätzen.",
            "Sie wenden unterschiedliche Arbeitstechniken im betrieblichen Umfeld an und schaffen für Lernende ein optimales Ausbildungsklima.",
            "Sie setzen Bildungsverordnung und Bildungsplan für Geomatiker/in EFZ in der Ausbildung von Lernenden um."],
        "lektionen": "68 Lektionen", "kosten": "CHF 1'600",
        "voraussetzungen": "Keine. Für den gesamtschweizerisch anerkannten Berufsbildner-Kursausweis: Grundbildung mit EFZ und zweijährige Praxis im Lehrgebiet.",
        "kurse": ["Initial Workshop GMT", "Persönliche Kompetenz", "Berufsbildnerkurs", "Arbeitstechnik"]},
 "b2": {"code": "B2", "kind": "basis", "title": "Kommunikation",
        "lead": "Wirkungsvoll präsentieren, kompetent verhandeln und Texte situationsgerecht verfassen.",
        "outcomes": ["Wirkungsvoll präsentieren, Vortragstechniken situationsgerecht anwenden und rhetorisches Grundverständnis umsetzen. Verhandlungen und Sitzungen kompetent führen. Verschiedene Textsorten kennen, Texte analysieren sowie Briefe und Protokolle verfassen."],
        "lektionen": "40 Lektionen", "kosten": "CHF 1'400",
        "voraussetzungen": "Keine",
        "kurse": ["Präsentieren", "Kommunizieren"]},
 "b3": {"code": "B3", "kind": "basis", "title": "Geschäftsprozesse",
        "lead": "Staatliche und wirtschaftliche Zusammenhänge, Normenwerk, Qualitätsmanagement und Projektmethodik.",
        "outcomes": ["Staatliche Verhältnisse der Schweiz beschreiben und wirtschaftliche Zusammenhänge erklären. Überblick über Normenwerk und wichtige SIA-Normen der Geomatikbranche. Aufbau eines Qualitätsmanagement-Systems und Arbeitssicherheit bedarfsgerecht umsetzen. Kundenorientierung entwickeln und analysieren. Methoden, Instrumente und Modalitäten des Projektmanagements zweckdienlich einsetzen."],
        "lektionen": "84 Lektionen", "kosten": "CHF 2'100",
        "voraussetzungen": "Keine",
        "kurse": ["Normen", "Staat und Wirtschaft", "Qualitätsmanagement", "Kunden", "Projektmanagement"]},
 "b4": {"code": "B4", "kind": "basis", "title": "Geomatik + IT",
        "lead": "Datenaustausch, relationale Datenbanken und Datenmodelle der amtlichen Vermessung.",
        "outcomes": ["Den Datenaustausch fachgerecht umsetzen und externe Daten kritisch und fehlerfrei anwenden. Grundlagen relationaler Datenbanken in der Geomatik anwenden und Datenmodelle der amtlichen Vermessung beschreiben."],
        "lektionen": "104 Lektionen", "kosten": "CHF 3'300",
        "voraussetzungen": "Keine",
        "kurse": ["Datenbank", "Datenbankverarbeitung FME", "Interlis I + II", "Datenmodelle", "Datenformate, Schnittstellen, XML"]},
 "b5": {"code": "B5", "kind": "basis", "title": "IT Administration",
        "lead": "IT-Projekte umsetzen, IT-Recht und Datenschutz anwenden sowie IT-Grundschutz sicherstellen.",
        "outcomes": ["Anforderungen von IT-Projekten wiedergeben und kleinere IT-Projekte umsetzen. Rechtsverhältnisse im IT-Bereich, Haftung und Strafrecht aufzeigen; Datenschutzaspekte beschreiben und anwenden. Schützenswerte Daten identifizieren, Schutzbedarf bestimmen und Sicherheitskonzepte für einen IT-Grundschutz aufzeigen."],
        "lektionen": "64 Lektionen", "kosten": "CHF 2'000",
        "voraussetzungen": ["Kursnachweis Projektmanagement", "Nachweis adäquate Kenntnisse"],
        "kurse": ["IT Datenmanagement", "IT Projekt", "IT Recht", "IT Sicherheit"]},
 # Wahlmodule
 "s1": {"code": "S1", "kind": "wahl", "title": "Amtliche Vermessung",
        "lead": "Rechtliche und geomatiktechnische Grundlagen der amtlichen Vermessung – von Grundbuch- und Baurecht bis zu den einzelnen Arbeitsschritten.",
        "outcomes": ["Rechtliche und geomatiktechnische Grundlagen auf Stufe Bund und Kanton beschreiben, Zusammenhänge in der amtlichen Vermessung unterscheiden und die Arbeitsschritte situationsgerecht anwenden. Die wichtigen Artikel aus Grundbuch-, Bau- und Raumplanungsrecht beschreiben und Vertragsverhältnisse aus dem Obligationenrecht anwenden; Grundzüge des Handels- und Gesellschaftsrechts sowie Personen- und Sachrecht korrekt anwenden."],
        "lektionen": "84 Lektionen", "kosten": "CHF 2'000",
        "voraussetzungen": "Grundkenntnisse in Geomatik",
        "kurse": ["Grundbuchrechte / Rechte", "Amtliche Vermessung", "ÖREB & DMAV"]},
 "s2": {"code": "S2", "kind": "wahl", "title": "3D-Geodaten",
        "lead": "3D-Projekte realisieren: Erfassung, Verwaltung, Analyse und Visualisierung von 3D-Geodaten für klein- und grossräumige Gebiete.",
        "outcomes": ["3D-Projekte realisieren, geeignete 3D-Erfassungstechniken für klein- und grossräumige Gebiete ableiten und Techniken kennen, wie 3D-Daten erfasst, verwaltet, analysiert und weitergegeben werden. Erfasste 3D-Daten anhand einfacher Darstellungsgrundsätze korrekt visualisieren."],
        "lektionen": "72 Lektionen", "kosten": "CHF 2'200",
        "voraussetzungen": "Modulabschluss GIS-Basis oder Erfassungstechnik, adäquate Kenntnisse oder Berufserfahrung im Bereich Geoinformatik, Geomatik oder Planung.",
        "kurse": ["3D-Geodatenerfassung", "3D-Geodatenverwaltung", "BIM-Datenmanagement", "Additive Fertigung"]},
 "s3": {"code": "S3", "kind": "wahl", "title": "Landmanagement",
        "lead": "Raumkataster, kommunale Planungsinstrumente und die Zusammenhänge zwischen Umwelttechnik und Raumplanung.",
        "outcomes": ["Konzeption des ÖREB-Katasters verstehen, Eigentumsbeschränkungen beschreiben und Ziele des Katasters erläutern. Grundkenntnisse kommunaler Planungsinstrumente und -verfahren nennen, räumliche Problemstellungen erfassen und beurteilen sowie planerischen Handlungsbedarf erkennen. Zusammenhänge zwischen Umwelttechnik und Raumplanung erläutern und Pläne der Umwelttechnik lesen und interpretieren."],
        "lektionen": "48 Lektionen", "kosten": "CHF 1'800",
        "voraussetzungen": "Keine",
        "kurse": ["Mobilität & Infrastruktur", "Raumplanung", "Umwelttechnik"]},
 "s4": {"code": "S4", "kind": "wahl", "title": "Geomatik im Bauwesen",
        "lead": "Vermessungsaufträge im Bauwesen effizient abwickeln – von der Bauvermessung bis zur höheren Ingenieurvermessung.",
        "outcomes": ["Vermessungsaufträge im Bauwesen mit effizienten Lösungsansätzen abwickeln, mathematische Fertigkeiten erweitern und um eine Einführung in die statistische Methodenlehre ergänzen. Aufgaben der Bauvermessung und der einfachen Ingenieurvermessung umsetzen und Aufgaben der höheren Ingenieurvermessung auf eigene Vorhaben übertragen."],
        "lektionen": "72 Lektionen", "kosten": "CHF 2'200",
        "voraussetzungen": "Module Erfassungstechnik und Fixpunkte empfehlenswert oder adäquate Kenntnisse.",
        "kurse": ["Technisches Rechnen", "Bauvermessung und BIM", "Ingenieurvermessung", "Werkleitungskataster"]},
 "s5": {"code": "S5", "kind": "wahl", "title": "GIS",
        "lead": "Ein Geoinformationssystem im Betrieb einführen und betreiben – Aufbau, Modellierung, Analyse und Datenaustausch.",
        "outcomes": ["Ein Geoinformationssystem im betrieblichen Umfeld einführen und die Betriebsorganisation (Systemumgebung, Nachführung, Datenausgabe, Metasystem) beschreiben. Aufbau und Funktionalität von GIS umsetzen, Daten-Modellierungstechniken anwenden sowie Methoden für Erfassung, Verwaltung, Analyse, Datenaustausch und Visualisierung von Geodaten anwenden."],
        "lektionen": "72 Lektionen", "kosten": "CHF 2'300",
        "voraussetzungen": "Nachgewiesene Basiskenntnisse im Bereich Geoinformation und Datenbanken (GIS-Basis).",
        "kurse": ["Netzinformationssysteme", "GIS Betriebsorganisation", "GIS Kompetenz", "GIS Werkstatt"]},
 "s6": {"code": "S6", "kind": "wahl", "title": "Erfassungstechnik",
        "lead": "Felderfassungsgeräte prüfen und einsetzen, Instrumente der Geodatenerfassung und die Grundlagen der digitalen Photogrammetrie.",
        "outcomes": ["Prüfung und Justierung heutiger Felderfassungsgeräte anwenden und Funktionalitäten und Genauigkeiten gängiger Instrumente beschreiben. Anwendungsgebiete der Erfassungsgeräte unterscheiden, Messgeräte der Ingenieurvermessung beschreiben und das Grundprinzip der digitalen Photogrammetrie verstehen und in Zusammenarbeit mit einer Fachperson anwenden."],
        "lektionen": "56 Lektionen", "kosten": "CHF 2'100",
        "voraussetzungen": ["Grundkenntnisse Fehlertheorie und Messunsicherheiten empfehlenswert", "GIS-Grundlagenkenntnisse"],
        "kurse": ["Digitale Photogrammetrie", "Messtechnik"]},
 "s7": {"code": "S7", "kind": "wahl", "title": "Fixpunkte",
        "lead": "Fehlertheorie, LFP3-Netze und Ausgleichrechnung als Grundlage zur Beurteilung von Genauigkeiten.",
        "outcomes": ["Grundbegriffe der Fehlertheorie verstehen, Fehlergesetze und Fehlerfortpflanzung als Grundlage zur Beurteilung von Genauigkeiten kennen. LFP3-Netze erstellen und pflegen, Messungen zur Ausgleichung aufbereiten, das Prinzip der Ausgleichrechnung verstehen und Genauigkeits- und Zuverlässigkeitsangaben im LTOP-Ausdruck beurteilen."],
        "lektionen": "72 Lektionen", "kosten": "CHF 1'900",
        "voraussetzungen": "Kenntnisse der Genauigkeiten gängiger Erfassungsmethoden.",
        "kurse": ["Fixpunktnetze", "Fehlertheorie"]},
 "s8": {"code": "S8", "kind": "wahl", "title": "Bautechnik",
        "lead": "Baugrund, Naturgefahren, Hydrologie und Baustatik – die bautechnischen Grundlagen der Geomatik.",
        "outcomes": ["Naturgefahrentypen kennen, grundlegende geotechnische Mechanismen und Einsatzgebiete geotechnischer Messverfahren verstehen. Wichtige Grundlagen der Hydrologie und wasserbauliche Systeme kennen und einfache hydrologische Berechnungen ausführen. Grundlagen der Baustatik verstehen und grundlegende Berechnungen ableiten und anwenden."],
        "lektionen": "72 Lektionen", "kosten": "CHF 2'300",
        "voraussetzungen": "Gutes mathematisches Verständnis; Interesse an klimatischen Auswirkungen im Mittelland und in Bergregionen.",
        "kurse": ["Wasserbau / Hydrologie", "Baugrund / Geologie", "Klimawandel sichtbar machen", "Alpine Fernerkundung"]},
}

if __name__ == "__main__":
    for key, m in MODULES.items():
        print("geschrieben:", page(key, m))
    print(f"\n{len(MODULES)} Modulseiten erzeugt.")
