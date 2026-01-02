#!/usr/bin/env python3
"""
Générateur de textures de planètes procédurales - Version HD
Génère des textures détaillées pour 6 types de planètes.

Résolution : 256px (rendu à 512px avec downscale pour anti-aliasing)
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../frontend/public/planets")
RENDER_SIZE = 512  # Taille de rendu interne
OUTPUT_SIZE = 256  # Taille finale
TEXTURES_PER_TYPE = 8

PLANET_TYPES = ["habitable", "desert", "ice", "volcanic", "barren", "gas"]


def noise2d(x: float, y: float, seed: int = 0) -> float:
    """Bruit pseudo-aléatoire 2D basé sur des coordonnées."""
    n = int(x * 374761393 + y * 668265263 + seed * 1013904223)
    n = (n ^ (n >> 13)) * 1274126177
    n = n ^ (n >> 16)
    return (n & 0x7fffffff) / 0x7fffffff


def smoothstep(t: float) -> float:
    """Interpolation lisse."""
    return t * t * (3 - 2 * t)


def lerp(a: float, b: float, t: float) -> float:
    """Interpolation linéaire."""
    return a + (b - a) * t


def interpolated_noise(x: float, y: float, seed: int = 0) -> float:
    """Bruit interpolé pour des transitions douces."""
    x0, y0 = int(math.floor(x)), int(math.floor(y))
    x1, y1 = x0 + 1, y0 + 1

    fx, fy = x - x0, y - y0
    fx, fy = smoothstep(fx), smoothstep(fy)

    n00 = noise2d(x0, y0, seed)
    n10 = noise2d(x1, y0, seed)
    n01 = noise2d(x0, y1, seed)
    n11 = noise2d(x1, y1, seed)

    nx0 = lerp(n00, n10, fx)
    nx1 = lerp(n01, n11, fx)

    return lerp(nx0, nx1, fy)


def fbm(x: float, y: float, octaves: int = 6, persistence: float = 0.5,
        lacunarity: float = 2.0, seed: int = 0) -> float:
    """Fractional Brownian Motion - bruit fractal multi-octaves."""
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0

    for i in range(octaves):
        value += amplitude * interpolated_noise(x * frequency, y * frequency, seed + i * 1000)
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return value / max_value


def turbulence(x: float, y: float, octaves: int = 6, seed: int = 0) -> float:
    """Turbulence - valeur absolue du bruit pour des motifs plus chaotiques."""
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0

    for i in range(octaves):
        value += amplitude * abs(2 * interpolated_noise(x * frequency, y * frequency, seed + i * 1000) - 1)
        max_value += amplitude
        amplitude *= 0.5
        frequency *= 2.0

    return value / max_value


def ridged_noise(x: float, y: float, octaves: int = 6, seed: int = 0) -> float:
    """Bruit à crêtes - pour les montagnes et canyons."""
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    weight = 1.0

    for i in range(octaves):
        n = interpolated_noise(x * frequency, y * frequency, seed + i * 1000)
        n = 1.0 - abs(2 * n - 1)  # Créer des crêtes
        n = n * n * weight
        weight = min(1.0, n * 2)
        value += n * amplitude
        amplitude *= 0.5
        frequency *= 2.0

    return value


def domain_warp(x: float, y: float, strength: float = 0.5, seed: int = 0) -> tuple:
    """Déformation du domaine pour des motifs plus organiques."""
    warp_x = fbm(x, y, 4, 0.5, 2.0, seed) * strength
    warp_y = fbm(x + 5.2, y + 1.3, 4, 0.5, 2.0, seed + 100) * strength
    return x + warp_x, y + warp_y


def color_lerp(c1: tuple, c2: tuple, t: float) -> tuple:
    """Interpolation entre deux couleurs."""
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(len(c1)))


def multicolor_gradient(colors: list, t: float) -> tuple:
    """Gradient multi-couleurs."""
    t = max(0, min(1, t))
    n = len(colors) - 1
    idx = min(int(t * n), n - 1)
    local_t = (t * n) - idx
    return color_lerp(colors[idx], colors[idx + 1], local_t)


def sphere_normal(px: int, py: int, size: int) -> tuple:
    """Calcule la normale d'une sphère au pixel donné."""
    cx, cy = size / 2, size / 2
    radius = size / 2 - 2

    dx = (px - cx) / radius
    dy = (py - cy) / radius
    dist_sq = dx * dx + dy * dy

    if dist_sq > 1:
        return None  # En dehors de la sphère

    dz = math.sqrt(1 - dist_sq)
    return (dx, dy, dz)


