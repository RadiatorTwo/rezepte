#!/usr/bin/env python3
"""
Konvertiert Markdown-Rezepte in JSON-Format für die Rezepte-Webseite.
Verwendung: python convert_recipes.py [rezepte-ordner] [ausgabe-datei]
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

def parse_ingredient(line: str) -> Optional[Dict]:
    """
    Parst eine Zutat-Zeile und extrahiert Menge, Einheit und Name.
    Beispiele:
    - "1/2 Stk. Spitzkohl" -> {amount: 0.5, unit: "Stk.", name: "Spitzkohl"}
    - "2 EL Mayonnaise" -> {amount: 2, unit: "EL", name: "Mayonnaise"}
    - "1 Prise Salz" -> {amount: 1, unit: "Prise", name: "Salz"}
    """
    line = line.strip()
    if not line:
        return None
    
    # Pattern für Brüche (1/2, 1/4, etc.)
    fraction_pattern = r'(\d+)/(\d+)'
    # Pattern für Dezimalzahlen und ganze Zahlen
    number_pattern = r'(\d+(?:[.,]\d+)?)'
    # Pattern für Einheiten (optional)
    unit_pattern = r'([A-Za-zäöüÄÖÜß]+\.?)'
    
    # Versuche Menge zu extrahieren
    amount = None
    unit = ""
    name = line
    
    # Prüfe auf Bruch
    fraction_match = re.match(rf'^{fraction_pattern}\s+', line)
    if fraction_match:
        numerator = float(fraction_match.group(1))
        denominator = float(fraction_match.group(2))
        amount = numerator / denominator
        rest = line[fraction_match.end():].strip()
    else:
        # Prüfe auf normale Zahl
        number_match = re.match(rf'^{number_pattern}\s+', line)
        if number_match:
            amount_str = number_match.group(1).replace(',', '.')
            amount = float(amount_str)
            rest = line[number_match.end():].strip()
        else:
            rest = line
    
    if amount is not None:
        # Versuche Einheit zu extrahieren
        unit_match = re.match(rf'^{unit_pattern}\s+', rest)
        if unit_match:
            unit = unit_match.group(1)
            name = rest[unit_match.end():].strip()
        else:
            name = rest
    
    return {
        'amount': amount,
        'unit': unit,
        'name': name,
        'original': line
    }

def parse_recipe_markdown(content: str, filename: str) -> Dict:
    """Parst eine Markdown-Rezept-Datei."""
    lines = content.split('\n')
    
    recipe = {
        'id': Path(filename).stem,
        'title': '',
        'image': '',
        'ingredients': [],
        'instructions': [],
        'category': '',
        'servings': 1  # Default-Portionen
    }
    
    # Titel extrahieren (erste # Überschrift)
    for line in lines:
        if line.startswith('# '):
            recipe['title'] = line[2:].strip()
            break
    
    # Bild extrahieren
    image_pattern = r'!\[.*?\]\((.*?)\)'
    for line in lines:
        match = re.search(image_pattern, line)
        if match:
            recipe['image'] = match.group(1)
            break
    
    # Inhalt in Zutaten und Anweisungen aufteilen
    # Annahme: Zeilen mit Mengenangaben sind Zutaten, der Rest sind Anweisungen
    in_ingredients = False
    ingredients_section = []
    instructions_section = []
    
    for line in lines:
        line = line.strip()
        
        # Überspringe Titel und Bilder
        if line.startswith('#') or line.startswith('!'):
            in_ingredients = True
            continue
        
        if not line:
            continue
        
        # Entferne Backslashes am Zeilenende
        line = line.rstrip('\\').strip()
        
        # Versuche zu erkennen, ob es eine Zutat ist
        # Zutaten beginnen typischerweise mit einer Zahl oder enthalten Mengenangaben
        if in_ingredients and (re.match(r'^\d', line) or 'Prise' in line or 'TL' in line or 'EL' in line):
            ingredients_section.append(line)
        elif in_ingredients and ingredients_section:
            # Wenn wir schon Zutaten haben und die Zeile keine Zutat ist, ist es eine Anweisung
            instructions_section.append(line)
    
    # Parse Zutaten
    for ing_line in ingredients_section:
        ingredient = parse_ingredient(ing_line)
        if ingredient:
            recipe['ingredients'].append(ingredient)
    
    # Anweisungen übernehmen
    recipe['instructions'] = instructions_section
    
    # Versuche Portionen zu erkennen (z.B. aus "für 4 Personen")
    full_text = content.lower()
    servings_match = re.search(r'(?:für|ergibt)\s+(\d+)\s+(?:personen|portionen)', full_text)
    if servings_match:
        recipe['servings'] = int(servings_match.group(1))
    
    return recipe

def parse_index_markdown(content: str) -> Dict[str, List[str]]:
    """Parst die index.md und extrahiert Kategorien."""
    categories = {}
    current_category = None
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        
        # Kategorie-Überschrift (## Kategorie)
        if line.startswith('## '):
            current_category = line[3:].strip()
            categories[current_category] = []
        
        # Rezept-Link (* [Name](URL))
        elif line.startswith('* [') and current_category:
            # Extrahiere den Namen aus [Name](URL)
            match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
            if match:
                name = match.group(1)
                url = match.group(2)
                # Extrahiere Dateinamen aus URL
                recipe_id = url.split('/')[-1]
                categories[current_category].append(recipe_id)
    
    return categories

def convert_recipes(recipes_dir: str, output_file: str):
    """Konvertiert alle Rezepte in JSON."""
    recipes_path = Path(recipes_dir)
    
    if not recipes_path.exists():
        print(f"Fehler: Verzeichnis {recipes_dir} nicht gefunden!")
        sys.exit(1)
    
    recipes = []
    categories_map = {}
    
    # Parse index.md für Kategorien
    index_file = recipes_path / 'index.md'
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            categories_map = parse_index_markdown(f.read())
    
    # Alle .md Dateien durchgehen (außer index.md)
    md_files = [f for f in recipes_path.glob('*.md') if f.name != 'index.md']
    
    for md_file in md_files:
        print(f"Verarbeite {md_file.name}...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        recipe = parse_recipe_markdown(content, md_file.name)
        
        # Kategorie zuordnen
        for category, recipe_ids in categories_map.items():
            if recipe['id'] in recipe_ids:
                recipe['category'] = category
                break
        
        recipes.append(recipe)
    
    # In JSON speichern
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ {len(recipes)} Rezepte erfolgreich konvertiert!")
    print(f"✓ Ausgabe gespeichert in: {output_file}")
    
    # Statistik
    categories_count = {}
    for recipe in recipes:
        cat = recipe.get('category', 'Ohne Kategorie')
        categories_count[cat] = categories_count.get(cat, 0) + 1
    
    print("\nKategorien:")
    for cat, count in sorted(categories_count.items()):
        print(f"  - {cat}: {count} Rezepte")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Verwendung: python convert_recipes.py [rezepte-ordner] [ausgabe-datei]")
        print("Beispiel: python convert_recipes.py ./rezepte recipes.json")
        sys.exit(1)
    
    recipes_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'recipes.json'
    
    convert_recipes(recipes_dir, output_file)
