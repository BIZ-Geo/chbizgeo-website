#!/usr/bin/env python3
"""Baut die Unterseiten des BIZ-Geo-Prototyps mit gemeinsamem Header/Footer.

Header und Footer werden aus index.html extrahiert, damit es genau eine
Quelle der Wahrheit gibt. Aufruf:  python3 _build/build.py
"""
import html, re, pathlib
import daten

esc = lambda t: html.escape(t, quote=False)
MODULE = daten.module()
EVENTS = daten.veranstaltungen()
HIGHLIGHTS = daten.highlights(EVENTS)
KURSE = [e for e in EVENTS if e["typ"] == "Kurs"][:3]      # «Aktuelle Kurse» (Weiterbildung)

ROOT = pathlib.Path(__file__).resolve().parent.parent
index = (ROOT / "index.html").read_text(encoding="utf-8")


def home_module(kind):
    return "".join(f"""      <a class="module module--{kind}" href="modul-{k}.html">
        <img class="module__icon" src="assets/eyecatcher/{m['code']}.png" alt="{daten.t('eyecatcher_modul')} {m['code']} – {esc(m['title'])}" loading="lazy">
        <span class="module__body">
          <span class="module__code">{daten.t('modul')} {m['code']}</span>
          <span class="module__title">{esc(m['title'])}</span>
        </span>
      </a>
""" for k, m in MODULE.items() if m["kind"] == kind)


def home_termine():
    mon = daten.MONATE_KURZ[daten.REGION]
    termine = [e for e in EVENTS if e["startseite"]][:5]
    if not termine:
        return f'      <li class="events__leer">{esc(daten.t("keine_termine"))}</li>\n'
    return "".join(f"""      <li>
        <span class="event__date"><b>{e["von"].day:02}</b><span>{mon[e["von"].month - 1]}</span></span>
        <span>
          <span class="event__title">{esc(e["titel"])}</span><br>
          <span class="event__meta">{esc(e["meta"])}</span>
        </span>
        <span class="event__tag">{e["typ"]}</span>
      </li>
""" for e in termine)


def home_highlights():
    out = ""
    # Highlights mit startseite=ja zuerst, dann nach Datum; höchstens drei Kacheln
    for h in sorted(HIGHLIGHTS, key=lambda h: not h["startseite"])[:3]:
        zeilen = [h["ort"], h["wann"]] if h["mehrfach"] else [h["wann"]]
        zeilen.append(h["text"])
        tag = (f'        <span class="event__tag card__tag">{daten.t("partner")} · {esc(h["partner"])}</span>\n'
               if h["partner"] else "")
        out += ('      <a class="card card--tone" href="veranstaltungen.html#highlights">\n'
                f'        <h3>{esc(h["titel"])}</h3>\n'
                + "".join(f"        <p>{esc(z)}</p>\n" for z in zeilen if z)
                + tag + "      </a>\n")
    return out or f'      <p class="grid__leer">{esc(daten.t("keine_highlights"))}</p>\n'


# Datengetriebene Bereiche der Startseite (zwischen <!-- DATEN:x --> und <!-- /DATEN:x -->) füllen
for _name, _inhalt in (("basismodule", home_module("basis")), ("wahlmodule", home_module("wahl")),
                       ("termine", home_termine()), ("highlights", home_highlights())):
    index = re.sub(rf"(<!-- DATEN:{_name} -->\n).*?(<!-- /DATEN:{_name} -->)",
                   lambda mt, i=_inhalt: mt.group(1) + i + mt.group(2), index, flags=re.S)
(ROOT / "index.html").write_text(index, encoding="utf-8")

HEADER = index[index.index("<!-- ================================================================ HEADER -->"):
               index.index("<!-- ================================================================== HERO -->")]
FOOTER = index[index.index("<!-- ================================================================ FOOTER -->"):
               index.index("<script src=\"assets/site.js\"></script>")]

HEAD = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} – BIZ Geo</title>
<meta name="description" content="{desc}">
<link rel="alternate" hreflang="de" href="https://biz-geo.ch/{slug}">
<link rel="alternate" hreflang="fr" href="https://biz-geo.ch/fr/{slug}">
<link rel="alternate" hreflang="it" href="https://biz-geo.ch/it/{slug}">
<link rel="icon" type="image/png" sizes="256x256" href="assets/favicon.png">
<link rel="apple-touch-icon" href="assets/favicon.png">
<link rel="stylesheet" href="assets/styles.css">
<link rel="stylesheet" href="assets/chatbot.css">
</head>
<body>
"""

TAIL = ('<script src="assets/site.js"></script>\n'
        '<script src="assets/chatbot.js"></script>\n</body>\n</html>\n')


def page(slug, title, desc, body):
    html = HEAD.format(title=title, desc=desc, slug=slug) + HEADER + body + FOOTER + TAIL
    (ROOT / slug).write_text(html, encoding="utf-8")
    print("geschrieben:", slug)


def hero(eyebrow, h1, lead, actions=""):
    return f"""
