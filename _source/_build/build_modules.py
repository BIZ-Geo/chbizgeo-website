#!/usr/bin/env python3
"""Erzeugt eine Detailseite pro Modul: modul-<key>.html

Vorlage + Daten getrennt: die Moduldaten (Beschreibung, Kompetenzen,
Voraussetzungen, Kurse, Lektionen, Kosten) stehen in _source/daten/module.csv.
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
# Quelle: _source/daten/module.csv (FR/IT kommen über translate_data.py dazu)
from daten import module as _module

MODULES = {key: {**m, "lead": m["lead"]["de"], "outcomes": m["outcomes"]["de"],
                 "voraussetzungen": m["voraussetzungen"]["de"], "kurse": m["kurse"]["de"]}
           for key, m in _module().items()}

if __name__ == "__main__":
    for key, m in MODULES.items():
        print("geschrieben:", page(key, m))
    print(f"\n{len(MODULES)} Modulseiten erzeugt.")
