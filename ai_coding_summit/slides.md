@layout: title

<img class="mark" src="assets/summit-bolt.png" alt="AI Coding Summit">

# AI Coding Summit London
## See how AI transforms software development

Tobias Kabbeck · 6.–7. Juli 2026 · London, UK & Online

---

@layout: default

## Inhalt

::: steps
- Einstieg — die Größenordnung: das ist kein Experiment mehr
- Stand der Technik — drei Stufen und was den Schwarm kollabieren lässt
- Skills — wiederverwendbare Anleitungen und ihre Grenzen
- Orchestrierung — wie das bei 527 Repos aussieht
- Verifikation — wer prüft, und warum grüne Checks nicht genügen
- Die dunkle Seite — Vergiftung und Drift
- Schluss — vier Beobachtungen, die sich durch alle Talks ziehen
:::

---

@layout: section

#### Teil 1
## Einstieg

Code schreiben ist billig geworden. Vertrauen nicht.

---

@layout: default
@class: wide
@talk: alberts

#### Jodan Alberts hat auf öffentlichem GitHub den Trailer `Co-Authored-By: Claude` ausgezählt
## 45 Millionen Commits. Interessant sind 8 Millionen davon.

::: stats
- 45 Mio. | signierte Commits seit Februar 2025, in 2,4 Mio. Repositories
- 8 Mio. | davon in Repos mit mindestens zwei Sternen
- 400.000 | neue signierte Commits pro Tag
:::

::: warn title="Warum die Sternzahl hier die eigentliche Kennzahl ist"
Zwei Sterne heißt: mindestens ein anderer Mensch hat das Repo nützlich gefunden.
Anfangs lagen über 90 % aller Claude-Commits unter dieser Schwelle — Lern- und
Wegwerfprojekte. Der Anteil sinkt. Die Gesamtmenge ist also kein Beleg. Die
8 Millionen sind einer.
:::

::: links
- Alberts' Dashboard — läuft weiter, Zahlen live | https://www.claudescode.dev
:::

---

@layout: default
@class: wide
@talk: alberts

#### Sechs Kategorien über 2.500 Commits: Bugfixes, Features, Doku, Refactoring, Tests, UI
## In ernsthaften Repos übernimmt Claude die Wartungslast

::: grid cols=2
::: card icon="🧹" title="Wartungslast wandert ab" tone=green
In Nicht-KI-Projekten überwiegen Bugfixes — die Arbeit, die niemand freiwillig
macht. Nur KI-Projekte selbst setzen Claude überwiegend für Features ein.
:::
::: card icon="🎨" title="UI ist die kleinste Kategorie" tone=amber
Vorsicht bei der Deutung: Sein Sample sind die meistgesternten Repos — Deno, Bun,
Home Assistant. Seine eigene Erklärung: In UI und UX sind Designer und
Entwickler noch stärker selbst beteiligt.
:::
:::

::: note title="Zwei Repos, zwei Nutzungsmuster"
**Apache Superset** ließ Claude vor allem die TypeScript-Qualität von menschlich
geschriebenem Code aufräumen. **ClickHouse** committet im gleichen Zeitraum
zehnmal so viel — fast alles CI, Tests, Infrastruktur, damit die Engineers an
Features arbeiten können.
:::

---

@layout: section

#### Teil 2
## Stand der Technik

Vom Prompt zum System — und woran die Zwischenstufen scheitern.

---

@layout: default
@class: wide
@talk: novick

#### Vladimir Novick hat drei Stufen durchlaufen — jede fühlte sich wie Fortschritt an
## Drei Stufen, drei Sollbruchstellen

::: grid cols=3
::: card icon="📝" title="Prompts" tone=amber
Zustandslos, jede Session fängt bei null an.

Den Kontext trägt **der Mensch** von Fenster zu Fenster.
:::
::: card icon="🧭" title="Single-Agent" tone=violet
Verliert im langen Thread den Faden.

Und **niemand prüft ihn** außer er selbst.
:::
::: card icon="🐝" title="Naiver Schwarm" tone=red
Kollabiert am schnellsten.