<section class="hero">
  <div class="wrap">
    <p class="breadcrumb"><a href="index.html">Start</a> &nbsp;/&nbsp; {eyebrow}</p>
    <h1 style="font-size:var(--step-3)">{h1}</h1>
    <p class="hero__claim">{lead}</p>
    {f'<div class="hero__actions">{actions}</div>' if actions else ''}
  </div>
</section>
"""


def module_card(kind, code, title, meta, anchor):
    """Modulkachel mit dem Original-Eyecatcher, verlinkt auf die Detailseite.

    Die Eyecatcher-Grafik bringt die Flächenfarbe nach CD-Regel bereits mit
    (Basismodule Greige, Wahlmodule Secondary Navy); die Kachel führt sie fort.
    Die Unterschrift (meta) wird nur ausgegeben, wenn sie gesetzt ist.
    """
    key, code = code, f"{daten.t('modul')} {code}"
    meta_html = f'\n          <span class="module__meta">{meta}</span>' if meta else ""
    return f"""      <a class="module module--{kind}" id="{anchor}" href="modul-{key.lower()}.html">
        <img class="module__icon" src="assets/eyecatcher/{key}.png" alt="{daten.t('eyecatcher_modul')} {key} – {title}" loading="lazy">
        <span class="module__body">
          <span class="module__code">{code}</span>
          <span class="module__title">{title}</span>{meta_html}
        </span>
      </a>
"""


# --------------------------------------------------------------- FACHAUSWEIS
basis = [(m["code"], esc(m["title"]), k) for k, m in MODULE.items() if m["kind"] == "basis"]
wahl = [(m["code"], esc(m["title"]), k) for k, m in MODULE.items() if m["kind"] == "wahl"]

fa_body = hero(
    "Eidg. Fachausweis",
    "Eidg. Fachausweis Geomatiktechnik",
    "Der berufsbegleitende Lehrgang qualifiziert Fachleute der Geomatik für anspruchsvolle "
    "Aufgaben in Vermessung, Geoinformation und Bauwesen – mit eidgenössisch anerkanntem Abschluss.",
    '<a class="btn btn--primary" href="anmeldung.html">Zur Anmeldung</a>'
    '<a class="btn btn--ghost" href="#ablauf">Ablauf ansehen</a>') + """
<section class="section" id="ueberblick">
  <div class="wrap">
    <div class="grid grid--2">
      <div>
        <p class="eyebrow">Auf einen Blick</p>
        <h2 style="font-size:var(--step-2)">Aufbau, Dauer, Kosten</h2>
        <p class="lead">Alle Eckdaten, die vor der Anmeldung zählen – ohne Suchen.</p>
      </div>
      <div class="grid" style="gap:0">
        <div class="filelist">
          <ul class="filelist">
            <li><strong>Aufbau</strong><br><span>5 Basismodule + mind. 5 Wahlmodule + Abschlussarbeit</span></li>
            <li><strong>Dauer</strong><br><span>Rund 2 Jahre berufsbegleitend</span></li>
            <li><strong>Unterricht</strong><br><span>Präsenzkurse primär in Zürich oder Zug, viele Kurstage online</span></li>
            <li><strong>Kosten</strong><br><span>Modulpreise gemäss Preisliste; <a href="https://www.sbfi.admin.ch/de/bundesbeitraege-fuer-kurse-die-auf-eidgenoessische-pruefungen-vorbereiten" target="_blank" rel="noopener">Bundesbeiträge</a> möglich</span></li>
            <li><strong>Voraussetzungen</strong><br><span>EFZ Geomatiker/in oder gleichwertige Qualifikation mit Berufspraxis</span></li>
            <li><strong>Abschluss</strong><br><span>Eidg. Fachausweis nach bestandener Berufsprüfung</span></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--greige" id="basismodule">
  <div class="wrap">
    <p class="eyebrow">Pflichtteil</p>
    <h2 style="font-size:var(--step-2)">Basismodule</h2>
    <p class="lead mb-3">Die gemeinsame Grundlage für alle Teilnehmenden.</p>
    <div class="grid grid--4">
""" + "".join(module_card("basis", c, t, "", a) for c, t, a in basis) + """
    </div>
  </div>
</section>

