#!/usr/bin/env python3
"""
Générateur de sprites de vaisseaux - Style LEGO Premium v3
============================================================

Style: LEGO pour adultes avec têtes de minifigures visibles
- Formes angulaires et modulaires (assemblage de briques)
- Studs (boutons LEGO) visibles comme signature visuelle
- TÊTES DE MINIFIGURES dans les cockpits
- Rendu 3D isométrique avec faces distinctes
- Armes progressives selon le niveau
- Design plus détaillé et imposant

Résolution: 1024px (rendu interne 4096px)
8 types × 4 niveaux = 32 sprites
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../frontend/public/ships")
RENDER_SIZE = 4096  # Rendu interne ultra HD
OUTPUT_SIZE = 1024  # Sortie 1K pour batailles
LEVELS_PER_TYPE = 4

# Facteur d'échelle pour adapter les éléments à la résolution 4K
S = RENDER_SIZE / 2048  # Facteur 2x par rapport à l'ancienne résolution

# ============================================================
# PALETTE LEGO PREMIUM - Couleurs officielles LEGO raffinées
# ============================================================

LEGO_COLORS = {
    # Gris techniques (LEGO Technic)
    "dark_bluish_gray": (89, 93, 96),
    "light_bluish_gray": (160, 165, 169),
    "medium_stone_gray": (156, 153, 149),
    "dark_stone_gray": (99, 95, 98),

    # Couleurs primaires LEGO
    "brick_red": (179, 62, 56),
    "bright_red": (196, 40, 27),
    "dark_red": (114, 35, 36),
    "bright_blue": (0, 85, 166),
    "dark_blue": (20, 48, 68),
    "medium_blue": (90, 147, 219),
    "bright_yellow": (245, 205, 47),
    "bright_orange": (254, 138, 24),
    "dark_orange": (169, 85, 0),
    "bright_green": (75, 151, 74),
    "dark_green": (39, 70, 45),
    "sand_green": (118, 150, 131),

    # Accents premium
    "pearl_gold": (220, 188, 129),
    "pearl_dark_gray": (87, 88, 87),
    "chrome_silver": (187, 187, 187),
    "warm_gold": (215, 175, 103),
    "metallic_silver": (165, 169, 180),

    # Bases
    "black": (33, 33, 33),
    "white": (242, 243, 242),
    "tan": (210, 190, 150),
    "dark_tan": (149, 125, 98),

    # Couleur peau minifig
    "minifig_yellow": (255, 205, 77),
    "minifig_flesh": (255, 207, 161),

    # Transparents (pour cockpits et effets)
    "trans_light_blue": (174, 233, 255),
    "trans_orange": (252, 172, 0),
    "trans_neon_green": (192, 255, 97),
}


def get_lego_palette(style: str) -> dict:
    """Retourne une palette de couleurs LEGO selon le style."""
    palettes = {
        "military": {
            "primary": LEGO_COLORS["dark_bluish_gray"],
            "secondary": LEGO_COLORS["light_bluish_gray"],
            "accent": LEGO_COLORS["bright_red"],
            "detail": LEGO_COLORS["black"],
            "highlight": LEGO_COLORS["chrome_silver"],
            "cockpit": LEGO_COLORS["trans_light_blue"],
            "engine": LEGO_COLORS["trans_orange"],
        },
        "alien": {
            "primary": LEGO_COLORS["dark_green"],
            "secondary": LEGO_COLORS["sand_green"],
            "accent": LEGO_COLORS["bright_orange"],
            "detail": LEGO_COLORS["dark_tan"],
            "highlight": LEGO_COLORS["bright_green"],
            "cockpit": LEGO_COLORS["trans_neon_green"],
            "engine": LEGO_COLORS["trans_orange"],
        },
        "recon": {
            "primary": LEGO_COLORS["dark_blue"],
            "secondary": LEGO_COLORS["medium_blue"],
            "accent": LEGO_COLORS["bright_yellow"],
            "detail": LEGO_COLORS["light_bluish_gray"],
            "highlight": LEGO_COLORS["white"],
            "cockpit": LEGO_COLORS["trans_light_blue"],
            "engine": LEGO_COLORS["trans_light_blue"],
        },
        "industrial": {
            "primary": LEGO_COLORS["dark_orange"],
            "secondary": LEGO_COLORS["bright_orange"],
            "accent": LEGO_COLORS["black"],
            "detail": LEGO_COLORS["dark_bluish_gray"],
            "highlight": LEGO_COLORS["bright_yellow"],
            "cockpit": LEGO_COLORS["trans_light_blue"],
            "engine": LEGO_COLORS["trans_orange"],
        },
        "tech": {
            "primary": LEGO_COLORS["dark_bluish_gray"],
            "secondary": LEGO_COLORS["medium_stone_gray"],
            "accent": LEGO_COLORS["bright_blue"],
            "detail": LEGO_COLORS["black"],
            "highlight": LEGO_COLORS["metallic_silver"],
            "cockpit": LEGO_COLORS["trans_light_blue"],
            "engine": LEGO_COLORS["trans_light_blue"],
        },
        "warship": {
            "primary": LEGO_COLORS["dark_stone_gray"],
            "secondary": LEGO_COLORS["dark_bluish_gray"],
            "accent": LEGO_COLORS["dark_red"],
            "detail": LEGO_COLORS["black"],
            "highlight": LEGO_COLORS["pearl_gold"],
            "cockpit": LEGO_COLORS["trans_light_blue"],
            "engine": LEGO_COLORS["trans_orange"],
        },
        "stealth": {
            "primary": LEGO_COLORS["black"],
            "secondary": LEGO_COLORS["dark_bluish_gray"],
            "accent": LEGO_COLORS["dark_red"],
            "detail": LEGO_COLORS["pearl_dark_gray"],
            "highlight": LEGO_COLORS["chrome_silver"],
            "cockpit": LEGO_COLORS["trans_light_blue"],
            "engine": LEGO_COLORS["trans_neon_green"],
        },
    }
    return palettes.get(style, palettes["military"])


SHIP_STYLES = {
    "fighter": "military",
    "bio": "alien",
    "scout": "recon",
    "colony": "industrial",
    "satellite": "tech",
    "tanker": "industrial",
    "battleship": "warship",
    "decoy": "stealth",
}


# ============================================================
# FONCTIONS DE RENDU LEGO
# ============================================================

def lighten(color, amount=30):
    """Éclaircit une couleur."""
    return tuple(min(255, c + amount) for c in color[:3])


def darken(color, amount=40):
    """Assombrit une couleur."""
    return tuple(max(0, c - amount) for c in color[:3])


def draw_lego_minifig_head(draw, cx, cy, size, expression="happy"):
    """
    Dessine une tête de minifigure LEGO classique (jaune avec expression).

    Args:
        draw: ImageDraw object
        cx, cy: Centre de la tête
        size: Taille de la tête (rayon)
        expression: "happy", "serious", "angry", "surprised"
    """
    r = size * S

    # Couleur jaune classique minifig
    head_color = LEGO_COLORS["minifig_yellow"]

    # Forme de la tête (cylindrique vue de profil = ovale)
    # Ombre
    draw.ellipse([cx - r + 4*S, cy - r*0.9 + 6*S, cx + r + 4*S, cy + r*0.9 + 6*S],
                 fill=darken(head_color, 60))

    # Tête principale (légèrement ovale)
    draw.ellipse([cx - r, cy - r*0.9, cx + r, cy + r*0.9], fill=head_color)

    # Reflet brillant (plastique)
    draw.arc([cx - r, cy - r*0.9, cx + r, cy + r*0.9],
             start=200, end=340, fill=lighten(head_color, 50), width=int(4*S))

    # Bord inférieur sombre
    draw.arc([cx - r, cy - r*0.9, cx + r, cy + r*0.9],
             start=20, end=160, fill=darken(head_color, 25), width=int(3*S))

    # Reflet spéculaire
    spec_r = r * 0.25
    draw.ellipse([cx - spec_r - r*0.3, cy - spec_r - r*0.4,
                  cx + spec_r - r*0.3, cy + spec_r - r*0.4],
                 fill=lighten(head_color, 70))

    # === VISAGE ===
    eye_size = max(2, int(r * 0.12))
    eye_y = cy - r * 0.15
    eye_spacing = r * 0.35

    # Yeux (points noirs classiques LEGO)
    for side in [-1, 1]:
        ex = cx + side * eye_spacing
        draw.ellipse([ex - eye_size, eye_y - eye_size,
                     ex + eye_size, eye_y + eye_size],
                    fill=(20, 20, 20))
        # Petit reflet dans l'œil
        draw.ellipse([ex - eye_size*0.4, eye_y - eye_size*0.6,
                     ex + eye_size*0.2, eye_y],
                    fill=(60, 60, 60))

    # Bouche selon expression
    mouth_y = cy + r * 0.35
    mouth_w = r * 0.5

    if expression == "happy":
        # Sourire classique
        draw.arc([cx - mouth_w, mouth_y - r*0.25, cx + mouth_w, mouth_y + r*0.2],
                start=0, end=180, fill=(20, 20, 20), width=int(3*S))
    elif expression == "serious":
        # Ligne droite
        draw.line([(cx - mouth_w*0.6, mouth_y), (cx + mouth_w*0.6, mouth_y)],
                 fill=(20, 20, 20), width=int(3*S))
    elif expression == "angry":
        # Bouche en V inversé
        draw.line([(cx - mouth_w*0.5, mouth_y - r*0.05), (cx, mouth_y + r*0.1)],
                 fill=(20, 20, 20), width=int(3*S))
        draw.line([(cx, mouth_y + r*0.1), (cx + mouth_w*0.5, mouth_y - r*0.05)],
                 fill=(20, 20, 20), width=int(3*S))
        # Sourcils froncés
        for side in [-1, 1]:
            brow_x = cx + side * eye_spacing
            brow_y = eye_y - eye_size*2.5
            draw.line([(brow_x - eye_size*1.5, brow_y + side*eye_size*0.5),
                      (brow_x + eye_size*1.5, brow_y - side*eye_size*0.5)],
                     fill=(20, 20, 20), width=int(2*S))
    elif expression == "surprised":
        # Bouche en O
        draw.ellipse([cx - mouth_w*0.3, mouth_y - r*0.1,
                     cx + mouth_w*0.3, mouth_y + r*0.15],
                    fill=(20, 20, 20))


def draw_lego_cockpit_with_pilot(draw, points, frame_color, glass_color, pilot_expression="happy"):
    """Dessine un cockpit LEGO avec un pilote minifigure visible."""
    bw = int(8 * S)

    # Cadre
    draw.polygon(points, fill=frame_color)

    # Contour du cadre
    for i in range(len(points)):
        draw.line([points[i], points[(i+1) % len(points)]],
                 fill=darken(frame_color, 30), width=int(bw * 0.6))

    # Vitre (légèrement plus petite)
    if len(points) >= 4:
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)

        inner = [(cx + (p[0] - cx) * 0.82, cy + (p[1] - cy) * 0.82) for p in points]
        draw.polygon(inner, fill=glass_color)

        # Reflet principal (diagonal)
        if len(inner) >= 2:
            draw.line([inner[0], inner[1]], fill=lighten(glass_color, 55), width=int(bw * 1.2))

        # Second reflet plus petit
        if len(inner) >= 3:
            mid_x = (inner[0][0] + inner[2][0]) / 2
            mid_y = (inner[0][1] + inner[2][1]) / 2
            draw.line([(mid_x - 15*S, mid_y - 10*S), (mid_x + 10*S, mid_y + 5*S)],
                     fill=lighten(glass_color, 40), width=int(bw * 0.6))

        # === PILOTE MINIFIG ===
        # Calculer la taille de la tête selon la taille du cockpit
        cockpit_w = max(abs(points[1][0] - points[0][0]), abs(points[2][0] - points[3][0])) if len(points) >= 4 else 50
        cockpit_h = max(abs(points[2][1] - points[1][1]), abs(points[3][1] - points[0][1])) if len(points) >= 4 else 50
        head_size = min(cockpit_w, cockpit_h) * 0.25 / S

        # Position de la tête (légèrement vers l'arrière du cockpit)
        head_x = cx - cockpit_w * 0.1
        head_y = cy

        if head_size > 8:  # Ne dessiner que si assez grand
            draw_lego_minifig_head(draw, head_x, head_y, head_size, pilot_expression)


def draw_lego_stud(draw, cx, cy, radius, color):
    """Dessine un stud LEGO (bouton cylindrique) avec aspect plastique brillant."""
    r = radius * S  # Appliquer le facteur d'échelle

    # Ombre portée du stud
    shadow_offset = int(6 * S)
    draw.ellipse([cx - r + shadow_offset, cy - r + shadow_offset,
                  cx + r + shadow_offset, cy + r + shadow_offset],
                 fill=darken(color, 70))

    # Anneau extérieur (bord du stud)
    draw.ellipse([cx - r - 2*S, cy - r - 2*S,
                  cx + r + 2*S, cy + r + 2*S],
                 fill=darken(color, 25))

    # Corps principal du stud
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    # Bord supérieur brillant (effet plastique)
    draw.arc([cx - r, cy - r, cx + r, cy + r],
             start=200, end=340, fill=lighten(color, 55), width=int(6 * S))

    # Bord inférieur sombre
    draw.arc([cx - r, cy - r, cx + r, cy + r],
             start=20, end=160, fill=darken(color, 35), width=int(4 * S))

    # Surface supérieure légèrement plus claire
    inner_r = r * 0.75
    draw.ellipse([cx - inner_r, cy - inner_r,
                  cx + inner_r, cy + inner_r],
                 fill=lighten(color, 12))

    # Reflet principal (aspect brillant plastique)
    spec_r = r * 0.35
    draw.ellipse([cx - spec_r - r * 0.2, cy - spec_r - r * 0.25,
                  cx + spec_r - r * 0.2, cy + spec_r - r * 0.25],
                 fill=lighten(color, 75))

    # Point de brillance
    dot_r = r * 0.12
    draw.ellipse([cx - dot_r - r * 0.15, cy - dot_r - r * 0.2,
                  cx + dot_r - r * 0.15, cy + dot_r - r * 0.2],
                 fill=lighten(color, 95))


def draw_studs_row(draw, x1, y, x2, color, stud_spacing=None, stud_radius=None):
    """Dessine une rangée de studs."""
    spacing = stud_spacing if stud_spacing else int(80 * S)
    radius = stud_radius if stud_radius else int(24 * S)

    width = x2 - x1
    num_studs = max(1, int(width / spacing))
    actual_spacing = width / (num_studs + 1)

    for i in range(num_studs):
        sx = x1 + actual_spacing * (i + 1)
        draw_lego_stud(draw, sx, y, radius / S, lighten(color, 15))


def draw_studs_grid(draw, x1, y1, x2, y2, color, spacing=None, radius=None):
    """Dessine une grille de studs sur une surface."""
    sp = spacing if spacing else int(80 * S)
    r = radius if radius else int(24 * S)

    width = x2 - x1
    height = y2 - y1

    cols = max(1, int(width / sp))
    rows = max(1, int(height / sp))

    x_spacing = width / (cols + 1)
    y_spacing = height / (rows + 1)

    for row in range(rows):
        for col in range(cols):
            sx = x1 + x_spacing * (col + 1)
            sy = y1 + y_spacing * (row + 1)
            draw_lego_stud(draw, sx, sy, r / S, lighten(color, 15))


def draw_lego_brick_3d(draw, x, y, width, height, depth, color, add_studs=True):
    """Dessine une brique LEGO en perspective isométrique avec aspect plastique."""
    bw = int(8 * S)  # Épaisseur des bords

    # Face avant (plus sombre) - le côté visible de la brique
    front = [
        (x, y + depth),
        (x + width, y + depth),
        (x + width, y + depth + height),
        (x, y + depth + height),
    ]
    draw.polygon(front, fill=darken(color, 20))

    # Dégradé subtil sur la face avant (effet plastique)
    for i in range(3):
        offset = int(i * 4 * S)
        shade = darken(color, 20 + i * 8)
        draw.line([(x + offset, y + depth + offset),
                   (x + offset, y + depth + height - offset)],
                  fill=shade, width=int(3 * S))

    # Bord lumineux face avant (haut)
    draw.line([front[0], front[1]], fill=lighten(color, 10), width=bw)
    # Bord sombre face avant (bas)
    draw.line([front[2], front[3]], fill=darken(color, 50), width=bw)

    # Face supérieure - la surface principale avec studs
    top = [
        (x, y),
        (x + width, y),
        (x + width, y + depth),
        (x, y + depth),
    ]
    draw.polygon(top, fill=color)

    # Bords lumineux face supérieure (effet chanfreiné)
    draw.line([top[0], top[1]], fill=lighten(color, 50), width=int(bw * 1.2))
    draw.line([top[0], top[3]], fill=lighten(color, 35), width=bw)
    draw.line([top[1], top[2]], fill=darken(color, 20), width=bw)

    # Ligne de séparation entre face sup et face avant
    draw.line([top[2], top[3]], fill=darken(color, 10), width=int(bw * 0.6))

    # Face droite (la plus sombre) - juste un accent
    draw.line([(x + width, y + depth), (x + width, y + depth + height)],
              fill=darken(color, 55), width=int(bw * 1.2))

    # Rainure intérieure sur la face supérieure
    inner_margin = int(16 * S)
    if width > inner_margin * 3 and depth > inner_margin * 2:
        draw.rectangle([x + inner_margin, y + inner_margin,
                       x + width - inner_margin, y + depth - inner_margin],
                      outline=darken(color, 12), width=int(2 * S))

    # Studs sur la face supérieure
    if add_studs:
        draw_studs_grid(draw, x + int(30*S), y + int(15*S),
                       x + width - int(30*S), y + depth - int(15*S),
                       color, spacing=int(90*S), radius=int(28*S))


def draw_lego_plate(draw, x1, y1, x2, y2, thickness, color, add_studs=True):
    """Dessine une plaque LEGO (brique fine)."""
    bw = int(6 * S)
    th = int(thickness * S * 2)

    # Face supérieure
    draw.rectangle([x1, y1, x2, y2], fill=color)

    # Épaisseur (face avant)
    draw.rectangle([x1, y2, x2, y2 + th], fill=darken(color, 25))

    # Bords chanfreinés
    draw.line([(x1, y1), (x2, y1)], fill=lighten(color, 50), width=bw)
    draw.line([(x1, y2 + th), (x2, y2 + th)], fill=darken(color, 55), width=bw)
    draw.line([(x1, y1), (x1, y2 + th)], fill=lighten(color, 30), width=int(bw * 0.7))
    draw.line([(x2, y1), (x2, y2 + th)], fill=darken(color, 35), width=int(bw * 0.7))

    if add_studs:
        draw_studs_row(draw, x1 + int(36*S), (y1 + y2) // 2, x2 - int(36*S), color)


def draw_lego_slope(draw, points, color, direction="right"):
    """Dessine une pièce LEGO en pente."""
    bw = int(8 * S)

    draw.polygon(points, fill=color)

    # Bords selon la direction avec effet plastique
    if len(points) >= 3:
        # Bord supérieur lumineux
        draw.line([points[0], points[1]], fill=lighten(color, 45), width=bw)
        # Bord inférieur sombre
        if len(points) >= 4:
            draw.line([points[2], points[3]], fill=darken(color, 45), width=int(bw * 0.8))


def draw_lego_cylinder(draw, cx, cy, rx, ry, color, depth=0):
    """Dessine un cylindre LEGO (comme une tourelle ou un réacteur)."""
    # Appliquer le facteur d'échelle
    rx_s = rx * S
    ry_s = ry * S
    depth_s = depth * S
    bw = int(6 * S)

    # Ombre portée
    if depth_s > 0:
        shadow_off = int(12 * S)
        draw.ellipse([cx - rx_s + shadow_off, cy - ry_s + shadow_off + depth_s,
                      cx + rx_s + shadow_off, cy + ry_s + shadow_off + depth_s],
                     fill=darken(color, 75))

    # Corps du cylindre (partie visible)
    if depth_s > 0:
        # Face latérale avec dégradé
        draw.rectangle([cx - rx_s, cy, cx + rx_s, cy + depth_s], fill=darken(color, 18))

        # Effet de dégradé sur le cylindre
        for i in range(int(rx_s // (8 * S))):
            x_off = int(rx_s - i * 8 * S)
            shade = darken(color, 18 + i * 5)
            draw.line([(cx - x_off, cy), (cx - x_off, cy + depth_s)], fill=shade, width=int(4*S))
            draw.line([(cx + x_off, cy), (cx + x_off, cy + depth_s)], fill=shade, width=int(4*S))

        draw.arc([cx - rx_s, cy + depth_s - ry_s, cx + rx_s, cy + depth_s + ry_s],
                 start=0, end=180, fill=darken(color, 40), width=bw)

    # Face supérieure (ellipse) avec effet plastique brillant
    draw.ellipse([cx - rx_s, cy - ry_s, cx + rx_s, cy + ry_s], fill=color)

    # Anneau extérieur
    draw.arc([cx - rx_s, cy - ry_s, cx + rx_s, cy + ry_s],
             start=0, end=360, fill=darken(color, 20), width=int(3*S))

    # Highlight supérieur (effet plastique)
    draw.arc([cx - rx_s, cy - ry_s, cx + rx_s, cy + ry_s],
             start=200, end=340, fill=lighten(color, 55), width=bw)

    # Ombre inférieure
    draw.arc([cx - rx_s, cy - ry_s, cx + rx_s, cy + ry_s],
             start=20, end=160, fill=darken(color, 35), width=int(bw * 0.8))

    # Surface intérieure légèrement plus claire
    inner_rx = rx_s * 0.8
    inner_ry = ry_s * 0.8
    draw.ellipse([cx - inner_rx, cy - inner_ry, cx + inner_rx, cy + inner_ry],
                fill=lighten(color, 8))

    # Reflet principal
    spec_rx = rx_s * 0.3
    spec_ry = ry_s * 0.3
    draw.ellipse([cx - spec_rx - rx_s * 0.2, cy - spec_ry - ry_s * 0.25,
                  cx + spec_rx - rx_s * 0.2, cy + spec_ry - ry_s * 0.25],
                 fill=lighten(color, 65))

    # Point de brillance
    dot_r = rx_s * 0.1
    draw.ellipse([cx - dot_r - rx_s * 0.15, cy - dot_r - ry_s * 0.2,
                  cx + dot_r - rx_s * 0.15, cy + dot_r - ry_s * 0.2],
                 fill=lighten(color, 90))


def draw_lego_sphere(draw, cx, cy, radius, color, depth=0):
    """Dessine une sphère LEGO (plus rond qu'un cylindre)."""
    r = radius * S
    depth_s = depth * S
    bw = int(6 * S)

    # Ombre portée
    shadow_off = int(15 * S)
    draw.ellipse([cx - r*0.9 + shadow_off, cy - r*0.9 + shadow_off + depth_s,
                  cx + r*0.9 + shadow_off, cy + r*0.9 + shadow_off + depth_s],
                 fill=darken(color, 80))

    # Corps principal de la sphère (cercle parfait)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    # Dégradé radial simulé avec des cercles concentriques
    for i in range(5):
        ring_r = r * (1 - i * 0.15)
        ring_color = lighten(color, i * 8)
        if ring_r > 0:
            draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
                        fill=ring_color)

    # Anneau extérieur sombre
    draw.arc([cx - r, cy - r, cx + r, cy + r],
             start=0, end=360, fill=darken(color, 30), width=int(4*S))

    # Highlight supérieur gauche (effet plastique 3D)
    draw.arc([cx - r, cy - r, cx + r, cy + r],
             start=190, end=280, fill=lighten(color, 70), width=int(bw * 1.5))

    # Ombre inférieure droite
    draw.arc([cx - r, cy - r, cx + r, cy + r],
             start=10, end=100, fill=darken(color, 45), width=int(bw * 1.2))

    # Grand reflet spéculaire (forme organique)
    spec_r = r * 0.4
    spec_offset_x = -r * 0.25
    spec_offset_y = -r * 0.3
    draw.ellipse([cx + spec_offset_x - spec_r*0.8, cy + spec_offset_y - spec_r*0.6,
                  cx + spec_offset_x + spec_r*0.8, cy + spec_offset_y + spec_r*0.6],
                 fill=lighten(color, 85))

    # Point de brillance intense
    dot_r = r * 0.12
    draw.ellipse([cx - r*0.35 - dot_r, cy - r*0.4 - dot_r,
                  cx - r*0.35 + dot_r, cy - r*0.4 + dot_r],
                 fill=lighten(color, 110))


