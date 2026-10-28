#!/usr/bin/env python3
"""Baut die Mehrregionen-Struktur: /de /fr /it + Root-Einstieg.

Phase 1 (Gerüst): DE trägt den aktuellen Inhalt; FR und IT sind Kopien mit
klar gekennzeichnetem Platzhalter-Banner (noch deutsche Inhalte). Pro Seite:
Sprach-Attribut, Sprach-Umschalter mit den richtigen Querverweisen, hreflang.

Ergebnis: Ordner _site/ mit index.html (Einstieg) und de/ fr/ it/. Die Inhalte
(Module, Kurse, Termine) kommen je Region aus _source/daten/<region>/*.csv; die
festen Seitentexte werden für FR/IT über translate_data.py übersetzt.
"""
import re, shutil, pathlib, subprocess, sys
from translate_data import TRIPLES

ROOT = pathlib.Path(__file__).resolve().parent.parent          # biz-geo-web

# DE -> {fr, it}: Übersetzungswörterbücher aus der Tabelle
DICT = {
    "fr": {de: fr for de, fr, it in TRIPLES},
    "it": {de: it for de, fr, it in TRIPLES},
}
# Vorkompilierte Ersetzer, längste Schlüssel zuerst (bündig, keine Teiltreffer)
def _compile(region):
    rules = []
    for de in sorted(DICT[region], key=len, reverse=True):
        core = r'\s+'.join(re.escape(p) for p in de.split())
        rules.append((re.compile(r'>\s*' + core + r'\s*<'),
                      re.compile(r'(alt|title|aria-label|content)="' + core + r'"'),
                      DICT[region][de]))
    return rules
_RULES = {r: _compile(r) for r in ("fr", "it")}


def translate(html, region):
    """Ersetzt deutsche Text-Knoten und Attributwerte durch die Übersetzung.
    Nur vollständige Knoten (>...<) bzw. Attributwerte werden getroffen –
    so kann 'Basismodul' nie in 'Basismodule' hineinragen."""
    for pat_text, pat_attr, val in _RULES[region]:
        html = pat_text.sub(lambda m, v=val: '>' + v + '<', html)
        html = pat_attr.sub(lambda m, v=val: m.group(1) + '="' + v + '"', html)
    return html
# Ausgabe nach _source/_site/ (von build.sh gesetzt; wird vor jedem Build geleert und von der
# GitHub Action als Pages-Artefakt veröffentlicht)
import os as _os
SITE = pathlib.Path(_os.environ.get("BIZGEO_SITE", ROOT / "_site"))
BASE = "https://biz-geo.github.io/chbizgeo-website"            # Livegang: -> https://biz-geo.ch

REGIONS = [("de", "Deutschschweiz", "Deutsch"),
           ("fr", "Romandie", "Français"),
           ("it", "Ticino", "Italiano")]
REGION_NAME = {c: n for c, n, _ in REGIONS}

EXCLUDE = {"varianten.html", "design-vorschau.html",
           "biz-geo-komplett.html", "biz-geo-praesentation.html"}


def pages():
    return sorted(p.name for p in ROOT.glob("*.html") if p.name not in EXCLUDE)


def langs_block(region, fname):
    items = []
    for code, _, _ in REGIONS:
        cur = ' aria-current="true"' if code == region else ''
        items.append(f'<a href="../{code}/{fname}"{cur}>{code.upper()}</a>')
    return '<div class="langs">\n            ' + '\n            '.join(items) + '\n          </div>'


def hreflang(fname):
    out = [f'<link rel="alternate" hreflang="{c}" href="{BASE}/{c}/{fname}">' for c, _, _ in REGIONS]
    out.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/de/{fname}">')
    return "\n".join(out)


def process(html, region, fname):
    # Inhalte übersetzen (nur FR/IT; DE bleibt Quelltext)
    if region != "de":
        html = translate(html, region)
    html = re.sub(r'<html lang="[^"]*"', f'<html lang="{region}"', html, count=1)
    # bestehende hreflang entfernen, korrekte setzen
    html = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*"[^>]*>', '', html)
    html = html.replace('</head>', hreflang(fname) + '\n</head>', 1)
    # Sprach-Umschalter mit echten Querverweisen
    html = re.sub(r'<div class="langs">.*?</div>', langs_block(region, fname), html, flags=re.S)
    return html


def build_flat(region):
    """Erzeugt die Quellseiten in _source/ mit den Inhalten aus daten/<region>/."""
    env = {**_os.environ, "BIZGEO_REGION": region}
    for s in ["build.py", "build_modules.py", "build_index.py"]:
        subprocess.run([sys.executable, str(ROOT / "_build" / s)], check=True, cwd=str(ROOT), env=env)