<section class="section" id="wahlmodule">
  <div class="wrap">
    <p class="eyebrow">Vertiefung</p>
    <h2 style="font-size:var(--step-2)">Wahlmodule</h2>
    <p class="lead mb-3">
      Mindestens fünf Wahlmodule werden für den Fachausweis angerechnet. Jedes Wahlmodul ist
      auch einzeln als Weiterbildung buchbar.
    </p>
    <div class="grid grid--4">
""" + "".join(module_card("wahl", c, t, "", a) for c, t, a in wahl) + """
    </div>
    <p class="note mt-2">
      Wahlmodule ohne garantierte Durchführung finden vorbehaltlich einer ausreichenden Zahl
      von Anmeldungen statt. Die aktuelle Modulplanung liegt im Downloadbereich.
    </p>
  </div>
</section>

<section class="section section--greige" id="regeln">
  <div class="wrap">
    <div class="grid grid--2">
      <div>
        <p class="eyebrow">Gut zu wissen</p>
        <h2 style="font-size:var(--step-2)">Regeln im Lehrgang</h2>
        <p class="lead">Was für Planung, Anmeldung und Modulprüfungen gilt.</p>
      </div>
      <ul class="filelist">
        <li><strong>Modulprüfungen</strong><br><span>Jedes Modul schliesst mit einer Modulprüfung ab; bestanden ab Note 4, gültig während sechs Jahren.</span></li>
        <li><strong>Lehrgangsstart</strong><br><span>Die Basismodule starten jeweils im August und dauern bis Juli des Folgejahres. Die Studienplätze sind beschränkt.</span></li>
        <li><strong>Wahlmodule</strong><br><span>Am besten nach den Basismodulen besuchen. Bei der Anmeldung den Klassencode angeben, z. B. S1-27 (siehe Modulplanung).</span></li>
        <li><strong>Planung</strong><br><span>Mindestens zwei Jahre einplanen. Für die Ferienplanung gilt der <a href="https://www.bbzh.ch/services/unterrichtszeiten-ferienplaene/" target="_blank" rel="noopener">Ferienplan des Kantons Zürich</a>.</span></li>
        <li><strong>Technik</strong><br><span>Persönlicher Laptop erforderlich; die GIS-Module benötigen Windows.</span></li>
        <li><strong>Berufsprüfung</strong><br><span>Anmeldung jeweils sechs Monate vor Prüfungsbeginn; bis dahin müssen alle gültigen Modulabschlüsse vorliegen.</span></li>
      </ul>
    </div>
  </div>
</section>

<section class="section section--dark" id="ablauf">
  <div class="wrap">
    <p class="eyebrow">Weg zum Abschluss</p>
    <h2 style="font-size:var(--step-2)">Weg zum Abschluss</h2>
    <ol class="steps mt-2" style="max-width:70ch">
      <li><div><h3>Beratung und Standortbestimmung</h3><p>Wir klären mit Ihnen Voraussetzungen, Anrechnungen und den passenden Einstiegszeitpunkt.</p></div></li>
      <li><div><h3>Anmeldung zum Lehrgang</h3><p>Anmeldung online; Aufnahme auf die Warteliste, falls ein Modul ausgebucht ist.</p></div></li>
      <li><div><h3>Basismodule absolvieren</h3><p>Fünf Module mit je einem Modulabschluss.</p></div></li>
      <li><div><h3>Wahlmodule vertiefen</h3><p>Mindestens fünf Module nach fachlichem Schwerpunkt.</p></div></li>
      <li><div><h3>Abschlussarbeit und Berufsprüfung</h3><p>Anmeldung zur eidg. Berufsprüfung über die Qualitätssicherungskommission (QSK).</p></div></li>
    </ol>
  </div>
</section>

