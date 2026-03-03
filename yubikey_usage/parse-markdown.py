#!/usr/bin/env python3
"""
Parse yubikey.md und konvertiere zu reveal.js HTML sections
"""

import re
import sys


def parse_markdown(input_file):
    with open(input_file, "r") as f:
        content = f.read()

    # An --- aufteilen
    slides = content.split("\n---\n")

    output = []
    first_slide = True

    for slide in slides:
        if not slide.strip():
            continue

        # Section öffnen
        if first_slide:
            output.append("            <!-- Titel -->")
            output.append('            <section class="title-slide">')
            first_slide = False
        else:
            output.append("            <section>")

        # Zeilen verarbeiten
        lines = slide.split("\n")
        in_code = False
        code_lang = ""
        in_table = False
        table_lines = []
        in_list = False
        list_lines = []
        in_html_tag = False

        # Inline Markdown konvertieren (Bold, Italic, Links)
        def convert_inline_markdown(text):
            # Markdown Links: [text](url)
            text = re.sub(
                r"\[([^\]]+)\]\(([^\)]+)\)",
                r'<a href="\2" target="_blank" style="color: #1976D2; text-decoration: none;">\1</a>',
                text,
            )
            # Bold: **text** oder __text__
            text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
            text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
            # Italic: *text* oder _text_ (aber nicht in URLs)
            text = re.sub(r"(?<!\w)\*([^\*]+?)\*(?!\w)", r"<em>\1</em>", text)
            text = re.sub(r"(?<!\w)_([^_]+?)_(?!\w)", r"<em>\1</em>", text)
            return text

        i = 0
        while i < len(lines):
            line = lines[i]
            # Code-Block Start
            if line.startswith("```"):
                if not in_code:
                    # Code-Block öffnen
                    code_lang = line[3:].strip()  # Sprache extrahieren
                    if code_lang:
                        output.append(
                            f'                <pre><code class="{code_lang}">'
                        )
                    else:
                        output.append("                <pre><code>")
                    in_code = True
                else:
                    # Code-Block schließen
                    output.append("                </code></pre>")
                    in_code = False
                    code_lang = ""
                i += 1
                continue

            # Im Code-Block: unverändert
            if in_code:
                output.append("                " + line)
                i += 1
                continue

            # Tabellen erkennen (Zeile startet mit |)
            if line.strip().startswith("|") and not in_table:
                # Prüfe ob nächste Zeile Separator ist
                if i + 1 < len(lines) and re.match(
                    r"^\s*\|[-\s|]+\|\s*$", lines[i + 1]
                ):
                    in_table = True
                    table_lines = [line, lines[i + 1]]
                    i += 2
                    continue

            # In Tabelle: Zeilen sammeln
            if in_table:
                if line.strip().startswith("|"):
                    table_lines.append(line)
                    i += 1
                    continue
                else:
                    # Tabelle beendet, HTML generieren
                    output.append(
                        '                <table style="font-size: 0.85em; border-collapse: collapse; width: 90%; margin: 1em auto;">'
                    )

                    # Header-Zeile
                    header_cells = [
                        cell.strip() for cell in table_lines[0].split("|")[1:-1]
                    ]
                    output.append("                    <thead>")
                    output.append("                        <tr>")
                    for cell in header_cells:
                        cell_content = convert_inline_markdown(cell)
                        output.append(
                            f'                            <th style="border: 1px solid #ddd; padding: 0.6em; background: rgba(0,0,0,0.05); text-align: left;">{cell_content}</th>'
                        )
                    output.append("                        </tr>")
                    output.append("                    </thead>")

                    # Daten-Zeilen (ab Index 2, da 0=Header, 1=Separator)
                    output.append("                    <tbody>")
                    for row in table_lines[2:]:
                        cells = [cell.strip() for cell in row.split("|")[1:-1]]
                        output.append("                        <tr>")
                        for cell in cells:
                            cell_content = convert_inline_markdown(cell)
                            output.append(
                                f'                            <td style="border: 1px solid #ddd; padding: 0.6em;">{cell_content}</td>'
                            )
                        output.append("                        </tr>")
                    output.append("                    </tbody>")
                    output.append("                </table>")

                    in_table = False
                    table_lines = []
                    # Aktuelle Zeile nicht überspringen, weiter verarbeiten

            # Listen erkennen (Zeile startet mit -, *, oder Nummer)
            if (
                re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line)
            ) and not in_list:
                in_list = True
                list_lines = [line]
                i += 1
                continue

            # In Liste: Zeilen sammeln
            if in_list:
                if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
                    list_lines.append(line)
                    i += 1
                    continue
                else:
                    # Liste beendet, HTML generieren
                    # Prüfe ob unordered oder ordered
                    is_ordered = re.match(r"^\s*\d+\.\s+", list_lines[0])

                    if is_ordered:
                        output.append(
                            '                <ol style="text-align: left; margin: 0.5em auto; max-width: 90%;">'
                        )
                    else:
                        output.append(
                            '                <ul style="text-align: left; margin: 0.5em auto; max-width: 90%;">'
                        )

                    for item in list_lines:
                        # Entferne List-Marker (-, *, oder 1.)
                        item_text = re.sub(r"^\s*[-*]\s+", "", item)
                        item_text = re.sub(r"^\s*\d+\.\s+", "", item_text)
                        item_content = convert_inline_markdown(item_text)
                        output.append(f"                    <li>{item_content}</li>")

                    if is_ordered:
                        output.append("                </ol>")
                    else:
                        output.append("                </ul>")

                    in_list = False
                    list_lines = []
                    # Aktuelle Zeile nicht überspringen, weiter verarbeiten

            # HTML passthrough - Mehrzeilige HTML-Tags erkennen
            if line.strip().startswith("<") and not line.strip().startswith("</"):
                # Prüfe ob Tag auf derselben Zeile geschlossen wird
                if not line.rstrip().endswith(">"):
                    # Mehrzeiliges HTML-Tag beginnt
                    in_html_tag = True
                output.append("                " + line)
                i += 1
                continue

            # In mehrzeiligem HTML-Tag
            if in_html_tag:
                output.append("                " + line)
                # Prüfe ob Tag geschlossen wird
                if line.rstrip().endswith(">"):
                    in_html_tag = False
                i += 1
                continue

            # HTML passthrough (schließende Tags)
            if line.strip().startswith("</"):
                output.append("                " + line)
                i += 1
                continue

            # Markdown zu HTML
            # H1
            match = re.match(r"^# (.+)$", line)
            if match:
                output.append(f"                <h1>{match.group(1)}</h1>")
                i += 1
                continue

            # H2
            match = re.match(r"^## (.+)$", line)
            if match:
                output.append(f"                <h2>{match.group(1)}</h2>")
                i += 1
                continue

            # H3
            match = re.match(r"^### (.+)$", line)
            if match:
                output.append(f"                <h3>{match.group(1)}</h3>")
                i += 1
                continue

            # Warnung-Boxen erkennen
            if line.strip().startswith("⚠️"):
                processed_line = convert_inline_markdown(line)
                output.append(
                    f'                <div style="background: rgba(255, 193, 7, 0.1); border-left: 4px solid #FFC107; padding: 0.8em 1em; margin: 0.5em 0; border-radius: 4px;">{processed_line}</div>'
                )
                i += 1
                continue

            # Normale Textzeilen (nicht-leer) als Absätze
            if line.strip():
                processed_line = convert_inline_markdown(line)
                output.append(f"                <p>{processed_line}</p>")
            else:
                output.append("")

            i += 1

        # Am Ende: Offene Listen schließen
        if in_list and list_lines:
            is_ordered = re.match(r"^\s*\d+\.\s+", list_lines[0])

            if is_ordered:
                output.append(
                    '                <ol style="text-align: left; margin: 0.5em auto; max-width: 90%;">'
                )
            else:
                output.append(
                    '                <ul style="text-align: left; margin: 0.5em auto; max-width: 90%;">'
                )

            for item in list_lines:
                item_text = re.sub(r"^\s*[-*]\s+", "", item)
                item_text = re.sub(r"^\s*\d+\.\s+", "", item_text)
                item_content = convert_inline_markdown(item_text)
                output.append(f"                    <li>{item_content}</li>")

            if is_ordered:
                output.append("                </ol>")
            else:
                output.append("                </ul>")

        # Section schließen
        output.append("            </section>")

    return "\n".join(output)


if __name__ == "__main__":
    result = parse_markdown("yubikey.md")
    print(result)
