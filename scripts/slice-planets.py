#!/usr/bin/env python3
"""
Script pour découper la planche de planètes en images individuelles.
Usage: python scripts/slice-planets.py <chemin_vers_spritesheet.png>
"""

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("PIL non installé. Installez-le avec: pip install Pillow")
    sys.exit(1)

# Configuration de la grille
COLS = 4
ROWS = 3
CELL_WIDTH = 256
CELL_HEIGHT = 256

# Noms des planètes dans l'ordre (ligne par ligne)
PLANET_NAMES = [
    # Row 1 - Habitable
    "planet-earthlike",
    "planet-ocean",
    "planet-desert",
    "planet-ice",
    # Row 2 - Hostile
    "planet-volcanic",
    "planet-toxic",
    "planet-barren",
    "planet-scorched",
    # Row 3 - Special
    "planet-gasgiant-a",
    "planet-gasgiant-b",
    "planet-asteroid",
    "planet-mysterious",
]

def slice_spritesheet(input_path: str, output_dir: str = None):
    """Découpe le sprite sheet en images individuelles."""

    input_file = Path(input_path)
    if not input_file.exists():
        print(f"Erreur: Fichier non trouvé: {input_path}")
        sys.exit(1)

    # Répertoire de sortie
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "frontend" / "public" / "planets"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Ouvrir l'image
    img = Image.open(input_path)
    print(f"Image chargée: {img.size[0]}x{img.size[1]}")

    # Calculer la taille réelle des cellules si différente
    actual_cell_width = img.size[0] // COLS
    actual_cell_height = img.size[1] // ROWS

    print(f"Taille de cellule détectée: {actual_cell_width}x{actual_cell_height}")

    # Découper chaque planète
    for idx, name in enumerate(PLANET_NAMES):
        row = idx // COLS
        col = idx % COLS

        left = col * actual_cell_width
        top = row * actual_cell_height
        right = left + actual_cell_width
        bottom = top + actual_cell_height

        # Extraire la cellule
        cell = img.crop((left, top, right, bottom))

        # Sauvegarder
        output_path = output_dir / f"{name}.png"
        cell.save(output_path, "PNG")
        print(f"  Sauvegardé: {output_path}")

    print(f"\nTerminé! {len(PLANET_NAMES)} textures extraites dans {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/slice-planets.py <spritesheet.png> [output_dir]")
        print("\nExemple:")
        print("  python scripts/slice-planets.py planets-spritesheet.png")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    slice_spritesheet(input_file, output_dir)
