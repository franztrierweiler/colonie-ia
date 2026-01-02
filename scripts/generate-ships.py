#!/usr/bin/env python3
"""
Générateur de sprites de vaisseaux HD - Style anime rétro
Inspiré de: Albator (Arcadia), Capitaine Flam (Cyberlabe), Goldorak (Spazer)

Résolution: 256px (rendu interne 512px)
8 types de vaisseaux, 4 variantes chacun
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../frontend/public/ships")
RENDER_SIZE = 512
OUTPUT_SIZE = 256
VARIANTS_PER_TYPE = 4

# Types de vaisseaux avec leur style associé
SHIP_STYLES = {
    # Style Goldorak - agressif, rouge/blanc, angulaire
    "fighter": "goldorak",
    "bio": "goldorak",

    # Style Capitaine Flam - rétro-futuriste, blanc/gris, cyan
    "scout": "flam",
    "colony": "flam",
    "satellite": "flam",
    "tanker": "flam",

    # Style Albator - militaire, vert sombre, allongé
    "battleship": "albator",
    "decoy": "albator",
}

# Palettes de couleurs par style
PALETTES = {
    "goldorak": {
        "primary": [(220, 40, 40), (200, 30, 30), (180, 25, 25)],
        "secondary": [(240, 240, 245), (220, 220, 230), (200, 200, 215)],
        "accent": [(40, 40, 50), (30, 30, 40), (20, 20, 30)],
        "detail": [(255, 200, 50), (255, 180, 30), (240, 160, 20)],
        "engine": [(255, 120, 60), (255, 80, 30), (255, 200, 100)],
    },
    "flam": {
        "primary": [(235, 235, 240), (220, 220, 230), (200, 200, 215)],
        "secondary": [(160, 165, 175), (140, 145, 155), (120, 125, 135)],
        "accent": [(100, 60, 70), (120, 70, 80), (80, 50, 60)],
        "detail": [(80, 200, 220), (60, 180, 200), (100, 220, 240)],
        "engine": [(80, 200, 230), (100, 220, 250), (60, 180, 210)],
    },
    "albator": {
        "primary": [(45, 70, 65), (35, 60, 55), (55, 80, 75)],
        "secondary": [(60, 85, 80), (50, 75, 70), (70, 95, 90)],
        "accent": [(30, 45, 42), (25, 38, 35), (35, 52, 48)],
        "detail": [(200, 200, 190), (180, 180, 170), (220, 220, 210)],
        "engine": [(255, 140, 50), (255, 120, 30), (255, 160, 70)],
    },
}


def draw_polygon(draw, points, color, outline=None):
    """Dessine un polygone."""
    if len(points) >= 3:
        draw.polygon(points, fill=color, outline=outline)


def draw_ellipse_at(draw, cx, cy, rx, ry, color, outline=None):
    """Dessine une ellipse centrée."""
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color, outline=outline)


def rotate_point(x, y, cx, cy, angle):
    """Rotation d'un point autour d'un centre."""
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    dx, dy = x - cx, y - cy
    return cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a


def add_engine_glow(img, positions, color, radius=15):
    """Ajoute un effet de lueur pour les réacteurs."""
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    for x, y in positions:
        for i in range(radius, 0, -2):
            alpha = int(100 * (1 - i / radius))
            glow_color = (*color[:3], alpha)
            glow_draw.ellipse([x - i, y - i, x + i, y + i], fill=glow_color)
        glow_draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255, 220))

    return Image.alpha_composite(img, glow)


# ============================================================
# GÉNÉRATEURS - STYLE GOLDORAK (Fighter, Bio)
# ============================================================

def generate_fighter(seed: int, variant: int) -> Image.Image:
    """Chasseur - Style Goldorak: agressif, ailes delta, rouge/blanc."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed + variant)
    palette = PALETTES["goldorak"]
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    red = random.choice(palette["primary"])
    white = random.choice(palette["secondary"])
    black = random.choice(palette["accent"])
    gold = random.choice(palette["detail"])

    # Corps principal - fuselage central
    body = [
        (cx, cy - 180), (cx + 40, cy - 100), (cx + 50, cy + 50),
        (cx + 35, cy + 130), (cx, cy + 150),
        (cx - 35, cy + 130), (cx - 50, cy + 50), (cx - 40, cy - 100),
    ]
    draw_polygon(draw, body, white)

    # Bande centrale rouge
    stripe = [
        (cx, cy - 180), (cx + 18, cy - 100), (cx + 18, cy + 130),
        (cx, cy + 150), (cx - 18, cy + 130), (cx - 18, cy - 100),
    ]
    draw_polygon(draw, stripe, red)

    # Ailes delta
    wing_r = [(cx + 45, cy - 20), (cx + 170, cy + 90), (cx + 150, cy + 115), (cx + 45, cy + 70)]
    wing_l = [(cx - 45, cy - 20), (cx - 170, cy + 90), (cx - 150, cy + 115), (cx - 45, cy + 70)]
    draw_polygon(draw, wing_r, red)
    draw_polygon(draw, wing_l, red)

    # Détails ailes blancs
    detail_r = [(cx + 55, cy), (cx + 140, cy + 75), (cx + 130, cy + 90), (cx + 55, cy + 25)]
    detail_l = [(cx - 55, cy), (cx - 140, cy + 75), (cx - 130, cy + 90), (cx - 55, cy + 25)]
    draw_polygon(draw, detail_r, white)
    draw_polygon(draw, detail_l, white)

    # Cockpit noir
    cockpit = [
        (cx, cy - 130), (cx + 14, cy - 85), (cx + 12, cy - 35),
        (cx, cy - 25), (cx - 12, cy - 35), (cx - 14, cy - 85),
    ]
    draw_polygon(draw, cockpit, black)
    draw.line([(cx - 6, cy - 110), (cx + 6, cy - 55)], fill=(100, 100, 130), width=3)

    # Réacteurs
    for ex in [cx - 22, cx + 22]:
        draw_ellipse_at(draw, ex, cy + 140, 14, 10, black)

    # Détails dorés
    draw_ellipse_at(draw, cx, cy - 160, 8, 8, gold)
    draw.line([(cx - 40, cy + 90), (cx - 65, cy + 90)], fill=gold, width=4)
    draw.line([(cx + 40, cy + 90), (cx + 65, cy + 90)], fill=gold, width=4)

    img = add_engine_glow(img, [(cx - 22, cy + 155), (cx + 22, cy + 155)],
                          palette["engine"][0], radius=25)
    return img


