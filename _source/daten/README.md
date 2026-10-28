# Inhalte pflegen (CSV)

Beschreibungen, Preise, Kursangebot und Kalender der Website stehen in CSV-Dateien –
**je Sprachregion ein eigener Ordner**, jede Datei nur in der Sprache der Region:

| Ordner | Region | Sprache der Inhalte | erscheint unter |
|---|---|---|---|
| `de/` | Deutschschweiz | Deutsch | `/de/` |
| `fr/` | Romandie | Französisch | `/fr/` |
| `it/` | Ticino | Italienisch | `/it/` |

Jeder Ordner enthält dieselben vier Dateien:

| Datei | Inhalt | erscheint auf |
|---|---|---|
| `module.csv` | 13 Module: Titel, Kurzbeschreibung, Kompetenzen, Voraussetzungen, Kurse, Lektionen, Kosten | Modulseiten, Startseite, Fachausweis |
| `fachgebiete.csv` | Die Fachgebiete mit Beschreibung | Weiterbildung |
| `kursangebot.csv` | Alle Einzelkurse, je einem Fachgebiet zugeordnet | Weiterbildung |
| `veranstaltungen.csv` | Termine (Unterricht, Kurse, Prüfungen, Anlässe, Fristen, Highlights) | Kalender, Startseite, Weiterbildung |

Die Regionen sind vollständig getrennt: Ein Termin in `de/veranstaltungen.csv` erscheint nur auf
den deutschsprachigen Seiten. Soll ein Anlass in mehreren Regionen erscheinen, wird er in jeder
Region-Datei eingetragen (in der jeweiligen Sprache).

Nach einer Änderung committen und pushen (oder direkt auf GitHub bearbeiten) – die GitHub Action
baut und veröffentlicht die Site. Lokal vorab prüfen: `cd _source && ./build.sh`
(zeigt je Region die Anzahl Module, Kurse und kommender Termine).

## Format

- **Trennzeichen Semikolon**, Kodierung **UTF-8** – so öffnet und speichert Excel (CH) die Dateien
  direkt. Beim Speichern in Excel «CSV UTF-8 (durch Trennzeichen getrennt)» wählen.
- **Spaltennamen** (erste Zeile) sind in allen Regionen gleich und bleiben deutsch – nicht umbenennen.
- **Listen in einer Zelle** mit ` | ` trennen, z. B. `Präsentieren | Kommunizieren`.
- **Ja/Nein-Spalten:** `ja` (auch `oui`, `sì`, `x`) oder leer.
- **Datum:** `TT.MM.JJJJ` (auch `TT.MM.JJ` oder `JJJJ-MM-TT` wird erkannt).
- Die **Reihenfolge der Zeilen** bestimmt die Reihenfolge auf der Website (Ausnahme: Termine,
  die nach Datum sortiert werden).

## module.csv

| Spalte | Beispiel | Hinweis |
|---|---|---|
| `code` | `B1` | B1–B5, S1–S8; bestimmt Seitenname `modul-b1.html` und Eyecatcher-Bild |
| `art` | `Basismodul` / `Wahlmodul` (FR `Module de base` / `Module à option`, IT `Modulo di base` / `Modulo a scelta`) | |
| `lektionen` | `68` | nur die Zahl |
| `kosten_chf` | `1600` | nur die Zahl, wird als `CHF 1'600` angezeigt |
| `titel`, `kurzbeschreibung` | | |
| `kompetenzen`, `voraussetzungen`, `kurse` | | Listen mit ` \| ` |

## fachgebiete.csv / kursangebot.csv

`fachgebiete.csv`: `id` (kurzer Schlüssel, z. B. `gis`), `titel`, `beschreibung`.
`kursangebot.csv`: `fachgebiet` (= `id` aus fachgebiete.csv) und `kurs`.

## veranstaltungen.csv

| Spalte | Beispiel | Hinweis |
|---|---|---|
| `datum` | `22.10.2026` | Pflicht |
| `bis` | `24.10.2026` | nur bei mehrtägigen Anlässen |
| `zeit` | `08:30 – 16:30` oder `ganztägig` | ohne «Uhr»; wird je Sprache formatiert (FR `08h30`) |
| `ort` | `PH Zürich` | in der Sprache der Region eintragen |
| `typ` | DE `Unterricht`, `Kurs`, `Prüfung`, `Anlass`, `Frist`, `Highlight` · FR `Enseignement`, `Cours`, `Examen`, `Événement`, `Délai`, `Temps fort` · IT `Lezione`, `Corso`, `Esame`, `Evento`, `Scadenza`, `Highlight` | |
| `klasse` | `S8-26` | optional; bei Kursen als «Kurs S8-26» angezeigt |
| `modul` | `S8` | optional; Eyecatcher-Bild bei «Aktuelle Kurse» |
| `partner` | `FHNW` | optional; zeigt «Partner · FHNW» auf der Highlight-Kachel |
| `startseite` | `ja` | Termin erscheint auf der Startseite (max. 5; Highlights mit `ja` haben dort Vorrang) |
| `highlight` | `ja` | erscheint als Kachel unter «Highlights»; gleiche Titel werden zu einer Kachel mit allen Daten zusammengefasst |
| `titel` | | |
| `text` | | Beschreibung auf der Highlight-Kachel (optional) |

**Vergangene Termine** werden beim Bauen automatisch ausgeblendet. Die Website wird jede Nacht
und nach jedem Push auf `_source/` von einer GitHub Action neu gebaut – eine CSV-Änderung, die
direkt auf GitHub bearbeitet und committet wird, ist nach wenigen Minuten live.
«Aktuelle Kurse» (Weiterbildung) zeigt die nächsten drei Termine vom Typ `Kurs`.
Ist eine Region-Datei ohne kommende Termine, zeigt die Website einen Hinweis
(«Aktuell sind keine Termine eingetragen.»).