<section class="section" id="downloads">
  <div class="wrap">
    <p class="eyebrow">Downloads</p>
    <h2 style="font-size:var(--step-2)">Schul- und Moduldaten</h2>
    <p class="lead mb-3">Aktuelle Planungsdokumente zum Herunterladen.</p>
    <ul class="filelist">
      <li><a href="https://geo-education.ch/wp-content/uploads/2026/08/Schulplanung__BIZGeo_20.08.2026.xlsx">Schulplanung BIZ Geo – Gesamtübersicht</a> <span>XLSX · Stand 20.08.2026</span></li>
      <li><a href="https://geo-education.ch/wp-content/uploads/2026/08/2026-08-20_Schulplanung_BIZGeo_Schuldatenliste.pdf" target="_blank" rel="noopener">Schuldatenliste</a> <span>PDF · Stand 20.08.2026</span></li>
      <li><a href="https://geo-education.ch/wp-content/uploads/2026/08/2026-09-21_Schulplanung_BIZGeo_B1-B5-1.pdf" target="_blank" rel="noopener">Schulplanung Basismodule B1–B5</a> <span>PDF</span></li>
      <li><a href="https://geo-education.ch/wp-content/uploads/2026/08/2026-08-21_Schulplanung_BIZGeo_S1-S8.pdf" target="_blank" rel="noopener">Schulplanung Wahlmodule S1–S8</a> <span>PDF</span></li>
      <li><a href="https://geo-education.ch/wp-content/uploads/2026/07/2026-07-19_Schulplanung_BIZGeo_Modulpruefungen.pdf" target="_blank" rel="noopener">Modulprüfungen – Termine</a> <span>PDF</span></li>
      <li><a href="https://geo-education.ch/wp-content/uploads/2026/07/2026-07-19_Schulplanung_BIZGeo_2026.pdf" target="_blank" rel="noopener">Modulplanung 2025–2027</a> <span>PDF · Stand 19.07.2026</span></li>
    </ul>
    <p class="note mt-2">
      <strong>Hinweis aus dem Workshop:</strong> Der bisherige Studierendenbereich (Dokumente,
      interne Unterlagen) wird künftig über Microsoft Teams abgewickelt und entfällt auf der Website.
      Öffentlich bleiben nur die hier gezeigten Planungsdokumente.
    </p>
  </div>
</section>

<section class="section section--greige" id="berufspruefung">
  <div class="wrap">
    <div class="grid grid--2">
      <div>
        <p class="eyebrow">Abschluss</p>
        <h2 style="font-size:var(--step-2)">Berufsprüfung</h2>
        <p class="lead">
          Der Lehrgang schliesst mit der eidgenössischen Berufsprüfung Geomatiktechnik ab.
          Prüfungsordnung, Wegleitung und Durchführung verantwortet die
          Qualitätssicherungskommission (QSK).
        </p>
        <p><a class="card__link" href="ueber-uns.html#qsk">Mehr zur QSK &rarr;</a></p>
      </div>
      <div>
        <ul class="filelist">
          <li><a href="https://www.berufsbildung-geomatik.ch/fileadmin/documents/Weiterbildung/QSK/PO_BP_Geomatiktechniker_d_genehmigt_20-05-2015.pdf" target="_blank" rel="noopener">Prüfungsordnung</a> <span>PDF · QSK</span></li>
          <li><a href="https://www.berufsbildung-geomatik.ch/fileadmin/documents/Weiterbildung/QSK/Wegleitung_Geomatiktechniker_d.pdf" target="_blank" rel="noopener">Wegleitung zur Prüfungsordnung</a> <span>PDF · QSK</span></li>
          <li><a href="http://portal.tv-geo.ch/" target="_blank" rel="noopener">Anmeldung Berufsprüfung</a> <span>Portal Trägerverein</span></li>
          <li><a href="https://geo-education.ch/wp-content/uploads/2026/07/1_Teilnahmebedingungen_20260716.pdf" target="_blank" rel="noopener">Teilnahmebedingungen</a> <span>PDF</span></li>
          <li><a href="https://geo-education.ch/wp-content/uploads/2020/06/Antragsformular-fu%CC%88r-Gleichwertigkeit_D.pdf" target="_blank" rel="noopener">Antrag Gleichwertigkeit Module</a> <span>PDF · QSK</span></li>
          <li><a href="https://www.sbfi.admin.ch/de/bundesbeitraege-fuer-kurse-die-auf-eidgenoessische-pruefungen-vorbereiten" target="_blank" rel="noopener">Bundesbeiträge (SBFI)</a> <span>Finanzierung</span></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <div class="cta">
      <div><h2>Fragen zum Lehrgang?</h2>
      <p style="margin:.5rem 0 0">Das Sekretariat berät Sie persönlich – auf Deutsch, Französisch oder Italienisch.</p></div>
      <a class="btn btn--primary" href="kontakt.html">Kontakt aufnehmen</a>
    </div>
  </div>
</section>
"""

page("fachausweis.html", "Eidg. Fachausweis Geomatiktechnik",
     "Aufbau, Dauer, Kosten, Voraussetzungen und Anmeldung zum Lehrgang Geomatiktechnik bei BIZ Geo.",
     fa_body)

# -------------------------------------------------------------- WEITERBILDUNG
# Fachgebiete und Kursangebot: _source/daten/fachgebiete.csv + kursangebot.csv
fields = [(esc(f["titel"]), esc(f["beschreibung"]), [esc(k) for k in f["kurse"]])
          for f in daten.fachgebiete()]

wb_body = hero(
    "Weiterbildung",
    "Weiterbildung und Einzelkurse",
    "Einzelne Module und Fachkurse – buchbar unabhängig vom Lehrgang. Für Fachleute, die "
    "gezielt eine Kompetenz aufbauen wollen, und für Betriebe, die ihr Team weiterbringen.",
    '<a class="btn btn--primary" href="anmeldung.html">Kurs buchen</a>') + """
