#!/usr/bin/env bash
# BIZ Geo – baut die Mehrregionen-Site aus _source/ und spiegelt die
# veröffentlichten Teile (index.html + de/ fr/ it/) an die Repo-Wurzel.
# Danach: git add -A && git commit -m "Rebuild" && git push
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"     # _source/
REPO="$(cd "$HERE/.." && pwd)"            # Repo-Wurzel
OUT="$(mktemp -d)"
echo "› Baue nach $OUT ..."
BIZGEO_SITE="$OUT" python3 "$HERE/_build/build_regions.py"
echo "› Spiegele Output an Repo-Wurzel ..."
rm -rf "$REPO/de" "$REPO/fr" "$REPO/it"
cp -r "$OUT/de" "$OUT/fr" "$OUT/it" "$REPO/"
cp "$OUT/index.html" "$REPO/index.html"
echo "✓ Fertig in $REPO"
echo "  Nächster Schritt:  git add -A && git commit -m 'Rebuild' && git push"