def draw_lego_tank_drum(draw, cx, cy, width, height, color, with_bands=True):
    """Dessine un bidon/citerne cylindrique LEGO horizontal."""
    w = width * S
    h = height * S
    bw = int(6 * S)

    # Ombre portée
    shadow_off = int(15 * S)
    draw.ellipse([cx - w*0.15 + shadow_off, cy - h*0.5 + shadow_off,
                  cx + w*0.15 + shadow_off, cy + h*0.5 + shadow_off],
                 fill=darken(color, 75))

    # Corps cylindrique (rectangle avec bouts arrondis)
    draw.rectangle([cx - w*0.4, cy - h*0.4, cx + w*0.4, cy + h*0.4],
                   fill=color)

    # Bout gauche (demi-cercle)
    draw.ellipse([cx - w*0.55, cy - h*0.4, cx - w*0.25, cy + h*0.4],
                fill=darken(color, 15))

    # Bout droit (demi-cercle plus clair)
    draw.ellipse([cx + w*0.25, cy - h*0.4, cx + w*0.55, cy + h*0.4],
                fill=lighten(color, 10))

    # Reflet central sur le cylindre
    draw.rectangle([cx - w*0.35, cy - h*0.35, cx + w*0.35, cy - h*0.1],
                   fill=lighten(color, 35))

    # Ombre inférieure
    draw.rectangle([cx - w*0.35, cy + h*0.15, cx + w*0.35, cy + h*0.35],
                   fill=darken(color, 25))

    # Bandes de renfort
    if with_bands:
        band_color = darken(color, 35)
        for offset in [-w*0.25, 0, w*0.25]:
            band_x = cx + offset
            draw.rectangle([band_x - w*0.03, cy - h*0.42,
                           band_x + w*0.03, cy + h*0.42],
                          fill=band_color)
            # Reflet sur la bande
            draw.line([(band_x - w*0.01, cy - h*0.4), (band_x - w*0.01, cy + h*0.4)],
                     fill=lighten(band_color, 30), width=int(2*S))

    # Bords supérieur/inférieur
    draw.line([(cx - w*0.4, cy - h*0.4), (cx + w*0.4, cy - h*0.4)],
             fill=lighten(color, 50), width=bw)
    draw.line([(cx - w*0.4, cy + h*0.4), (cx + w*0.4, cy + h*0.4)],
             fill=darken(color, 45), width=bw)