Fehler heben sich nicht auf, sie **multiplizieren sich** bei jeder Übergabe.
:::
:::

::: danger title="Verkettete Zuverlässigkeit: 95 % → 77 % → 36 %"
Novicks Reihe für immer längere Ketten. Fehler heben sich nicht gegenseitig auf,
sie multiplizieren sich — jede weitere Übergabe drückt das Ergebnis. Das gilt für
jede mehrstufige Kette; der Schwarm hat nur die meisten Übergaben.
:::

::: links
- Warum Multi-Agent-Systeme scheitern: MAST-Studie, UC Berkeley | https://arxiv.org/abs/2503.13657
:::

---

@layout: default
@class: wide
@talk: novick

#### Seine Antwort auf den Kollaps: einer besitzt den Kontext, Worker melden zurück
## Nicht besser prompten — ein System bauen, das prüft

::: grid cols=3
::: card icon="⚖️" title="Architektur ist Gesetz" tone=accent
Contracts und Grenzen werden **mechanisch erzwungen** — über Typen, Linting,
Tests. Nicht per Absprache in einer Regeldatei.
:::
::: card icon="🔀" title="Kontext ist ein Protokoll" tone=green
Kein großer Prompt, sondern **strukturierte Übergaben**, die den einzelnen Lauf
überdauern. Worker arbeiten isoliert.
:::
::: card icon="🚦" title="Fertig ist messbar" tone=violet
„Fertig" entscheidet, **was nicht halluzinieren kann**: Tests, Types, Lint,
Build. Nie die Aussage eines Modells.
:::
:::

::: tip title="Nicht Multi-Agent ist das Problem, sondern der unstrukturierte Schwarm"
Nur die Struktur zu ändern — gleiches Modell — brachte in Coding- und
Reasoning-Benchmarks 12 bis 23 % mehr.
:::

::: links
- Novicks Spec, offen | https://github.com/vnovick/orchestrated-coding
- Seine Implementierung davon | https://github.com/vnovick/itervox
:::

---

@layout: default
@class: wide
@talk: novick

#### Vier Reifegrade — der Unterschied ist nicht das Werkzeug
## Wer darf entscheiden, dass etwas fertig ist?

| Stufe | „Fertig" entscheidet | Im Alltag heißt das |
|-------|----------------------|---------------------|
| **L0** assistiert | der Mensch | Agent schreibt, Mensch liest und merged jede Änderung |
| **L1** orchestriert | der Mensch | System verteilt und übergibt geordnet — reviewt wird weiter alles |
| **L2** governed | das Gate | unabhängiges Review plus grüne Checks, dann landet es von selbst |
| **L3** resilient | das Gate | System pausiert bei Unklarheit, fragt nach, nimmt selbst wieder auf |

::: note title="Der Sprung von L1 nach L2 ist keine Anschaffung"
Zwischen den ersten beiden Zeilen und den letzten beiden liegt kein Werkzeug,
sondern eine Entscheidung: ob wir einem automatischen Gate zutrauen, für uns zu
entscheiden. Alles darüber setzt voraus, dass das Gate wirklich prüft.
:::

---

@layout: section

#### Teil 3
## Skills

Wiederverwendbare Anleitungen statt immer neuer Prompts.

---

@layout: default
@class: wide
@talk: gechev

#### Minko Gechev, Google: „Diese Skills sind nicht für Menschen, sie sind für Agenten"
## Eine Anleitung, kein Aufsatz

::: grid cols=2
::: card icon="📚" title="Doku für Menschen" tone=amber
Erklärt Zusammenhänge, begründet Entscheidungen, arbeitet mit Analogien und
Beispielen.

Ein Agent braucht davon fast nichts.
:::
::: card icon="🔧" title="Skill für Agenten" tone=green
Sagt Schritt für Schritt, was zu tun ist. Drei Teile: `SKILL.md`,
deterministische Scripts, Referenzdateien.

Nachladen statt vorhalten.
:::
:::