def apply_lighting(base_color: tuple, normal: tuple, light_dir: tuple = (-0.5, -0.3, 0.8),
                   ambient: float = 0.15, specular_power: float = 20,
                   specular_strength: float = 0.3) -> tuple:
    """Applique un éclairage Phong complet."""
    if normal is None:
        return (0, 0, 0, 0)

    # Normaliser la direction de la lumière
    light_len = math.sqrt(sum(l*l for l in light_dir))
    light = tuple(l / light_len for l in light_dir)

    # Diffus (Lambertien)
    diffuse = max(0, sum(n * l for n, l in zip(normal, light)))

    # Spéculaire (Phong)
    # Direction de vue (vers la caméra)
    view = (0, 0, 1)
    # Réflexion
    dot_nl = sum(n * l for n, l in zip(normal, light))
    reflect = tuple(2 * dot_nl * n - l for n, l in zip(normal, light))
    spec_dot = max(0, sum(r * v for r, v in zip(reflect, view)))
    specular = specular_strength * (spec_dot ** specular_power)

    # Rim lighting (lumière sur les bords)
    rim = 1.0 - normal[2]
    rim = rim * rim * 0.3

    # Combiner
    intensity = ambient + diffuse * 0.7 + rim

    r = min(255, int(base_color[0] * intensity + specular * 255))
    g = min(255, int(base_color[1] * intensity + specular * 255))
    b = min(255, int(base_color[2] * intensity + specular * 255))

    return (r, g, b, 255)


def add_atmosphere(img: Image.Image, color: tuple, intensity: float = 0.5,
                   inner_radius: float = 0.85) -> Image.Image:
    """Ajoute une atmosphère lumineuse autour de la planète."""
    size = img.size[0]
    result = img.copy()
    pixels = result.load()

    cx, cy = size / 2, size / 2
    outer_radius = size / 2 - 1
    inner_r = outer_radius * inner_radius

    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy)

            if inner_r < dist < outer_radius:
                # Gradient d'atmosphère
                t = (dist - inner_r) / (outer_radius - inner_r)
                t = smoothstep(t)
                alpha = (1 - t) * intensity

                current = pixels[x, y]
                if current[3] > 0:  # Pixel existant
                    r = int(current[0] * (1 - alpha * 0.3) + color[0] * alpha * 0.3)
                    g = int(current[1] * (1 - alpha * 0.3) + color[1] * alpha * 0.3)
                    b = int(current[2] * (1 - alpha * 0.3) + color[2] * alpha * 0.3)
                    pixels[x, y] = (r, g, b, current[3])
                else:
                    # Halo externe
                    glow_alpha = int(alpha * 100)
                    if glow_alpha > 0:
                        pixels[x, y] = (color[0], color[1], color[2], glow_alpha)

    return result


