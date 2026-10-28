# BIZ Geo – Website (chbizgeo-website)

Statische, mehrsprachige Website für das **Bildungszentrum Geomatik Schweiz (BIZ Geo)**,
Domain künftig **biz-geo.ch** (vormals geo-education.ch). Veröffentlichung über **GitHub Pages**
per GitHub Action (`.github/workflows/pages.yml`, Pages-Quelle «GitHub Actions»).
Remote: `BIZ-Geo/chbizgeo-website`.

## WICHTIG: Quelle vs. Ausgabe

- **`_source/`** – die **einzige Quelle**: deutsche Quellseiten, Build-Pipeline (`_build/`),
  Übersetzungstabelle und die gepflegten Inhalte je Sprachregion (`daten/<region>/*.csv`). Hier wird entwickelt.
- **`_source/_site/`** – die **generierte Ausgabe** (`index.html` + `de/ fr/ it/`). Nicht im Repo
  (`.gitignore`), wird bei jedem Build geleert und neu geschrieben. **Niemals von Hand bearbeiten.**
- Im Repo liegt **kein Build-Output** mehr; es gibt keine `de/ fr/ it/` und keine `index.html` an der Wurzel.

> Faustregel: **Immer in `_source/` ändern** (Inhalte in `_source/daten/<region>/*.csv`), committen, pushen –
> die Action baut und veröffentlicht.

## Bauen & Veröffentlichen

**Live geht, was die Action baut.** `.github/workflows/pages.yml` baut in CI frisch aus `_source/`
(`./build.sh`) und lädt `_source/_site/` als Pages-Artefakt hoch. Auslöser:
- täglich 01:15 UTC – damit **vergangene Termine** aus dem Kalender verschwinden,
- jeder Push auf `main`, der `_source/**` ändert (auch CSV-Änderungen direkt im Browser auf GitHub),
- manuell: Actions → «Website bauen und veröffentlichen» → Run workflow.

Die Action committet nichts; der Branch-Schutz auf `main` (Änderungen per PR) bleibt unberührt.

**Lokale Vorschau** (optional, z. B. vor einem PR):

```bash
cd _source
./build.sh                                              # baut nach _source/_site/
python3 -m http.server 8765 --directory _site           # http://localhost:8765
```

`build.sh` setzt `BIZGEO_SITE=_source/_site`; `build_regions.py` leert diesen Ordner vor dem Bauen –
deshalb `BIZGEO_SITE` nie auf einen anderen Ordner (schon gar nicht die Repo-Wurzel) zeigen lassen.

### Build-Pipeline (`_source/_build/`)

| Skript | Zweck |
|---|---|
| `build_regions.py` | **Hauptskript.** Baut Root-Picker + `de/ fr/ it/` nach `_source/_site/`. Für jede Region (fr, it, de – DE zuletzt) ruft es die drei folgenden mit `BIZGEO_REGION=<region>` auf, kopiert `assets/` und übersetzt die festen Seitentexte (FR/IT). Meldet je Region die Anzahl Module/Kurse/Termine und am Ende unübersetzte DE-Reste. |
| `build.py` | Hauptseiten aus Inline-DE-HTML (fachausweis, weiterbildung, veranstaltungen, ueber-uns, anmeldung, kontakt, datenschutz); füllt ausserdem die `<!-- DATEN:… -->`-Bereiche der Quell-`index.html` (Module, Termine, Highlights) mit den Inhalten der Region. |
| `build_modules.py` | 13 Modul-Detailseiten `modul-b1…s8.html` aus `daten/<region>/module.csv`. |
| `build_index.py` | `assets/search-index.json` für den Frage-Bot. |
| `daten.py` | Liest `_source/daten/<region>/*.csv` (Region aus `BIZGEO_REGION`), formatiert Daten/Zeiten in der Sprache der Region, blendet vergangene Termine aus; enthält die Textbausteine (`TEXT`), die mit CSV-Inhalten kombiniert werden. |
| `translate_data.py` | **Übersetzungstabelle** `TRIPLES = [(DE, FR, IT), …]` für die festen Seitentexte. |
| `assemble_single.py` u. a. | Hilfsskripte (eingebettete Präsentationsdatei, Höhenlinien, Varianten). |