def draw_lego_technic_beam(draw, x1, y1, x2, y2, color, holes=True):
    """Dessine une poutre Technic avec trous caractéristiques."""
    bw = int(6 * S)
    height = abs(y2 - y1)

    # Corps de la poutre
    draw.rectangle([x1, y1, x2, y2], fill=color)

    # Bords chanfreinés
    draw.line([(x1, y1), (x2, y1)], fill=lighten(color, 45), width=bw)
    draw.line([(x1, y2), (x2, y2)], fill=darken(color, 40), width=bw)
    draw.line([(x1, y1), (x1, y2)], fill=lighten(color, 30), width=int(bw * 0.7))
    draw.line([(x2, y1), (x2, y2)], fill=darken(color, 30), width=int(bw * 0.7))

    if holes:
        width = x2 - x1
        hole_spacing = int(100 * S)
        num_holes = max(1, int(width / hole_spacing))

        for i in range(num_holes):
            hx = x1 + (width / (num_holes + 1)) * (i + 1)
            hy = (y1 + y2) // 2
            hole_r = min(int(24 * S), height // 3)

            # Trou (fond sombre)
            if hole_r > 0:
                draw.ellipse([hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r],
                            fill=darken(color, 70))

                # Anneau intérieur (effet 3D)
                inner_r = max(1, hole_r - int(4 * S))
                draw.ellipse([hx - inner_r, hy - inner_r, hx + inner_r, hy + inner_r],
                            fill=darken(color, 55))

                # Bord lumineux en haut du trou
                arc_margin = int(3*S)
                if hole_r > arc_margin * 2:
                    draw.arc([hx - hole_r + arc_margin, hy - hole_r + arc_margin,
                             hx + hole_r - arc_margin, hy + hole_r - arc_margin],
                            start=200, end=340, fill=darken(color, 35), width=int(4*S))

                    # Bord sombre en bas
                    draw.arc([hx - hole_r + arc_margin, hy - hole_r + arc_margin,
                             hx + hole_r - arc_margin, hy + hole_r - arc_margin],
                            start=20, end=160, fill=darken(color, 80), width=int(3*S))


def draw_lego_cannon(draw, x, y, length, barrel_r, color, accent_color):
    """Dessine un canon LEGO détaillé."""
    l = length * S
    r = barrel_r * S
    bw = int(4 * S)

    # Support/base du canon
    draw_lego_cylinder(draw, x, y, barrel_r * 1.5, barrel_r * 1.2, color, depth=15)

    # Canon principal (tube)
    draw.rectangle([x, y - r*0.5, x + l*0.85, y + r*0.5], fill=color)

    # Reflet sur le tube
    draw.rectangle([x, y - r*0.4, x + l*0.85, y - r*0.15],
                   fill=lighten(color, 35))

    # Ombre sous le tube
    draw.rectangle([x, y + r*0.2, x + l*0.85, y + r*0.45],
                   fill=darken(color, 30))

    # Bout du canon (embout)
    end_x = x + l
    draw_lego_cylinder(draw, end_x - l*0.1, y, barrel_r * 0.8, barrel_r * 0.6,
                       darken(color, 20), depth=0)

    # Bouche du canon (trou noir)
    draw.ellipse([end_x - r*0.5, y - r*0.35, end_x + r*0.1, y + r*0.35],
                fill=(20, 20, 20))

    # Point rouge/accent au bout
    draw.ellipse([end_x - r*0.2, y - r*0.15, end_x, y + r*0.15],
                fill=accent_color)


def draw_lego_missile(draw, x, y, length, width, color, tip_color):
    """Dessine un missile LEGO."""
    l = length * S
    w = width * S

    # Corps du missile
    draw.rectangle([x, y - w*0.4, x + l*0.7, y + w*0.4], fill=color)

    # Reflet
    draw.rectangle([x, y - w*0.35, x + l*0.7, y - w*0.1],
                   fill=lighten(color, 40))

    # Pointe (triangle)
    tip_pts = [
        (x + l*0.7, y - w*0.5),
        (x + l, y),
        (x + l*0.7, y + w*0.5),
    ]
    draw.polygon(tip_pts, fill=tip_color)
    draw.line([tip_pts[0], tip_pts[1]], fill=lighten(tip_color, 40), width=int(2*S))

    # Ailettes arrière
    for side in [-1, 1]:
        fin_pts = [
            (x, y + side * w*0.3),
            (x - l*0.15, y + side * w*0.7),
            (x + l*0.1, y + side * w*0.35),
        ]
        draw.polygon(fin_pts, fill=darken(color, 20))


def draw_lego_turret(draw, cx, cy, size, barrel_count, barrel_len, color, accent_color):
    """Dessine une tourelle LEGO avec nombre variable de canons."""
    sz = size * S
    bl = barrel_len * S

    # Base de la tourelle
    draw_lego_cylinder(draw, cx, cy, size * 1.2, size, darken(color, 15), depth=20)

    # Dôme de la tourelle
    draw_lego_sphere(draw, cx, cy - sz*0.3, size * 0.8, color)

    # Canons
    angle_spread = 8  # degrés entre les canons
    start_angle = -angle_spread * (barrel_count - 1) / 2

    for i in range(barrel_count):
        angle = start_angle + i * angle_spread
        rad = math.radians(angle)

        # Position de départ du canon
        bx = cx + sz * 0.4
        by = cy + math.sin(rad) * sz * 0.3

        # Canon
        end_x = bx + bl * math.cos(rad)
        end_y = by + bl * math.sin(rad)

        # Tube du canon
        draw.line([(bx, by), (end_x, end_y)], fill=darken(color, 30), width=int(10*S))
        draw.line([(bx, by), (end_x, end_y)], fill=color, width=int(7*S))

        # Bout du canon
        draw.ellipse([end_x - 4*S, end_y - 4*S, end_x + 4*S, end_y + 4*S],
                    fill=accent_color)


def draw_lego_engine(draw, cx, cy, outer_r, inner_r, color, glow_color):
    """Dessine un réacteur style LEGO avec effet de propulsion."""
    # Appliquer le facteur d'échelle
    or_s = outer_r * S
    ir_s = inner_r * S

    # Anneau externe (tuyère)
    draw_lego_cylinder(draw, cx, cy, outer_r, outer_r * 0.6, color, depth=45)

    # Intérieur sombre de la tuyère
    draw.ellipse([cx - ir_s, cy - ir_s * 0.6,
                  cx + ir_s, cy + ir_s * 0.6],
                 fill=darken(color, 75))

    # Anneaux concentriques (détail mécanique)
    for i in range(3):
        ring_r = ir_s * (0.9 - i * 0.15)
        draw.arc([cx - ring_r, cy - ring_r * 0.6,
                 cx + ring_r, cy + ring_r * 0.6],
                start=0, end=360, fill=darken(color, 60 + i * 10), width=int(3*S))

    # Coeur lumineux (plasma)
    core_r = ir_s * 0.65
    draw.ellipse([cx - core_r, cy - core_r * 0.5,
                  cx + core_r, cy + core_r * 0.5],
                 fill=glow_color)

    # Halo intérieur
    halo_r = core_r * 0.7
    draw.ellipse([cx - halo_r, cy - halo_r * 0.5,
                  cx + halo_r, cy + halo_r * 0.5],
                 fill=lighten(glow_color, 40))

    # Point central ultra brillant
    dot_r = int(12 * S)
    draw.ellipse([cx - dot_r, cy - dot_r * 0.6,
                 cx + dot_r, cy + dot_r * 0.6],
                 fill=lighten(glow_color, 85))


def draw_lego_wing(draw, points, color, add_detail=True):
    """Dessine une aile LEGO angulaire avec effet plastique."""
    bw = int(8 * S)

    # Surface principale
    draw.polygon(points, fill=color)

    # Bords 3D avec effet chanfreiné
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]

        # Direction du bord
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        if dy < -abs(dx) * 0.3:  # Bord vers le haut
            edge_color = lighten(color, 50)
            width = bw
        elif dy > abs(dx) * 0.3:  # Bord vers le bas
            edge_color = darken(color, 45)
            width = int(bw * 0.8)
        else:
            edge_color = darken(color, 25)
            width = int(bw * 0.7)

        draw.line([p1, p2], fill=edge_color, width=width)

    # Détails de surface (lignes de panneaux)
    if add_detail and len(points) >= 3:
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)

        # Lignes de panneau
        panel_len = int(60 * S)
        draw.line([(cx - panel_len, cy), (cx + panel_len, cy)],
                 fill=darken(color, 20), width=int(4 * S))

        # Stud central sur l'aile
        draw_lego_stud(draw, cx, cy, int(12), lighten(color, 15))