::: tip title="Sein schärfstes Beispiel: Prosa durch ein Script ersetzen"
„Prüfe erst, ob npm installiert ist, suche dann die Pakete …" — jede Zeile Prosa
kann mehrere Tool-Calls und je eine Runde zurück zum Modell bedeuten. Dieselben
Schritte als Script: ein Aufruf, deterministisch, und testbar.
:::

::: links
- Seine Folien, alle 40 | https://mgechev.github.io/skill-design-for-llm-agents-slides/
:::

---

@layout: default
@class: wide
@talk: avila

#### Drei Ebenen, gestaffelt danach, was sie an Kontext kosten
## Was gehört wohin?

::: grid cols=3
::: card icon="📌" title="CLAUDE.md" tone=amber
Geht bei **jedem** Request mit. Also: Stack und ein paar Regeln, sonst nichts.
:::
::: card icon="♻️" title="Skill" tone=green
Greift **nur, wenn er gebraucht wird**, bleibt dann in der Session und lädt
Referenzen nach.
:::
::: card icon="🧵" title="Sub-Agent" tone=violet
**Eigener Kontext** für Aufgaben, die den Hauptthread sonst zumüllen.
:::
:::

::: tip title="Ávilas Kniff: lesen lassen oder ausführen lassen"
Eine Referenzdatei **lesen lassen** heißt: sie steht vollständig im Kontext. Ein
Script **ausführen** lassen und nur die Ausgabe lesen kostet fast nichts.
:::

::: links
- Seine Komponentensammlung zum Stöbern | https://aitmpl.com
- Claude Code Templates, Open Source | https://github.com/davila7/claude-code-templates
:::

---

@layout: default
@class: wide
@talk: gechev

#### Auch ungenutzte Skills kosten Kontext — ihre Beschreibung liegt dauerhaft drin
## Wie viele Skills verträgt ein Setup?

::: stats
- 20–30 | idealer Bereich, unter 50 bleiben
- ~200 | ab hier sinkt die Genauigkeit merklich
- 500 | spätestens hier muss aufgeräumt werden
:::

::: warn title="Gechevs Antwort: Unit-Tests für Skills"
Skill-Ordner wachsen nicht geplant, sie wachsen nebenbei. Sein Tool SkillGrade
erzeugt aus einer Skill-Datei automatisch Evaluationen und fährt Smoke-Tests. Im
Trajectory-Log sieht man dann, an welcher Stelle der Agent falsch abgebogen ist —
sein Beispiel: ein Skill bestand 4 von 5 Läufen, es fehlten zwei Anweisungen.
:::

::: links
- SkillGrade, Open Source | https://github.com/mgechev/skillgrade
:::

---

@layout: default
@class: wide
@talk: korop

#### Povilas Korop: 18 Modelle, 5 Projekte, 5 Läufe — ausgewertet per Tests, nicht per LLM-Urteil
## Modellwahl nach Aufgabentyp

| Aufgabe | Modell | Warum |
|---------|--------|-------|
| Planen, Architektur, harte Analyse | **Opus**, **Fable** oder **GPT** | teuer — aber hier entscheidet sich alles |
| Umsetzung nach Plan | ein **günstigeres** Modell, er nennt Composer 2.5 | Fleißarbeit mit klarer Vorgabe |
| Review | ein **anderes** Modell als beim Schreiben | siehe Teil 5 |
| Routine, z. B. Commit-Nachrichten | **Haiku**, niedriger Effort | Ávilas Empfehlung, nicht Korops |

::: note title="Zwei Befunde, die länger halten als jede Modellrangliste"
Offizielle Benchmarks wie SWE-Bench werden von Modellen inzwischen erkannt und
bedient — für Alltagsaufgaben sagen sie wenig. Und am Ende entscheidet der ganze
Harness: IDE, Skills, Prompts, Guardrails. Nicht das Modell allein.
:::

::: links
- Sein Benchmark, laufend aktualisiert | https://aicodingdaily.substack.com
:::

---

@layout: default

#### Skill-Hygiene
## Vier Fragen, die jedes Setup irgendwann einholen