## Inhalte aus CSV (`_source/daten/<region>/`)

Module (Beschreibungen, Kompetenzen, Voraussetzungen, Kurse, Lektionen, Preise), Fachgebiete,
Kursangebot und Veranstaltungskalender werden **manuell in CSV-Dateien gepflegt – je Sprachregion
getrennt**: `daten/de/` (Deutschschweiz), `daten/fr/` (Romandie), `daten/it/` (Ticino), jeweils
`module.csv`, `fachgebiete.csv`, `kursangebot.csv`, `veranstaltungen.csv`. Jede Datei ist **einsprachig**
(Sprache der Region); die Spaltennamen sind überall gleich (deutsch). Spalten und Format in
**`_source/daten/README.md`**. Kurz: Semikolon, UTF-8, Listen mit ` | `, Datum `TT.MM.JJJJ`.

- Die Regionen sind vollständig getrennt: Inhalte aus `daten/fr/` erscheinen nur unter `/fr/` usw.
  Es gibt keine Übersetzung der CSV-Inhalte zwischen den Regionen.
- **Vergangene Termine** blendet der Build aus (Stichtag = Build-Datum, Zeitzone Europe/Zurich).
  Ohne kommende Termine zeigt die Seite einen Hinweis («Aktuell sind keine Termine eingetragen.»).
- Die Bereiche zwischen `<!-- DATEN:x -->` und `<!-- /DATEN:x -->` in `_source/index.html` werden bei
  jedem Build überschrieben – dort nicht von Hand ändern.

## Übersetzung pflegen

- DE ist die Quelle. Übersetzt wird beim Bauen durch **randbündige Ersetzung** ganzer Textknoten
  (`>…<`) und der Attribute `alt/title/aria-label/content` – längste Schlüssel zuerst, damit z. B.
  „Basismodul" nie in „Basismodule" hineinragt.
- **Inhalte aus CSV** werden nicht übersetzt: jede Region hat ihre eigenen, einsprachigen Dateien.
  Textbausteine, die mit CSV-Inhalten kombiniert werden (z. B. «Modul B1», «Kurs S8-26», Datumsformat),
  stehen in `TEXT` bzw. den Formatfunktionen in `daten.py`.
- **Neue feste Seitentexte (im Code) ⇒ Zeile `(DE, FR, IT)` in `_source/_build/translate_data.py` ergänzen.**
- **Nicht übersetzt (bewusst):** BIZ Geo, QSK, FHNW, FME, GIS, BIM, XML, LFP3, LTOP, SIA, EFZ,
  Modulcodes (B1, S8-26), CHF-Beträge, Eigennamen/Adressen, Region-Namen im Root-Picker.
- **Festgelegte Fachbegriffe:** SBFI→SEFRI, ÖREB→RDPPF (FR)/RDPP (IT), DMAV→MD.MO/MD.MU,
  „eidg. Fachausweis"→„brevet fédéral"/„attestato professionale federale",
  „Lehrgang"→„cursus"/„ciclo di formazione", „Lektionen"→„leçons"/„lezioni".
- **Qualitätscheck** (nach dem Build, in `_source/_site/`): jeder Textknoten in FR/IT, der identisch
  zur DE-Fassung ist, deutet auf eine Lücke (Ausnahmen: sprachgleiche Begriffe wie Team, PDF, Tel.,
  Vision, Eigennamen).

## Corporate Design (verbindlich)

- Deep Geo Navy `#16202B` (primär), Secondary Navy `#2A3A4F`, Greige `#DCD9D2`.
- Logo-Rot `#C23726` **nur fürs Logo**, nie für UI/Text.
- Schrift **Segoe UI Regular** (Fallbacks Selawik/system-ui/Arial). **Schrift immer weiss auf Blau.**
- Header bleibt beim Scrollen fixiert, ohne graue Trennlinie. Höhenlinien (`assets/contours*.svg`)
  dezent im Hintergrund.
