#!/bin/sh
# Usage: tools/typeset/typeset.sh article.md OutputName "Running header"
# Writes OutputName.docx and OutputName.pdf in the current directory.
set -e
D=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d)
python3 -I "$D/md2json.py" "$1" "$T/content.json"
CONTENT="$T/content.json" OUT="$T/base.docx" HDR="$3" DESC="$3" NOFN=1 node "$D/build.js"
python3 -I "$D/embed.py" "$T/base.docx" "$2.docx"
soffice --headless --convert-to pdf "$2.docx" >/dev/null 2>&1
pdfinfo "$2.pdf" | grep Pages
