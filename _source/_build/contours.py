#!/usr/bin/env python3
"""Erzeugt topografische Höhenlinien als SVG – die Tiefenebene der Seite.

Echte Höhenlinien statt gezeichneter Kurven: Es wird zuerst ein glattes
Geländemodell (Summe mehrerer Gauss-Hügel) berechnet und daraus per
Marching-Squares die Iso-Linien auf gleichmässigen Höhenstufen extrahiert.
So laufen die Linien wie auf einer Landeskarte parallel und kreuzen sich nie.
Anschliessend werden die Polylinien mit dem Chaikin-Verfahren zweifach
geglättet und als weiche Bézier-Pfade ausgegeben.

CD-konform: reine Linien in Secondary Navy (#2A3A4F) – die CD nennt diese
Farbe ausdrücklich für „grafische Elemente und Linien". Volle Deckung.

Ausgabe:
  assets/contours.svg        – Variante für den Hero
  assets/contours-light.svg  – zweite Variante (anderes Gelände) für Sektionen
"""
import math, pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1200, 820
GX, GY = 240, 164          # Auflösung des Höhengitters (fein = glatt)
SECONDARY = "#2A3A4F"


def terrain(seed, peaks):
    """Glattes Höhenfeld aus mehreren Gauss-Hügeln plus sanfter Grosswelle."""
    rng = np.random.default_rng(seed)
    xs = np.linspace(0, W, GX)
    ys = np.linspace(0, H, GY)
    gx, gy = np.meshgrid(xs, ys)
    field = np.zeros_like(gx)
    for (cx, cy, amp, sx, sy) in peaks:
        field += amp * np.exp(-(((gx - cx) ** 2) / (2 * sx ** 2) +
                                ((gy - cy) ** 2) / (2 * sy ** 2)))
    # sehr weiche, grossräumige Modulation für organische Grate
    field += 0.20 * np.sin(gx / W * math.pi * 1.3 + 0.5) * np.cos(gy / H * math.pi * 1.1)
    field += 0.12 * np.sin(gx / W * math.pi * 2.1 + rng.uniform(0, 3))
    return xs, ys, field


def iso_segments(xs, ys, F, level):
    """Marching Squares: Liniensegmente für eine Höhenstufe."""
    segs = []
    def interp(p1, p2, v1, v2):
        t = (level - v1) / (v2 - v1) if v2 != v1 else 0.5
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            x0, x1 = xs[i], xs[i + 1]
            y0, y1 = ys[j], ys[j + 1]
            a = F[j, i]; b = F[j, i + 1]; c = F[j + 1, i + 1]; d = F[j + 1, i]
            idx = (a > level) | ((b > level) << 1) | ((c > level) << 2) | ((d > level) << 3)
            idx = int(idx)
            TL, TR, BR, BL = (x0, y0), (x1, y0), (x1, y1), (x0, y1)
            top    = lambda: interp(TL, TR, a, b)
            right  = lambda: interp(TR, BR, b, c)
            bottom = lambda: interp(BL, BR, d, c)
            left   = lambda: interp(TL, BL, a, d)
            e = {
                1: [(left, top)], 2: [(top, right)], 3: [(left, right)],
                4: [(right, bottom)], 5: [(left, bottom), (top, right)],
                6: [(top, bottom)], 7: [(left, bottom)], 8: [(left, bottom)],
                9: [(top, bottom)], 10: [(left, top), (right, bottom)],
                11: [(right, bottom)], 12: [(left, right)], 13: [(top, right)],
                14: [(left, top)],
            }.get(idx, [])
            for f1, f2 in e:
                segs.append((f1(), f2()))
    return segs