::: steps
- Bestand — welche Skills existieren, und wer weiß davon
- Nutzung — welche greifen im Alltag, welche nie
- Prüfung — woran wird sichtbar, dass ein Skill schlechter geworden ist
- Pflege — wer entfernt, was niemand mehr benutzt
:::

---

@layout: section

#### Teil 4
## Orchestrierung in der Praxis

---

@layout: default
@class: wide
@talk: leimonis

#### Konstantinos Leimonis betreut die Plattform hinter über 500 Micro-Frontends
## Eine Node-Migration über 527 Repositories

::: stats
- 527 | Repositories, ein Versionssprung
- 87 % | liefen ohne jeden menschlichen Eingriff durch
- 3 statt 6 | Monate — das System selbst brauchte davon ein paar
:::

::: note title="Warum kein Codemod"
Ein Umschreibe-Skript löst die vorhersehbare Mehrheit und scheitert am
unübersichtlichen Rest — und behauptet dabei, die Migration sei fertig. Genau
dieser Rest entscheidet. Also bauten sie stattdessen ein System aus parallel
laufenden Agenten — und das läuft nach der Migration weiter: für den nächsten
Versionssprung, den nächsten Lint-Rollout.
:::

---

@layout: default
@class: wide
@talk: leimonis

#### Der Orchestrator ist eine Schleife, die alle paar Stunden über ein Board läuft
## Woran das System hängt

::: grid cols=2
::: card icon="📋" title="Das Board ist der Vertrag" tone=accent
Agenten reden nie miteinander. Jeder liest festgelegte Zeilen, erledigt eine
Aufgabe, schreibt zurück, stoppt.
:::
::: card icon="⚙️" title="Skript oder Modell, nie beides" tone=green
Version hochziehen, Lockfile, Tests: Skript, kostet nichts — und rät im Zweifel
nicht, sondern hält an. Nur das Reparieren braucht ein Modell.
:::
::: card icon="📏" title="Baseline vor Migration" tone=violet
Vorher bauen und testen, festhalten was schon kaputt war. Repariert wird nur, was
die Migration neu zerbricht.

**Ohne Tests keine Baseline, ohne Baseline keine Autonomie.**
:::
::: card icon="🔒" title="Der Loop hat ein Ende" tone=amber
Günstiges Modell zuerst, teures höchstens zweimal, dann „stuck" — und das Board
zeigt, bei welchem Schritt.
:::
:::

---

@layout: default
@class: wide
@talk: iatsko

#### Valerii Iatsko, Google — dasselbe Prinzip, eine Nummer kleiner
## Ein Loop ist vier Dateien und ein Script

::: grid cols=2-1
::: pane
```text
spec.md       was am Ende dastehen soll — vorab geschrieben,
              nicht im Loop
plan.md       die Schritte dorthin, laufend gegen die Spec
              abgeglichen — das Herz des Ganzen
agents.md     Ausführungsregeln für die Agenten
progress.md   wo der Loop gerade steht
loop.sh       liest alles und läuft
```
:::
::: pane tone=sunken
#### Drei Bedingungen
Wiederkehrend · überprüfbar · begrenzt

#### Eine Regel
Tests bleiben **read-only**.
:::
:::

::: danger title="Was passiert, wenn die dritte Bedingung fehlt"
Ein Team ließ über Nacht sechs Projekte bauen — 50.000 $ Budget, 800 $
verbraucht. Der Refactoring-Loop danach lieferte **einen PR mit 20.000
Zeilen und 1.600 To-dos**. Nicht gemergt, für einen Menschen nicht verifizierbar.
:::

::: links
- Woher der Begriff kommt: Addy Osmani, Juni 2026 | https://addyosmani.com/blog/loop-engineering/
:::

---

@layout: section

#### Teil 5
## Verifikation

Wer prüft, womit — und warum grüne Checks nicht genügen.

---

@layout: default
@class: wide
@talk: sogl

## Wie viel davon ist überhaupt noch unser Code?

::: stats
- 42 % | KI-generiert oder KI-unterstützt, laut Sonar-Umfrage
- ~90 % | Sogls eigene Schätzung aus Kundenprojekten
:::