def add_lego_engine_glow(img, positions, glow_color, radius=35):
    """Ajoute l'effet de propulsion aux réacteurs."""
    r = int(radius * S)  # Appliquer le facteur d'échelle

    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    for x, y in positions:
        # Flamme allongée (effet de propulsion)
        for i in range(r, 0, -int(6 * S)):
            alpha = int(130 * (1 - (i / r) ** 0.5))
            stretch = 3.0

            glow_draw.ellipse([
                x - i * stretch, y - i * 0.45,
                x + i * 0.6, y + i * 0.45
            ], fill=(*glow_color[:3], alpha))

        # Halo externe
        halo_r = r * 0.5
        glow_draw.ellipse([x - halo_r * 2, y - halo_r * 0.8,
                          x + halo_r * 0.5, y + halo_r * 0.8],
                         fill=(*glow_color[:3], 80))

        # Coeur brillant
        core_r = r * 0.35
        glow_draw.ellipse([x - core_r, y - core_r * 0.6,
                          x + core_r * 0.4, y + core_r * 0.6],
                         fill=(*lighten(glow_color, 65), 255))

        # Point central ultra-brillant
        dot_r = int(10 * S)
        glow_draw.ellipse([x - dot_r, y - dot_r * 0.6,
                         x + dot_r * 0.5, y + dot_r * 0.6],
                        fill=(255, 255, 255, 255))

    return Image.alpha_composite(img, glow)


def add_shadow(img, offset=None, blur=None, opacity=0.4):
    """Ajoute une ombre portée."""
    off = offset if offset else (int(50 * S), int(70 * S))
    bl = blur if blur else int(40 * S)

    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    alpha = img.split()[3]
    shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, int(255 * opacity)))
    shadow_layer.putalpha(alpha)
    shadow.paste(shadow_layer, off)
    shadow = shadow.filter(ImageFilter.GaussianBlur(bl))

    result = Image.new('RGBA', img.size, (0, 0, 0, 0))
    result = Image.alpha_composite(result, shadow)
    result = Image.alpha_composite(result, img)
    return result


# ============================================================
# GÉNÉRATEURS DE VAISSEAUX LEGO
# ============================================================

def generate_fighter(seed: int, level: int) -> Image.Image:
    """Chasseur LEGO - Style X-Wing/Starfighter avec armes progressives."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed)
    p = get_lego_palette("military")
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    scale = 0.85 + level * 0.05
    body_len = int(320 * scale)
    body_h = int(55 * scale)

    # === AILES (style X-Wing) ===
    wing_span = int(90 * scale) + level * 18
    wing_len = int(180 * scale)

    for side in [-1, 1]:
        wy = cy + side * (body_h + wing_span // 2)

        # Aile principale (plaque LEGO)
        wing_pts = [
            (cx + body_len * 0.15, cy + side * body_h * 0.6),
            (cx + body_len * 0.35, wy - side * 8),
            (cx - body_len * 0.25, wy),
            (cx - body_len * 0.35, cy + side * body_h * 0.7),
        ]
        draw_lego_wing(draw, wing_pts, p["secondary"])

        # Studs sur l'aile
        if abs(wing_pts[1][0] - wing_pts[2][0]) > 60:
            mid_x = (wing_pts[1][0] + wing_pts[2][0]) / 2
            mid_y = (wing_pts[1][1] + wing_pts[2][1]) / 2
            draw_lego_stud(draw, mid_x - 25, mid_y, 7, lighten(p["secondary"], 15))
            draw_lego_stud(draw, mid_x + 25, mid_y, 7, lighten(p["secondary"], 15))

        # === ARMES SUR LES AILES (progressif selon niveau) ===
        # Niveau 1: 1 canon par aile
        # Niveau 2: 1 canon + 1 missile
        # Niveau 3: 2 canons + 1 missile
        # Niveau 4: 2 canons + 2 missiles

        cannon_y = wy
        cannon_x = cx + body_len * 0.2

        # Canon principal (tous niveaux)
        draw_lego_cannon(draw, cannon_x, cannon_y, 60 + level * 12, 8, p["detail"], p["accent"])

        # Second canon (niveau 3+)
        if level >= 3:
            draw_lego_cannon(draw, cannon_x - 30, cannon_y + side * 15, 50 + level * 8, 6,
                            p["detail"], p["accent"])

        # Missiles (niveau 2+)
        if level >= 2:
            missile_x = cx - body_len * 0.1
            draw_lego_missile(draw, missile_x, wy + side * 12, 45, 10,
                             p["secondary"], p["accent"])

            # Second missile (niveau 4)
            if level >= 4:
                draw_lego_missile(draw, missile_x - 40, wy + side * 5, 40, 8,
                                 p["secondary"], p["accent"])

    # === FUSELAGE PRINCIPAL ===
    # Corps central (assemblage de briques)
    draw_lego_brick_3d(draw,
                       cx - body_len * 0.35, cy - body_h,
                       body_len * 0.7, body_h * 1.2, body_h * 0.8,
                       p["primary"])

    # Nez (pente LEGO)
    nose_pts = [
        (cx + body_len * 0.35, cy - body_h * 0.7),
        (cx + body_len * 0.55, cy),
        (cx + body_len * 0.35, cy + body_h * 0.3),
        (cx + body_len * 0.35, cy - body_h * 0.7),
    ]
    draw_lego_slope(draw, nose_pts, p["primary"])

    # === COCKPIT AVEC PILOTE ===
    cockpit_pts = [
        (cx + body_len * 0.15, cy - body_h * 0.85),
        (cx + body_len * 0.32, cy - body_h * 0.4),
        (cx + body_len * 0.28, cy - body_h * 0.25),
        (cx, cy - body_h * 0.6),
    ]
    draw_lego_cockpit_with_pilot(draw, cockpit_pts, p["detail"], p["cockpit"], "serious")

    # === DÉTAILS ===
    # Bande d'accent
    draw_lego_plate(draw,
                    cx - body_len * 0.1, cy - body_h * 0.15,
                    cx + body_len * 0.15, cy + body_h * 0.15,
                    8, p["accent"], add_studs=False)

    # Marquages de niveau
    for i in range(level):
        mx = cx - body_len * 0.2 + i * 28
        draw_lego_stud(draw, mx, cy - body_h * 0.5, 6, p["highlight"])

    # === RÉACTEURS ===
    engines = []
    engine_x = cx - body_len * 0.38

    for side in [-1, 1]:
        ey = cy + side * body_h * 0.45
        draw_lego_engine(draw, engine_x, ey, 28 + level * 3, 18, p["primary"], p["engine"])
        engines.append((engine_x - 35, ey))

    # Réacteur central (niveau 3+)
    if level >= 3:
        draw_lego_engine(draw, engine_x + 10, cy, 22, 14, p["primary"], p["engine"])
        engines.append((engine_x - 25, cy))

    img = add_lego_engine_glow(img, engines, p["engine"], radius=35 + level * 8)
    img = add_shadow(img)

    return img


def generate_bio(seed: int, level: int) -> Image.Image:
    """Vaisseau Bio LEGO - Style créature alien modulaire."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed)
    p = get_lego_palette("alien")
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    scale = 0.82 + level * 0.06
    body_len = int(340 * scale)

    # === QUEUE SEGMENTÉE (briques empilées) ===
    num_segments = 5 + level
    tail_x = cx - body_len * 0.35

    for i in range(num_segments):
        seg_x = tail_x - i * 30
        seg_size = max(18, 38 - i * 3)

        # Segment comme un cylindre LEGO
        draw_lego_cylinder(draw, seg_x, cy, seg_size, seg_size * 0.7, p["primary"], depth=12)

        # Stud sur chaque segment
        if seg_size > 22:
            draw_lego_stud(draw, seg_x, cy - seg_size * 0.3, 6, lighten(p["primary"], 20))

    # Aiguillon caudal
    tail_end = tail_x - num_segments * 30
    sting_pts = [
        (tail_end, cy),
        (tail_end - 50 - level * 10, cy - 15),
        (tail_end - 70 - level * 12, cy),
        (tail_end - 50 - level * 10, cy + 15),
    ]
    draw_lego_slope(draw, sting_pts, p["accent"])

    # === ABDOMEN (briques principales) ===
    abdomen_x = cx - body_len * 0.15
    abdomen_w = int(160 * scale)
    abdomen_h = int(70 * scale)

    draw_lego_brick_3d(draw,
                       abdomen_x - abdomen_w // 2, cy - abdomen_h,
                       abdomen_w, abdomen_h * 1.1, abdomen_h * 0.7,
                       p["primary"])

    # Plaques dorsales
    for i in range(3):
        plate_x = abdomen_x - abdomen_w // 3 + i * (abdomen_w // 3)
        draw_lego_plate(draw,
                        plate_x - 18, cy - abdomen_h - 22,
                        plate_x + 18, cy - abdomen_h - 8,
                        6, p["secondary"], add_studs=False)

    # === TÊTE ===
    head_x = cx + body_len * 0.22
    head_w = int(85 * scale)
    head_h = int(55 * scale)

    # Crâne (forme trapézoïdale LEGO)
    head_pts = [
        (head_x - head_w * 0.4, cy - head_h),
        (head_x + head_w * 0.5, cy - head_h * 0.6),
        (head_x + head_w * 0.7, cy),
        (head_x + head_w * 0.5, cy + head_h * 0.6),
        (head_x - head_w * 0.4, cy + head_h),
        (head_x - head_w * 0.6, cy),
    ]
    draw.polygon(head_pts, fill=p["primary"])

    # Bords de la tête
    for i in range(len(head_pts)):
        draw.line([head_pts[i], head_pts[(i+1) % len(head_pts)]],
                 fill=darken(p["primary"], 30), width=int(3*S))

    # Highlight supérieur
    draw.line([head_pts[0], head_pts[1]], fill=lighten(p["primary"], 40), width=int(3*S))

    # Studs sur la tête
    draw_lego_stud(draw, head_x, cy - head_h * 0.5, 8, lighten(p["primary"], 15))
    draw_lego_stud(draw, head_x - head_w * 0.25, cy, 8, lighten(p["primary"], 15))

    # === MANDIBULES ===
    mand_len = 60 + level * 12
    for side in [-1, 1]:
        mand_pts = [
            (head_x + head_w * 0.5, cy + side * head_h * 0.35),
            (head_x + head_w * 0.5 + mand_len, cy + side * head_h * 0.15),
            (head_x + head_w * 0.5 + mand_len - 15, cy + side * head_h * 0.5),
        ]
        draw_lego_slope(draw, mand_pts, p["accent"])

    # === YEUX ===
    for side in [-1, 1]:
        eye_x = head_x + head_w * 0.35
        eye_y = cy + side * head_h * 0.4

        # Globe (cylindre LEGO)
        draw_lego_cylinder(draw, eye_x, eye_y, 18 + level * 2, 14, p["detail"], depth=8)

        # Pupille
        draw.ellipse([eye_x - 8, eye_y - 6, eye_x + 8, eye_y + 6],
                    fill=(200, 50, 30))
        draw.ellipse([eye_x - 3, eye_y - 3, eye_x + 3, eye_y + 3],
                    fill=(30, 10, 10))

        # Reflet
        draw.ellipse([eye_x + 3, eye_y - 5, eye_x + 7, eye_y - 1],
                    fill=(255, 220, 200))

    # === PATTES (poutres Technic) ===
    num_legs = 4 + level // 2
    for i in range(num_legs):
        leg_x = abdomen_x - abdomen_w // 2 + 20 + i * (abdomen_w // num_legs)

        # Segment supérieur
        draw_lego_technic_beam(draw,
                               leg_x - 8, cy + abdomen_h * 0.5,
                               leg_x + 8, cy + abdomen_h * 0.5 + 45,
                               p["secondary"], holes=True)

        # Segment inférieur (plus petit)
        draw_lego_technic_beam(draw,
                               leg_x - 6, cy + abdomen_h * 0.5 + 48,
                               leg_x + 6, cy + abdomen_h * 0.5 + 85,
                               p["detail"], holes=False)

    # === ORGANE BIOLUMINESCENT (niveau 3+) ===
    if level >= 3:
        organ_x = abdomen_x
        organ_r = 28 + level * 5

        draw_lego_cylinder(draw, organ_x, cy, organ_r + 6, organ_r * 0.6, p["detail"], depth=10)
        draw.ellipse([organ_x - organ_r, cy - organ_r * 0.5,
                     organ_x + organ_r, cy + organ_r * 0.5],
                    fill=p["cockpit"])
        draw.ellipse([organ_x - organ_r * 0.4, cy - organ_r * 0.25,
                     organ_x + organ_r * 0.4, cy + organ_r * 0.25],
                    fill=lighten(p["cockpit"], 60))

    # === PROPULSION ===
    engines = []
    prop_x = tail_end - 25

    for offset in [-20, 20]:
        draw_lego_engine(draw, prop_x, cy + offset, 22, 14, p["secondary"], p["engine"])
        engines.append((prop_x - 30, cy + offset))

    img = add_lego_engine_glow(img, engines, p["engine"], radius=28 + level * 6)
    img = add_shadow(img)

    return img


