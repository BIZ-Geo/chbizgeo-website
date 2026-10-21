#!/usr/bin/env python3
"""Baut eine einzige, vollständig eingebettete index-Datei für Präsentationen.

Alles inline: styles.css + chatbot.css als <style>, site.js + chatbot.js als
<script>, sämtliche Bilder (Logo, Eyecatcher, Höhenlinien) als data:-URIs und
der Suchindex des Frage-Bots als JS-Variable. Ergebnis läuft per Doppelklick
von jedem Ort – ohne assets-Ordner, ohne Server, iCloud-sicher.
"""
import base64, json, pathlib, re, mimetypes

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = ROOT / "assets"

def datauri(path):
    mime, _ = mimetypes.guess_type(str(path))
    if path.suffix == ".svg":
        mime = "image/svg+xml"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"

# ---- Basis: Startseite
html = (ROOT / "index.html").read_text(encoding="utf-8")

# ---- CSS zusammenführen und Höhenlinien-URLs zu data-URIs machen
css = (A / "styles.css").read_text(encoding="utf-8")
css += "\n" + (A / "chatbot.css").read_text(encoding="utf-8")
css = css.replace('url("contours.svg")', f'url("{datauri(A / "contours.svg")}")')
css = css.replace('url("contours-light.svg")', f'url("{datauri(A / "contours-light.svg")}")')

# ---- JS zusammenführen; Bot-Fetch durch eingebetteten Index ersetzen
site_js = (A / "site.js").read_text(encoding="utf-8")
bot_js = (A / "chatbot.js").read_text(encoding="utf-8")
bot_js = bot_js.replace(
    'fetch("assets/search-index.json")',
    'Promise.resolve({ json: function () { return window.__BIZ_INDEX__; } })'
)
index_json = (A / "search-index.json").read_text(encoding="utf-8")

# ---- Stylesheet-Links durch Inline-Style ersetzen
html = re.sub(r'<link rel="stylesheet" href="assets/styles\.css">\s*'
              r'<link rel="stylesheet" href="assets/chatbot\.css">',
              "<style>\n" + css + "\n</style>", html)

# ---- Script-Tags durch Inline-Scripts ersetzen (Index zuerst)
html = html.replace(
    '<script src="assets/site.js"></script>\n<script src="assets/chatbot.js"></script>',
    "<script>window.__BIZ_INDEX__ = " + index_json + ";</script>\n"
    "<script>\n" + site_js + "\n</script>\n"
    "<script>\n" + bot_js + "\n</script>"
)

# ---- Alle Bild-Referenzen (Logo, Eyecatcher) einbetten
def embed(m):
    rel = m.group(1)
    p = ROOT / rel
    if p.exists():
        return 'src="' + datauri(p) + '"'
    return m.group(0)
html = re.sub(r'src="(assets/[^"]+)"', embed, html)
# Favicon (href) ebenfalls einbetten
html = html.replace('href="assets/favicon.png"', 'href="' + datauri(ROOT / "assets" / "favicon.png") + '"')

# ---- interne Links: bleiben relativ (funktionieren nur mit den anderen Seiten);
#      für die Einzeldatei-Präsentation Anker/# unverändert lassen.

out = ROOT / "biz-geo-praesentation.html"
out.write_text(html, encoding="utf-8")
kb = out.stat().st_size // 1024
print(f"geschrieben: {out.name}  ({kb} KB)")
# Kontrolle: keine externen assets/ mehr referenziert?
leftover = re.findall(r'(?:src|href)="assets/[^"]+"', html)
print("verbleibende assets-Referenzen:", leftover or "keine")