def generate_bio(seed: int, variant: int) -> Image.Image:
    """Vaisseau Biologique - Style Goldorak: organique, rouge/noir, menaçant."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed + variant)
    palette = PALETTES["goldorak"]
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    red = random.choice(palette["primary"])
    dark_red = (red[0] - 50, max(0, red[1] - 25), max(0, red[2] - 15))
    black = random.choice(palette["accent"])
    gold = random.choice(palette["detail"])

    # Corps organique
    body_points = []
    for i in range(20):
        angle = math.radians(i * 18)
        r = 90 + 35 * math.cos(angle * 2) + 20 * math.sin(angle * 3 + seed * 0.1)
        body_points.append((cx + r * math.sin(angle), cy - r * math.cos(angle) * 1.4))
    draw_polygon(draw, body_points, dark_red)

    # Nervures
    for i in range(6):
        angle = math.radians(i * 60 + 30)
        for r in range(25, 110, 18):
            x = cx + r * math.sin(angle)
            y = cy - r * math.cos(angle) * 1.4
            draw_ellipse_at(draw, x, y, 7 + r // 18, 4 + r // 25, red)

    # Yeux
    for ex, ey in [(cx - 35, cy - 70), (cx + 35, cy - 70)]:
        draw_ellipse_at(draw, ex, ey, 22, 28, black)
        draw_ellipse_at(draw, ex, ey, 14, 18, (180, 30, 30))
        draw_ellipse_at(draw, ex + 4, ey - 6, 5, 5, (255, 100, 100))

    # Tentacules
    for tx, ty in [(cx - 80, cy + 50), (cx + 80, cy + 50), (cx - 60, cy + 95), (cx + 60, cy + 95)]:
        pts = [(tx, ty)]
        for i in range(1, 7):
            wave = 18 * math.sin(i * 0.9 + seed * 0.15)
            pts.append((tx + wave + (tx - cx) * 0.25 * i, ty + i * 18))
        for i in range(len(pts) - 1):
            w = max(3, 10 - i)
            draw.line([pts[i], pts[i + 1]], fill=dark_red, width=w)
        draw_ellipse_at(draw, pts[-1][0], pts[-1][1], 8, 8, red)

    # Organe central
    draw_ellipse_at(draw, cx, cy, 30, 38, black)
    draw_ellipse_at(draw, cx, cy, 20, 26, gold)
    draw_ellipse_at(draw, cx, cy - 6, 10, 12, (255, 255, 200))

    img = add_engine_glow(img, [(cx, cy + 140)], (255, 80, 80), radius=30)
    return img


# ============================================================
# GÉNÉRATEURS - STYLE CAPITAINE FLAM (Scout, Colony, Satellite, Tanker)
# ============================================================

def generate_scout(seed: int, variant: int) -> Image.Image:
    """Éclaireur - Style Capitaine Flam: sphère centrale, nacelles, blanc/cyan."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed + variant)
    palette = PALETTES["flam"]
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    white = random.choice(palette["primary"])
    grey = random.choice(palette["secondary"])
    bordeaux = random.choice(palette["accent"])
    cyan = random.choice(palette["detail"])

    # Nacelles (4 bras)
    nacelles = [(cx - 130, cy - 90), (cx + 130, cy - 90), (cx - 110, cy + 110), (cx + 110, cy + 110)]
    engine_pos = []

    for nx, ny in nacelles:
        # Bras
        arm = [(cx + 35 * (1 if nx > cx else -1), cy),
               (nx, ny), (nx + 12 * (1 if nx > cx else -1), ny + 18),
               (cx + 30 * (1 if nx > cx else -1), cy + 12)]
        draw_polygon(draw, arm, grey)
        # Nacelle
        draw.rounded_rectangle([nx - 18, ny - 30, nx + 18, ny + 30], radius=8, fill=white)
        draw_ellipse_at(draw, nx, ny + 38, 14, 10, cyan)
        engine_pos.append((nx, ny + 45))

    # Corps sphérique
    draw_ellipse_at(draw, cx, cy, 80, 80, white)

    # Anneau bordeaux
    draw.arc([cx - 70, cy - 70, cx + 70, cy + 70], 0, 360, fill=bordeaux, width=12)

    # Panneaux
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        draw_ellipse_at(draw, cx + 55 * math.cos(rad), cy + 55 * math.sin(rad), 10, 10, grey)

    # Centre lumineux
    draw_ellipse_at(draw, cx, cy, 30, 30, grey)
    draw_ellipse_at(draw, cx, cy, 22, 22, (255, 200, 80))
    draw_ellipse_at(draw, cx, cy, 12, 12, (255, 255, 210))

    # Antenne
    draw.line([(cx, cy - 80), (cx, cy - 130)], fill=grey, width=5)
    draw_ellipse_at(draw, cx, cy - 138, 12, 12, cyan)

    img = add_engine_glow(img, engine_pos, palette["engine"][0], radius=18)
    return img