def generate_scout(seed: int, level: int) -> Image.Image:
    """Éclaireur LEGO - Style sonde/satellite compact."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed)
    p = get_lego_palette("recon")
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    scale = 0.88 + level * 0.04
    body_r = int(80 * scale)

    # === CORPS SPHÉRIQUE (cylindre vu de dessus style LEGO) ===
    draw_lego_cylinder(draw, cx, cy, body_r, body_r, p["primary"], depth=35)

    # Anneau équatorial
    ring_h = 14 + level * 2
    draw_lego_plate(draw,
                    cx - body_r - 15, cy - ring_h,
                    cx + body_r + 15, cy + ring_h,
                    10, p["secondary"], add_studs=True)

    # === NACELLES LATÉRALES ===
    engines = []
    nacelle_offset = body_r + 55

    for side in [-1, 1]:
        ny = cy + side * nacelle_offset

        # Pylône (poutre Technic)
        draw_lego_technic_beam(draw,
                               cx - 10, min(cy, ny) + 15,
                               cx + 10, max(cy, ny) - 15,
                               p["detail"], holes=True)

        # Nacelle (brique)
        nacelle_w = 90 + level * 10
        nacelle_h = 28 + level * 4

        draw_lego_brick_3d(draw,
                          cx - nacelle_w // 2, ny - nacelle_h,
                          nacelle_w, nacelle_h * 0.9, nacelle_h * 0.6,
                          p["primary"])

        # Réacteur
        engine_r = 22 + level * 3
        draw_lego_engine(draw, cx - nacelle_w // 2 - 5, ny, engine_r, engine_r - 6,
                        p["secondary"], p["engine"])
        engines.append((cx - nacelle_w // 2 - engine_r - 20, ny))

    # Nacelles supplémentaires (niveau 3+)
    if level >= 3:
        for side in [-1, 1]:
            ny = cy + side * (nacelle_offset + 60)

            draw_lego_technic_beam(draw,
                                   cx - 8, min(cy, ny) + 20,
                                   cx + 8, max(cy, ny) - 12,
                                   p["detail"], holes=False)

            draw_lego_brick_3d(draw,
                              cx - 45, ny - 20,
                              90, 22, 18,
                              p["secondary"])

            draw_lego_engine(draw, cx - 52, ny, 18, 12, p["secondary"], p["engine"])
            engines.append((cx - 72, ny))

    # === ANTENNE PRINCIPALE ===
    antenna_len = int(110 * scale) + level * 20
    antenna_end = cx + body_r + antenna_len

    # Mât (poutre)
    draw_lego_technic_beam(draw,
                           cx + body_r, cy - 8,
                           antenna_end - 25, cy + 8,
                           p["detail"], holes=True)

    # Parabole (disque LEGO)
    dish_r = 32 + level * 6
    draw_lego_cylinder(draw, antenna_end, cy, dish_r, dish_r, p["primary"], depth=12)
    draw_lego_cylinder(draw, antenna_end, cy, dish_r * 0.5, dish_r * 0.5, p["accent"], depth=0)
    draw_lego_stud(draw, antenna_end, cy, 8, p["highlight"])

    # === COCKPIT CENTRAL AVEC PILOTE ===
    cockpit_r = body_r * 0.5
    # Dessiner un petit cockpit en dôme
    cockpit_pts = [
        (cx - cockpit_r * 0.8, cy - cockpit_r * 0.6),
        (cx + cockpit_r * 0.8, cy - cockpit_r * 0.6),
        (cx + cockpit_r * 0.6, cy + cockpit_r * 0.4),
        (cx - cockpit_r * 0.6, cy + cockpit_r * 0.4),
    ]
    draw_lego_cockpit_with_pilot(draw, cockpit_pts, p["detail"], p["cockpit"], "happy")

    # Antennes secondaires (niveau 2+)
    if level >= 2:
        for angle in [45, -45]:
            rad = math.radians(angle)
            base_x = cx + body_r * 0.7 * math.cos(rad)
            base_y = cy + body_r * 0.7 * math.sin(rad)
            end_x = base_x + 55 * math.cos(rad)
            end_y = base_y + 55 * math.sin(rad)

            draw.line([(base_x, base_y), (end_x, end_y)],
                     fill=p["detail"], width=int(6*S))
            draw_lego_cylinder(draw, end_x, end_y, 10, 10, p["accent"], depth=0)

    img = add_lego_engine_glow(img, engines, p["engine"], radius=24 + level * 6)
    img = add_shadow(img)

    return img


def generate_colony(seed: int, level: int) -> Image.Image:
    """Vaisseau Colonial LEGO - Style cargo/transport modulaire avec pilote."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed)
    p = get_lego_palette("industrial")
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    scale = 0.8 + level * 0.07
    body_len = int(320 * scale)
    body_h = int(85 * scale)

    # === COQUE PRINCIPALE (grande brique) ===
    hull_x = cx - body_len * 0.4
    hull_w = body_len * 0.8

    draw_lego_brick_3d(draw,
                       hull_x, cy - body_h,
                       hull_w, body_h * 1.1, body_h * 0.8,
                       p["primary"])

    # === MODULES CARGO (briques empilées avec fenêtres) ===
    num_modules = level + 1
    module_spacing = hull_w / (num_modules + 0.5)

    for i in range(num_modules):
        mx = hull_x + module_spacing * (i + 0.75)
        my = cy - body_h - 45

        # Module (petite brique)
        draw_lego_brick_3d(draw,
                          mx - 30, my - 35,
                          60, 40, 30,
                          p["secondary"])

        # Fenêtres du module avec minifigs visibles
        for row in range(2):
            for col in range(2):
                wx = mx - 15 + col * 30
                wy = my - 28 + row * 18
                # Fenêtre
                draw.rectangle([wx - 8, wy - 5, wx + 8, wy + 5],
                              fill=p["cockpit"])
                # Petite tête de minifig dans la fenêtre
                if row == 0:  # Seulement rangée du haut
                    draw_lego_minifig_head(draw, wx, wy, 4, "happy")

    # === PONT DE COMMANDEMENT AVEC PILOTE ===
    bridge_x = cx + body_len * 0.35
    bridge_w = 70
    bridge_h = 50

    # Tour
    draw_lego_brick_3d(draw,
                       bridge_x - bridge_w // 2, cy - body_h - bridge_h,
                       bridge_w, bridge_h, 35,
                       p["secondary"])

    # Cockpit avec pilote
    cockpit_pts = [
        (bridge_x - bridge_w * 0.4, cy - body_h - bridge_h - 8),
        (bridge_x + bridge_w * 0.4, cy - body_h - bridge_h - 8),
        (bridge_x + bridge_w * 0.35, cy - body_h - bridge_h + 22),
        (bridge_x - bridge_w * 0.35, cy - body_h - bridge_h + 22),
    ]
    draw_lego_cockpit_with_pilot(draw, cockpit_pts, p["detail"], p["cockpit"], "happy")

    # === BANDE D'AVERTISSEMENT ===
    stripe_y = cy - body_h * 0.1
    for i in range(8):
        sx = hull_x + 15 + i * (hull_w - 30) / 8
        stripe_color = p["highlight"] if i % 2 == 0 else p["detail"]
        draw.rectangle([sx, stripe_y - 12, sx + (hull_w - 30) / 16, stripe_y + 12],
                      fill=stripe_color)

    # === GRUES DE CHARGEMENT (niveau 2+) ===
    if level >= 2:
        for i in range(min(level - 1, 3)):
            crane_x = hull_x + hull_w * 0.2 + i * hull_w * 0.3
            crane_y = cy - body_h - 60

            # Base
            draw_lego_cylinder(draw, crane_x, crane_y, 15, 15, p["detail"], depth=20)

            # Bras
            arm_len = 55 + level * 8
            draw_lego_technic_beam(draw,
                                   crane_x - 6, crane_y - 50,
                                   crane_x + arm_len, crane_y - 38,
                                   p["highlight"], holes=True)

    # === RÉACTEURS ===
    engines = []
    engine_x = hull_x - 5
    num_engines = 3 + level // 2

    for i in range(num_engines):
        t = i / (num_engines - 1) if num_engines > 1 else 0.5
        ey = cy - body_h * 0.5 + t * body_h

        draw_lego_engine(draw, engine_x, ey, 30 + level * 2, 20, p["secondary"], p["engine"])
        engines.append((engine_x - 35, ey))

    img = add_lego_engine_glow(img, engines, p["engine"], radius=30 + level * 7)
    img = add_shadow(img)

    return img