def stitch(segments, tol=1.2):
    """Segmente zu durchgehenden Polylinien verketten."""
    def key(p): return (round(p[0] / tol), round(p[1] / tol))
    from collections import defaultdict
    ends = defaultdict(list)
    for s in segments:
        ends[key(s[0])].append(s)
        ends[key(s[1])].append(s)
    used = set()
    paths = []
    for s0 in segments:
        if id(s0) in used:
            continue
        used.add(id(s0))
        pts = [s0[0], s0[1]]
        # nach vorne wachsen
        changed = True
        while changed:
            changed = False
            for cand in ends[key(pts[-1])]:
                if id(cand) in used:
                    continue
                if key(cand[0]) == key(pts[-1]):
                    pts.append(cand[1]); used.add(id(cand)); changed = True; break
                if key(cand[1]) == key(pts[-1]):
                    pts.append(cand[0]); used.add(id(cand)); changed = True; break
        # nach hinten wachsen
        changed = True
        while changed:
            changed = False
            for cand in ends[key(pts[0])]:
                if id(cand) in used:
                    continue
                if key(cand[0]) == key(pts[0]):
                    pts.insert(0, cand[1]); used.add(id(cand)); changed = True; break
                if key(cand[1]) == key(pts[0]):
                    pts.insert(0, cand[0]); used.add(id(cand)); changed = True; break
        if len(pts) >= 4:
            paths.append(pts)
    return paths


def chaikin(pts, iters=2):
    """Weiche Kurve durch Eckenabschliff (Chaikin)."""
    closed = math.dist(pts[0], pts[-1]) < 3
    for _ in range(iters):
        out = [] if not closed else []
        n = len(pts)
        if not closed:
            out.append(pts[0])
        for i in range(n - 1):
            p, q = pts[i], pts[i + 1]
            out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts


def simplify(pts, step=5.0):
    """Punkte entlang der Bogenlänge ausdünnen: es wird erst wieder ein Punkt
    gesetzt, wenn er weit genug vom letzten entfernt ist. Da die Kurve durch
    Chaikin schon glatt ist, bleibt die Form erhalten, die Datei wird klein."""
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for p in pts[1:-1]:
        if math.dist(p, out[-1]) >= step:
            out.append(p)
    out.append(pts[-1])
    return out


def to_path(pts):
    d = "M %.1f %.1f " % pts[0]
    d += " ".join("L %.1f %.1f" % p for p in pts[1:])
    return d


def build(seed, peaks):
    xs, ys, F = terrain(seed, peaks)
    lo, hi = float(F.min()), float(F.max())
    levels = np.linspace(lo + (hi - lo) * 0.06, hi - (hi - lo) * 0.04, 15)
    body = []
    for li, lvl in enumerate(levels):
        segs = iso_segments(xs, ys, F, lvl)
        if not segs:
            continue
        for poly in stitch(segs):
            sm = simplify(chaikin(poly, 2), step=5.0)
            if len(sm) < 4:
                continue
            sw = 1.1 if li % 5 == 0 else 0.75    # dezent: dünne Linien, jede fünfte etwas kräftiger
            body.append(f'<path d="{to_path(sm)}" fill="none" stroke="{SECONDARY}" '
                        f'stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'preserveAspectRatio="xMidYMid slice" aria-hidden="true">\n%s\n</svg>\n'
            % (W, H, "\n".join(body))), len(body)


# Zwei unterschiedliche Gelände – Hauptgipfel rechts, ruhig links
PEAKS_A = [
    (W * 0.82, H * 0.36, 1.00, 260, 220),
    (W * 0.62, H * 0.60, 0.55, 200, 170),
    (W * 0.16, H * 0.82, 0.62, 230, 190),
    (W * 0.30, H * 0.20, 0.30, 180, 150),
]
PEAKS_B = [
    (W * 0.20, H * 0.34, 0.95, 250, 210),
    (W * 0.44, H * 0.66, 0.50, 210, 180),
    (W * 0.84, H * 0.78, 0.66, 240, 200),
    (W * 0.72, H * 0.18, 0.34, 190, 150),
]

svg_a, na = build(34, PEAKS_A)
svg_b, nb = build(71, PEAKS_B)
(ROOT / "assets" / "contours.svg").write_text(svg_a, encoding="utf-8")
(ROOT / "assets" / "contours-light.svg").write_text(svg_b, encoding="utf-8")
print(f"contours.svg ({na} Linien) und contours-light.svg ({nb} Linien) geschrieben")