::: warn title="Daniel Sogl"
Die 42 % sind Selbstauskunft von Entwickler:innen, erhoben von einem Anbieter,
der in dem Feld Produkte verkauft — mit Vorsicht zu lesen. Denselben Befund
zeigen die anderen Zahlen, die er zitiert: Review-Zeiten explodieren und 31 %
werden ganz ohne Review gemergt (Faros AI), Incidents nehmen zu (Googles
DORA-Report). Dazu Code Churn — Code, den man direkt nach dem Merge wieder
anfassen muss.
:::

::: links
- Die Umfrage selbst, 1.100 Entwickler:innen — zum Nachprüfen | https://www.sonarsource.com/state-of-code-developer-survey-report.pdf
:::

---

@layout: default
@class: wide
@talk: sogl

## Wer prüft, darf nicht derselbe sein

::: steps
- Deterministisch zuerst — Linter, Typen, Tests, Hooks. Günstig, schnell, verlässlich
- Dann Sub-Agents im Loop — Feedback über Hooks, während der Agent noch arbeitet
- Dann PR-Services — hilfreich, aber Vorsicht vor Lärm
:::

::: warn title="Zwei Trennungen: anderes Modell, andere Session"
Nicht das Modell, das den Code geschrieben hat — und nicht die Session, in der
er entstanden ist. Ebenso wenig taugen KI-generierte Tests für bestehenden Code:
die bestätigen nur den Status quo.
:::

---

@layout: default
@class: wide
@talk: waardenburg

## Die vierte Prüfebene: strukturelle Drift

::: grid cols=1-2
::: pane tone=sunken
#### Üblich sind drei Ebenen
Typen · Linting · Tests

#### Was keine davon sieht
Der Code ist gültig und passt trotzdem nicht mehr zum Rest des Systems. Toter
Code, Duplizierung, Grenzverletzungen.
:::
::: pane
```bash
# In CLAUDE.md: eine Bitte, die niemand prüft
"Bitte immer die bestehenden Utils verwenden"

# Als Hook vor git commit: eine Bedingung
fallow audit --gate new-only
  → Pass / Warn / Fail
  → nur geänderte Dateien
  → neue Verstöße blockieren
  → geerbte Verstöße nur melden
```

::: links
- fallow — statische Analyse, Open Source | https://github.com/fallow-rs/fallow
:::
:::
:::

::: tip title="Für die vierte Ebene reicht keine Regeldatei"
Waardenburgs Bild: Eine Regeldatei ist die Sicherheitsansage im Flugzeug —
wichtige Information, ohne Garantie, dass jemand zuhört. Anthropics Doku sagt es
trockener: CLAUDE.md kommt als User-Message, ohne Garantie auf strikte Befolgung.
Was an einem festen Punkt laufen muss, gehört in einen Hook.
:::

---

@layout: center
@talk: novick

## Ein Gate, das nicht prüft, ist schlimmer als keins

Man übernimmt seinen blinden Fleck — und hört auf, selbst hinzusehen. Novick
schätzt rund 70 % der Fehler auf grüne Checks, die nichts geprüft haben.

---

@layout: default
@class: wide
@talk: pierzchala

#### Mobile QA: Der Diff ist lesbar, das CI grün — und die App auf dem Gerät kaputt
## Der Merge-Button ist eine Vertrauensentscheidung

::: stats
- 90 Mio. | gemergte PRs pro Monat, +100 % im Jahr
- ≤ 60 % | der Bugs findet ein Mensch — und nur als Expert:in, unter 200 Zeilen Diff
:::

::: grid cols=2
::: card icon="🙈" title="Im Diff unsichtbar" tone=amber
Die eingeblendete Tastatur verdeckt den Absenden-Button. Der Release-Build
stürzt ab, der Debug-Build lief.
:::
::: card icon="📱" title="App Behavior Review" tone=green
Ein Agent auf Simulator oder echtem Gerät, enge Mission aus den PR-Metadaten.
Screenshots als Beleg im PR.
:::
:::