def generate_satellite(seed: int, level: int) -> Image.Image:
    """Satellite LEGO - Station orbitale TRÈS RONDE."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed)
    p = get_lego_palette("tech")
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    scale = 0.82 + level * 0.06
    body_r = int(85 * scale)  # Plus grand pour être plus rond

    # === CORPS CENTRAL SPHÉRIQUE ===
    draw_lego_sphere(draw, cx, cy, body_r, p["primary"])

    # Anneaux décoratifs sur la sphère
    for ring_offset in [-body_r * 0.4, 0, body_r * 0.4]:
        ring_y = cy + ring_offset * S
        ring_r = body_r * math.sqrt(1 - (ring_offset / body_r) ** 2) if abs(ring_offset) < body_r else 0
        if ring_r > 10:
            draw.arc([cx - ring_r * S, ring_y - 4*S, cx + ring_r * S, ring_y + 4*S],
                    start=0, end=360, fill=darken(p["primary"], 30), width=int(3*S))

    # Studs sur la sphère (en cercle)
    num_studs = 4 + level
    for i in range(num_studs):
        angle = (i / num_studs) * 2 * math.pi
        stud_r = body_r * 0.7
        sx = cx + stud_r * S * math.cos(angle)
        sy = cy + stud_r * S * 0.5 * math.sin(angle)  # Perspective
        draw_lego_stud(draw, sx, sy, 8, lighten(p["primary"], 20))

    # === ANNEAU ÉQUATORIAL ===
    ring_r = body_r * 1.3
    draw_lego_plate(draw,
                    cx - ring_r * S - 10, cy - 12*S,
                    cx + ring_r * S + 10, cy + 12*S,
                    10, p["secondary"], add_studs=True)

    # === MODULES SPHÉRIQUES LATÉRAUX ===
    for side in [-1, 1]:
        module_x = cx + side * (body_r + 45) * S
        # Petite sphère attachée
        draw_lego_sphere(draw, module_x, cy, body_r * 0.4, p["secondary"])

        # Connecteur (s'assurer que x1 < x2)
        conn_x1 = cx + side * body_r * S * 0.7
        conn_x2 = module_x - side * body_r * 0.3 * S
        draw.rectangle([min(conn_x1, conn_x2), cy - 8*S,
                       max(conn_x1, conn_x2), cy + 8*S],
                      fill=p["detail"])

    # === PANNEAUX SOLAIRES ===
    panel_len = int(140 * scale) + level * 30
    panel_h = 20 + level * 5

    for side in [-1, 1]:
        py = cy + side * (body_r * 1.4 * S + 30)

        # Bras de support (poutre Technic)
        draw_lego_technic_beam(draw,
                               cx - 10, min(cy, py) + 15,
                               cx + 10, max(cy, py) - 15,
                               p["detail"], holes=True)

        # Panneau solaire (grande plaque)
        panel_x1 = cx - panel_len // 2
        panel_x2 = cx + panel_len // 2

        # Cadre
        draw_lego_plate(draw,
                        panel_x1 - 6, py - panel_h - 6,
                        panel_x2 + 6, py + panel_h + 6,
                        10, p["secondary"], add_studs=False)

        # Cellules solaires (bleu foncé)
        draw.rectangle([panel_x1, py - panel_h, panel_x2, py + panel_h],
                      fill=(25, 45, 80))

        # Grille de cellules
        num_cells = 6 + level
        cell_w = (panel_x2 - panel_x1) / num_cells
        for i in range(num_cells + 1):
            x = panel_x1 + i * cell_w
            draw.line([(x, py - panel_h), (x, py + panel_h)],
                     fill=(45, 75, 120), width=int(2*S))

        for j in range(3):
            y = py - panel_h + j * panel_h
            draw.line([(panel_x1, y), (panel_x2, y)],
                     fill=(45, 75, 120), width=int(2*S))

    # === ANTENNE PARABOLIQUE ===
    antenna_len = int(95 * scale) + level * 18
    dish_r = 35 + level * 7
    dish_x = cx + body_r * S + antenna_len

    # Support
    draw_lego_technic_beam(draw,
                           cx + body_r * S * 0.8, cy - 7,
                           dish_x - dish_r, cy + 7,
                           p["detail"], holes=True)

    # Parabole (plus ronde)
    draw_lego_sphere(draw, dish_x, cy, dish_r * 0.8, p["primary"])
    draw_lego_cylinder(draw, dish_x, cy, dish_r * 0.3, dish_r * 0.3, p["accent"], depth=0)
    draw_lego_stud(draw, dish_x, cy, 7, p["highlight"])

    # === TOURELLES (niveau 2+) ===
    if level >= 2:
        turret_angles = [45, -45]
        if level >= 3:
            turret_angles.extend([135, -135])

        for angle in turret_angles:
            rad = math.radians(angle)
            tx = cx + int(body_r * 0.85 * S * math.cos(rad))
            ty = cy + int(body_r * 0.85 * S * math.sin(rad))

            # Base tourelle (sphérique)
            draw_lego_sphere(draw, tx, ty, 14, p["secondary"])

            # Canon
            barrel_len = 35 + level * 5
            end_x = tx + barrel_len * math.cos(rad)
            end_y = ty + barrel_len * math.sin(rad)

            draw.line([(tx, ty), (end_x, end_y)], fill=p["detail"], width=int(8*S))
            draw.line([(tx, ty), (end_x, end_y)], fill=p["secondary"], width=int(5*S))

            # Bout du canon
            draw.ellipse([end_x - 5*S, end_y - 5*S, end_x + 5*S, end_y + 5*S],
                        fill=p["accent"])

    # === COCKPIT AVEC PILOTE (au centre) ===
    cockpit_r = body_r * 0.35
    cockpit_pts = [
        (cx - cockpit_r * S, cy - cockpit_r * S * 0.7),
        (cx + cockpit_r * S, cy - cockpit_r * S * 0.7),
        (cx + cockpit_r * S * 0.8, cy + cockpit_r * S * 0.5),
        (cx - cockpit_r * S * 0.8, cy + cockpit_r * S * 0.5),
    ]
    draw_lego_cockpit_with_pilot(draw, cockpit_pts, p["detail"], p["cockpit"], "happy")

    # === PROPULSEUR ===
    engines = []
    engine_x = cx - body_r * S - 8
    draw_lego_engine(draw, engine_x, cy, 18 + level * 2, 12, p["secondary"], p["engine"])
    engines.append((engine_x - 25, cy))

    img = add_lego_engine_glow(img, engines, p["engine"], radius=18 + level * 5)
    img = add_shadow(img)

    return img


def generate_tanker(seed: int, level: int) -> Image.Image:
    """Ravitailleur LEGO - Gros bidons/citernes style camion-citerne."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed)
    p = get_lego_palette("industrial")
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    scale = 0.8 + level * 0.07

    # Configuration des GROS bidons
    num_tanks = 2 + level  # Plus de bidons selon le niveau
    tank_w = int(90 * scale)  # Largeur de chaque bidon
    tank_h = int(70 * scale)  # Hauteur de chaque bidon
    tank_spacing = tank_w * 1.1
    total_w = (num_tanks - 1) * tank_spacing
    start_x = cx - total_w // 2

    # === GROS BIDONS CYLINDRIQUES ===
    for i in range(num_tanks):
        tx = start_x + i * tank_spacing

        # Dessiner un gros bidon horizontal
        draw_lego_tank_drum(draw, tx, cy, tank_w, tank_h, p["secondary"], with_bands=True)

        # Marquage danger sur le bidon
        draw.rectangle([tx - tank_w*0.25*S, cy - tank_h*0.5*S - 10*S,
                       tx + tank_w*0.25*S, cy - tank_h*0.5*S + 5*S],
                      fill=p["highlight"])

        # Texte "FUEL" stylisé (juste des rectangles)
        fuel_x = tx - tank_w*0.15*S
        for j in range(3):
            draw.rectangle([fuel_x + j*8*S, cy - tank_h*0.5*S - 6*S,
                           fuel_x + j*8*S + 4*S, cy - tank_h*0.5*S + 2*S],
                          fill=p["detail"])

        # Jauge de niveau sur le côté
        gauge_x = tx + tank_w*0.35*S
        gauge_h = tank_h * 0.6 * S

        # Cadre de jauge
        draw.rectangle([gauge_x - 6*S, cy - gauge_h // 2,
                       gauge_x + 6*S, cy + gauge_h // 2],
                      fill=p["detail"])

        # Niveau de carburant (variable)
        fill_level = 0.35 + level * 0.12 + i * 0.08
        fill_h = int(gauge_h * min(0.85, fill_level))
        draw.rectangle([gauge_x - 4*S, cy + gauge_h // 2 - fill_h,
                       gauge_x + 4*S, cy + gauge_h // 2 - 3*S],
                      fill=p["engine"][:3])

        # Studs décoratifs sur le bidon
        draw_lego_stud(draw, tx - tank_w*0.15*S, cy, 10, lighten(p["secondary"], 15))
        draw_lego_stud(draw, tx + tank_w*0.15*S, cy, 10, lighten(p["secondary"], 15))

    # === STRUCTURE PORTEUSE ===
    struct_y = cy + tank_h * 0.5 * S + 30*S
    struct_x1 = start_x - tank_w * 0.6 * S
    struct_x2 = start_x + (num_tanks - 1) * tank_spacing + tank_w * 0.6 * S

    draw_lego_technic_beam(draw,
                           struct_x1, struct_y - 18*S,
                           struct_x2, struct_y + 18*S,
                           p["primary"], holes=True)

    # Connecteurs aux bidons
    for i in range(num_tanks):
        tx = start_x + i * tank_spacing
        draw_lego_technic_beam(draw,
                               tx - 14*S, cy + tank_h*0.4*S,
                               tx + 14*S, struct_y - 15*S,
                               p["detail"], holes=False)

    # === CABINE AVEC PILOTE ===
    cabin_x = struct_x2 + 60*S
    cabin_w = 80*S
    cabin_h = 65*S

    draw_lego_brick_3d(draw,
                       cabin_x - cabin_w // 2, cy - cabin_h,
                       cabin_w, cabin_h * 0.9, cabin_h * 0.7,
                       p["secondary"])

    # Cockpit avec pilote
    cockpit_pts = [
        (cabin_x - cabin_w * 0.4, cy - cabin_h - 8*S),
        (cabin_x + cabin_w * 0.4, cy - cabin_h - 8*S),
        (cabin_x + cabin_w * 0.35, cy - cabin_h + 28*S),
        (cabin_x - cabin_w * 0.35, cy - cabin_h + 28*S),
    ]
    draw_lego_cockpit_with_pilot(draw, cockpit_pts, p["detail"], p["cockpit"], "happy")

    # === BRAS DE RAVITAILLEMENT ===
    num_arms = min(level, 3)
    for i in range(num_arms):
        arm_x = start_x + i * tank_spacing + tank_spacing // 2
        arm_y = cy - tank_h * 0.5 * S - 15*S

        # Bras articulé
        draw_lego_technic_beam(draw,
                               arm_x - 60*S, arm_y - 45*S,
                               arm_x + 15*S, arm_y - 30*S,
                               p["highlight"], holes=True)

        # Tête de ravitaillement (embout de pompe)
        draw_lego_cylinder(draw, arm_x - 65, arm_y - 40, 18, 18, p["secondary"], depth=10)
        draw_lego_cylinder(draw, arm_x - 65, arm_y - 40, 10, 10, p["engine"][:3], depth=0)

        # Tuyau flexible (courbé)
        for j in range(5):
            pipe_x = arm_x - 65 - j * 12
            pipe_y = arm_y - 40 + j * 8
            draw.ellipse([pipe_x - 5*S, pipe_y - 5*S, pipe_x + 5*S, pipe_y + 5*S],
                        fill=p["detail"])

    # === RÉSERVOIR SUPPLÉMENTAIRE (niveau 3+) ===
    if level >= 3:
        extra_x = struct_x1 - 50*S
        draw_lego_tank_drum(draw, extra_x, cy - 20, tank_w * 0.6, tank_h * 0.5,
                           p["primary"], with_bands=True)

    # === RÉACTEURS ===
    engines = []
    engine_x = struct_x1 - 20*S

    for i in range(2 + (level >= 3)):
        ey = struct_y - 15*S + i * 20*S
        draw_lego_engine(draw, engine_x, ey, 28, 18, p["secondary"], p["engine"])
        engines.append((engine_x - 35, ey))

    img = add_lego_engine_glow(img, engines, p["engine"], radius=28 + level * 6)
    img = add_shadow(img)

    return img


def generate_battleship(seed: int, level: int) -> Image.Image:
    """Cuirassé LEGO - Navire de guerre MASSIF et INTIMIDANT."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed)
    p = get_lego_palette("warship")
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    # Plus gros selon le niveau
    scale = 0.80 + level * 0.08  # Augmenté
    body_len = int(420 * scale)  # Plus long
    body_h = int(95 * scale)  # Plus haut

    # === COQUE PRINCIPALE (MASSIVE) ===
    hull_x = cx - body_len * 0.48
    hull_w = body_len * 0.96

    draw_lego_brick_3d(draw,
                       hull_x, cy - body_h,
                       hull_w, body_h * 1.2, body_h * 0.85,
                       p["primary"])

    # Seconde couche de blindage
    armor_margin = 25 * S
    draw_lego_plate(draw,
                    hull_x + armor_margin, cy - body_h * 0.8,
                    hull_x + hull_w - armor_margin, cy - body_h * 0.6,
                    12, darken(p["primary"], 15), add_studs=True)

    # Proue AGRESSIVE (pente LEGO pointue)
    bow_pts = [
        (hull_x + hull_w, cy - body_h * 0.8),
        (hull_x + hull_w + body_len * 0.15, cy - body_h * 0.2),
        (hull_x + hull_w + body_len * 0.18, cy),  # Pointe
        (hull_x + hull_w + body_len * 0.15, cy + body_h * 0.2),
        (hull_x + hull_w, cy + body_h * 0.4),
    ]
    draw.polygon(bow_pts, fill=p["primary"])
    draw.line([bow_pts[0], bow_pts[1]], fill=lighten(p["primary"], 40), width=int(6*S))
    draw.line([bow_pts[2], bow_pts[3]], fill=darken(p["primary"], 30), width=int(4*S))

    # Éperon de proue (agressif)
    ram_pts = [
        (hull_x + hull_w + body_len * 0.15, cy),
        (hull_x + hull_w + body_len * 0.25, cy - body_h * 0.1),
        (hull_x + hull_w + body_len * 0.28, cy),
        (hull_x + hull_w + body_len * 0.25, cy + body_h * 0.1),
    ]
    draw.polygon(ram_pts, fill=p["accent"])
    draw.line([ram_pts[0], ram_pts[1]], fill=lighten(p["accent"], 40), width=int(4*S))

    # === AILERONS IMPOSANTS ===
    fin_h = int(80 * scale) + level * 15

    for side in [-1, 1]:
        fin_pts = [
            (hull_x + hull_w * 0.2, cy + side * body_h * 0.5),
            (hull_x + hull_w * 0.12, cy + side * (body_h + fin_h * 0.85)),
            (hull_x - hull_w * 0.05, cy + side * (body_h + fin_h)),
            (hull_x - hull_w * 0.02, cy + side * body_h * 0.7),
        ]
        draw_lego_wing(draw, fin_pts, p["secondary"])

        # Studs sur l'aileron
        fin_cx = sum(pt[0] for pt in fin_pts) / 4
        fin_cy = sum(pt[1] for pt in fin_pts) / 4
        draw_lego_stud(draw, fin_cx, fin_cy, 9, lighten(p["secondary"], 15))
        draw_lego_stud(draw, fin_cx - 30*S, fin_cy, 7, lighten(p["secondary"], 15))

    # === SUPERSTRUCTURE (TOUR DE COMMANDEMENT) ===
    tower_x = cx + body_len * 0.05
    tower_w = int(90 * scale)
    tower_h = int(75 * scale)

    # Base de la tour
    draw_lego_brick_3d(draw,
                       tower_x - tower_w // 2, cy - body_h - tower_h * 0.6,
                       tower_w, tower_h * 0.6, 45,
                       p["secondary"])

    # Tour supérieure
    draw_lego_brick_3d(draw,
                       tower_x - tower_w * 0.35, cy - body_h - tower_h,
                       tower_w * 0.7, tower_h * 0.45, 35,
                       darken(p["secondary"], 10))

    # Passerelle avec pilote
    bridge_y = cy - body_h - tower_h + 20*S
    cockpit_pts = [
        (tower_x - tower_w * 0.35, bridge_y - 35*S),
        (tower_x + tower_w * 0.35, bridge_y - 35*S),
        (tower_x + tower_w * 0.3, bridge_y + 5*S),
        (tower_x - tower_w * 0.3, bridge_y + 5*S),
    ]
    draw_lego_cockpit_with_pilot(draw, cockpit_pts, p["detail"], p["cockpit"], "angry")

    # Mât radar imposant
    mast_h = 50*S + level * 12*S
    mast_top = cy - body_h - tower_h - mast_h
    mast_bottom = cy - body_h - tower_h
    draw.rectangle([tower_x - 5*S, mast_top,
                   tower_x + 5*S, mast_bottom],
                  fill=p["detail"])

    # Radar rotatif
    draw_lego_cylinder(draw, tower_x, cy - body_h - tower_h - mast_h + 10,
                       22, 8, p["secondary"], depth=0)

    # === TOURELLES PRINCIPALES (PROGRESSIF) ===
    # Niveau 1: 2 tourelles doubles
    # Niveau 2: 3 tourelles doubles
    # Niveau 3: 3 tourelles doubles + 2 triples
    # Niveau 4: 4 tourelles triples

    turret_configs = {
        1: [
            (hull_x + hull_w * 0.75, cy - body_h * 0.8, 2, 65),
            (hull_x + hull_w * 0.45, cy + body_h * 0.7, 2, 55),
        ],
        2: [
            (hull_x + hull_w * 0.78, cy - body_h * 0.8, 2, 70),
            (hull_x + hull_w * 0.50, cy - body_h * 0.75, 2, 65),
            (hull_x + hull_w * 0.45, cy + body_h * 0.72, 2, 60),
        ],
        3: [
            (hull_x + hull_w * 0.80, cy - body_h * 0.8, 3, 75),
            (hull_x + hull_w * 0.52, cy - body_h * 0.78, 2, 70),
            (hull_x + hull_w * 0.28, cy - body_h * 0.75, 3, 65),
            (hull_x + hull_w * 0.48, cy + body_h * 0.73, 2, 60),
            (hull_x + hull_w * 0.70, cy + body_h * 0.76, 2, 55),
        ],
        4: [
            (hull_x + hull_w * 0.82, cy - body_h * 0.82, 3, 80),
            (hull_x + hull_w * 0.55, cy - body_h * 0.80, 3, 75),
            (hull_x + hull_w * 0.30, cy - body_h * 0.78, 3, 70),
            (hull_x + hull_w * 0.50, cy + body_h * 0.75, 3, 65),
            (hull_x + hull_w * 0.72, cy + body_h * 0.78, 3, 60),
            (hull_x + hull_w * 0.25, cy + body_h * 0.73, 2, 55),
        ],
    }

    for tx, ty, barrel_count, barrel_len in turret_configs[level]:
        draw_lego_turret(draw, tx, ty, 22 + level * 2, barrel_count, barrel_len,
                        p["secondary"], p["accent"])

    # === MISSILES (niveau 3+) ===
    if level >= 3:
        missile_x = hull_x + hull_w * 0.15
        for i in range(level - 1):
            my = cy - body_h * 0.6 + i * 25*S
            draw_lego_missile(draw, missile_x, my, 50, 12, p["detail"], p["accent"])

    # === EMBLÈME INTIMIDANT ===
    emblem_x = hull_x + hull_w * 0.88
    emblem_r = 28 + level * 5

    draw_lego_cylinder(draw, emblem_x, cy, emblem_r, emblem_r, p["highlight"], depth=0)

    # Tête de mort stylisée (plus détaillée)
    skull_color = p["detail"]
    # Crâne
    draw.ellipse([emblem_x - emblem_r * 0.7, cy - emblem_r * 0.8,
                 emblem_x + emblem_r * 0.7, cy + emblem_r * 0.5],
                fill=skull_color)

    # Yeux menaçants
    for side in [-1, 1]:
        ex = emblem_x + side * emblem_r * 0.3
        ey = cy - emblem_r * 0.15
        # Orbite
        draw.ellipse([ex - 6*S, ey - 6*S, ex + 6*S, ey + 6*S], fill=(30, 10, 10))
        # Pupille rouge
        draw.ellipse([ex - 3*S, ey - 3*S, ex + 3*S, ey + 3*S], fill=p["accent"])

    # Mâchoire
    draw.rectangle([emblem_x - emblem_r * 0.4, cy + emblem_r * 0.2,
                   emblem_x + emblem_r * 0.4, cy + emblem_r * 0.4],
                  fill=skull_color)
    # Dents
    for i in range(4):
        tooth_x = emblem_x - emblem_r * 0.3 + i * emblem_r * 0.2
        draw.rectangle([tooth_x, cy + emblem_r * 0.15,
                       tooth_x + emblem_r * 0.1, cy + emblem_r * 0.35],
                      fill=(200, 200, 200))

    # === RÉACTEURS MASSIFS ===
    engines = []
    engine_x = hull_x - 12*S
    num_engines = 3 + level // 2

    for i in range(num_engines):
        t = i / (num_engines - 1) if num_engines > 1 else 0.5
        ey = cy - body_h * 0.45 + t * body_h * 0.9

        draw_lego_engine(draw, engine_x, ey, 38 + level * 4, 26, p["secondary"], p["engine"])
        engines.append((engine_x - 50*S, ey))

    img = add_lego_engine_glow(img, engines, p["engine"], radius=50 + level * 12)
    img = add_shadow(img, offset=(int(22*S), int(28*S)), blur=int(18*S), opacity=0.5)

    return img


def generate_decoy(seed: int, level: int) -> Image.Image:
    """Leurre LEGO - Vaisseau furtif angulaire avec pilote."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    random.seed(seed)
    p = get_lego_palette("stealth")
    cx, cy = RENDER_SIZE // 2, RENDER_SIZE // 2

    scale = 0.8 + level * 0.06
    body_len = int(220 * scale)
    body_h = int(50 * scale)

    # === COQUE FURTIVE (très angulaire) ===
    hull_pts = [
        (cx + body_len * 0.55, cy),
        (cx + body_len * 0.4, cy - body_h * 0.4),
        (cx + body_len * 0.15, cy - body_h * 0.65),
        (cx - body_len * 0.25, cy - body_h * 0.6),
        (cx - body_len * 0.45, cy - body_h * 0.25),
        (cx - body_len * 0.45, cy + body_h * 0.25),
        (cx - body_len * 0.25, cy + body_h * 0.6),
        (cx + body_len * 0.15, cy + body_h * 0.65),
        (cx + body_len * 0.4, cy + body_h * 0.4),
    ]

    # Face principale
    draw.polygon(hull_pts, fill=p["primary"])

    # Bords angulaires avec éclairage
    for i in range(len(hull_pts)):
        p1 = hull_pts[i]
        p2 = hull_pts[(i + 1) % len(hull_pts)]
        dy = p2[1] - p1[1]

        if dy < -10:
            edge_color = lighten(p["primary"], 35)
            width = int(3*S)
        elif dy > 10:
            edge_color = darken(p["primary"], 35)
            width = int(2*S)
        else:
            edge_color = darken(p["primary"], 15)
            width = int(2*S)

        draw.line([p1, p2], fill=edge_color, width=width)

    # Panneaux furtifs (lignes angulaires)
    for i in range(3 + level):
        px1 = cx - body_len * 0.35 + i * body_len * 0.15
        draw.line([(px1, cy - body_h * 0.55), (px1 + 25, cy + body_h * 0.55)],
                 fill=p["secondary"], width=int(3*S))

    # === AILERONS ANGULAIRES ===
    fin_h = int(40 * scale) + level * 6

    for side in [-1, 1]:
        fin_pts = [
            (cx - body_len * 0.2, cy + side * body_h * 0.5),
            (cx - body_len * 0.38, cy + side * (body_h + fin_h * 0.75)),
            (cx - body_len * 0.32, cy + side * (body_h + fin_h)),
            (cx - body_len * 0.25, cy + side * body_h * 0.55),
        ]
        draw_lego_wing(draw, fin_pts, p["secondary"], add_detail=False)

    # === VRAI COCKPIT AVEC PILOTE ===
    cockpit_pts = [
        (cx + body_len * 0.2, cy - body_h * 0.5),
        (cx + body_len * 0.38, cy - body_h * 0.25),
        (cx + body_len * 0.35, cy - body_h * 0.1),
        (cx + body_len * 0.12, cy - body_h * 0.35),
    ]
    draw_lego_cockpit_with_pilot(draw, cockpit_pts, p["detail"], p["cockpit"], "serious")

    # Fausses tourelles (niveau 2+)
    if level >= 2:
        for i, (fx, fy) in enumerate([(cx + body_len * 0.28, cy - body_h * 0.58),
                                       (cx - body_len * 0.02, cy - body_h * 0.52)]):
            if i < level - 1:
                draw_lego_cylinder(draw, fx, fy, 10, 8, p["secondary"], depth=6)
                draw.line([(fx, fy), (fx + 25, fy - 3)], fill=p["detail"], width=int(4*S))

    # === ÉMETTEURS DE LEURRE ===
    if level >= 2:
        for side in [-1, 1]:
            ex = cx
            ey = cy + side * body_h * 0.4

            draw_lego_cylinder(draw, ex, ey, 12, 12, p["secondary"], depth=8)
            draw.ellipse([ex - 7*S, ey - 7*S, ex + 7*S, ey + 7*S], fill=p["engine"][:3])
            draw.ellipse([ex - 3*S, ey - 3*S, ex + 3*S, ey + 3*S],
                        fill=lighten(p["engine"][:3], 60))

    # Émetteurs latéraux (niveau 3+)
    if level >= 3:
        for i in range(2):
            ex = cx - body_len * 0.2 + i * body_len * 0.25
            for side in [-1, 1]:
                ey = cy + side * body_h * 0.5
                draw_lego_cylinder(draw, ex, ey, 8, 8, p["detail"], depth=0)
                draw.ellipse([ex - 4*S, ey - 4*S, ex + 4*S, ey + 4*S], fill=p["engine"][:3])

    # === RÉACTEURS ===
    engines = []
    engine_x = cx - body_len * 0.43

    draw_lego_engine(draw, engine_x, cy, 18, 12, p["secondary"], p["engine"])
    engines.append((engine_x - 25, cy))

    if level >= 3:
        for side in [-1, 1]:
            ey = cy + side * body_h * 0.35
            draw_lego_engine(draw, engine_x + 8, ey, 13, 9, p["secondary"], p["engine"])
            engines.append((engine_x - 15, ey))

    img = add_lego_engine_glow(img, engines, p["engine"], radius=22 + level * 6)
    img = add_shadow(img)

    return img


# ============================================================
# GÉNÉRATION PRINCIPALE
# ============================================================

GENERATORS = {
    "fighter": generate_fighter,
    "bio": generate_bio,
    "scout": generate_scout,
    "colony": generate_colony,
    "satellite": generate_satellite,
    "tanker": generate_tanker,
    "battleship": generate_battleship,
    "decoy": generate_decoy,
}


def generate_ship(ship_type: str, seed: int, level: int) -> Image.Image:
    """Génère un sprite de vaisseau LEGO."""
    generator = GENERATORS.get(ship_type, generate_fighter)
    img = generator(seed, level)
    img = img.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)
    return img


def main():
    print("═" * 66)
    print("  GÉNÉRATEUR DE VAISSEAUX - Style LEGO Premium v3")
    print("═" * 66)
    print(f"  Résolution: {OUTPUT_SIZE}px (rendu interne: {RENDER_SIZE}px)")
    print("  Nouveautés:")
    print("    • Têtes de minifigures visibles dans les cockpits")
    print("    • Satellites plus ronds (sphériques)")
    print("    • Armes progressives selon le niveau")
    print("    • Tankers avec gros bidons")
    print("    • Cuirassés plus imposants et intimidants")
    print("═" * 66 + "\n")

    total = 0
    for ship_type, style in SHIP_STYLES.items():
        type_dir = os.path.join(OUTPUT_DIR, ship_type)
        os.makedirs(type_dir, exist_ok=True)

        print(f"► {ship_type.upper()} ({style}):")
        for level in range(1, LEVELS_PER_TYPE + 1):
            seed = hash(f"{ship_type}_lego_v3") & 0xFFFFFFFF
            img = generate_ship(ship_type, seed, level)
            filename = f"ship-{level:02d}.png"
            filepath = os.path.join(type_dir, filename)
            img.save(filepath, "PNG", optimize=True)
            print(f"    Niveau {level}: {filename}")
            total += 1
        print()

    print("═" * 66)
    print(f"  ✓ {total} sprites LEGO générés avec succès!")
    print("  → Pilotes minifigures dans tous les cockpits")
    print("  → Armes progressives (canons, missiles, tourelles)")
    print("═" * 66)


if __name__ == "__main__":
    main()
