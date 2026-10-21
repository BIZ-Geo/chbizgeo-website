#!/usr/bin/env python3
"""Baut design-vorschau.html – eine eigenständige Vorschau der Design-Richtungen.

Zeigt vier Vorschläge gegen den „flachen" Eindruck, jeweils mit Beschriftung,
in den echten CD-Farben und Schriften. Alle Assets eingebettet -> läuft überall.
"""
import base64, mimetypes, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = ROOT / "assets"

def uri(p):
    m, _ = mimetypes.guess_type(str(p))
    if p.suffix == ".svg": m = "image/svg+xml"
    return f"data:{m};base64," + base64.b64encode(p.read_bytes()).decode("ascii")

CONTOUR = uri(A / "contours.svg")
LOGO = uri(A / "logo-bizgeo.png")
S2 = uri(A / "eyecatcher" / "S2.png")
S7 = uri(A / "eyecatcher" / "S7.png")

HTML = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BIZ Geo – Design-Vorschau</title>
<style>
:root {{
  --navy:#16202B; --greige:#DCD9D2; --navy2:#2A3A4F; --red:#C23726;
  --ink:#16202B; --muted:#4A5666; --paper:#fff;
  --font:"Segoe UI","Selawik",-apple-system,BlinkMacSystemFont,"Roboto","Helvetica Neue",Arial,sans-serif;
}}
*{{box-sizing:border-box;}}
body{{margin:0;font-family:var(--font);color:var(--ink);background:#f4f3f0;line-height:1.6;-webkit-font-smoothing:antialiased;}}
.wrap{{width:min(1160px,100% - 3rem);margin-inline:auto;}}
h1,h2,h3{{line-height:1.12;letter-spacing:-.02em;margin:0 0 .4em;}}

/* Kapitel-Label über jedem Vorschlag */
.demo-label{{background:var(--navy);color:#fff;padding:1.1rem 0;}}
.demo-label .wrap{{display:flex;gap:1rem;align-items:baseline;flex-wrap:wrap;}}
.demo-label b{{font-size:1.05rem;}}
.demo-label span{{opacity:.75;font-size:.9rem;}}
.demo-note{{background:#fff;border-bottom:1px solid #e5e3dd;}}
.demo-note .wrap{{padding:.8rem 0;color:var(--muted);font-size:.9rem;}}

.eyebrow{{font-size:.8rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--navy2);
  display:inline-flex;align-items:center;gap:.6rem;margin:0 0 1rem;}}
.eyebrow::before{{content:"";width:12px;height:12px;border:1.5px solid currentColor;border-radius:50%;
  background:linear-gradient(currentColor,currentColor) center/100% 1.5px no-repeat,
             linear-gradient(currentColor,currentColor) center/1.5px 100% no-repeat;}}

/* ---------- 1) HERO mit Höhenlinien-Einzeichnen ---------- */
.hero{{position:relative;overflow:hidden;background:var(--navy);color:#fff;padding:5.5rem 0;}}
.hero::before{{content:"";position:absolute;inset:0;background:url("{CONTOUR}") center/cover no-repeat;}}
.hero.play::before{{animation:draw 1.8s cubic-bezier(.22,.61,.36,1) both;}}
@keyframes draw{{from{{clip-path:inset(0 100% 0 0);}}to{{clip-path:inset(0 0 0 0);}}}}
.hero .wrap{{position:relative;z-index:1;}}
.hero h1{{font-size:clamp(2.2rem,4vw,3.6rem);max-width:16ch;}}
.hero p{{max-width:52ch;font-size:1.15rem;color:#fff;opacity:.92;}}
.replay{{margin-top:1.5rem;display:inline-block;background:#fff;color:var(--navy);border:0;
  padding:.7rem 1.3rem;border-radius:4px;font:inherit;font-weight:600;cursor:pointer;}}

/* ---------- 2) Redaktionell / asymmetrisch ---------- */
.editorial{{background:#fff;padding:5rem 0;}}
.editorial .grid{{display:grid;grid-template-columns:1.05fr .95fr;gap:clamp(2rem,6vw,5rem);align-items:start;}}
.editorial .idx{{font-size:clamp(3.5rem,7vw,6rem);font-weight:800;line-height:.8;color:var(--greige);
  letter-spacing:-.04em;margin-bottom:1rem;}}
.editorial h2{{font-size:clamp(2rem,3.4vw,3rem);max-width:14ch;}}
.editorial .lead{{font-size:1.15rem;color:var(--muted);}}
.editorial .pts{{margin-top:1.5rem;display:grid;gap:1.1rem;}}
.editorial .pt{{border-left:3px solid var(--navy2);padding-left:1rem;}}
.editorial .pt b{{display:block;}}
.editorial .pt span{{color:var(--muted);font-size:.95rem;}}
@media(max-width:760px){{.editorial .grid{{grid-template-columns:1fr;}}}}

/* ---------- 3) Schräge Schnittkante ---------- */
.diag{{background:var(--navy2);color:#fff;padding:5rem 0 7rem;position:relative;}}
.diag::after{{content:"";position:absolute;left:0;right:0;bottom:-1px;height:70px;background:#fff;
  clip-path:polygon(0 100%,100% 0,100% 100%);}}
.diag h2{{font-size:clamp(1.8rem,3vw,2.6rem);}}
.diag p{{max-width:56ch;opacity:.9;}}
.diag-after{{background:#fff;padding:4rem 0 5rem;}}
.diag-after h3{{font-size:1.3rem;}}
.diag-after p{{color:var(--muted);max-width:60ch;}}

/* ---------- 4) Übergrosses Eyecatcher-Wasserzeichen ---------- */
.mark{{position:relative;overflow:hidden;background:var(--navy2);color:#fff;padding:5.5rem 0;}}
.mark img{{position:absolute;right:-8%;top:50%;transform:translateY(-50%);height:160%;
  pointer-events:none;}}
.mark .wrap{{position:relative;z-index:1;}}
.mark h2{{font-size:clamp(2rem,3.4vw,3rem);max-width:15ch;}}
.mark p{{max-width:48ch;opacity:.92;}}
.mark small{{display:block;margin-top:1.5rem;opacity:.6;font-size:.85rem;}}

.foot{{padding:3rem 0;text-align:center;color:var(--muted);font-size:.9rem;background:#f4f3f0;}}
</style>
</head>
<body>

<!-- 1 -->
<div class="demo-label"><div class="wrap"><b>Vorschlag 1 — Höhenlinien beleben</b>
  <span>Die Linien zeichnen sich beim Laden von links ein. Dezent, aber lebendiger Auftakt.</span></div></div>
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Bildungszentrum Geomatik Schweiz</p>
    <h1>Technisch engagiert für die Gestaltung der Umwelt.</h1>
    <p>BIZ Geo ist das nationale Bildungszentrum der Schweizer Geomatikbranche.</p>
    <button class="replay" id="replay">Animation nochmal abspielen</button>
  </div>
</section>

<!-- 2 -->
<div class="demo-label"><div class="wrap"><b>Vorschlag 2 — Redaktionelles, asymmetrisches Layout</b>
  <span>Grosse Zahl, Überschrift links, Inhalt rechts. Der stärkste Hebel gegen den „Word-Look".</span></div></div>
<section class="editorial">
  <div class="wrap">
    <div class="grid">
      <div>
        <div class="idx">01</div>
        <p class="eyebrow">Lehrgang Geomatiktechnik</p>
        <h2>Fünf Basismodule, acht Wahlmodule</h2>
      </div>
      <div>
        <p class="lead">Die Basismodule vermitteln die gemeinsame Grundlage, die Wahlmodule
        die fachliche Vertiefung. Jedes Modul ist auch einzeln als Weiterbildung buchbar.</p>
        <div class="pts">
          <div class="pt"><b>Berufsbegleitend</b><span>Modulare Termine, planbar neben dem Tagesgeschäft.</span></div>
          <div class="pt"><b>Eidgenössisch anerkannt</b><span>Module zahlen auf den Fachausweis ein.</span></div>
          <div class="pt"><b>In allen Sprachregionen</b><span>Deutsch, Französisch und Italienisch.</span></div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- 3 -->
<div class="demo-label"><div class="wrap"><b>Vorschlag 3 — Schräge Schnittkante</b>
  <span>Diagonaler statt gerader Übergang zwischen den Farbflächen. Dynamischer, moderner.</span></div></div>
<section class="diag">
  <div class="wrap">
    <p class="eyebrow" style="color:#fff;opacity:.8">Aus dem Kalender</p>
    <h2>Nächste Veranstaltungen</h2>
    <p>Unterricht, Modulabschlüsse, Kurse und Anlässe – die schräge Kante trennt den Abschnitt
    lebendiger von der nächsten Fläche als eine gerade Linie.</p>
  </div>
</section>
<section class="diag-after">
  <div class="wrap">
    <h3>Der Übergang „schneidet" in die helle Fläche</h3>
    <p>So wirkt die Seite gebaut statt gestapelt – ohne neue Farben, nur über die Form.</p>
  </div>
</section>

<!-- 4 -->
<div class="demo-label"><div class="wrap"><b>Vorschlag 4 — Übergrosses Eyecatcher-Wasserzeichen</b>
  <span>Ein Motiv riesig und angeschnitten hinter dem Text. Grafischer Blickfang, nimmt die Marke auf.</span></div></div>
<section class="mark">
  <img src="{S7}" alt="">
  <div class="wrap">
    <p class="eyebrow" style="color:#fff;opacity:.8">Vertiefung</p>
    <h2>Wahlmodule für Ihren Schwerpunkt</h2>
    <p>Ein einzelnes Eyecatcher-Motiv wird zum grossflächigen grafischen Element und gibt
    dem Abschnitt Charakter – ganz im Corporate Design.</p>
    <small>Hier Modul S7 · Fixpunkte als Beispiel</small>
  </div>
</section>

<div class="foot">Design-Vorschau · BIZ Geo · alle Elemente im Corporate Design (Deep Geo Navy, Greige, Secondary Navy)</div>

<script>
(function(){{
  var hero = document.querySelector('.hero');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(!reduce) hero.classList.add('play');
  var btn = document.getElementById('replay');
  if(btn) btn.addEventListener('click', function(){{
    hero.classList.remove('play');
    void hero.offsetWidth;      // Reflow erzwingen, damit die Animation neu startet
    hero.classList.add('play');
  }});
}})();
</script>
</body>
</html>
"""

out = ROOT / "design-vorschau.html"
out.write_text(HTML, encoding="utf-8")
print("geschrieben:", out.name, out.stat().st_size // 1024, "KB")