def generate_habitable(seed: int) -> Image.Image:
    """Génère une planète habitable type Terre."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    ocean_seed = seed
    land_seed = seed + 1000
    cloud_seed = seed + 2000

    # Couleurs
    deep_ocean = (15, 50, 120)
    shallow_ocean = (30, 100, 180)
    beach = (210, 190, 140)
    lowland = (60, 140, 60)
    highland = (40, 100, 40)
    mountain = (100, 90, 80)
    snow = (240, 245, 255)

    # Niveau de la mer
    sea_level = 0.45 + random.uniform(-0.05, 0.05)

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            normal = sphere_normal(x, y, RENDER_SIZE)
            if normal is None:
                continue

            # Coordonnées sphériques pour le mapping
            u = 0.5 + math.atan2(normal[0], normal[2]) / (2 * math.pi)
            v = 0.5 - math.asin(max(-1, min(1, normal[1]))) / math.pi

            # Terrain avec domain warping pour formes plus organiques
            wu, wv = domain_warp(u * 4, v * 4, 0.3, land_seed)
            terrain = fbm(wu, wv, 8, 0.55, 2.1, land_seed)

            # Détails de montagne
            mountain_detail = ridged_noise(u * 8, v * 8, 5, land_seed + 500) * 0.3
            terrain = terrain * 0.7 + mountain_detail * terrain

            # Déterminer la couleur de base
            if terrain < sea_level:
                # Océan
                depth = (sea_level - terrain) / sea_level
                base_color = color_lerp(shallow_ocean, deep_ocean, depth)
                # Caustiques sous-marines subtiles
                caustic = fbm(u * 20, v * 20, 3, 0.5, 2.0, ocean_seed) * 0.1
                base_color = color_lerp(base_color, (100, 180, 220), caustic * (1 - depth))
            else:
                # Terre
                height = (terrain - sea_level) / (1 - sea_level)

                # Latitude pour les calottes polaires
                latitude = abs(normal[1])
                polar_factor = smoothstep((latitude - 0.7) / 0.3)

                if polar_factor > 0.5:
                    base_color = color_lerp(mountain, snow, (polar_factor - 0.5) * 2)
                elif height < 0.05:
                    base_color = beach
                elif height < 0.3:
                    # Variation de végétation
                    veg_noise = fbm(u * 15, v * 15, 4, 0.5, 2.0, land_seed + 200)
                    base_color = color_lerp(lowland, highland, veg_noise)
                elif height < 0.6:
                    base_color = color_lerp(highland, mountain, (height - 0.3) / 0.3)
                else:
                    snow_line = 0.6 + (1 - latitude) * 0.3
                    if height > snow_line:
                        base_color = color_lerp(mountain, snow, (height - snow_line) / (1 - snow_line))
                    else:
                        base_color = mountain

            # Nuages
            cloud_wu, cloud_wv = domain_warp(u * 3 + 0.5, v * 3, 0.4, cloud_seed)
            cloud_density = fbm(cloud_wu, cloud_wv, 5, 0.6, 2.0, cloud_seed)
            cloud_density = smoothstep((cloud_density - 0.4) / 0.3)

            if cloud_density > 0:
                cloud_color = (255, 255, 255)
                base_color = color_lerp(base_color, cloud_color, cloud_density * 0.8)

            # Appliquer l'éclairage
            lit_color = apply_lighting(base_color, normal, specular_strength=0.4 if terrain < sea_level else 0.15)
            pixels[x, y] = lit_color

    # Atmosphère bleutée
    img = add_atmosphere(img, (100, 150, 255), 0.6, 0.88)

    return img


def generate_desert(seed: int) -> Image.Image:
    """Génère une planète désertique."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    dune_seed = seed
    rock_seed = seed + 1000

    # Palette désertique variée
    palettes = [
        [(180, 120, 60), (220, 170, 100), (240, 200, 140), (200, 140, 80)],  # Sable doré
        [(160, 80, 50), (200, 110, 70), (180, 95, 60), (140, 70, 45)],  # Mars rouge
        [(200, 180, 150), (170, 150, 120), (220, 200, 170), (190, 170, 140)],  # Beige pâle
    ]
    palette = palettes[seed % len(palettes)]

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            normal = sphere_normal(x, y, RENDER_SIZE)
            if normal is None:
                continue

            u = 0.5 + math.atan2(normal[0], normal[2]) / (2 * math.pi)
            v = 0.5 - math.asin(max(-1, min(1, normal[1]))) / math.pi

            # Dunes avec domain warping
            wu, wv = domain_warp(u * 6, v * 6, 0.5, dune_seed)
            dune_pattern = fbm(wu, wv, 6, 0.45, 2.2, dune_seed)

            # Motif de rides de dunes
            dune_ridges = math.sin(u * 40 + dune_pattern * 5) * 0.5 + 0.5
            dune_ridges = dune_ridges * fbm(u * 10, v * 10, 3, 0.5, 2.0, dune_seed + 100)

            # Formations rocheuses
            rock_formation = ridged_noise(u * 8, v * 8, 5, rock_seed)

            # Combiner les éléments
            terrain = dune_pattern * 0.6 + dune_ridges * 0.2 + rock_formation * 0.2

            # Couleur basée sur le terrain
            base_color = multicolor_gradient(palette, terrain)

            # Ajouter des roches sombres occasionnelles
            if rock_formation > 0.7:
                rock_color = (80, 60, 50)
                base_color = color_lerp(base_color, rock_color, (rock_formation - 0.7) / 0.3)

            # Tempête de sable subtile dans certaines zones
            storm = fbm(u * 4 + seed * 0.1, v * 4, 4, 0.5, 2.0, dune_seed + 500)
            if storm > 0.6:
                storm_color = (230, 200, 150)
                base_color = color_lerp(base_color, storm_color, (storm - 0.6) * 0.5)

            lit_color = apply_lighting(base_color, normal, specular_strength=0.1)
            pixels[x, y] = lit_color

    # Atmosphère orangée/poussiéreuse
    img = add_atmosphere(img, (255, 180, 100), 0.4, 0.9)

    return img


