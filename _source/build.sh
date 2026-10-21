#!/usr/bin/env bash
# BIZ Geo – baut die Mehrregionen-Site aus _source/ nach _source/_site/
# (index.html + de/ fr/ it/). Lokal = Vorschau; live geht, was die GitHub Action
# (.github/workflows/pages.yml) in CI frisch baut und aus _source/_site/ veröffentlicht.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"     # _source/
OUT="$HERE/_site"                         # wird bei jedem Build geleert (build_regions.py)
echo "› Baue nach $OUT ..."
BIZGEO_SITE="$OUT" python3 "$HERE/_build/build_regions.py"
echo "✓ Fertig in $OUT"
echo "  Vorschau:  python3 -m http.server 8765 --directory \"$OUT\""