<section class="section" id="fachgebiete">
  <div class="wrap">
    <p class="eyebrow">Fachgebiete</p>
    <h2 style="font-size:var(--step-2)">Fachgebiete</h2>
    <p class="lead mb-3">Fünf Fachgebiete bündeln das gesamte Kursangebot.</p>
    <div class="grid grid--3">
""" + "".join(f"""      <div class="card">
        <h3>{t}</h3><p>{d}</p>
        <div class="chips mt-2 mb-3">{"".join(f'<span class="chip">{k}</span>' for k in kurse)}</div>
        <a class="card__link" href="#kurse">Kurse ansehen →</a>
      </div>
""" for t, d, kurse in fields) + """
    </div>
  </div>
</section>

<section class="section" id="kurse">
  <div class="wrap">
    <p class="eyebrow">Nächste Durchführungen</p>
    <h2 style="font-size:var(--step-2)">Aktuelle Kurse</h2>
    <div class="grid grid--3 mt-2">
""" + "".join(f"""      <a class="module module--{kind}" href="anmeldung.html">
        <img class="module__icon" src="assets/eyecatcher/{key}.png" alt="{daten.t('eyecatcher')} {key} – {t}" loading="lazy">
        <span class="module__body">
          <span class="module__code">{code}</span>
          <span class="module__title">{t}</span>
          <span class="module__meta">{meta}</span>
        </span>
      </a>
""" for key, kind, code, t, meta in [
    (e["modul"] or "S2", "basis" if (e["modul"] or "S").startswith("B") else "wahl",
     f"{daten.t('kurs')} {e['klasse']}" if e["klasse"] else daten.t("einzelkurs"), esc(e["titel"]),
     esc(" · ".join(x for x in (e["datum_lang"], e["ort"]) if x)))
    for e in KURSE
]) + ("" if KURSE else f'      <p class="grid__leer">{esc(daten.t("keine_kurse"))}</p>\n') + """
    </div>
    <p class="note mt-2">
      Jeder Kurs trägt das Eyecatcher-Motiv seines Moduls – die Kachelfläche entspricht der
      Motivfarbe (Basismodule Greige, Wahlmodule Secondary Navy). Im Livebetrieb wird diese Liste
      aus der Veranstaltungsdatenbank gefüllt und lässt sich nach Fachgebiet, Datum, Ort und
      Sprache filtern.
    </p>
  </div>
</section>

<section class="section" id="arbeitgeber">
  <div class="wrap">
    <div class="grid grid--2">
      <div>
        <p class="eyebrow">Für Arbeitgeber und Berufsbildner</p>
        <h2 style="font-size:var(--step-2)">Für Arbeitgeber</h2>
        <p class="lead">
          Weiterbildung bei BIZ Geo ist auf den Schweizer Geomatikalltag zugeschnitten – von
          Fachleuten aus der Praxis, für die Praxis.
        </p>
      </div>
      <div class="grid" style="gap:1.25rem">
        <div class="audience"><h3>Berufsbegleitend</h3><p>Modulare Termine, planbar neben dem Tagesgeschäft.</p></div>
        <div class="audience"><h3>Anerkannt</h3><p>Module zahlen auf den eidg. Fachausweis ein.</p></div>
        <div class="audience"><h3>Gefördert</h3><p><a href="https://www.sbfi.admin.ch/de/bundesbeitraege-fuer-kurse-die-auf-eidgenoessische-pruefungen-vorbereiten" target="_blank" rel="noopener">Bundesbeiträge</a> für die Vorbereitung auf die Berufsprüfung.</p></div>
        <div class="audience"><h3>Mehrsprachig</h3><p>Angebote in allen Sprachregionen der Schweiz.</p></div>
      </div>
    </div>
  </div>