def generate_ice(seed: int) -> Image.Image:
    """Génère une planète de glace."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    ice_seed = seed
    crack_seed = seed + 1000

    # Couleurs de glace
    deep_ice = (150, 200, 240)
    surface_ice = (220, 240, 255)
    blue_ice = (100, 160, 220)
    crack_color = (60, 100, 160)
    snow = (250, 252, 255)

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            normal = sphere_normal(x, y, RENDER_SIZE)
            if normal is None:
                continue

            u = 0.5 + math.atan2(normal[0], normal[2]) / (2 * math.pi)
            v = 0.5 - math.asin(max(-1, min(1, normal[1]))) / math.pi

            # Texture de glace de base
            ice_texture = fbm(u * 8, v * 8, 6, 0.5, 2.0, ice_seed)

            # Crevasses
            crack_pattern = ridged_noise(u * 15, v * 15, 5, crack_seed)
            crack_detail = ridged_noise(u * 30, v * 30, 4, crack_seed + 100) * 0.5
            cracks = max(0, crack_pattern * 0.7 + crack_detail * 0.3)

            # Glaciers et formations
            glacier = fbm(u * 4, v * 4, 5, 0.6, 2.0, ice_seed + 200)

            # Couleur de base
            if glacier > 0.6:
                # Zone de neige fraîche
                base_color = color_lerp(surface_ice, snow, (glacier - 0.6) / 0.4)
            else:
                # Glace avec variation de profondeur
                base_color = color_lerp(deep_ice, surface_ice, ice_texture)

                # Zones de glace bleue (ancienne, compressée)
                if ice_texture < 0.3:
                    base_color = color_lerp(blue_ice, base_color, ice_texture / 0.3)

            # Appliquer les crevasses
            if cracks > 0.7:
                crack_intensity = (cracks - 0.7) / 0.3
                base_color = color_lerp(base_color, crack_color, crack_intensity * 0.8)

            # Reflets cristallins
            sparkle = noise2d(x * 0.5, y * 0.5, ice_seed + 300)
            if sparkle > 0.97:
                base_color = color_lerp(base_color, (255, 255, 255), 0.5)

            # Éclairage avec fort spéculaire pour l'aspect brillant de la glace
            lit_color = apply_lighting(base_color, normal, specular_strength=0.6, specular_power=30)
            pixels[x, y] = lit_color

    # Atmosphère blanche/bleutée
    img = add_atmosphere(img, (200, 220, 255), 0.5, 0.88)

    return img


def generate_volcanic(seed: int) -> Image.Image:
    """Génère une planète volcanique."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    lava_seed = seed
    rock_seed = seed + 1000

    # Couleurs
    cooled_rock = (30, 25, 25)
    warm_rock = (60, 35, 30)
    hot_rock = (120, 50, 30)
    lava_cool = (180, 80, 20)
    lava_hot = (255, 150, 50)
    lava_white = (255, 220, 150)

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            normal = sphere_normal(x, y, RENDER_SIZE)
            if normal is None:
                continue

            u = 0.5 + math.atan2(normal[0], normal[2]) / (2 * math.pi)
            v = 0.5 - math.asin(max(-1, min(1, normal[1]))) / math.pi

            # Terrain rocheux
            rock_terrain = fbm(u * 6, v * 6, 6, 0.55, 2.0, rock_seed)
            rock_detail = turbulence(u * 12, v * 12, 5, rock_seed + 100)

            # Rivières de lave avec domain warping pour un aspect fluide
            wu, wv = domain_warp(u * 5, v * 5, 0.6, lava_seed)
            lava_flow = ridged_noise(wu, wv, 6, lava_seed)

            # Lacs de lave
            lava_pools = fbm(u * 3, v * 3, 4, 0.5, 2.0, lava_seed + 200)

            # Cratères
            crater_noise = fbm(u * 8, v * 8, 4, 0.5, 2.0, rock_seed + 300)

            # Déterminer le type de surface
            lava_intensity = max(lava_flow, lava_pools * 0.8)

            if lava_intensity > 0.65:
                # Lave active
                heat = (lava_intensity - 0.65) / 0.35
                heat = smoothstep(heat)

                # Gradient de chaleur dans la lave
                if heat > 0.7:
                    base_color = color_lerp(lava_hot, lava_white, (heat - 0.7) / 0.3)
                else:
                    base_color = color_lerp(lava_cool, lava_hot, heat / 0.7)

                # La lave émet sa propre lumière
                lit_color = base_color + (255,)

                # Ajouter un peu de variation
                flow_var = fbm(u * 20, v * 20, 3, 0.5, 2.0, lava_seed + 400)
                lit_color = color_lerp(lit_color[:3], (255, 200, 100), flow_var * 0.2) + (255,)
            else:
                # Roche
                rock_heat = smoothstep((lava_intensity - 0.4) / 0.25) if lava_intensity > 0.4 else 0

                # Couleur de roche basée sur la distance à la lave
                if rock_heat > 0:
                    base_color = color_lerp(warm_rock, hot_rock, rock_heat)
                else:
                    # Variation dans la roche refroidie
                    rock_var = rock_terrain * 0.5 + rock_detail * 0.5
                    base_color = color_lerp(cooled_rock, warm_rock, rock_var * 0.5)

                # Cratères sombres
                if crater_noise < 0.25:
                    base_color = color_lerp(base_color, (15, 12, 12), (0.25 - crater_noise) / 0.25)

                lit_color = apply_lighting(base_color, normal, specular_strength=0.2,
                                          ambient=0.1 + rock_heat * 0.2)

            pixels[x, y] = lit_color

    # Atmosphère rouge/orange toxique
    img = add_atmosphere(img, (255, 100, 50), 0.5, 0.85)

    return img


