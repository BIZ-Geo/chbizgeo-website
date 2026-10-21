# BIZ Geo – Website (chbizgeo-website)

Statische, mehrsprachige Website für das **Bildungszentrum Geomatik Schweiz (BIZ Geo)**,
Domain künftig **biz-geo.ch** (vormals geo-education.ch). Veröffentlichung über **GitHub Pages**
aus der Repo-Wurzel. Remote: `BIZ-Geo/chbizgeo-website`.

## WICHTIG: Quelle vs. Ausgabe

Dieses Repo enthält **zwei Ebenen**:

- **`_source/`** – die **Quelle** (deutsche Quellseiten + Build-Pipeline + Übersetzungstabelle).
  Hier wird entwickelt. Der Ordner beginnt mit `_`, daher schließt GitHub Pages (Jekyll) ihn
  **automatisch von der Veröffentlichung aus**.
- **Repo-Wurzel** (`index.html`, `de/`, `fr/`, `it/`) – die **generierte Ausgabe**, die Pages
  ausliefert. **Niemals von Hand bearbeiten** – wird vom Build überschrieben.

> Faustregel: **Immer in `_source/` ändern, dann `build.sh` laufen lassen.**

## Bauen & Veröffentlichen

```bash
cd _source
./build.sh            # baut nach temp und spiegelt index.html + de/ fr/ it/ an die Repo-Wurzel
cd ..
git add -A && git commit -m "Rebuild" && git push   # GitHub Pages deployt automatisch
```

`build.sh` baut in einen Temp-Ordner (via `BIZGEO_SITE`) und kopiert nur die veröffentlichten
Teile an die Wurzel – es löscht nie das Repo. (Hintergrund: `build_regions.py` räumt sein
Ausgabeverzeichnis vor dem Bauen auf; deshalb nie direkt auf die Repo-Wurzel bauen lassen.)

### Build-Pipeline (`_source/_build/`)

| Skript | Zweck |
|---|---|
| `build_regions.py` | **Hauptskript.** Baut Root-Picker + `de/ fr/ it/`; ruft die drei folgenden auf, kopiert `assets/` je Region und übersetzt FR/IT. Meldet am Ende unübersetzte DE-Reste. |
| `build.py` | Hauptseiten aus Inline-DE-HTML (fachausweis, weiterbildung, veranstaltungen, ueber-uns, anmeldung, kontakt, datenschutz). |
| `build_modules.py` | 13 Modul-Detailseiten `modul-b1…s8.html` aus dem `MODULES`-Dict. |
| `build_index.py` | `assets/search-index.json` für den Frage-Bot. |
| `translate_data.py` | **Übersetzungstabelle** `TRIPLES = [(DE, FR, IT), …]` (≈505 Einträge). |
| `assemble_single.py` u. a. | Hilfsskripte (eingebettete Präsentationsdatei, Höhenlinien, Varianten). |

## Übersetzung pflegen

- DE ist die Quelle. Übersetzt wird beim Bauen durch **randbündige Ersetzung** ganzer Textknoten
  (`>…<`) und der Attribute `alt/title/aria-label/content` – längste Schlüssel zuerst, damit z. B.
  „Basismodul" nie in „Basismodule" hineinragt.
- **Neue sichtbare DE-Texte ⇒ Zeile `(DE, FR, IT)` in `_source/_build/translate_data.py` ergänzen.**
- **Nicht übersetzt (bewusst):** BIZ Geo, QSK, FHNW, FME, GIS, BIM, XML, LFP3, LTOP, SIA, EFZ,
  Modulcodes (B1, S8-26), CHF-Beträge, Eigennamen/Adressen, Region-Namen im Root-Picker.
- **Festgelegte Fachbegriffe:** SBFI→SEFRI, ÖREB→RDPPF (FR)/RDPP (IT), DMAV→MD.MO/MD.MU,
  „eidg. Fachausweis"→„brevet fédéral"/„attestato professionale federale",
  „Lehrgang"→„cursus"/„ciclo di formazione", „Lektionen"→„leçons"/„lezioni".
- **Qualitätscheck** (nach dem Build, Output z. B. in `/tmp/out`): jeder Textknoten in FR/IT,
  der identisch zur DE-Fassung ist, deutet auf eine Lücke (Ausnahmen: sprachgleiche Begriffe wie
  Team, PDF, Tel., Vision, Eigennamen).

## Corporate Design (verbindlich)

- Deep Geo Navy `#16202B` (primär), Secondary Navy `#2A3A4F`, Greige `#DCD9D2`.
- Logo-Rot `#C23726` **nur fürs Logo**, nie für UI/Text.
- Schrift **Segoe UI Regular** (Fallbacks Selawik/system-ui/Arial). **Schrift immer weiss auf Blau.**
- Header bleibt beim Scrollen fixiert, ohne graue Trennlinie. Höhenlinien (`assets/contours*.svg`)
  dezent im Hintergrund.
- Modulkacheln: Fläche in Motivfarbe (Basismodule Greige, Wahlmodule Secondary Navy), Eyecatcher
  kleiner/zentriert mit Rand in Logofarbe. Highlights-Kacheln tone-in-tone, ohne Kontur, weisse
  Schrift, Partner-Hinweis unten in der Kachel.

## Mehrregionen / Einstieg

Root-`index.html`: trilingualer Picker (Deutschschweiz / Romandie / Ticino), setzt Cookie
`bizgeo_region` und leitet Wiederkehrer automatisch weiter. hreflang je Seite, `x-default`→`/de`.
`BASE` in `build_regions.py` steht auf `…github.io/chbizgeo-website` → **zum Livegang auf
`https://biz-geo.ch` umstellen.**

## `@claude` im Repo

`.github/workflows/claude.yml` ist eingerichtet: In einem Issue/PR-Kommentar `@claude …` schreiben,
dann arbeitet Claude in GitHub Actions am Repo und öffnet PRs.

## Offene To-dos

- **Live-Fix ausstehend:** FR/IT im Repo sind noch die Version *vor* dem „Lektionen"-Fix.
  Erster `./build.sh` + Push bringt die Korrektur (leçons/lezioni, Breadcrumbs, Modul-Badges) live.
- FHNW-Infoanlass: echtes Datum (aktuell „Termin folgt").
- QSK: direkte PDF-Links statt Übersichtsseite.
- Teamseite: Kernteam mit Fotos, Dozierende als Text.
- Datenmodell: Module/Kurse/Veranstaltungen je Region aus XLSX/CSV speisen.
- Livegang: `BASE`/hreflang auf biz-geo.ch; geprüfte Datenschutzerklärung (revidiertes DSG).

## Konventionen für Claude Code

1. Quelle in `_source/` bearbeiten – **nie** die generierten `de/ fr/ it/` oder die Wurzel-`index.html`.
2. Neue Texte immer mit FR/IT in `translate_data.py` nachziehen.
3. `./build.sh` ausführen, Übersetzungscheck ansehen, dann committen & pushen.
4. CD strikt einhalten (weisse Schrift auf Blau; Rot nur Logo).