::: links
- agent-device — sein CLI dafür, Open Source | https://github.com/callstack/agent-device
:::

---

@layout: section

#### Teil 6
## Die dunkle Seite

---

@layout: default
@class: wide
@talk: kutsenko

#### Was ein Agent aus Logs, Events und Tool-Ergebnissen liest, prüft er nicht nach
## Man muss das Modell nicht angreifen — nur seine Datenquelle

::: grid cols=2
::: card icon="🔌" title="Warum das funktioniert" tone=red
Ein Agent glaubt seinen Werkzeugen. Dieselbe Falschinformation als Text im
Prompt: **zu 0 % übernommen**. Als Ergebnis eines echten Tool-Aufrufs:
**zu 100 %**.
:::
::: card icon="🌊" title="Wo angesetzt wird" tone=amber
Überall, wo jemand in den Datenstrom schreiben kann. Ihr Beispiel: ein Konto
über längere Zeit mit kleinen, unauffälligen Buchungen normal aussehen lassen —
dann die eigentliche Betrugstransaktion.
:::
:::

::: warn title="Ihre Antwort: den eigenen Datenstrom als ungeprüfte Eingabe behandeln"
Data Contracts statt reinem Schema-Check — also Wertebereiche und Fachregeln,
nicht nur „Feld ist eine Zahl". Dazu Lineage: nachvollziehbar halten, woher ein
Wert stammt und was ihn unterwegs verändert hat.
:::

::: links
- Auch das Training ist billig zu vergiften: 250 Dokumente genügen | https://www.anthropic.com/research/small-samples-poison
:::

---

@layout: default
@class: wide
@talk: komesarook

#### Drift: Der Agent läuft erfolgreich durch — und tut trotzdem nicht das Gemeinte
## Kein Absturz, kein Stacktrace, keine Fehlermeldung

::: grid cols=3
::: card icon="🧩" title="Warum es schwer zu finden ist" tone=amber
Ein Compile-Fehler zeigt die Stelle. Drift ist ein Laufzeitfehler — man muss den
ganzen Lauf nachvollziehen.
:::
::: card icon="🔬" title="Womit man es sichtbar macht" tone=violet
Traces und Spans statt Logs: ein Lauf ist ein Trace, jeder Schritt ein Span mit
Modell, Tokens, Latenz.
:::
::: card icon="🎯" title="Wo die Ursache fast immer liegt" tone=green
Im Kontextfenster genau dieses Moments. Erst dort nachsehen, dann übers
Modelltauschen nachdenken.
:::
:::

::: note title="Bei tausend Läufen liest niemand mehr mit"
Dann werden Läufe geclustert und nach Verhaltensmustern gruppiert — etwa
ineffiziente Token-Nutzung oder Nutzer, die im Verlauf zunehmend genervt
reagieren. Nur für geschäftskritisches Verhalten lohnt ein Echtzeit-Signal.
:::

---

@layout: section

#### Teil 7
## Schluss

---

@layout: default
@class: wide

## Vier Beobachtungen, die sich durch alle Talks ziehen

::: steps
- Vom Prompt zum System — die Arbeit verschiebt sich vom Formulieren zum Bauen von etwas, das Code erzeugt und prüft
- Kontext ist die knappe Ressource — nicht die Modellgröße begrenzt, sondern was im Fenster steht
- Der Flaschenhals ist die Prüfung — Erzeugen ist billig geworden, Verifizieren nicht
- Verbindlich ist nur, was erzwungen wird — Tests, Typen, Hooks, Gates. Bitten in einer Regeldatei reichen nicht
:::

::: note title="Bemerkenswert ist die Übereinstimmung"
Keiner dieser Punkte kam von einem einzelnen Sprecher — sie tauchten unabhängig
voneinander auf, in Talks über Skills, Migrationen, Review und Sicherheit. Und
keiner davon nennt ein Werkzeug als Antwort.
:::

---

@layout: end

## Fragen?

Vielen Dank für die Aufmerksamkeit.

Tobias Kabbeck · [tobias.kabbeck@zeit.de](mailto:tobias.kabbeck@zeit.de)