def generate_barren(seed: int) -> Image.Image:
    """Génère une planète stérile/lunaire avec cratères."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    terrain_seed = seed
    crater_seed = seed + 1000

    # Palette grise variée
    palettes = [
        [(80, 80, 85), (120, 120, 125), (100, 100, 105)],  # Gris neutre
        [(90, 85, 80), (130, 125, 115), (110, 105, 100)],  # Gris chaud
        [(70, 75, 85), (110, 115, 125), (90, 95, 105)],    # Gris froid
    ]
    palette = palettes[seed % len(palettes)]

    # Générer des cratères
    num_craters = 15 + (seed % 10)
    craters = []
    random.seed(crater_seed)
    for _ in range(num_craters):
        cu = random.uniform(0, 1)
        cv = random.uniform(0, 1)
        cr = random.uniform(0.02, 0.12)
        depth = random.uniform(0.3, 0.8)
        craters.append((cu, cv, cr, depth))

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            normal = sphere_normal(x, y, RENDER_SIZE)
            if normal is None:
                continue

            u = 0.5 + math.atan2(normal[0], normal[2]) / (2 * math.pi)
            v = 0.5 - math.asin(max(-1, min(1, normal[1]))) / math.pi

            # Terrain de base
            terrain = fbm(u * 10, v * 10, 6, 0.5, 2.0, terrain_seed)
            detail = turbulence(u * 20, v * 20, 4, terrain_seed + 100) * 0.3

            surface = terrain * 0.7 + detail

            # Appliquer les cratères
            crater_effect = 0
            for cu, cv, cr, depth in craters:
                # Distance au centre du cratère (avec wrapping)
                du = min(abs(u - cu), 1 - abs(u - cu))
                dv = abs(v - cv)
                dist = math.sqrt(du * du + dv * dv)

                if dist < cr:
                    # Intérieur du cratère
                    normalized_dist = dist / cr

                    if normalized_dist < 0.8:
                        # Fond du cratère (plus sombre)
                        crater_depth = (1 - normalized_dist / 0.8) * depth
                        crater_effect = max(crater_effect, -crater_depth)
                    else:
                        # Rebord du cratère (plus clair)
                        rim = (normalized_dist - 0.8) / 0.2
                        rim_height = math.sin(rim * math.pi) * 0.3
                        crater_effect = max(crater_effect, rim_height)
                elif dist < cr * 1.3:
                    # Éjecta autour du cratère
                    ejecta = (cr * 1.3 - dist) / (cr * 0.3)
                    ejecta_pattern = noise2d(u * 50, v * 50, crater_seed) * ejecta * 0.2
                    crater_effect = max(crater_effect, ejecta_pattern)

            surface += crater_effect

            # Couleur basée sur la hauteur
            base_color = multicolor_gradient(palette, surface * 0.5 + 0.5)

            # Assombrir les cratères
            if crater_effect < 0:
                darken = abs(crater_effect)
                base_color = color_lerp(base_color, (40, 40, 45), darken)

            # Roches et débris
            rock_noise = noise2d(u * 100, v * 100, terrain_seed + 200)
            if rock_noise > 0.9:
                base_color = color_lerp(base_color, (60, 60, 65), 0.3)

            lit_color = apply_lighting(base_color, normal, ambient=0.12, specular_strength=0.15)
            pixels[x, y] = lit_color

    # Pas d'atmosphère (ou très fine)
    img = add_atmosphere(img, (150, 150, 160), 0.15, 0.92)

    return img


def generate_gas(seed: int) -> Image.Image:
    """Génère une géante gazeuse style Jupiter/Saturne."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    band_seed = seed
    storm_seed = seed + 1000

    # Différentes palettes pour variété
    palettes = [
        # Jupiter
        [(180, 140, 100), (220, 180, 140), (160, 120, 80), (200, 160, 120), (140, 100, 70)],
        # Saturne
        [(210, 180, 140), (230, 200, 160), (190, 160, 120), (220, 190, 150), (180, 150, 110)],
        # Neptune bleu
        [(60, 100, 180), (80, 130, 200), (50, 80, 150), (70, 110, 190), (40, 70, 140)],
        # Uranus cyan
        [(100, 180, 200), (130, 200, 220), (80, 160, 180), (110, 190, 210), (70, 150, 170)],
    ]
    palette = palettes[seed % len(palettes)]

    # Position des grandes tempêtes
    num_storms = 2 + (seed % 3)
    storms = []
    random.seed(storm_seed)
    for _ in range(num_storms):
        su = random.uniform(0, 1)
        sv = random.uniform(0.2, 0.8)  # Éviter les pôles
        sr = random.uniform(0.03, 0.08)
        storms.append((su, sv, sr))

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            normal = sphere_normal(x, y, RENDER_SIZE)
            if normal is None:
                continue

            u = 0.5 + math.atan2(normal[0], normal[2]) / (2 * math.pi)
            v = 0.5 - math.asin(max(-1, min(1, normal[1]))) / math.pi

            # Bandes horizontales avec perturbations
            band_frequency = 15 + (seed % 10)

            # Perturbation des bandes
            wu, wv = domain_warp(u * 3, v * 3, 0.15, band_seed)

            # Motif de bandes principal
            band_base = math.sin((wv + wu * 0.1) * band_frequency * math.pi)

            # Ajouter des turbulences dans les bandes
            band_turb = fbm(u * 20, v * 10, 5, 0.5, 2.0, band_seed + 100)
            band_detail = fbm(u * 40, v * 20, 4, 0.5, 2.0, band_seed + 200) * 0.3

            band_pattern = band_base * 0.6 + band_turb * 0.3 + band_detail
            band_pattern = (band_pattern + 1) / 2  # Normaliser à 0-1

            # Couleur de base des bandes
            base_color = multicolor_gradient(palette, band_pattern)

            # Tourbillons et vortex
            vortex = 0
            for i in range(8):
                vu = (u + i * 0.15) % 1
                vv = v + 0.05 * math.sin(u * 20 + i)
                swirl = fbm(vu * 10, vv * 10, 4, 0.5, 2.0, band_seed + 300 + i * 100)
                angle = swirl * math.pi * 2
                swirl_u = u + math.cos(angle) * 0.02
                swirl_v = v + math.sin(angle) * 0.02
                local_vortex = fbm(swirl_u * 15, swirl_v * 15, 3, 0.5, 2.0, band_seed + 400 + i * 100)
                vortex = max(vortex, local_vortex * (0.5 + band_turb * 0.5))

            if vortex > 0.6:
                vortex_color = color_lerp(palette[2], palette[0], (vortex - 0.6) / 0.4)
                base_color = color_lerp(base_color, vortex_color, (vortex - 0.6) * 0.8)

            # Grandes tempêtes (style Grande Tache Rouge)
            for su, sv, sr in storms:
                du = min(abs(u - su), 1 - abs(u - su))
                dv = abs(v - sv)

                # Forme elliptique
                dist = math.sqrt((du / sr) ** 2 + (dv / (sr * 0.6)) ** 2)

                if dist < 1:
                    # Intérieur de la tempête
                    storm_t = 1 - dist
                    storm_t = smoothstep(storm_t)

                    # Spirale
                    angle = math.atan2(dv, du)
                    spiral = math.sin(angle * 3 + dist * 10) * 0.5 + 0.5

                    # Couleur de tempête (plus foncée au centre)
                    storm_color = color_lerp(palette[2], palette[4], spiral)
                    if dist < 0.5:
                        storm_color = color_lerp(storm_color, palette[4], (0.5 - dist) * 0.5)

                    base_color = color_lerp(base_color, storm_color, storm_t * 0.9)

            lit_color = apply_lighting(base_color, normal, ambient=0.2, specular_strength=0.25)
            pixels[x, y] = lit_color

    # Atmosphère colorée selon la palette
    atmo_color = palette[1]
    img = add_atmosphere(img, atmo_color, 0.4, 0.88)

    return img