ROOT_INDEX = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BIZ Geo – Sprachregion wählen / Choisir la région / Scegli la regione</title>
<link rel="icon" type="image/png" sizes="256x256" href="de/assets/favicon.png">
<link rel="alternate" hreflang="de" href="__BASE__/de/index.html">
<link rel="alternate" hreflang="fr" href="__BASE__/fr/index.html">
<link rel="alternate" hreflang="it" href="__BASE__/it/index.html">
<link rel="alternate" hreflang="x-default" href="__BASE__/de/index.html">
<style>
  :root{--navy:#16202B;--navy2:#2A3A4F;--greige:#DCD9D2;--font:"Segoe UI","Selawik",-apple-system,BlinkMacSystemFont,Roboto,Arial,sans-serif;}
  *{box-sizing:border-box;}
  body{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--navy);color:#fff;font-family:var(--font);padding:2rem;}
  .box{width:min(760px,100%);text-align:center;}
  .logo{width:76px;height:76px;margin:0 auto 1.5rem;display:block;}
  h1{font-size:clamp(1.5rem,3vw,2.2rem);margin:0 0 .4rem;letter-spacing:-.01em;}
  p.sub{color:var(--greige);opacity:.85;margin:0 0 2.25rem;}
  .regions{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;}
  @media(max-width:620px){.regions{grid-template-columns:1fr;}}
  .region{display:flex;flex-direction:column;gap:.35rem;padding:1.6rem 1.25rem;border-radius:6px;
    background:var(--navy2);color:#fff;text-decoration:none;transition:transform .16s ease,background .16s ease;position:relative;}
  .region:hover{transform:translateY(-4px);background:#33475f;}
  .region b{font-size:1.15rem;}
  .region span{font-size:.9rem;color:var(--greige);opacity:.85;}
  footer{margin-top:2.5rem;font-size:.8rem;color:var(--greige);opacity:.6;}
</style>
</head>
<body>
  <div class="box">
    <img class="logo" src="de/assets/logo-bizgeo.png" alt="BIZ Geo">
    <h1>Willkommen · Bienvenue · Benvenuti</h1>
    <p class="sub">Bitte wählen Sie Ihre Sprachregion. · Veuillez choisir votre région. · Scegli la tua regione.</p>
    <div class="regions">
      <a class="region" href="de/index.html" data-code="de"><b>Deutschschweiz</b><span>Deutsch</span></a>
      <a class="region" href="fr/index.html" data-code="fr"><b>Romandie</b><span>Français</span></a>
      <a class="region" href="it/index.html" data-code="it"><b>Ticino</b><span>Italiano</span></a>
    </div>
    <footer>BIZ Geo – Bildungszentrum Geomatik Schweiz</footer>
  </div>
<script>
(function(){
  function getCookie(n){var m=document.cookie.match('(?:^|; )'+n+'=([^;]*)');return m?m[1]:null;}
  var valid={de:1,fr:1,it:1};
  // Wiederkehrer mit gemerkter Region direkt weiterleiten
  var saved=getCookie('bizgeo_region');
  if(saved&&valid[saved]){ location.replace(saved+'/index.html'); return; }
  // Wahl merken (Cookie) beim Klick
  document.querySelectorAll('.region').forEach(function(a){
    a.addEventListener('click',function(){
      document.cookie='bizgeo_region='+a.dataset.code+'; max-age=31536000; path=/';
    });
  });
})();
</script>
</body>
</html>
""".replace("__BASE__", BASE)


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    # Jede Region mit ihren eigenen Inhalten (daten/<region>/) bauen. DE zuletzt, damit die
    # Quellseiten in _source/ (index.html, fachausweis.html, …) deutsch und unverändert bleiben.
    for region in ("fr", "it", "de"):
        build_flat(region)
        plist = pages()
        rdir = SITE / region
        rdir.mkdir()
        shutil.copytree(ROOT / "assets", rdir / "assets")
        for fname in plist:
            html = (ROOT / fname).read_text(encoding="utf-8")
            (rdir / fname).write_text(process(html, region, fname), encoding="utf-8")
    (SITE / "index.html").write_text(ROOT_INDEX, encoding="utf-8")
    print("Struktur gebaut in", SITE.name)
    print("  Root: index.html (Einstieg)")
    for region, _, _ in REGIONS:
        inhalt = subprocess.run([sys.executable, "-c", "import daten; print(daten.zusammenfassung())"],
                                cwd=str(ROOT / "_build"), env={**_os.environ, "BIZGEO_REGION": region},
                                capture_output=True, text=True, check=True).stdout.strip()
        print(f"  /{region}/: {len(plist)} Seiten + assets · {inhalt}")

    # Rest-Kontrolle: unübersetzte deutsche Text-Knoten in FR/IT?
    for region in ("fr", "it"):
        residual = set()
        for fname in plist:
            html = (SITE / region / fname).read_text(encoding="utf-8")
            for de in DICT[region]:
                core = r'\s+'.join(re.escape(p) for p in de.split())
                if re.search(r'>\s*' + core + r'\s*<', html):
                    residual.add(de)
        if residual:
            print(f"  ⚠ /{region}/: {len(residual)} deutsche Strings noch sichtbar:")
            for r in sorted(residual)[:20]:
                print("      -", r)
        else:
            print(f"  ✓ /{region}/: keine deutschen Text-Knoten mehr gefunden")


if __name__ == "__main__":
    main()