</section>
"""

page("weiterbildung.html", "Weiterbildung und Einzelkurse",
     "Einzelkurse und Module von BIZ Geo in fünf Fachgebieten – berufsbegleitend und anerkannt.",
     wb_body)

# ------------------------------------------------------------ VERANSTALTUNGEN
# Termine: _source/daten/veranstaltungen.csv (vergangene werden beim Build ausgeblendet)
MON = daten.MONATE_KURZ[daten.REGION]


def event_items(events):
    if not events:
        return f'      <li class="events__leer">{esc(daten.t("keine_termine"))}</li>\n'
    return "".join(f"""      <li>
        <span class="event__date"><b>{e["von"].day:02}</b><span>{MON[e["von"].month - 1]}</span></span>
        <span><span class="event__title">{esc(e["titel"])}</span><br><span class="event__meta">{esc(e["meta"])}</span></span>
        <span class="event__tag">{e["typ"]}</span>
      </li>
""" for e in events)


def highlight_cards(items):
    out = ""
    for h in items:
        tag = (f'        <span class="event__tag" style="border-color:var(--geo-navy-2);color:var(--geo-navy-2);'
               f'margin-bottom:.6rem;display:inline-block">{daten.t("partner")} · {esc(h["partner"])}</span>\n') if h["partner"] else ""
        ort = f'        <p>{esc(h["ort"])}</p>\n' if h["mehrfach"] and h["ort"] else ""
        text = f'        <p>{esc(h["text"])}</p>\n' if h["text"] else ""
        out += (f'      <div class="card">\n{tag}        <h3>{esc(h["titel"])}</h3>\n{ort}'
                f'        <p>{esc(h["wann"])}</p>\n{text}      </div>\n')
    return out or f'      <p class="grid__leer">{esc(daten.t("keine_highlights"))}</p>\n'


va_body = hero(
    "Veranstaltungen",
    "Veranstaltungskalender",
    "Unterricht, Modulabschlüsse, Kurse, Fristen und Anlässe – alle Termine an einem Ort.") + """
<section class="section section--dark">
  <div class="wrap">
    <p class="eyebrow">Alle Termine</p>
    <h2 style="font-size:var(--step-2)">Kommende Veranstaltungen</h2>
    <ul class="events mt-2">
""" + event_items(EVENTS) + """
    </ul>
    <p class="lead mt-2" style="font-size:.95rem">
      Im Livebetrieb: Filter nach Typ (Unterricht, Prüfung, Kurs, Anlass, Frist), Sprachregion
      und Zeitraum sowie iCal-Abo pro Klasse.
    </p>
  </div>
</section>

<section class="section" id="highlights">
  <div class="wrap">
    <p class="eyebrow">Höhepunkte</p>
    <h2 style="font-size:var(--step-2)">Highlights</h2>
    <p class="lead mb-3">Ausgewählte Höhepunkte im Jahr – über den regulären Unterricht hinaus.
      Hier zeigen wir auch Hinweise unserer Partnerschulen.</p>
    <div class="grid grid--3">
""" + highlight_cards(HIGHLIGHTS) + """    </div>
  </div>
</section>
"""

page("veranstaltungen.html", "Veranstaltungskalender",
     "Alle Termine von BIZ Geo: Unterricht, Modulabschlüsse, Kurse, Anmeldefristen und Anlässe.",
     va_body)

# ----------------------------------------------------------------- ÜBER UNS
ub_body = hero(
    "Über uns",
    "BIZ Geo – Bildungszentrum Geomatik Schweiz",
    "Wir sind das nationale Kompetenzzentrum für die höhere Berufsbildung in der Geomatik – "
    "getragen von den Verbänden und der Branche, tätig in allen Sprachregionen.") + """
<section class="section" id="vision">
  <div class="wrap">
    <div class="grid grid--2">
      <div>
        <p class="eyebrow">Unser Anspruch</p>
        <h2 style="font-size:var(--step-2)">Vision</h2>
        <p class="lead">
          Technisch engagiert für die Gestaltung der Umwelt: Geomatik macht den Raum verstehbar
          und planbar. Wir befähigen Fachleute, diesen Raum fachlich fundiert, digital und
          verantwortungsvoll mitzugestalten.
        </p>
      </div>
      <div class="grid" style="gap:1.25rem">
        <div class="audience"><h3>Praxisnah</h3><p>Dozierende aus Betrieben, Verwaltungen und Hochschulen.</p></div>
        <div class="audience"><h3>National</h3><p>Deutsch, Französisch und Italienisch – ein Zentrum für die ganze Schweiz.</p></div>
        <div class="audience"><h3>Anerkannt</h3><p>Eidgenössische Berufsprüfung, getragen von den Branchenverbänden.</p></div>
      </div>
    </div>
  </div>
</section>

