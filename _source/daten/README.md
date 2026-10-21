# Inhalte pflegen (CSV)

Beschreibungen, Preise, Kursangebot und Kalender der Website stehen in diesen vier Dateien.
Nach einer Änderung wird die Site neu gebaut (`cd _source && ./build.sh`), danach committen und pushen.

| Datei | Inhalt | erscheint auf |
|---|---|---|
| `module.csv` | 13 Module: Titel, Kurzbeschreibung, Kompetenzen, Voraussetzungen, Kurse, Lektionen, Kosten | Modulseiten, Startseite, Fachausweis |
| `fachgebiete.csv` | Die fünf Fachgebiete mit Beschreibung | Weiterbildung |
| `kursangebot.csv` | Alle Einzelkurse, je einem Fachgebiet zugeordnet | Weiterbildung |
| `veranstaltungen.csv` | Termine (Unterricht, Kurse, Prüfungen, Anlässe, Fristen, Highlights) | Kalender, Startseite, Weiterbildung |

## Format

- **Trennzeichen Semikolon**, Kodierung **UTF-8** – so öffnet und speichert Excel (CH) die Dateien direkt.
  Beim Speichern in Excel «CSV UTF-8 (durch Trennzeichen getrennt)» wählen.
- **Drei Sprachen pro Text:** Spalten `…_de`, `…_fr`, `…_it`. Ist FR oder IT leer, erscheint vorerst
  der deutsche Text und der Build meldet die Lücke («⚠ CSV: … fehlende Übersetzungen»).
- **Listen in einer Zelle** mit ` | ` trennen, z. B. `Präsentieren | Kommunizieren`.
  FR/IT-Listen brauchen gleich viele Einträge in derselben Reihenfolge.
- **Ja/Nein-Spalten:** `ja` oder leer.
- **Datum:** `TT.MM.JJJJ` (auch `TT.MM.JJ` oder `JJJJ-MM-TT` wird erkannt).
- Die **Reihenfolge der Zeilen** bestimmt die Reihenfolge auf der Website (Ausnahme: Termine, die nach Datum sortiert werden).

## module.csv

| Spalte | Beispiel | Hinweis |
|---|---|---|
| `code` | `B1` | B1–B5, S1–S8; bestimmt Seitenname `modul-b1.html` und Eyecatcher-Bild |
| `art` | `Basismodul` / `Wahlmodul` | |
| `lektionen` | `68` | nur die Zahl |
| `kosten_chf` | `1600` | nur die Zahl, wird als `CHF 1'600` angezeigt |
| `titel_*`, `kurzbeschreibung_*` | | |
| `kompetenzen_*`, `voraussetzungen_*`, `kurse_*` | | Listen mit ` \| ` |

## fachgebiete.csv / kursangebot.csv

`fachgebiete.csv`: `id` (kurzer Schlüssel, z. B. `gis`), Titel und Beschreibung in drei Sprachen.
`kursangebot.csv`: `fachgebiet` (= `id` aus fachgebiete.csv) und der Kursname in drei Sprachen.

## veranstaltungen.csv

| Spalte | Beispiel | Hinweis |
|---|---|---|
| `datum` | `22.10.2026` | Pflicht |
| `bis` | `24.10.2026` | nur bei mehrtägigen Anlässen |
| `zeit` | `08:30 – 16:30` oder `ganztägig` | ohne «Uhr»; FR/IT werden automatisch formatiert |
| `ort` | `PH Zürich` | Zürich, Bern, Zug, Basel, Luzern werden für FR/IT übersetzt |
| `typ` | `Unterricht`, `Kurs`, `Prüfung`, `Anlass`, `Frist`, `Highlight` | |
| `klasse` | `S8-26` | optional; bei Kursen als «Kurs S8-26» angezeigt |
| `modul` | `S8` | optional; Eyecatcher-Bild bei «Aktuelle Kurse» |
| `partner` | `FHNW` | optional; zeigt «Partner · FHNW» auf der Highlight-Kachel |
| `startseite` | `ja` | Termin erscheint auf der Startseite (max. 5; Highlights mit `ja` haben dort Vorrang) |
| `highlight` | `ja` | erscheint als Kachel unter «Highlights»; gleiche Titel werden zu einer Kachel mit allen Daten zusammengefasst |
| `titel_*` | | |
| `text_*` | | Beschreibung auf der Highlight-Kachel (optional) |

**Vergangene Termine** werden beim Bauen automatisch ausgeblendet. Die Website zeigt also den Stand
des letzten Builds – damit der Kalender aktuell bleibt, regelmässig neu bauen und pushen.
«Aktuelle Kurse» (Weiterbildung) zeigt die nächsten drei Termine vom Typ `Kurs`.