def generate_colony(seed: int, variant: int) -> Image.Image:
    """Vaisseau Colonial - Style Flam: grand, modulaire, blanc/gris."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed + variant)
    palette = PALETTES["flam"]
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    white = random.choice(palette["primary"])
    grey = random.choice(palette["secondary"])
    bordeaux = random.choice(palette["accent"])
    cyan = random.choice(palette["detail"])

    # Corps arrière
    draw_ellipse_at(draw, cx, cy + 50, 90, 115, white)

    # Corps avant
    draw.rounded_rectangle([cx - 60, cy - 80, cx + 60, cy + 30], radius=15, fill=white)
    draw_ellipse_at(draw, cx, cy - 80, 60, 35, white)

    # Modules latéraux
    for side in [-1, 1]:
        mx = cx + side * 115
        draw.rounded_rectangle([mx - 38, cy - 30, mx + 38, cy + 75], radius=10, fill=grey)
        for wy in range(int(cy - 15), int(cy + 60), 25):
            draw.rectangle([mx - 25, wy, mx + 25, wy + 14], fill=cyan)
        x1, x2 = min(cx + side * 65, cx + side * 78), max(cx + side * 65, cx + side * 78)
        draw.rectangle([x1, cy + 5, x2, cy + 40], fill=grey)

    # Bandes bordeaux
    draw.rectangle([cx - 50, cy - 65, cx + 50, cy - 52], fill=bordeaux)
    draw.rectangle([cx - 60, cy + 115, cx + 60, cy + 128], fill=bordeaux)

    # Pont de commandement
    draw_ellipse_at(draw, cx, cy - 100, 30, 18, grey)
    draw_ellipse_at(draw, cx, cy - 100, 18, 12, (40, 40, 55))

    # Réacteurs
    engines = [(cx - 50, cy + 165), (cx, cy + 165), (cx + 50, cy + 165)]
    for ex, ey in engines:
        draw_ellipse_at(draw, ex, ey - 10, 22, 14, grey)
        draw_ellipse_at(draw, ex, ey - 10, 14, 9, (40, 40, 55))

    img = add_engine_glow(img, engines, palette["engine"][0], radius=22)
    return img


def generate_satellite(seed: int, variant: int) -> Image.Image:
    """Satellite - Style Flam: compact, panneaux solaires, antennes."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed + variant)
    palette = PALETTES["flam"]
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    white = random.choice(palette["primary"])
    grey = random.choice(palette["secondary"])
    cyan = random.choice(palette["detail"])

    # Corps octogonal
    body = [(cx + 60 * math.cos(math.radians(i * 45 + 22.5)),
             cy + 60 * math.sin(math.radians(i * 45 + 22.5))) for i in range(8)]
    draw_polygon(draw, body, white)

    # Panneaux solaires
    for side in [-1, 1]:
        px = cx + side * 160
        x1, x2 = min(cx + side * 60, cx + side * 105), max(cx + side * 60, cx + side * 105)
        draw.rectangle([x1, cy - 6, x2, cy + 6], fill=grey)
        draw.rectangle([px - 60, cy - 95, px + 60, cy + 95], fill=(50, 60, 105))
        for py in range(int(cy - 85), int(cy + 85), 24):
            for ppx in range(int(px - 50), int(px + 50), 24):
                draw.rectangle([ppx, py, ppx + 18, py + 18], fill=(70, 90, 145))

    # Antenne principale
    draw.line([(cx, cy - 60), (cx, cy - 150)], fill=grey, width=5)
    draw_ellipse_at(draw, cx, cy - 160, 25, 25, white)
    draw_ellipse_at(draw, cx, cy - 160, 16, 16, cyan)

    # Antennes secondaires
    for angle in [35, 145]:
        rad = math.radians(angle)
        ex, ey = cx + 95 * math.cos(rad), cy - 95 * math.sin(rad)
        draw.line([(cx, cy - 50), (ex, ey)], fill=grey, width=3)
        draw_ellipse_at(draw, ex, ey, 10, 10, cyan)

    # Senseurs
    for i in range(8):
        rad = math.radians(i * 45 + 22.5)
        draw_ellipse_at(draw, cx + 42 * math.cos(rad), cy + 42 * math.sin(rad), 8, 8, grey)

    # Centre
    draw_ellipse_at(draw, cx, cy, 25, 25, grey)
    draw_ellipse_at(draw, cx, cy, 16, 16, cyan)

    img = add_engine_glow(img, [(cx, cy + 60)], palette["engine"][0], radius=12)
    return img