<section class="section section--greige" id="team">
  <div class="wrap">
    <p class="eyebrow">Organisation</p>
    <h2 style="font-size:var(--step-2)">Team</h2>
    <div class="grid grid--3 mt-2">
      <div class="card"><h3>Schulleitung</h3><p>Strategische und operative Führung des Bildungszentrums.</p></div>
      <div class="card"><h3>Sekretariat</h3><p>Franziska André – Anmeldungen, Auskünfte, Administration.</p>
        <a class="card__link" href="kontakt.html">Kontakt →</a></div>
      <div class="card"><h3>Dozierende</h3><p>Fachleute aus der Praxis in allen drei Sprachregionen.</p>
        <a class="card__link" href="#stellen">Mitmachen →</a></div>
    </div>
  </div>
</section>

<section class="section" id="qsk">
  <div class="wrap">
    <div class="grid grid--2">
      <div>
        <p class="eyebrow">QSK</p>
        <h2 style="font-size:var(--step-2)">Qualitätssicherungskommission</h2>
        <p class="lead">
          Die QSK verantwortet die eidgenössische Berufsprüfung Geomatiktechnik: Reglement,
          Wegleitung, Prüfungsdurchführung und Qualitätssicherung.
        </p>
      </div>
      <div>
        <ul class="filelist">
          <li><a href="https://www.berufsbildung-geomatik.ch/fileadmin/documents/Weiterbildung/QSK/PO_BP_Geomatiktechniker_d_genehmigt_20-05-2015.pdf" target="_blank" rel="noopener">Prüfungsordnung Berufsprüfung Geomatiktechnik</a> <span>PDF · QSK</span></li>
          <li><a href="https://www.berufsbildung-geomatik.ch/fileadmin/documents/Weiterbildung/QSK/Wegleitung_Geomatiktechniker_d.pdf" target="_blank" rel="noopener">Wegleitung zur Prüfungsordnung</a> <span>PDF · QSK</span></li>
          <li><a href="http://portal.tv-geo.ch/" target="_blank" rel="noopener">Anmeldung Berufsprüfung (QSK)</a> <span>Portal Trägerverein</span></li>
          <li><a href="https://geo-education.ch/wp-content/uploads/2020/06/Antragsformular-fu%CC%88r-Gleichwertigkeit_D.pdf" target="_blank" rel="noopener">Antrag Gleichwertigkeit Module</a> <span>PDF · QSK</span></li>
          <li><a href="https://www.berufsbildung-geomatik.ch/de/weiterbildung/kommission-fuer-qualitaetssicherung-qsk.html" target="_blank" rel="noopener">Reglement Abschlussarbeit</a> <span>QSK</span></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="section section--dark" id="partner">
  <div class="wrap">
    <p class="eyebrow">Netzwerk</p>
    <h2 style="font-size:var(--step-2)">Partnerschaften</h2>
    <p class="lead mb-3">
      BIZ Geo arbeitet eng mit Verbänden, Behörden und Bildungspartnern zusammen – unter anderem
      mit dem SBFI und den Trägerorganisationen der Geomatikberufe.
    </p>
    <div class="grid grid--4">
      <div class="card"><h3>Trägerverbände</h3><p>Fachliche Verankerung und Qualitätssicherung.</p></div>
      <div class="card"><h3>SBFI</h3><p>Eidgenössische Anerkennung und Subventionierung.</p></div>
      <div class="card"><h3>Geounity</h3><p>Branchenplattform und Nachwuchsförderung.</p></div>
      <div class="card"><h3>Bildungspartner</h3><p>Kooperationen mit Schulen und Hochschulen.</p></div>
    </div>
  </div>
</section>

<section class="section" id="stellen">
  <div class="wrap">
    <div class="cta">
      <div>
        <h2>Offene Stellen</h2>
        <p style="margin:.5rem 0 0">
          Als Dozentin oder Dozent mitwirken: Wir suchen laufend Fachleute, die ihr Wissen
          weitergeben – in allen Sprachregionen.
        </p>
      </div>
      <a class="btn btn--primary" href="kontakt.html">Offene Stellen und Kontakt</a>
    </div>
  </div>
</section>
"""

page("ueber-uns.html", "Über uns", "BIZ Geo – Vision, Team, Qualitätssicherungskommission und Partnerschaften.", ub_body)

# ----------------------------------------------------------------- ANMELDUNG
an_body = hero(
    "Anmeldung",
    "Anmeldung",
    "Für den gesamten Lehrgang, für einzelne Module oder für Einzelkurse – die Anmeldung läuft online.") + """