def generate_planet(planet_type: str, seed: int) -> Image.Image:
    """Génère une planète du type spécifié."""
    generators = {
        "habitable": generate_habitable,
        "desert": generate_desert,
        "ice": generate_ice,
        "volcanic": generate_volcanic,
        "barren": generate_barren,
        "gas": generate_gas,
    }

    generator = generators.get(planet_type, generate_barren)
    img = generator(seed)

    # Downscale avec antialiasing de haute qualité
    img = img.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)

    return img


def main():
    """Point d'entrée principal."""
    print(f"Génération des textures de planètes HD ({OUTPUT_SIZE}px)...")
    print(f"Rendu interne à {RENDER_SIZE}px pour qualité optimale\n")

    for planet_type in PLANET_TYPES:
        type_dir = os.path.join(OUTPUT_DIR, planet_type)
        os.makedirs(type_dir, exist_ok=True)

        print(f"{planet_type}:")
        for i in range(1, TEXTURES_PER_TYPE + 1):
            # Seed unique pour chaque texture
            seed = hash(f"{planet_type}_{i}") & 0xFFFFFFFF

            img = generate_planet(planet_type, seed)

            filename = f"planet-{i:03d}.png"
            filepath = os.path.join(type_dir, filename)
            img.save(filepath, "PNG", optimize=True)
            print(f"  {filename}")

        print()

    total = len(PLANET_TYPES) * TEXTURES_PER_TYPE
    print(f"Terminé! {total} textures générées en {OUTPUT_SIZE}x{OUTPUT_SIZE}px.")


if __name__ == "__main__":
    main()
