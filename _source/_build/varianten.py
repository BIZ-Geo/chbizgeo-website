#!/usr/bin/env python3
"""Baut varianten.html – Vergleichsseite für die Darstellung der Modulkacheln."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
index = (ROOT / "index.html").read_text(encoding="utf-8")
HEADER = index[index.index("<!-- ================================================================ HEADER -->"):
               index.index("<!-- ================================================================== HERO -->")]
FOOTER = index[index.index("<!-- ================================================================ FOOTER -->"):
               index.index('<script src="assets/site.js"></script>')]

BASIS = [("B1", "Persönliche Kompetenzen"), ("B2", "Kommunikation"), ("B3", "Geschäftsprozesse"),
         ("B4", "Geomatik + IT"), ("B5", "IT Administration")]
WAHL = [("S1", "Amtliche Vermessung"), ("S2", "3D-Geodaten"), ("S3", "Landmanagement"),
        ("S4", "Geomatik im Bauwesen"), ("S5", "GIS"), ("S6", "Erfassungstechnik"),
        ("S7", "Fixpunkte"), ("S8", "Bautechnik")]


def img(k, t):
    return f'<img src="assets/eyecatcher/{k}.png" alt="Eyecatcher {k} – {t}" loading="lazy">'


def head(tag, title, text):
    return (f'<div class="variant-head"><span class="variant-tag">{tag}</span>'
            f'<h2>{title}</h2><p>{text}</p></div>')


# ---------------------------------------------------------------- Variante A
a = "".join(f'''      <a class="mod-a" href="fachausweis.html#{k.lower()}">
        {img(k, t)}
        <span class="mod-a__txt">
          <span class="mod-a__code">Modul {k}</span>
          <span class="mod-a__title">{t}</span>
        </span>
      </a>
''' for k, t in BASIS + WAHL)

VA = f'''
<section class="section">
  <div class="wrap">
    {head("Variante A", "Kompakte Zeile",
          "Der Eyecatcher wird zum Farbmarker: klein, quadratisch, links. Der Blick läuft an einer "
          "Kante entlang statt über 13 grosse Felder. Braucht am wenigsten Platz und bleibt auch bei "
          "20 Modulen übersichtlich – wirkt dafür sachlich statt plakativ.")}
    <div class="grid grid--3">
{a}    </div>
  </div>
</section>
'''

# ---------------------------------------------------------------- Variante B
def b(k, t, kind):
    return f'''      <a class="mod-b mod-b--{kind}" href="fachausweis.html#{k.lower()}">
        {img(k, t)}
        <span class="mod-b__txt">
          <span class="mod-b__code">Modul {k}</span>
          <span class="mod-b__title">{t}</span>
        </span>
      </a>
'''

VB = f'''
<section class="section section--tight">
  <div class="wrap">
    {head("Variante B", "Grosse Fläche mit Beschnitt",
          "Das Motiv wird herangezoomt und angeschnitten, der Text sitzt direkt auf der Farbfläche. "
          "Der Leerraum um die Zeichnungen verschwindet, die Kacheln bekommen Gewicht. Die stärkste "
          "Bildwirkung – die Motive sind allerdings nicht mehr vollständig zu sehen.")}
    <h3 style="margin-top:2rem">Basismodule</h3>
    <div class="grid grid--4 mt-2">
{"".join(b(k, t, "basis") for k, t in BASIS)}    </div>
    <h3 style="margin-top:3rem">Wahlmodule</h3>
    <div class="grid grid--4 mt-2">
{"".join(b(k, t, "wahl") for k, t in WAHL)}    </div>
  </div>
</section>
'''

# ---------------------------------------------------------------- Variante C
def c(k, t, kind):
    return f'''      <a class="mod-c mod-c--{kind}" href="fachausweis.html#{k.lower()}">
        {img(k, t)}
        <span class="mod-c__txt">
          <span class="mod-c__code">Modul {k}</span>
          <span class="mod-c__title">{t}</span>
        </span>
      </a>
'''

VC = f'''
<section class="section section--dark">
  <div class="wrap">
    {head("Variante C", "Kacheln auf dunkler Sektion",
          "Gleiche Kachel wie bisher, aber der Abschnitt steht auf Deep Geo Navy. Die Greige-Flächen "
          "haben plötzlich Halt und wirken als Fläche statt als heller Fleck auf Weiss – genau das "
          "Problem, das auf der Startseite auffällt. Kleinster Eingriff mit grosser Wirkung.")}
    <h3 style="margin-top:2rem">Basismodule</h3>
    <div class="grid grid--4 mt-2">
{"".join(c(k, t, "basis") for k, t in BASIS)}    </div>
    <h3 style="margin-top:3rem">Wahlmodule</h3>
    <div class="grid grid--4 mt-2">
{"".join(c(k, t, "wahl") for k, t in WAHL)}    </div>
  </div>
</section>
'''

# ---------------------------------------------------------------- Variante D
def d(k, t, kind):
    return f'''      <a class="mod-d mod-d--{kind}" href="fachausweis.html#{k.lower()}">
        {img(k, t)}
        <span class="mod-d__txt">
          <span class="mod-d__code">Modul {k}</span>
          <span class="mod-d__title">{t}</span>
        </span>
      </a>
'''

VD = f'''
<section class="section">
  <div class="wrap">
    {head("Variante D", "Geschlossene Modulwand",
          "Kein Weissraum zwischen den Kacheln: Die Basismodule bilden eine zusammenhängende "
          "Greige-Fläche, die Wahlmodule eine Navy-Fläche, getrennt nur durch eine Haarfuge. "
          "Die Module lesen sich als zwei Blöcke statt als 13 Einzelteile – nah an einer "
          "gedruckten Modulübersicht.")}
    <h3 style="margin-top:2rem">Basismodule</h3>
    <div class="mod-d-wall mod-d-wall--basis mt-2">
{"".join(d(k, t, "basis") for k, t in BASIS)}    </div>
    <h3 style="margin-top:3rem">Wahlmodule</h3>
    <div class="mod-d-wall mod-d-wall--wahl mt-2">
{"".join(d(k, t, "wahl") for k, t in WAHL)}    </div>
  </div>
</section>
'''

# ---------------------------------------------------------------- Variante E
def e(k, t, kind, extra=""):
    return f'''      <a class="mod-e mod-e--{kind} {extra}" href="fachausweis.html#{k.lower()}">
        <span class="mod-e__fig">{img(k, t)}</span>
        <span class="mod-e__txt">
          <span class="mod-e__code">Modul {k}</span>
          <span class="mod-e__title">{t}</span>
        </span>
      </a>
'''

VE = f'''
<section class="section">
  <div class="wrap">
    {head("Variante E – umgesetzt", "Grosse Fläche, Motiv zentriert",
          "Format und Textführung wie Variante B, aber ohne Beschnitt: Die Kachel ist vollflächig in "
          "der Modulfarbe, das Motiv steht kleiner und mittig darin und bekommt ringsum Luft in "
          "derselben Farbe. Weil die Eyecatcher ihre Flächenfarbe selbst mitbringen, ist keine "
          "Bildkante sichtbar. Diese Variante ist im Prototyp eingebaut.")}
    <h3 style="margin-top:2rem">Basismodule</h3>
    <div class="grid grid--4 mt-2">
{"".join(e(k, t, "basis") for k, t in BASIS)}    </div>
    <h3 style="margin-top:3rem">Wahlmodule</h3>
    <div class="grid grid--4 mt-2">
{"".join(e(k, t, "wahl") for k, t in WAHL)}    </div>

    <h3 style="margin-top:3.5rem">Feinabstufung des Innenabstands</h3>
    <p class="lead mb-3" style="font-size:1rem">
      Wie viel Luft das Motiv bekommt, lässt sich frei einstellen. Links wenig (9 %),
      in der Mitte der Vorschlag (14 %), rechts viel (20 %).
    </p>
    <div class="grid grid--3">
{e("S2", "3D-Geodaten", "wahl", "mod-e--luft-klein")}{e("S2", "3D-Geodaten", "wahl")}{e("S2", "3D-Geodaten", "wahl", "mod-e--luft-gross")}    </div>
  </div>
</section>
'''

HERO = '''
<section class="hero" style="padding-block:clamp(3rem,7vw,5rem)">
  <div class="wrap">
    <p class="breadcrumb"><a href="index.html">Start</a> &nbsp;/&nbsp; Varianten</p>
    <h1 style="font-size:var(--step-3)">Modulkacheln – Varianten</h1>
    <p class="hero__claim">
      Alle halten die CD-Regel ein: Basismodule Greige mit Motiv in Secondary Navy,
      Wahlmodule umgekehrt, Schrift auf blauem Grund weiss. Unterschiedlich sind Grösse,
      Beschnitt und Umgebung der Fläche. Variante E steht zuoberst und ist im Prototyp umgesetzt.
    </p>
  </div>
</section>
'''

html = f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Modulkacheln – Varianten – BIZ Geo</title>
<meta name="robots" content="noindex">
<link rel="stylesheet" href="assets/styles.css">
<link rel="stylesheet" href="assets/varianten.css">
</head>
<body>
{HEADER}{HERO}{VE}{VC}{VB}{VD}{VA}{FOOTER}<script src="assets/site.js"></script>
</body>
</html>
'''

(ROOT / "varianten.html").write_text(html, encoding="utf-8")
print("geschrieben: varianten.html")
