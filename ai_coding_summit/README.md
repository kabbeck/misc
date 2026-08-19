# AI Coding Summit — Präsentation

Reveal.js-Deck, gebaut aus einer Markdown-Datei. Kein Node, keine Abhängigkeiten,
nur Python 3 aus der Standardbibliothek.

Live: https://kabbeck.github.io/misc/ai_coding_summit/

## Bauen & Vorschau

```bash
python3 build.py            # index.html neu erzeugen
python3 build.py --serve    # bauen und auf http://localhost:8000 servieren
```

`index.html` ist generiert — **nie von Hand editieren**, sondern `slides.md`,
`deck.json`, `templates/` oder `css/` ändern und neu bauen.

## Dateien

```
slides.md            Inhalt (Single Source of Truth)
deck.json            Metadaten: Titel, Untertitel, Autor, Org, Datum, Sprache
build.py             Markdown -> HTML (Parser + Komponenten-Registry)
templates/
  base.html            Grundgerüst mit {{platzhalter}} und {{> partials}}
  partials/head.html   Fonts, Reveal-CSS, eigene CSS-Ebenen
  partials/footer.html Fußzeile (nutzt deck.json-Werte)
  partials/scripts.html Reveal-Initialisierung
css/
  tokens.css           Farben, Typo-Skala, Abstände — nur Variablen
  base.css             Element-Typografie: Text, Listen, Tabellen, Code
  layouts.css          Folien-Gerüste (@layout) + Fußzeile
  components.css       Bausteine (:::-Blöcke)
assets/              Bilder
index.html           generiert
```

Vier Regeln halten das System klein:

1. **Inhalt enthält kein Styling.** In `slides.md` stehen keine `style=`-Attribute.
2. **Farben und Größen stehen nur in `tokens.css`.** Alles andere referenziert sie.
3. **Layout ≠ Komponente.** `@layout` bestimmt die Anordnung der Folie,
   `:::`-Blöcke bestimmen das Aussehen der Inhalte.
4. **Feste Bühne 1600 × 900.** Alle px-Werte im CSS beziehen sich darauf,
   Reveal skaliert auf den Bildschirm. Keine em-Rechnerei.

## Folien schreiben

Folien werden durch `---` auf einer eigenen Zeile getrennt. Optionale
Kopfzeilen am Anfang einer Folie steuern das Layout:

```markdown
@layout: default
@class: wide

## Überschrift

Inhalt …
```

| Kopfzeile | Wirkung |
|-----------|---------|
| `@layout:` | `default` (Standard), `title`, `section`, `center`, `full`, `end` |
| `@class:`  | Zusatzklassen: `wide` (volle Textbreite), `middle` (alles mittig), `top` (oben bündig), `tight`, `fill` |
| `@talk:`   | Quellenzeile unten links: Foto, Sprecher:in, verlinkter Talk-Titel — Schlüssel aus `talks.json` |
| `@bg:`     | Hintergrundfarbe der Folie, z. B. `#10151b` |

Markdown-Umfang: Überschriften `#`–`####`, Listen (verschachtelbar), Tabellen
mit Ausrichtung, Code-Blöcke mit Sprache, Zitate, Links, `**fett**`, `*kursiv*`,
`` `code` ``, `[[Taste]]` für Tastenkappen, rohes HTML. `{+}` am Zeilenende macht
aus einem Absatz oder Listenpunkt ein Reveal-Fragment (blendet später ein).

`####` vor `##` wird automatisch zur Kapitelzeile (Eyebrow) über der Überschrift.

## Bausteine

Blöcke werden mit `:::` geöffnet und mit `:::` geschlossen, Attribute stehen in
der Öffnungszeile. Blöcke sind beliebig verschachtelbar.

| Baustein | Attribute | Zweck |
|----------|-----------|-------|
| `::: grid` | `cols=2\|3\|4\|1-2\|2-1` | Spaltenraster |
| `::: flow` | – | Kette mit Pfeilen zwischen den Elementen |
| `::: card` | `icon=` `title=` `tone=accent\|green\|amber\|red\|violet\|dark` | Kachel |
| `::: pane` | `tone=plain\|boxed\|sunken` | neutraler Container für freien Inhalt |
| `::: note` `::: tip` `::: warn` `::: danger` | `title=` `icon=` | Hinweisbox |
| `::: steps` | – | nummerierte Abfolge, `- Titel — Erläuterung` |
| `::: stats` | – | Kennzahlen, `- 68 % \| Beschriftung` |
| `::: links` | – | Verweise auf die eigentliche Arbeit, `- Beschriftung \| https://…` |
| `::: quote` | `by=` | Zitat mit Quelle |
| `::: figure` | `src=` `alt=` `caption=` | Bild mit Bildunterschrift |
| `::: notes` | – | Sprechernotizen (Taste `S`) |

Beispiel:

```markdown
::: grid cols=3
::: card icon="⚡" title="Autocomplete" tone=accent
Zeile für Zeile im Editor.
:::
::: card icon="🧭" title="Agent" tone=green
Ganze Aufgabe, mehrere Dateien.
:::
:::
```

## Quellenzeile und Sprecherfotos

`talks.json` ist die Quellenliste: ein Schlüssel pro Talk, dazu Sprecher:in,
Organisation, Talk-Titel und die GitNation-URL. `@talk: leimonis` auf einer Folie
blendet daraus unten links Foto, Name und den verlinkten Titel ein.

Das Foto wird unter `assets/speakers/<schlüssel>.jpg` erwartet — gleicher Name
wie der Schlüssel. Die vorhandenen stammen von der Event-Übersicht
(gitnation.com), quadratisch auf 200 px zugeschnitten. Ein neues Foto ergänzen:

```bash
curl -o assets/speakers/<schlüssel>.jpg \
  "<cloudinary-url-von-der-eventseite>"
```

Fehlt ein Schlüssel in `talks.json`, bricht der Build mit einer Meldung ab —
statt eine Folie ohne Quelle auszuliefern.

Die Quellenzeile verweist auf den *Talk*. Auf die *eigentliche Arbeit* — das
Dashboard, die Studie, das Repo — verweist `::: links` mitten auf der Folie:

```markdown
::: links
- Alberts' Dashboard — läuft weiter, Zahlen live | https://www.claudescode.dev
:::
```

Angezeigt wird die URL ohne `https://` und `www.`, damit man sie von der Leinwand
abtippen kann. Deshalb gehören dorthin kurze, sprechende URLs — keine
Deep-Links mit Query-String.

## Erweitern

**Neuer Baustein** = eine Funktion in `build.py` + ein Eintrag in `COMPONENTS`
+ ein Block in `css/components.css`:

```python
def c_badge(attrs, body, blocks):
    return f'<span class="badge">{blocks(body)}</span>'

COMPONENTS = {..., "badge": c_badge}
```

**Neues Layout** = ein Wert für `@layout:` + ein Block `.slide--name .slide__inner`
in `css/layouts.css`.

## Reveal-Version

Gepinnt auf **6.0.1** in `templates/partials/head.html` und `scripts.html` —
bewusst keine Range wie `@6`, damit ein CDN-Update das Deck nicht verändert.

Zum Anheben: aktuelle Version prüfen und beide Partials ändern.

```bash
curl -s https://registry.npmjs.org/reveal.js | python3 -c "import json,sys; print(json.load(sys.stdin)['dist-tags']['latest'])"
```

## Steuerung während des Vortrags

`→` / `Leertaste` weiter · `ESC` Übersicht · `S` Sprechernotizen · `F` Vollbild ·
`B` Pause (schwarz)
