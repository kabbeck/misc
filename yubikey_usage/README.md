# YubiKey Präsentation

Eine Präsentation über YubiKey Installation und Verwendung, basierend auf [Dr. Duh's YubiKey Guide](https://github.com/drduh/YubiKey-Guide).

## Lokale Vorschau

Da reveal.js die Markdown-Datei über JavaScript lädt, benötigen Sie einen lokalen Webserver:

```bash
# Mit Python 3
python3 -m http.server 8000

# Oder mit Node.js (npx)
npx http-server -p 8000
```

Dann öffnen Sie: http://localhost:8000

## GitHub Pages

Die Präsentation wird automatisch auf GitHub Pages veröffentlicht nach dem Push.

## Steuerung

- **Pfeiltasten** oder **Leertaste**: Nächste Folie
- **ESC**: Übersicht aller Folien
- **S**: Notizen-Ansicht
- **F**: Vollbild

## Struktur

- `yubikey.md` - Präsentationsinhalt (Markdown, Single Source of Truth)
- `yubikey.css` - Custom Styles und Typografie
- `template.html` - HTML-Wrapper mit Reveal.js
- `parse-markdown.py` - Markdown → HTML Konverter
- `build-presentation.sh` - Build-Script
- `index.html` - Generierte Präsentation (nicht manuell editieren!)

## Build-System

```bash
# Präsentation neu bauen
./build-presentation.sh

# Änderungen in yubikey.md werden automatisch verarbeitet
```