<section class="section">
  <div class="wrap">
    <div class="grid grid--3">
      <div class="card">
        <h3>Lehrgang Geomatiktechnik</h3>
        <p>Anmeldung für den gesamten Lehrgang inkl. Basismodule.</p>
        <p class="note" style="font-size:.9rem">Anmeldungen für die Basismodule 2027 sind ab sofort möglich – die Studienplätze sind beschränkt.</p>
        <a class="card__link" href="#formular">Zum Formular →</a>
      </div>
      <div class="card">
        <h3>Einzelne Module</h3>
        <p>Basis- oder Wahlmodule separat buchen, mit Anrechnung an den Fachausweis.</p>
        <a class="card__link" href="#formular">Zum Formular →</a>
      </div>
      <div class="card">
        <h3>Berufsprüfung (QSK)</h3>
        <p>Anmeldung zur eidgenössischen Berufsprüfung über die Qualitätssicherungskommission.</p>
        <a class="card__link" href="ueber-uns.html#qsk">Zur QSK →</a>
      </div>
    </div>
  </div>
</section>

<section class="section section--greige" id="formular">
  <div class="wrap" style="max-width:760px">
    <p class="eyebrow">Formular</p>
    <h2 style="font-size:var(--step-2)">Anmeldung erfassen</h2>
    <p class="lead">
      Bitte füllen Sie das folgende Formular aus, um sich anzumelden.
    </p>
    <iframe
      src="https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=8_apS4QoKkW1z8WV9_7Cg9t2AP5fxhJOlEjgGGekZg9UQU9YMEMwR0RIQ01EUUlZTTVRSVhHUzhSTy4u"
      title="Anmeldeformular"
      style="width:100%;min-height:900px;border:0"
      allowfullscreen
      loading="lazy">
    </iframe>
  </div>
</section>
"""
page("anmeldung.html", "Anmeldung", "Anmeldung zum Lehrgang, zu einzelnen Modulen und zu Einzelkursen bei BIZ Geo.", an_body)

# ------------------------------------------------------------------- KONTAKT
ko_body = hero(
    "Kontakt",
    "Kontakt",
    "Das Sekretariat beantwortet Fragen zu Lehrgang, Kursen und Anmeldung – auf Deutsch, "
    "Französisch und Italienisch.") + """
<section class="section">
  <div class="wrap">
    <div class="grid grid--2">
      <div>
        <p class="eyebrow">Sekretariat</p>
        <h2 style="font-size:var(--step-2)">Bildungszentrum Geomatik Schweiz</h2>
        <p>
          Franziska André<br>
          Ringoldswilstrasse 228<br>
          3656 Tschingel
        </p>
        <p>
          Tel. <a href="tel:+41786741377">+41 78 674 13 77</a><br>
          E-Mail <a href="mailto:andre@biz-geo.ch">andre@biz-geo.ch</a>
        </p>
        <p class="note">
          Domainwechsel: geo-education.ch wird dauerhaft auf biz-geo.ch weitergeleitet.
          E-Mail-Adressen laufen bereits auf @biz-geo.ch.
        </p>
      </div>
      <div class="card">
        <h3>Nachricht senden</h3>
        <p>Formular-Platzhalter für den Prototyp.</p>
        <ul class="filelist">
          <li>Anliegen wählen: Lehrgang · Einzelkurs · Arbeitgeber · Medien</li>
          <li>Name, E-Mail, Sprachregion</li>
          <li>Nachricht</li>
        </ul>
        <a class="btn btn--outline" href="#" style="align-self:flex-start">Absenden</a>
      </div>
    </div>
  </div>
</section>
"""
page("kontakt.html", "Kontakt", "Kontakt zum Sekretariat des Bildungszentrums Geomatik Schweiz.", ko_body)

# ---------------------------------------------------------------- DATENSCHUTZ
ds_body = hero("Datenschutz", "Datenschutzerklärung",
               "Informationen zur Bearbeitung von Personendaten auf biz-geo.ch.") + """
<section class="section">
  <div class="wrap" style="max-width:75ch">
    <h2 style="font-size:var(--step-2)">Platzhalter</h2>
    <p>
      Dieser Text wird vor dem Livegang durch die geprüfte Datenschutzerklärung ersetzt
      (revidiertes Schweizer DSG). Zu regeln sind mindestens: verantwortliche Stelle,
      bearbeitete Daten, Anmeldeformulare, Newsletter, Analyse-Tools, Aufbewahrung,
      Rechte der betroffenen Personen und Kontaktadresse.
    </p>
    <p class="note">
      Aus dem Workshop: Datenschutz wird von einer Unterseite auf eine eigenständige Seite
      gehoben und zusätzlich prominent im Footer verlinkt.
    </p>
  </div>
</section>
"""
page("datenschutz.html", "Datenschutz", "Datenschutzerklärung von BIZ Geo.", ds_body)

print("\nFertig.")
