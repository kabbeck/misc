#!/usr/bin/env bash
set -euo pipefail

# Farben für Output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔨 Building presentation from yubikey.md...${NC}"

# Dateien prüfen
if [[ ! -f yubikey.md ]]; then
    echo "Error: yubikey.md not found"
    exit 1
fi
if [[ ! -f template.html ]]; then
    echo "Error: template.html not found"
    exit 1
fi

# Temporäre Datei für Slides
SLIDES_TMP=$(mktemp)

echo "  → Parsing yubikey.md..."

# Python-Script für Markdown-Parsing
python3 parse-markdown.py > "$SLIDES_TMP"

SLIDE_COUNT=$(grep -c '<section' "$SLIDES_TMP" || echo "0")
echo "  → Generated $SLIDE_COUNT slides"

# Template laden und Platzhalter ersetzen
echo "  → Merging with template.html..."

# Python Script für Replacement
python3 -c "
import sys

# Dateien einlesen
with open('template.html', 'r') as f:
    template = f.read()

with open('$SLIDES_TMP', 'r') as f:
    slides = f.read()

# Platzhalter ersetzen
result = template.replace('{{SLIDES}}', slides)

# Ausgabe
with open('index.html', 'w') as f:
    f.write(result)
"

# Cleanup
rm "$SLIDES_TMP"

echo -e "${GREEN}✅ Successfully built index.html${NC}"
echo -e "   Preview: ${BLUE}http://localhost:8000${NC}"
