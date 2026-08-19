#!/usr/bin/env python3
"""
build.py — baut index.html aus slides.md + templates/ + deck.json

    python3 build.py            # bauen
    python3 build.py --serve    # bauen und auf http://localhost:8000 servieren

Nur Standardbibliothek, keine Abhängigkeiten.

Aufbau:
    inline()     Inline-Markdown (Code, Links, Bold, Italic, kbd)
    Parser       Block-Ebene (Überschriften, Listen, Tabellen, Code, :::-Blöcke)
    COMPONENTS   Registry: ':::-Name' -> Render-Funktion  <- hier erweitern
    render_deck  Folien-Split + @meta-Zeilen
    build        Template + Partials + Platzhalter
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SLIDES_MD = ROOT / "slides.md"
DECK_JSON = ROOT / "deck.json"
TALKS_JSON = ROOT / "talks.json"
SPEAKER_DIR = "assets/speakers"
TEMPLATE = ROOT / "templates" / "base.html"
PARTIALS = ROOT / "templates" / "partials"
OUTPUT = ROOT / "index.html"


# ---------------------------------------------------------------- inline ----

RE_CODE = re.compile(r"`([^`]+)`")
RE_IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
RE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
RE_BOLD = re.compile(r"\*\*(.+?)\*\*")
RE_ITALIC = re.compile(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])")
RE_KBD = re.compile(r"\[\[(.+?)\]\]")
RE_PLACEHOLDER = re.compile(r"\x00(\d+)\x00")


def inline(text: str) -> str:
    """Inline-Markdown -> HTML. Code-Spans werden escaped, sonst passthrough."""
    stash: list[str] = []

    def keep(match: re.Match) -> str:
        stash.append(html.escape(match.group(1)))
        return f"\x00{len(stash) - 1}\x00"

    out = RE_CODE.sub(keep, text)
    out = RE_IMG.sub(r'<img src="\2" alt="\1">', out)
    out = RE_LINK.sub(r'<a href="\2" target="_blank" rel="noopener">\1</a>', out)
    out = RE_BOLD.sub(r"<strong>\1</strong>", out)
    out = RE_ITALIC.sub(r"<em>\1</em>", out)
    out = RE_KBD.sub(r"<kbd>\1</kbd>", out)
    return RE_PLACEHOLDER.sub(lambda m: f"<code>{stash[int(m.group(1))]}</code>", out)


def fragment(text: str) -> tuple[str, str]:
    """'Text {+}' -> ('Text', ' class="fragment"') für Reveal-Einblendungen."""
    if text.rstrip().endswith("{+}"):
        return text.rstrip()[:-3].rstrip(), ' class="fragment"'
    return text, ""


# ------------------------------------------------------------ components ----
#
# Signatur: render(attrs: dict, body: list[str], blocks) -> str
#   attrs   Attribute der :::-Zeile, z. B. ::: card icon="🔐" tone=green
#   body    Rohzeilen zwischen ::: und :::
#   blocks  Callback, das Rohzeilen rekursiv als Blöcke rendert


def c_grid(attrs, body, blocks):
    cols = attrs.get("cols", "2")
    return f'<div class="grid grid--{cols}">{blocks(body)}</div>'


def c_flow(attrs, body, blocks):
    return f'<div class="flow">{blocks(body)}</div>'


def c_card(attrs, body, blocks):
    tone = attrs.get("tone", "neutral")
    parts = [f'<div class="card card--{tone}">']
    if "icon" in attrs:
        parts.append(f'<div class="card__icon">{attrs["icon"]}</div>')
    if "title" in attrs:
        parts.append(f'<h3 class="card__title">{inline(attrs["title"])}</h3>')
    parts.append(f'<div class="card__body">{blocks(body)}</div>')
    parts.append("</div>")
    return "".join(parts)


def c_pane(attrs, body, blocks):
    tone = attrs.get("tone", "plain")
    return f'<div class="pane pane--{tone}">{blocks(body)}</div>'


def c_callout(attrs, body, blocks, tone="note"):
    icon = attrs.get("icon", {"note": "📌", "tip": "💡", "warn": "⚠️", "danger": "🛑"}[tone])
    title = f'<b class="callout__title">{inline(attrs["title"])}</b>' if "title" in attrs else ""
    return (
        f'<div class="callout callout--{tone}">'
        f'<span class="callout__icon">{icon}</span>'
        f'<div class="callout__body">{title}{blocks(body)}</div>'
        f"</div>"
    )


def c_steps(attrs, body, blocks):
    items = [re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", ln) for ln in body if ln.strip()]
    out = ['<ol class="steps">']
    for n, item in enumerate(items, 1):
        title, _, rest = item.partition(" — ")
        out.append(
            f'<li class="step"><span class="step__num">{n}</span>'
            f'<span class="step__text"><b>{inline(title)}</b>'
            + (f"<span>{inline(rest)}</span>" if rest else "")
            + "</span></li>"
        )
    out.append("</ol>")
    return "".join(out)


def c_stats(attrs, body, blocks):
    out = ['<div class="stats">']
    for line in body:
        if not line.strip():
            continue
        value, _, label = re.sub(r"^\s*[-*]\s+", "", line).partition("|")
        out.append(
            f'<div class="stat"><span class="stat__value">{inline(value.strip())}</span>'
            f'<span class="stat__label">{inline(label.strip())}</span></div>'
        )
    out.append("</div>")
    return "".join(out)


def c_links(attrs, body, blocks):
    """Prominente Verweise auf die eigentliche Arbeit eines Talks.

    Eine Zeile pro Verweis: '- Beschriftung | https://…'. Angezeigt wird die
    URL ohne Schema und 'www.' — auf der Leinwand soll man sie abtippen können.
    """
    out = ['<div class="links">']
    for line in body:
        if not line.strip():
            continue
        label, _, url = re.sub(r"^\s*[-*]\s+", "", line).partition("|")
        url = url.strip()
        if not url:
            raise SystemExit(f"'::: links': Zeile ohne URL — '{line.strip()}'")
        shown = re.sub(r"^https?://(www\.)?", "", url).rstrip("/")
        out.append(
            f'<a class="link" href="{url}" target="_blank" rel="noopener">'
            f'<span class="link__label">{inline(label.strip())}</span>'
            f'<span class="link__url">{shown}</span></a>'
        )
    out.append("</div>")
    return "".join(out)


def c_quote(attrs, body, blocks):
    cite = f'<cite class="quote__cite">{inline(attrs["by"])}</cite>' if "by" in attrs else ""
    return f'<figure class="quote">{blocks(body)}{cite}</figure>'


def c_figure(attrs, body, blocks):
    caption = f'<figcaption>{inline(attrs["caption"])}</figcaption>' if "caption" in attrs else ""
    return (
        f'<figure class="figure">'
        f'<img src="{attrs.get("src", "")}" alt="{attrs.get("alt", "")}">'
        f"{caption}</figure>"
    )


def c_notes(attrs, body, blocks):
    return f'<aside class="notes">{blocks(body)}</aside>'


COMPONENTS = {
    "grid": c_grid,
    "flow": c_flow,
    "card": c_card,
    "pane": c_pane,
    "steps": c_steps,
    "stats": c_stats,
    "links": c_links,
    "quote": c_quote,
    "figure": c_figure,
    "notes": c_notes,
    "note": lambda a, b, r: c_callout(a, b, r, "note"),
    "tip": lambda a, b, r: c_callout(a, b, r, "tip"),
    "warn": lambda a, b, r: c_callout(a, b, r, "warn"),
    "danger": lambda a, b, r: c_callout(a, b, r, "danger"),
}


# ----------------------------------------------------------------- parser ---

RE_OPEN = re.compile(r"^:::\s*([\w-]+)\s*(.*)$")
RE_CLOSE = re.compile(r"^:::\s*$")
RE_ATTR = re.compile(r'([\w-]+)(?:=(?:"([^"]*)"|(\S+)))?')
RE_HEADING = re.compile(r"^(#{1,4})\s+(.*)$")
RE_BULLET = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
RE_TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


def parse_attrs(raw: str) -> dict[str, str]:
    # Ein gerades " im Wert beendet das Attribut still und der Rest wird als
    # Attributname verschluckt — lieber laut abbrechen als halbe Titel ausliefern.
    if raw.count('"') % 2:
        raise SystemExit(
            f"Ungerade Zahl von Anführungszeichen in ':::'-Attributen: {raw.strip()}\n"
            "Für Anführungszeichen im Wert typografische verwenden: „ und \u201c"
        )
    return {m.group(1): (m.group(2) or m.group(3) or "") for m in RE_ATTR.finditer(raw)}


class Parser:
    """Wandelt Markdown-Zeilen in HTML-Blöcke um."""

    def __init__(self, lines: list[str]):
        self.lines = lines
        self.i = 0

    # -- Hilfen ------------------------------------------------------------
    def at_end(self) -> bool:
        return self.i >= len(self.lines)

    def line(self) -> str:
        return self.lines[self.i]

    def take_until_close(self) -> list[str]:
        """Zeilen bis zum passenden ':::' einsammeln (verschachtelbar)."""
        depth, body = 1, []
        while not self.at_end():
            line = self.line()
            self.i += 1
            if RE_OPEN.match(line):
                depth += 1
            elif RE_CLOSE.match(line):
                depth -= 1
                if depth == 0:
                    return body
            body.append(line)
        return body

    # -- Hauptschleife ------------------------------------------------------
    def render(self) -> str:
        out: list[str] = []
        while not self.at_end():
            line = self.line()
            if not line.strip():
                self.i += 1
            elif RE_OPEN.match(line):
                out.append(self.component())
            elif line.lstrip().startswith("```"):
                out.append(self.code())
            elif line.lstrip().startswith("|") and self.next_is_table_sep():
                out.append(self.table())
            elif RE_BULLET.match(line):
                out.append(self.list_())
            elif RE_HEADING.match(line):
                out.append(self.heading())
            elif line.lstrip().startswith(">"):
                out.append(self.blockquote())
            elif line.lstrip().startswith("<"):
                out.append(self.raw_html())
            else:
                out.append(self.paragraph())
        return "\n".join(out)

    # -- Blocktypen ---------------------------------------------------------
    def component(self) -> str:
        name, raw_attrs = RE_OPEN.match(self.line()).groups()
        self.i += 1
        body = self.take_until_close()
        render = COMPONENTS.get(name)
        if render is None:
            raise SystemExit(f"Unbekannte Komponente '::: {name}' — bekannt: {', '.join(sorted(COMPONENTS))}")
        return render(parse_attrs(raw_attrs), body, lambda lines: Parser(lines).render())

    def code(self) -> str:
        lang = self.line().strip()[3:].strip()
        self.i += 1
        body = []
        while not self.at_end() and not self.line().lstrip().startswith("```"):
            body.append(self.line())
            self.i += 1
        self.i += 1  # schließendes ```
        cls = f' class="language-{lang}"' if lang else ""
        return f"<pre><code{cls}>{html.escape(chr(10).join(body))}</code></pre>"

    def next_is_table_sep(self) -> bool:
        return self.i + 1 < len(self.lines) and bool(RE_TABLE_SEP.match(self.lines[self.i + 1]))

    def table(self) -> str:
        def cells(row: str) -> list[str]:
            return [c.strip() for c in row.strip().strip("|").split("|")]

        header = cells(self.line())
        aligns = []
        for spec in cells(self.lines[self.i + 1]):
            aligns.append("center" if spec.startswith(":") and spec.endswith(":") else "right" if spec.endswith(":") else "left")
        self.i += 2

        out = ["<table>", "<thead><tr>"]
        for cell, align in zip(header, aligns):
            out.append(f'<th class="ta-{align}">{inline(cell)}</th>')
        out.append("</tr></thead>")
        out.append("<tbody>")
        while not self.at_end() and self.line().lstrip().startswith("|"):
            out.append("<tr>")
            for cell, align in zip(cells(self.line()), aligns):
                out.append(f'<td class="ta-{align}">{inline(cell)}</td>')
            out.append("</tr>")
            self.i += 1
        out.append("</tbody></table>")
        return "".join(out)

    def list_(self) -> str:
        items: list[tuple[int, str, str]] = []  # (indent, marker, text)
        while not self.at_end() and (m := RE_BULLET.match(self.line())):
            items.append((len(m.group(1)), m.group(2), m.group(3)))
            self.i += 1
        return self.render_list(items, 0, 0)[0]

    def render_list(self, items, start: int, indent: int) -> tuple[str, int]:
        tag = "ol" if items[start][1] not in ("-", "*") else "ul"
        out, i = [f"<{tag}>"], start
        while i < len(items):
            level, _, text = items[i]
            if level < indent:
                break
            if level > indent:
                nested, i = self.render_list(items, i, level)
                if out[-1].endswith("</li>"):  # Unterliste gehört in das letzte <li>
                    out[-1] = out[-1][: -len("</li>")] + nested + "</li>"
                else:
                    out.append(nested)
                continue
            text, cls = fragment(text)
            out.append(f"<li{cls}>{inline(text)}</li>")
            i += 1
        out.append(f"</{tag}>")
        return "".join(out), i

    def heading(self) -> str:
        hashes, text = RE_HEADING.match(self.line()).groups()
        self.i += 1
        level = len(hashes)
        return f"<h{level}>{inline(text)}</h{level}>"

    def blockquote(self) -> str:
        body = []
        while not self.at_end() and self.line().lstrip().startswith(">"):
            body.append(self.line().lstrip()[1:].strip())
            self.i += 1
        return f"<blockquote>{inline(' '.join(body))}</blockquote>"

    def raw_html(self) -> str:
        body = []
        while not self.at_end() and self.line().strip():
            body.append(self.line())
            self.i += 1
        return "\n".join(body)

    def paragraph(self) -> str:
        body = []
        while not self.at_end() and self.line().strip() and not self.starts_block():
            body.append(self.line().strip())
            self.i += 1
        text, cls = fragment(" ".join(body))
        return f"<p{cls}>{inline(text)}</p>"

    def starts_block(self) -> bool:
        line = self.line()
        return bool(
            RE_OPEN.match(line)
            or RE_CLOSE.match(line)
            or RE_HEADING.match(line)
            or RE_BULLET.match(line)
            or line.lstrip().startswith(("```", "|", ">", "<"))
        )


# ------------------------------------------------------------------ deck ----

RE_META = re.compile(r"^@([\w-]+):\s*(.*)$")


def source_badge(key: str) -> str:
    """Quellenzeile einer Folie: Foto, Sprecher:in, verlinkter Talk-Titel."""
    talks = json.loads(TALKS_JSON.read_text()) if TALKS_JSON.exists() else {}
    talk = talks.get(key)
    if talk is None:
        raise SystemExit(f"Unbekannter Talk '@talk: {key}' — bekannt: {', '.join(sorted(talks))}")
    org = f' · {inline(talk["org"])}' if talk.get("org") else ""
    return (
        f'<a class="source" href="{talk["url"]}" target="_blank" rel="noopener">'
        f'<img class="source__photo" src="{SPEAKER_DIR}/{key}.jpg" alt="{talk["speaker"]}">'
        f'<span class="source__text">'
        f'<span class="source__name">{inline(talk["speaker"])}{org}</span>'
        f'<span class="source__talk">{inline(talk["title"])}</span>'
        f"</span></a>"
    )


def render_slide(source: str) -> str:
    """Eine Folie: optionale '@key: value'-Kopfzeilen + Markdown-Inhalt."""
    lines = source.split("\n")
    meta: dict[str, str] = {}
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and (m := RE_META.match(lines[0].strip())):
        meta[m.group(1)] = m.group(2).strip()
        lines.pop(0)

    classes = ["slide", f'slide--{meta.get("layout", "default")}']
    if "class" in meta:
        classes.append(meta["class"])
    badge = ""
    if "talk" in meta:
        classes.append("has-source")
        badge = "\n" + source_badge(meta["talk"])
    attrs = f' data-background-color="{meta["bg"]}"' if "bg" in meta else ""

    # .slide__inner trägt das Layout: Reveal setzt auf <section> ein inline
    # 'display: block', ein innerer Container bleibt davon unberührt.
    body = Parser(lines).render()
    return (
        f'<section class="{" ".join(classes)}"{attrs}>\n'
        f'<div class="slide__inner">\n{body}\n</div>{badge}\n'
        f"</section>"
    )


def render_deck(markdown: str) -> str:
    slides = [s for s in re.split(r"^---\s*$", markdown, flags=re.M) if s.strip()]
    return "\n\n".join(render_slide(s) for s in slides)


# ----------------------------------------------------------------- build ----

RE_INCLUDE = re.compile(r"{{>\s*([\w-]+)\s*}}")
RE_VAR = re.compile(r"{{\s*([\w-]+)\s*}}")


def expand(template: str, values: dict[str, str]) -> str:
    template = RE_INCLUDE.sub(lambda m: (PARTIALS / f"{m.group(1)}.html").read_text(), template)
    return RE_VAR.sub(lambda m: values.get(m.group(1), m.group(0)), template)


def build() -> int:
    config = json.loads(DECK_JSON.read_text())
    slides = render_deck(SLIDES_MD.read_text())
    values = {**{k: str(v) for k, v in config.items()}, "slides": slides}
    # Partials dürfen selbst Variablen enthalten -> zweimal expandieren.
    OUTPUT.write_text(expand(expand(TEMPLATE.read_text(), values), values))
    count = slides.count("<section")
    print(f"✅ {OUTPUT.name}: {count} Folien")
    return count


def serve(port: int = 8000) -> None:
    import http.server
    import socketserver

    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(ROOT), **kw)
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"→ http://localhost:{port}  (Strg+C beendet)")
        httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="nach dem Bauen lokal servieren")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    build()
    if args.serve:
        serve(args.port)