def generate_tanker(seed: int, variant: int) -> Image.Image:
    """Ravitailleur - Style Flam: cylindrique, réservoirs, massif."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed + variant)
    palette = PALETTES["flam"]
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    white = random.choice(palette["primary"])
    grey = random.choice(palette["secondary"])
    bordeaux = random.choice(palette["accent"])
    cyan = random.choice(palette["detail"])

    # 3 réservoirs
    tanks = [(cx - 70, cy), (cx, cy - 25), (cx + 70, cy)]
    for tx, ty in tanks:
        draw.rectangle([tx - 35, ty - 115, tx + 35, ty + 115], fill=white)
        draw_ellipse_at(draw, tx, ty - 115, 35, 18, white)
        draw_ellipse_at(draw, tx, ty + 115, 35, 18, grey)
        for by in [ty - 70, ty, ty + 70]:
            draw.rectangle([tx - 38, by - 6, tx + 38, by + 6], fill=grey)
        draw.rectangle([tx - 25, ty - 95, tx + 25, ty - 82], fill=bordeaux)

    # Structure
    draw.rectangle([cx - 95, cy + 50, cx + 95, cy + 75], fill=grey)
    draw.rectangle([cx - 85, cy + 75, cx + 85, cy + 100], fill=grey)

    # Cabine
    cabin = [(cx - 30, cy - 165), (cx + 30, cy - 165), (cx + 42, cy - 120), (cx - 42, cy - 120)]
    draw_polygon(draw, cabin, grey)
    draw.rectangle([cx - 18, cy - 158, cx + 18, cy - 135], fill=(40, 40, 55))

    # Bras ravitaillement
    for side in [-1, 1]:
        ax = cx + side * 115
        draw.line([(cx + side * 70, cy + 60), (ax, cy + 35)], fill=grey, width=8)
        draw_ellipse_at(draw, ax, cy + 35, 18, 18, grey)
        draw_ellipse_at(draw, ax, cy + 35, 10, 10, cyan)

    # Réacteurs
    engines = [(cx - 50, cy + 155), (cx + 50, cy + 155)]
    for ex, ey in engines:
        draw_ellipse_at(draw, ex, ey - 10, 24, 14, grey)

    img = add_engine_glow(img, engines, palette["engine"][0], radius=22)
    return img


# ============================================================
# GÉNÉRATEURS - STYLE ALBATOR (Battleship, Decoy)
# ============================================================

def generate_battleship(seed: int, variant: int) -> Image.Image:
    """Cuirassé - Style Albator: allongé, militaire, vert sombre, canons."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed + variant)
    palette = PALETTES["albator"]
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    dark = random.choice(palette["primary"])
    med = random.choice(palette["secondary"])
    very_dark = random.choice(palette["accent"])
    bone = random.choice(palette["detail"])

    # Coque
    hull = [
        (cx, cy - 210), (cx + 30, cy - 170), (cx + 55, cy - 90),
        (cx + 68, cy + 50), (cx + 62, cy + 135), (cx + 45, cy + 175), (cx, cy + 195),
        (cx - 45, cy + 175), (cx - 62, cy + 135), (cx - 68, cy + 50),
        (cx - 55, cy - 90), (cx - 30, cy - 170),
    ]
    draw_polygon(draw, hull, dark)

    # Superstructure
    draw.rounded_rectangle([cx - 38, cy - 115, cx + 38, cy + 75], radius=5, fill=med)

    # Tour de commandement
    draw.rounded_rectangle([cx - 25, cy - 70, cx + 25, cy + 30], radius=3, fill=very_dark)
    draw.rectangle([cx - 18, cy - 58, cx + 18, cy - 35], fill=(30, 42, 48))

    # Tête de mort
    skull_y = cy - 182
    draw_ellipse_at(draw, cx, skull_y, 18, 22, bone)
    draw_ellipse_at(draw, cx - 7, skull_y - 4, 5, 6, very_dark)
    draw_ellipse_at(draw, cx + 7, skull_y - 4, 5, 6, very_dark)
    draw_polygon(draw, [(cx, skull_y + 3), (cx - 4, skull_y + 12), (cx + 4, skull_y + 12)], very_dark)

    # Canons
    cannons = [(cx, cy - 135, 0), (cx - 48, cy - 48, -18), (cx + 48, cy - 48, 18),
               (cx - 42, cy + 95, -12), (cx + 42, cy + 95, 12)]
    for cannon_x, cannon_y, angle in cannons:
        draw_ellipse_at(draw, cannon_x, cannon_y, 15, 15, med)
        rad = math.radians(angle)
        bx = cannon_x + 45 * math.sin(rad)
        by = cannon_y - 45 * math.cos(rad)
        draw.line([(cannon_x, cannon_y), (bx, by)], fill=very_dark, width=8)

    # Ailerons
    for side in [-1, 1]:
        fin = [(cx + side * 62, cy + 75), (cx + side * 115, cy + 115),
               (cx + side * 105, cy + 150), (cx + side * 58, cy + 115)]
        draw_polygon(draw, fin, dark)

    # Panneaux
    for py in range(-160, 165, 48):
        draw.line([(cx - 52, cy + py), (cx + 52, cy + py)], fill=very_dark, width=1)

    # Réacteurs
    engines = [(cx - 30, cy + 195), (cx + 30, cy + 195)]
    for ex, ey in engines:
        draw_ellipse_at(draw, ex, ey - 8, 22, 12, very_dark)

    img = add_engine_glow(img, engines, palette["engine"][0], radius=28)
    return img


