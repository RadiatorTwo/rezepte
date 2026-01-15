#!/usr/bin/env python3
"""
Migriert alte Rezept-Markdown-Dateien zum neuen Format mit ## Zutaten und ## Zubereitung.
"""

import re
from pathlib import Path

def is_ingredient_line(line: str) -> bool:
    """Prüft ob eine Zeile eine Zutat ist."""
    line = line.strip().rstrip('\\').strip()
    if not line:
        return False
    # Beginnt mit Zahl oder enthält typische Einheiten
    if re.match(r'^\d', line):
        return True
    if any(unit in line for unit in ['Prise', ' TL ', ' EL ', ' ml ', ' g ', ' kg ', ' l ', ' Stk']):
        return True
    # Kurze Zeilen ohne Verb sind wahrscheinlich Zutaten
    verbs = ['schneiden', 'geben', 'mischen', 'rühren', 'braten', 'kochen', 'backen', 'würzen', 'lassen', 'servieren', 'verteilen', 'legen', 'stellen', 'nehmen', 'formen', 'wenden', 'streichen', 'bestreuen', 'anbraten', 'dazugeben', 'hinzufügen', 'verrühren', 'vermischen', 'abschmecken', 'marinieren']
    line_lower = line.lower()
    has_verb = any(verb in line_lower for verb in verbs)
    # Wenn kein Verb und relativ kurz, ist es wahrscheinlich eine Zutat
    if not has_verb and len(line) < 60:
        return True
    return False

def migrate_recipe(filepath: Path) -> bool:
    """Migriert ein einzelnes Rezept zum neuen Format."""
    content = filepath.read_text(encoding='utf-8')

    # Prüfe ob schon im neuen Format
    if '## Zutaten' in content and '## Zubereitung' in content:
        return False  # Bereits migriert

    lines = content.split('\n')

    # Extrahiere Teile
    title_line = None
    image_line = None
    portionen_line = None
    other_lines = []

    for line in lines:
        if line.startswith('# ') and not line.startswith('## ') and title_line is None:
            title_line = line
        elif line.strip().startswith('!['):
            image_line = line
        elif line.strip().lower().startswith('portionen:'):
            portionen_line = line.strip()
        else:
            other_lines.append(line)

    # Trenne Zutaten von Zubereitung
    ingredients = []
    instructions = []
    found_first_instruction = False

    for line in other_lines:
        line_stripped = line.strip().rstrip('\\').strip()

        # Überspringe leere Zeilen und Metadaten
        if not line_stripped:
            continue
        if line_stripped.lower().startswith('zutaten'):
            continue

        # Prüfe ob es eine Gruppen-Überschrift ist (z.B. "Für das Hähnchen:")
        if line_stripped.endswith(':') and len(line_stripped) < 50 and not found_first_instruction:
            # Das ist eine Zutaten-Gruppe
            ingredients.append(('group', line_stripped.rstrip(':')))
            continue

        if not found_first_instruction:
            if is_ingredient_line(line_stripped):
                ingredients.append(('item', line_stripped))
            else:
                found_first_instruction = True
                instructions.append(line_stripped)
        else:
            if line_stripped:
                instructions.append(line_stripped)

    # Baue neues Format
    new_lines = []

    # Titel
    if title_line:
        new_lines.append(title_line)
        new_lines.append('')

    # Bild
    if image_line:
        new_lines.append(image_line)
        new_lines.append('')

    # Portionen
    if portionen_line:
        new_lines.append(portionen_line)
    else:
        new_lines.append('Portionen: 1')
    new_lines.append('')

    # Zutaten
    new_lines.append('## Zutaten')
    new_lines.append('')

    current_group = None
    for item_type, item_value in ingredients:
        if item_type == 'group':
            new_lines.append(f'### {item_value}')
            current_group = item_value
        else:
            new_lines.append(item_value)

    new_lines.append('')

    # Zubereitung
    new_lines.append('## Zubereitung')
    new_lines.append('')
    for instruction in instructions:
        new_lines.append(instruction)

    # Schreibe neue Datei
    new_content = '\n'.join(new_lines)
    filepath.write_text(new_content, encoding='utf-8')
    return True

def main():
    recipes_dir = Path(__file__).parent / 'markdown'
    exclude = {'index.md', 'VORLAGE.md'}

    migrated = 0
    skipped = 0

    for md_file in sorted(recipes_dir.glob('*.md')):
        if md_file.name in exclude:
            continue

        if migrate_recipe(md_file):
            print(f"[OK] Migriert: {md_file.name}")
            migrated += 1
        else:
            print(f"[--] Uebersprungen (bereits neu): {md_file.name}")
            skipped += 1

    print(f"\nFertig! {migrated} migriert, {skipped} uebersprungen.")

if __name__ == '__main__':
    main()
