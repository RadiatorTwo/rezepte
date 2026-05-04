---
name: add-recipe
description: Nimmt einen Rezepttext in beliebiger Form/Sprache entgegen, übersetzt ihn bei Bedarf ins Deutsche, erstellt nach der Vorlage in source/markdown/VORLAGE.md eine neue Rezeptdatei, trägt sie in source/markdown/index.md unter der passenden Gruppe ein und gibt am Ende den benötigten Bild-Dateinamen zurück. Verwende diesen Skill wenn der Benutzer ein neues Rezept hinzufügen möchte.
---

# add-recipe

Erstelle aus einem beliebigen Rezepttext (in beliebiger Sprache und Form) ein neues Rezept im Projekt-Format.

## Eingabe

Der Benutzer übergibt den vollständigen Rezepttext als Argument oder im Prompt. Der Text kann in einer Fremdsprache vorliegen, schlecht strukturiert sein oder nur als Mengenliste mit Beschreibung kommen.

## Ablauf

Führe die Schritte exakt in dieser Reihenfolge aus.

### 1. Rezept verstehen und ins Deutsche übersetzen

- Lies den übergebenen Rezepttext vollständig.
- Falls der Text nicht in deutscher Sprache vorliegt, übersetze **alle** Inhalte (Titel, Zutaten, Mengen, Zubereitungsschritte, Notizen) ins Deutsche.
- Mengenangaben werden in metrische Einheiten umgerechnet (g, ml, EL, TL, Stück). Behalte sinnvolle Originalformulierungen wenn passend (z. B. "1 Dose Mais", "1 Prise Salz").
- Stelle sicher, dass jede Zutat mit korrekter Menge erfasst ist. Wenn die Quelle Mengen für mehrere Portionen angibt, übernimm die Originalangabe und vermerke die Portionenzahl.

### 2. Vorlage lesen

Lies vor dem Schreiben **immer** die aktuelle Vorlage:

```
source/markdown/VORLAGE.md
```

Halte dich exakt an deren Struktur:

- `# Rezeptname` als Überschrift
- Bild-Zeile: `![](https://radiatortwo.github.io/rezepte/pics/<bilddatei>.jpg)`
- `Portionen: <n>`
- `## Zutaten` mit optionalen Untergruppen `### Hauptzutaten`, `### Für die Sauce` etc.
- `## Zubereitung` mit optionalen Untergruppen passend zu den Zutatengruppen
- Optional `## Notizen`
- Innerhalb von Zutaten- und Zubereitungslisten werden Zeilen mit einem Backslash `\` am Zeilenende getrennt (Markdown-Hardbreak), wie in der Vorlage. Die letzte Zeile eines Blocks erhält **keinen** Backslash.
- Zwischen Abschnitten (Überschriften, Absätzen) eine Leerzeile.

Wenn das Rezept nur einen einzigen Zutaten- bzw. Zubereitungsblock hat, dürfen die `### …`-Untergruppen entfallen (siehe z. B. `GrueneBohnenHackfleischPfanne.md`). Der Rest der Struktur bleibt jedoch identisch zur Vorlage.

### 3. Dateinamen für Rezept und Bild bestimmen

- **Rezept-Dateiname**: PascalCase ohne Leerzeichen, ohne Umlaute (`ä→ae`, `ö→oe`, `ü→ue`, `ß→ss`), ohne Sonderzeichen, Endung `.md`. Beispiele: `KartoffelSuppe.md`, `BangBangShrimp.md`, `GrueneBohnenHackfleischPfanne.md`.
- **Bild-Dateiname**: Kleinbuchstaben, Wörter durch Bindestriche getrennt, ohne Umlaute/Sonderzeichen, Endung `.jpg`. Beispiel: `gruene-bohnen-hackfleisch-pfanne.jpg`.
- Vor dem Schreiben mit `Glob` prüfen, ob der Rezept-Dateiname unter `source/markdown/` bereits existiert. Falls ja, hänge eine sinnvolle Unterscheidung an (z. B. Variante, Stilrichtung) — nicht einfach Zahlen.

### 4. Rezeptdatei schreiben

Schreibe die Datei unter:

```
source/markdown/<RezeptDateiname>.md
```

Inhalt strikt nach Vorlage. Die Bild-URL lautet:

```
![](https://radiatortwo.github.io/rezepte/pics/<bild-dateiname>.jpg)
```

Achte auf:

- Korrekte Mengen mit Einheit und Leerzeichen (z. B. `400 g`, `250 ml`, `1 EL`, `1 TL`, `2 Knoblauchzehen`).
- Konsistente Schreibweise: `EL`, `TL`, `g`, `ml`, `kg`, `l` (deutsche Konvention).
- Zubereitung in Fließtext-Schritten (Absätze) oder als Backslash-getrennte Zeilen, je nachdem wie es zur Vorlage passt. Bei längeren Schritten ist Absatzform (wie `GrueneBohnenHackfleischPfanne.md`) zu bevorzugen.
- `## Notizen` nur einfügen, wenn das Originalrezept tatsächlich Notizen/Tipps enthält.

### 5. index.md aktualisieren

- Lies `source/markdown/index.md`.
- Wähle die passende Gruppe. Gruppen sind die `##`-Überschriften, z. B. `## Soßen & Dips`, `## Asiatisch`, `## BBQ & Grillen`, `## Tex-Mex`, `## Burger & Sandwiches`, `## Pasta & Nudeln`, `## Suppen & Eintöpfe`, `## Pfannengerichte`, `## Italienisch`, `## Griechisch`, `## Österreichisch`, `## Russisch`, `## Snacks & Fingerfood`, `## Airfryer Rezepte`, `## Mealprep`, `## Dessert`, `## Beilagen & Salate`.
- Wenn keine vorhandene Gruppe passt, erstelle eine neue `##`-Gruppe an einer thematisch passenden Stelle.
- Füge am **Ende** der Gruppenliste eine neue Zeile im Format ein:

  ```
  * [<Anzeigename>](https://radiatortwo.github.io/rezepte/<RezeptDateinameOhneEndung>)
  ```

  Der Anzeigename ist der vollständige deutsche Rezepttitel (mit Umlauten und Sonderzeichen). Der Link enthält den **Dateinamen ohne `.md`-Endung**.

### 6. Ergebnis ausgeben

Antworte am Ende **kurz** mit:

1. Welche Datei angelegt wurde (Pfad).
2. In welche Gruppe der index.md-Eintrag eingefügt wurde.
3. **Den benötigten Bild-Dateinamen** (z. B. `gruene-bohnen-hackfleisch-pfanne.jpg`) klar hervorgehoben — dieser wird im Anschluss vom Benutzer für das Rezept-Bild verwendet.

## Wichtige Regeln

- Halte dich **exakt** an die Vorlage-Struktur. Keine zusätzlichen Abschnitte erfinden, die nicht in der Vorlage stehen.
- Verändere keine anderen Rezepte und keine bestehenden Einträge in `index.md`.
- Erstelle das Bild **nicht** selbst und lade nichts hoch — gib nur den erwarteten Dateinamen zurück.
- Keine Commits oder git-Aktionen ausführen, sofern der Benutzer das nicht ausdrücklich verlangt.
- Mengen niemals raten: Wenn das Originalrezept eine Menge nicht eindeutig nennt, formuliere wie in den Beispielrezepten (z. B. `Salz`, `Pfeffer`, `Öl zum Anbraten`) ohne erfundene Zahlenwerte.
