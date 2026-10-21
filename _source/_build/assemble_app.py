#!/usr/bin/env python3
"""Baut EINE eigenständige Datei mit allen Seiten – vollständig klickbar offline.

Alle Unterseiten werden in ein Dokument gebündelt und per JavaScript
umgeschaltet (kein Nachladen weiterer Dateien). CSS, JS, Bilder, Höhenlinien
und der Such-Index sind eingebettet. Damit funktioniert die komplette
Navigation auch über file:// und trotz iCloud – ohne Server.

Ergebnis: biz-geo-komplett.html
"""
import base64, mimetypes, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = ROOT / "assets"

PAGES = ["index", "fachausweis", "weiterbildung", "veranstaltungen",
         "ueber-uns", "anmeldung", "kontakt", "datenschutz"] + \
        [f"modul-{k}" for k in ["b1", "b2", "b3", "b4", "b5",
                                "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"]]
FOOTER_MARKER = "<!-- ================================================================ FOOTER -->"


def datauri(path):
    mime, _ = mimetypes.guess_type(str(path))
    if path.suffix == ".svg":
        mime = "image/svg+xml"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


# ---- Gemeinsame Hülle aus index.html: HEAD, HEADER, FOOTER
index_html = (ROOT / "index.html").read_text(encoding="utf-8")
header = index_html[index_html.index("<!-- ================================================================ HEADER -->"):
                    index_html.index("<!-- ================================================================== HERO -->")]
footer = index_html[index_html.index(FOOTER_MARKER):
                    index_html.index('<script src="assets/site.js"></script>')]


def body_of(page):
    """Seiteninhalt zwischen </header> und dem FOOTER-Marker."""
    html = (ROOT / f"{page}.html").read_text(encoding="utf-8")
    start = html.index("</header>") + len("</header>")
    end = html.index(FOOTER_MARKER)
    return html[start:end].strip()


# ---- Alle Seiten als umschaltbare Blöcke
pages_html = []
for i, p in enumerate(PAGES):
    hidden = "" if i == 0 else " hidden"
    pages_html.append(f'<div class="page" data-page="{p}"{hidden}>\n{body_of(p)}\n</div>')
pages_block = "\n".join(pages_html)

# ---- CSS inline + Höhenlinien als data-URI
css = (A / "styles.css").read_text(encoding="utf-8") + "\n" + (A / "chatbot.css").read_text(encoding="utf-8")
css = css.replace('url("contours.svg")', f'url("{datauri(A / "contours.svg")}")')
css += "\n.page[hidden]{display:none!important;}\n"

# ---- JS inline; Bot-Fetch -> eingebetteter Index
site_js = (A / "site.js").read_text(encoding="utf-8")
bot_js = (A / "chatbot.js").read_text(encoding="utf-8").replace(
    'fetch("assets/search-index.json")',
    'Promise.resolve({ json: function () { return window.__BIZ_INDEX__; } })')
index_json = (A / "search-index.json").read_text(encoding="utf-8")

# ---- Router: fängt Klicks auf *.html ab und schaltet die Seite um
router = r"""
(function () {
  function pages() { return Array.prototype.slice.call(document.querySelectorAll('.page')); }
  function reveal(container) {
    // In der gebündelten Fassung sofort einblenden – der Scroll-Observer
    // greift nur für sichtbare Elemente, umgeschaltete Seiten sonst leer.
    container.querySelectorAll('[data-reveal], [data-reveal-group]').forEach(function (n) {
      n.classList.add('in-view');
    });
  }
  function show(name, anchor) {
    var found = false;
    pages().forEach(function (p) {
      var on = p.dataset.page === name;
      p.hidden = !on;
      if (on) { reveal(p); found = true; }
    });
    if (!found) return false;
    // aktive Navigation markieren
    document.querySelectorAll('.nav a[data-page]').forEach(function (a) {
      a.toggleAttribute('aria-current', a.getAttribute('data-page') === name);
    });
    if (anchor) {
      var el = document.getElementById(anchor);
      if (el) { el.scrollIntoView(); return true; }
    }
    window.scrollTo(0, 0);
    return true;
  }
  // Menü-Links mit ihrer Zielseite markieren (für aktiven Zustand)
  document.querySelectorAll('a[href]').forEach(function (a) {
    var m = (a.getAttribute('href') || '').match(/^([a-z0-9-]+)\.html/);
    if (m) a.setAttribute('data-page', m[1]);
  });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var m = href.match(/^([a-z0-9-]+)\.html(?:#(.+))?$/);
    if (!m) return;                 // externe/Anker-Links normal lassen
    if (show(m[1], m[2])) {
      e.preventDefault();
      var nav = document.querySelector('.nav');
      if (nav) nav.classList.remove('is-open');   // Mobilmenü schliessen
    }
  });
})();
"""

html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BIZ Geo – Bildungszentrum Geomatik Schweiz</title>
<link rel="icon" type="image/png" sizes="256x256" href="{datauri(A / 'favicon.png')}">
<link rel="apple-touch-icon" href="{datauri(A / 'favicon.png')}">
<style>
{css}
</style>
</head>
<body>
{header}
{pages_block}
{footer}
<script>window.__BIZ_INDEX__ = {index_json};</script>
<script>
{site_js}
</script>
<script>
{bot_js}
</script>
<script>
{router}
</script>
</body>
</html>
"""

# ---- Bilder (Logo, Eyecatcher) einbetten
def embed(m):
    p = ROOT / m.group(1)
    return 'src="' + datauri(p) + '"' if p.exists() else m.group(0)
html = re.sub(r'src="(assets/[^"]+)"', embed, html)

out = ROOT / "biz-geo-komplett.html"
out.write_text(html, encoding="utf-8")
print(f"geschrieben: {out.name}  ({out.stat().st_size // 1024} KB)")
leftover = re.findall(r'(?:src|href)="assets/[^"]+"', html)
print("externe assets-Referenzen:", leftover or "keine")
print("gebündelte Seiten:", len(PAGES))