- Modulkacheln: Fläche in Motivfarbe (Basismodule Greige, Wahlmodule Secondary Navy), Eyecatcher
  kleiner/zentriert mit Rand in Logofarbe. Highlights-Kacheln tone-in-tone, ohne Kontur, weisse
  Schrift, Partner-Hinweis unten in der Kachel.

## Design-Entscheide (nicht umkehren)

Bewusst so gewählt (Team-Feedback) – nicht „verbessern", nur bei echten Defekten melden:
- Weisse Schrift auf blauem/Secondary-Navy-Hintergrund (Hausregel). Logo-Rot nur fürs Logo.
- Modulkachel = Fläche in Eyecatcher-Motivfarbe (Basis Greige, Wahl Secondary Navy);
  Eyecatcher klein/zentriert mit farbigem Rand. Kein Umfärben der Kacheln/Logos.
- Highlights-Kacheln tone-in-tone (Secondary Navy), ohne Kontur, weisse Schrift,
  Partner-Hinweis unten in der Kachel. Keine weissen Highlight-Kacheln.
- Verworfen: Editorial-Layout; Diagonal-Übergänge zwischen Sektionen (Scroll-Animation bleibt);
  Flaggen-Emojis + „Empfohlen"-Badge im Regionen-Picker.
- Fixierter Header ohne graue Trennlinie; dezente Höhenlinien im Hintergrund;
  Logo oben links nicht zu klein; Scroll-Cue sichtbar lassen.

## Mehrregionen / Einstieg

Die generierte `_site/index.html` ist der trilinguale Picker (Deutschschweiz / Romandie / Ticino);
er setzt das Cookie `bizgeo_region` und leitet Wiederkehrer automatisch weiter. Quelle: `ROOT_INDEX`
in `build_regions.py`. hreflang je Seite, `x-default`→`/de`. `BASE` in `build_regions.py` steht auf
`…github.io/chbizgeo-website` → **zum Livegang auf `https://biz-geo.ch` umstellen.**

## `@claude` im Repo

`.github/workflows/claude.yml` ist eingerichtet: In einem Issue/PR-Kommentar `@claude …` schreiben,
dann arbeitet Claude in GitHub Actions am Repo und öffnet PRs.

## Offene To-dos

- Teamseite: Kernteam mit Fotos, Dozierende als Text.
- Romandie/Ticino: eigene Termine in `daten/fr|it/veranstaltungen.csv` eintragen; Module und
  Kursangebot sind Übersetzungen der Deutschschweiz und von den Schulen zu prüfen/anzupassen.
- Frage-Bot (`search-index.json`) wird je Region aus den noch nicht übersetzten Seiten gebaut
  (feste Texte deutsch) – ggf. auf die übersetzten Seiten umstellen.
- Downloads (Schulplanung, Teilnahmebedingungen) liegen noch auf geo-education.ch → vor dem
  Domainwechsel ins Repo holen.
- Livegang: `BASE`/hreflang auf biz-geo.ch; geprüfte Datenschutzerklärung (revidiertes DSG).

## Konventionen für Claude Code

1. Nur in `_source/` arbeiten – `_source/_site/` ist Build-Ausgabe und nicht im Repo.
2. Inhalte (Module, Kurse, Termine, Preise) in `_source/daten/<region>/*.csv` ändern, nicht im Code –
   immer in der richtigen Region (de/fr/it) und in deren Sprache. Neue feste
   Seitentexte immer mit FR/IT in `translate_data.py` nachziehen.
3. Vor dem PR `./build.sh` ausführen und Übersetzungscheck ansehen; veröffentlicht wird nach dem
   Merge automatisch durch die Action.
4. CD und die **Design-Entscheide** strikt einhalten (weisse Schrift auf Blau; Rot nur Logo).