def generate_decoy(seed: int, variant: int) -> Image.Image:
    """Leurre - Style Albator: similaire au cuirassé mais plus petit."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed + variant)
    palette = PALETTES["albator"]
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    dark = random.choice(palette["primary"])
    med = random.choice(palette["secondary"])
    very_dark = random.choice(palette["accent"])
    bone = random.choice(palette["detail"])

    # Coque simplifiée
    hull = [
        (cx, cy - 155), (cx + 35, cy - 95), (cx + 48, cy + 50),
        (cx + 35, cy + 115), (cx, cy + 135),
        (cx - 35, cy + 115), (cx - 48, cy + 50), (cx - 35, cy - 95),
    ]
    draw_polygon(draw, hull, dark)

    # Faux canons
    for pos in [(cx - 30, cy - 70), (cx + 30, cy - 70), (cx, cy + 50)]:
        draw_ellipse_at(draw, pos[0], pos[1], 10, 10, med)
        draw_ellipse_at(draw, pos[0], pos[1], 6, 6, very_dark)

    # Fausse passerelle
    draw.rectangle([cx - 18, cy - 48, cx + 18, cy - 25], fill=very_dark)

    # Marquage leurre (bandes)
    for i in range(-4, 5):
        draw.line([(cx - 38 + i * 18, cy - 115), (cx - 38 + i * 18 + 50, cy + 95)],
                  fill=bone, width=3)

    # Ailerons
    for side in [-1, 1]:
        fin = [(cx + side * 42, cy + 50), (cx + side * 85, cy + 85),
               (cx + side * 75, cy + 108), (cx + side * 42, cy + 85)]
        draw_polygon(draw, fin, dark)

    # Réacteur
    draw_ellipse_at(draw, cx, cy + 130, 18, 12, very_dark)
    img = add_engine_glow(img, [(cx, cy + 142)], palette["engine"][0], radius=22)
    return img


# ============================================================
# GÉNÉRATION PRINCIPALE
# ============================================================

GENERATORS = {
    "fighter": generate_fighter,
    "scout": generate_scout,
    "colony": generate_colony,
    "satellite": generate_satellite,
    "tanker": generate_tanker,
    "battleship": generate_battleship,
    "decoy": generate_decoy,
    "bio": generate_bio,
}


def generate_ship(ship_type: str, seed: int, variant: int) -> Image.Image:
    """Génère un vaisseau du type spécifié."""
    generator = GENERATORS.get(ship_type, generate_fighter)
    img = generator(seed, variant)
    img = img.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)
    return img


def main():
    """Point d'entrée principal."""
    print(f"Génération des sprites de vaisseaux HD ({OUTPUT_SIZE}px)...")
    print(f"Rendu interne à {RENDER_SIZE}px")
    print(f"Styles: Goldorak, Capitaine Flam, Albator\n")

    total = 0
    for ship_type, style in SHIP_STYLES.items():
        type_dir = os.path.join(OUTPUT_DIR, ship_type)
        os.makedirs(type_dir, exist_ok=True)

        print(f"{ship_type} (style {style}):")
        for variant in range(1, VARIANTS_PER_TYPE + 1):
            seed = hash(f"{ship_type}_{variant}") & 0xFFFFFFFF
            img = generate_ship(ship_type, seed, variant)

            filename = f"ship-{variant:02d}.png"
            filepath = os.path.join(type_dir, filename)
            img.save(filepath, "PNG", optimize=True)
            print(f"  {filename}")
            total += 1
        print()

    print(f"Terminé! {total} sprites générés en {OUTPUT_SIZE}x{OUTPUT_SIZE}px.")


if __name__ == "__main__":
    main()
