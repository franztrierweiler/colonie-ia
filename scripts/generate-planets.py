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
                   inner_radius: float = 0.85, glow_strength: float = 1.0) -> Image.Image:
    """Ajoute une atmosphère lumineuse autour de la planète.

    Args:
        glow_strength: Multiplicateur pour le halo externe (1.0 = normal, 2.0+ = plus visible)
    """
    size = img.size[0]
    result = img.copy()
    pixels = result.load()

    cx, cy = size / 2, size / 2
    outer_radius = size / 2 - 1
    inner_r = outer_radius * inner_radius

    # Extension du halo externe
    halo_outer = outer_radius + (size * 0.05 * glow_strength)

    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy)

            if inner_r < dist < outer_radius:
                # Gradient d'atmosphère sur la planète
                t = (dist - inner_r) / (outer_radius - inner_r)
                t = smoothstep(t)
                alpha = (1 - t) * intensity

                current = pixels[x, y]
                if current[3] > 0:  # Pixel existant
                    blend = alpha * 0.4 * glow_strength
                    r = int(current[0] * (1 - blend) + color[0] * blend)
                    g = int(current[1] * (1 - blend) + color[1] * blend)
                    b = int(current[2] * (1 - blend) + color[2] * blend)
                    pixels[x, y] = (r, g, b, current[3])
                else:
                    # Halo externe
                    glow_alpha = int(alpha * 120 * glow_strength)
                    if glow_alpha > 0:
                        pixels[x, y] = (color[0], color[1], color[2], min(255, glow_alpha))

            elif dist < halo_outer and glow_strength > 1.0:
                # Halo étendu pour planètes gazeuses
                t = (dist - outer_radius) / (halo_outer - outer_radius)
                t = smoothstep(t)
                glow_alpha = int((1 - t) * 80 * glow_strength)
                if glow_alpha > 0:
                    current = pixels[x, y]
                    if current[3] == 0:
                        pixels[x, y] = (color[0], color[1], color[2], min(255, glow_alpha))

    return result


def generate_habitable(seed: int) -> Image.Image:
    """Génère une planète habitable luxuriante - océans bleus profonds, forêts vertes, fleuves visibles."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    continent_seed = seed
    detail_seed = seed + 1000
    river_seed = seed + 2000
    cloud_seed = seed + 3000
    lake_seed = seed + 4000

    # === PALETTE TRÈS SATURÉE ===
    # Océans - bleus profonds et vibrants
    abyss = (0, 15, 80)                # Abysses très sombres
    deep_ocean = (5, 35, 130)          # Bleu profond intense
    mid_ocean = (15, 70, 175)          # Bleu moyen vif
    shallow_ocean = (40, 120, 210)     # Bleu clair brillant
    coastal_water = (70, 160, 230)     # Bleu turquoise côtier
    reef_water = (80, 190, 220)        # Eau peu profonde (récifs)

    # Plages
    beach_wet = (190, 175, 140)
    beach_dry = (220, 205, 170)

    # Végétation - verts très saturés et variés
    jungle_dark = (5, 85, 20)          # Jungle dense sombre
    jungle = (15, 120, 30)             # Jungle tropicale
    tropical_forest = (25, 140, 40)    # Forêt tropicale
    forest_dark = (20, 100, 35)        # Forêt tempérée sombre
    temperate_forest = (40, 135, 50)   # Forêt tempérée
    grassland = (80, 170, 55)          # Prairie verte vive
    meadow = (110, 185, 70)            # Prairie claire
    savanna = (150, 160, 75)           # Savane

    # Autres terrains
    tundra = (120, 140, 115)
    rock_low = (115, 105, 95)
    rock_high = (85, 80, 75)
    snow_dirty = (215, 220, 225)
    snow_pure = (248, 252, 255)

    # Eau douce - bleus distincts
    river_color = (45, 110, 180)       # Rivières bleu vif
    river_shallow = (65, 140, 200)     # Rivières peu profondes
    lake_deep = (30, 90, 170)          # Lacs profonds
    lake_color = (50, 130, 195)        # Lacs

    # Plus d'océan visible (60-65% de la surface)
    sea_level = 0.48 + random.uniform(-0.02, 0.02)

    # === LACS ET MERS INTÉRIEURES ===
    num_lakes = 5 + (seed % 5)
    lakes = []
    random.seed(lake_seed)
    for _ in range(num_lakes):
        lu = random.uniform(0.05, 0.95)
        lv = random.uniform(0.15, 0.85)
        lr = random.uniform(0.015, 0.07)
        depth = random.uniform(0.5, 1.0)
        lakes.append((lu, lv, lr, depth))

    # === GRANDS FLEUVES ===
    num_rivers = 8 + (seed % 6)
    river_sources = []
    random.seed(river_seed)
    for _ in range(num_rivers):
        ru = random.uniform(0, 1)
        rv = random.uniform(0.1, 0.9)
        river_sources.append((ru, rv))

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            normal = sphere_normal(x, y, RENDER_SIZE)
            if normal is None:
                continue

            u = 0.5 + math.atan2(normal[0], normal[2]) / (2 * math.pi)
            v = 0.5 - math.asin(max(-1, min(1, normal[1]))) / math.pi
            latitude = abs(normal[1])

            # === TERRAIN CONTINENTAL ===
            wu, wv = domain_warp(u * 2.5, v * 2.5, 0.5, continent_seed)
            continent_base = fbm(wu, wv, 7, 0.55, 2.0, continent_seed)

            # Côtes découpées
            coastline = fbm(u * 12, v * 12, 5, 0.5, 2.0, continent_seed + 50) * 0.12
            peninsula = fbm(u * 6, v * 6, 4, 0.5, 2.0, continent_seed + 100) * 0.1

            # Relief montagneux
            mountains = ridged_noise(u * 5, v * 5, 6, detail_seed) * 0.3
            hills = fbm(u * 10, v * 10, 4, 0.5, 2.0, detail_seed + 100) * 0.12

            # Micro-détails
            micro = fbm(u * 30, v * 30, 3, 0.4, 2.0, detail_seed + 200) * 0.04

            terrain = continent_base + coastline + peninsula
            terrain += mountains * max(0, continent_base - 0.3) + hills + micro

            # === SYSTÈME FLUVIAL ÉLABORÉ ===
            river_intensity = 0
            is_river = False
            river_width = 0

            # Grands fleuves qui serpentent
            for ri, (ru, rv) in enumerate(river_sources):
                # Le fleuve serpente avec du domain warping
                rwu, rwv = domain_warp(u * 8, v * 8, 0.3, river_seed + ri * 100)

                # Distance au tracé du fleuve
                du = u - ru
                if du > 0.5: du -= 1
                elif du < -0.5: du += 1

                # Le fleuve coule vers les basses altitudes (généralement vers l'équateur et la mer)
                flow_direction = rv + rwv * 0.2
                dv = abs(v - flow_direction)

                # Tracé sinueux
                sine_offset = math.sin((u + ri * 0.1) * 15 + rwu * 3) * 0.03
                dv = abs(v - flow_direction + sine_offset)

                # Largeur variable (plus large vers l'embouchure)
                base_width = 0.008 + (1 - abs(v - 0.5) * 2) * 0.006
                dist_to_river = math.sqrt(du * du * 4 + dv * dv)

                if dist_to_river < base_width and terrain > sea_level and terrain < sea_level + 0.35:
                    # Vérifier qu'on est sur terre et pas trop haut
                    river_intensity = max(river_intensity, 1 - dist_to_river / base_width)
                    river_width = base_width
                    is_river = True

            # Affluents et rivières secondaires
            river_network = ridged_noise(u * 20, v * 20, 4, river_seed + 500)
            river_detail = fbm(u * 25, v * 25, 3, 0.5, 2.0, river_seed + 600)

            if terrain > sea_level and terrain < sea_level + 0.25:
                secondary_river = river_network * river_detail
                if secondary_river > 0.82:
                    is_river = True
                    river_intensity = max(river_intensity, (secondary_river - 0.82) / 0.18 * 0.7)

            # === LACS ===
            is_lake = False
            lake_depth_factor = 0
            for lu, lv, lr, ldepth in lakes:
                du = min(abs(u - lu), 1 - abs(u - lu))
                dv = abs(v - lv)
                dist = math.sqrt(du * du + dv * dv)
                if dist < lr and terrain > sea_level:
                    is_lake = True
                    lake_depth_factor = (1 - dist / lr) * ldepth
                    break

            # === COULEUR FINALE ===

            if terrain < sea_level:
                # === OCÉAN ===
                depth = (sea_level - terrain) / sea_level

                if depth < 0.08:
                    # Récifs et eaux très peu profondes
                    base_color = color_lerp(reef_water, coastal_water, depth / 0.08)
                elif depth < 0.2:
                    base_color = color_lerp(coastal_water, shallow_ocean, (depth - 0.08) / 0.12)
                elif depth < 0.45:
                    base_color = color_lerp(shallow_ocean, mid_ocean, (depth - 0.2) / 0.25)
                elif depth < 0.7:
                    base_color = color_lerp(mid_ocean, deep_ocean, (depth - 0.45) / 0.25)
                else:
                    base_color = color_lerp(deep_ocean, abyss, (depth - 0.7) / 0.3)

                # Courants marins visibles
                current = fbm(u * 6, v * 6, 4, 0.5, 2.0, continent_seed + 500)
                current_color = color_lerp(base_color, (60, 130, 200), 0.1)
                base_color = color_lerp(base_color, current_color, current * 0.15)

            elif is_lake:
                # Lac avec profondeur
                if lake_depth_factor > 0.6:
                    base_color = color_lerp(lake_color, lake_deep, (lake_depth_factor - 0.6) / 0.4)
                else:
                    base_color = color_lerp(coastal_water, lake_color, lake_depth_factor / 0.6)

            elif is_river:
                # Rivière avec variation de profondeur
                if river_intensity > 0.5:
                    base_color = color_lerp(river_shallow, river_color, (river_intensity - 0.5) / 0.5)
                else:
                    base_color = color_lerp(coastal_water, river_shallow, river_intensity / 0.5)

            else:
                # === TERRE - VÉGÉTATION LUXURIANTE ===
                height = (terrain - sea_level) / (1 - sea_level)
                climate = 1 - latitude  # 1 = tropical, 0 = polaire

                # Humidité basée sur proximité eau et latitude
                humidity = fbm(u * 8, v * 8, 4, 0.5, 2.0, detail_seed + 900)
                humidity = humidity * 0.6 + (1 - latitude) * 0.4

                # Calottes polaires
                polar_threshold = 0.78 - height * 0.1
                if latitude > polar_threshold:
                    polar_blend = smoothstep((latitude - polar_threshold) / 0.18)
                    base_color = color_lerp(tundra, snow_pure, polar_blend)

                elif height < 0.02:
                    # Plage étroite
                    beach_var = fbm(u * 50, v * 50, 2, 0.5, 2.0, detail_seed + 300)
                    base_color = color_lerp(beach_wet, beach_dry, beach_var)

                elif height < 0.12:
                    # Plaines côtières - TRÈS VERTES
                    veg_var = fbm(u * 20, v * 20, 4, 0.5, 2.0, detail_seed + 400)
                    if climate > 0.65:
                        # Tropical - jungle
                        base_color = color_lerp(jungle, tropical_forest, veg_var)
                    elif climate > 0.35:
                        # Tempéré - forêts denses
                        base_color = color_lerp(forest_dark, temperate_forest, veg_var)
                    else:
                        base_color = color_lerp(tundra, grassland, veg_var * 0.6)

                elif height < 0.3:
                    # Plaines et forêts - COUVERTURE VERTE DENSE
                    forest_density = fbm(u * 15, v * 15, 5, 0.55, 2.0, detail_seed + 500)
                    if climate > 0.55:
                        # Forêt tropicale dense
                        if humidity > 0.5:
                            base_color = color_lerp(jungle_dark, jungle, forest_density)
                        else:
                            base_color = color_lerp(tropical_forest, grassland, forest_density * 0.4)
                    elif climate > 0.3:
                        # Forêt tempérée
                        base_color = color_lerp(forest_dark, temperate_forest, forest_density)
                        base_color = color_lerp(base_color, meadow, (1 - forest_density) * 0.3)
                    else:
                        base_color = color_lerp(tundra, grassland, forest_density * 0.5)

                elif height < 0.5:
                    # Collines verdoyantes
                    hill_veg = fbm(u * 18, v * 18, 4, 0.5, 2.0, detail_seed + 600)
                    if climate > 0.4:
                        base_color = color_lerp(grassland, temperate_forest, hill_veg * 0.7)
                    else:
                        base_color = color_lerp(tundra, savanna, hill_veg * 0.5)
                    # Transition vers roche
                    rock_blend = smoothstep((height - 0.4) / 0.1) * 0.3
                    base_color = color_lerp(base_color, rock_low, rock_blend)

                elif height < 0.7:
                    # Montagnes avec végétation résiduelle
                    rock_var = turbulence(u * 25, v * 25, 4, detail_seed + 700)
                    veg_patches = fbm(u * 20, v * 20, 3, 0.5, 2.0, detail_seed + 750)
                    base_color = color_lerp(rock_low, rock_high, rock_var * 0.5)
                    if veg_patches > 0.6 and climate > 0.3:
                        base_color = color_lerp(base_color, tundra, (veg_patches - 0.6) * 0.5)

                else:
                    # Sommets enneigés
                    snow_line = 0.7 - climate * 0.12
                    snow_blend = smoothstep((height - snow_line) / 0.12)
                    snow_var = fbm(u * 30, v * 30, 3, 0.5, 2.0, detail_seed + 800)
                    base_color = color_lerp(rock_high, snow_dirty, snow_blend)
                    base_color = color_lerp(base_color, snow_pure, snow_var * snow_blend)

            # === NUAGES RÉALISTES ===
            cloud_wu, cloud_wv = domain_warp(u * 3, v * 3, 0.35, cloud_seed)
            cloud_base = fbm(cloud_wu, cloud_wv, 5, 0.55, 2.0, cloud_seed)
            cloud_detail = fbm(u * 10, v * 10, 4, 0.5, 2.0, cloud_seed + 100) * 0.25
            cloud_wisps = turbulence(u * 15, v * 15, 3, cloud_seed + 200) * 0.15
            cloud_density = cloud_base + cloud_detail + cloud_wisps

            cloud_threshold = 0.52
            if cloud_density > cloud_threshold:
                cloud_t = (cloud_density - cloud_threshold) / 0.3
                cloud_opacity = smoothstep(cloud_t) * 0.7
                cloud_color = color_lerp((225, 230, 235), (255, 255, 255), cloud_t)
                base_color = color_lerp(base_color, cloud_color, cloud_opacity)

            # === ÉCLAIRAGE ===
            is_water = terrain < sea_level or is_lake or is_river
            lit_color = apply_lighting(
                base_color, normal,
                specular_strength=0.55 if is_water else 0.08,
                specular_power=35 if is_water else 15
            )
            pixels[x, y] = lit_color

    # Pas de halo
    return img


def generate_desert(seed: int) -> Image.Image:
    """Génère une planète désertique style Mars (tons ocre/rouille)."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    dune_seed = seed
    rock_seed = seed + 1000

    # Palettes OCRE / MARS - toutes dans les tons rouille/orange
    palettes = [
        # Mars classique - ocre rouille
        [(180, 100, 50), (200, 120, 60), (220, 140, 70), (190, 110, 55), (170, 90, 45)],
        # Mars foncé - brun rougeâtre
        [(150, 80, 40), (180, 100, 50), (200, 115, 55), (165, 85, 42), (140, 70, 35)],
        # Mars clair - ocre doré
        [(200, 130, 60), (220, 150, 70), (235, 165, 80), (210, 140, 65), (190, 120, 55)],
        # Mars rouge intense
        [(175, 85, 45), (195, 100, 50), (210, 120, 55), (185, 95, 48), (160, 75, 40)],
    ]
    palette = palettes[seed % len(palettes)]

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            normal = sphere_normal(x, y, RENDER_SIZE)
            if normal is None:
                continue

            u = 0.5 + math.atan2(normal[0], normal[2]) / (2 * math.pi)
            v = 0.5 - math.asin(max(-1, min(1, normal[1]))) / math.pi

            # Latitude pour les calottes polaires (optionnelles)
            latitude = abs(normal[1])

            # Dunes avec domain warping
            wu, wv = domain_warp(u * 6, v * 6, 0.5, dune_seed)
            dune_pattern = fbm(wu, wv, 6, 0.45, 2.2, dune_seed)

            # Motif de rides de dunes
            dune_ridges = math.sin(u * 40 + dune_pattern * 5) * 0.5 + 0.5
            dune_ridges = dune_ridges * fbm(u * 10, v * 10, 3, 0.5, 2.0, dune_seed + 100)

            # Formations rocheuses (mesas, canyons)
            rock_formation = ridged_noise(u * 8, v * 8, 5, rock_seed)

            # Cratères d'impact (Mars en a beaucoup)
            crater_pattern = fbm(u * 12, v * 12, 4, 0.5, 2.0, rock_seed + 200)

            # Combiner les éléments
            terrain = dune_pattern * 0.5 + dune_ridges * 0.2 + rock_formation * 0.2 + crater_pattern * 0.1

            # Couleur basée sur le terrain - tons OCRE
            base_color = multicolor_gradient(palette, terrain)

            # Formations rocheuses plus sombres (basalte)
            if rock_formation > 0.7:
                rock_color = (100, 60, 35)  # Roche sombre ocre
                base_color = color_lerp(base_color, rock_color, (rock_formation - 0.7) / 0.3)

            # Dépressions/cratères plus sombres
            if crater_pattern < 0.3:
                dark_color = (130, 70, 40)  # Ombres ocre foncé
                base_color = color_lerp(base_color, dark_color, (0.3 - crater_pattern) * 0.4)

            # Tempête de sable (poussière ocre)
            storm = fbm(u * 4 + seed * 0.1, v * 4, 4, 0.5, 2.0, dune_seed + 500)
            if storm > 0.65:
                storm_color = (230, 170, 100)  # Poussière ocre clair
                base_color = color_lerp(base_color, storm_color, (storm - 0.65) * 0.7)

            # Petite calotte polaire possible (glace de CO2 style Mars)
            if latitude > 0.85:
                polar_blend = smoothstep((latitude - 0.85) / 0.12)
                polar_color = (240, 235, 230)  # Blanc cassé / givre
                base_color = color_lerp(base_color, polar_color, polar_blend * 0.6)

            # Variation fine de texture (régolithe)
            regolith = noise2d(u * 100, v * 100, dune_seed + 600) * 0.08
            r = min(255, max(0, int(base_color[0] * (1 + regolith))))
            g = min(255, max(0, int(base_color[1] * (1 + regolith))))
            b = min(255, max(0, int(base_color[2] * (1 + regolith))))
            base_color = (r, g, b)

            lit_color = apply_lighting(base_color, normal, specular_strength=0.08)
            pixels[x, y] = lit_color

    # Pas de halo
    return img


def generate_ice(seed: int) -> Image.Image:
    """Génère une planète de glace avec banquise dominante."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    ice_seed = seed
    crack_seed = seed + 1000

    # Couleurs de glace - dominante BLANCHE
    snow_pure = (252, 254, 255)      # Blanc pur
    snow_blue = (240, 248, 255)      # Blanc légèrement bleuté
    ice_white = (230, 245, 255)      # Glace blanche
    ice_light = (210, 235, 255)      # Glace claire
    ice_blue = (170, 210, 250)       # Glace bleutée (zones profondes)
    crack_dark = (80, 130, 180)      # Crevasses profondes
    crack_light = (140, 180, 220)    # Crevasses légères

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            normal = sphere_normal(x, y, RENDER_SIZE)
            if normal is None:
                continue

            u = 0.5 + math.atan2(normal[0], normal[2]) / (2 * math.pi)
            v = 0.5 - math.asin(max(-1, min(1, normal[1]))) / math.pi

            # Latitude - plus de neige aux pôles
            latitude = abs(normal[1])

            # Texture de glace de base
            ice_texture = fbm(u * 6, v * 6, 6, 0.5, 2.0, ice_seed)

            # Crevasses fines et nombreuses
            crack_fine = ridged_noise(u * 25, v * 25, 5, crack_seed)
            crack_medium = ridged_noise(u * 12, v * 12, 4, crack_seed + 100)

            # Banquise / plaques de glace
            pack_ice = fbm(u * 3, v * 3, 4, 0.6, 2.0, ice_seed + 200)

            # Neige fraîche (couche supérieure)
            snow_layer = fbm(u * 8, v * 8, 3, 0.5, 2.0, ice_seed + 300)

            # Déterminer la couverture neigeuse (beaucoup plus de blanc!)
            # Base très blanche, avec quelques variations bleues dans les crevasses
            snow_coverage = 0.7 + latitude * 0.2 + snow_layer * 0.2

            if snow_coverage > 0.75:
                # Neige pure dominante (la majorité de la surface)
                snow_var = fbm(u * 15, v * 15, 2, 0.5, 2.0, ice_seed + 400) * 0.15
                base_color = color_lerp(snow_blue, snow_pure, snow_coverage - 0.75 + snow_var)
            elif snow_coverage > 0.55:
                # Neige/glace mixte
                t = (snow_coverage - 0.55) / 0.2
                base_color = color_lerp(ice_white, snow_blue, t)
            else:
                # Zones de glace visible (rares)
                t = snow_coverage / 0.55
                base_color = color_lerp(ice_blue, ice_white, t)

            # Plaques de glace plus blanches
            if pack_ice > 0.6:
                pack_brightness = (pack_ice - 0.6) / 0.4
                base_color = color_lerp(base_color, snow_pure, pack_brightness * 0.5)

            # Crevasses subtiles (plus fines et moins prononcées pour garder l'aspect blanc)
            if crack_fine > 0.8:
                crack_intensity = (crack_fine - 0.8) / 0.2
                base_color = color_lerp(base_color, crack_light, crack_intensity * 0.4)

            if crack_medium > 0.85:
                crack_intensity = (crack_medium - 0.85) / 0.15
                base_color = color_lerp(base_color, crack_dark, crack_intensity * 0.5)

            # Reflets cristallins (plus nombreux)
            sparkle = noise2d(x * 0.4, y * 0.4, ice_seed + 500)
            if sparkle > 0.94:
                base_color = color_lerp(base_color, (255, 255, 255), 0.7)

            # Subtile texture de neige (grains)
            grain = noise2d(x * 2, y * 2, ice_seed + 600) * 0.05
            r = min(255, int(base_color[0] * (1 + grain)))
            g = min(255, int(base_color[1] * (1 + grain)))
            b = min(255, int(base_color[2] * (1 + grain)))
            base_color = (r, g, b)

            # Éclairage avec fort spéculaire pour l'aspect brillant de la glace
            lit_color = apply_lighting(base_color, normal, specular_strength=0.7, specular_power=25)
            pixels[x, y] = lit_color

    # Pas de halo
    return img


def generate_volcanic(seed: int) -> Image.Image:
    """Génère une planète volcanique avec coulées de lave rouge vif."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    lava_seed = seed
    rock_seed = seed + 1000

    # Couleurs - ROUGE VIF dominant
    cooled_rock = (25, 20, 20)        # Roche très sombre
    warm_rock = (50, 25, 20)          # Roche tiède
    hot_rock = (90, 30, 15)           # Roche chaude
    glowing_rock = (140, 40, 15)      # Roche incandescente

    lava_dark = (180, 30, 10)         # Lave rouge sombre
    lava_red = (255, 50, 10)          # Lave rouge vif
    lava_orange = (255, 120, 20)      # Lave orange
    lava_yellow = (255, 200, 60)      # Lave très chaude
    lava_white = (255, 240, 180)      # Lave au cœur

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

            # Rivières de lave principales - nombreuses et visibles
            wu, wv = domain_warp(u * 4, v * 4, 0.7, lava_seed)
            lava_rivers = ridged_noise(wu, wv, 6, lava_seed)

            # Rivières secondaires plus fines
            wu2, wv2 = domain_warp(u * 8, v * 8, 0.5, lava_seed + 50)
            lava_tributaries = ridged_noise(wu2, wv2, 5, lava_seed + 100)

            # Grands lacs de lave
            lava_pools = fbm(u * 2, v * 2, 4, 0.5, 2.0, lava_seed + 200)

            # Petits points de lave (fissures)
            lava_fissures = fbm(u * 15, v * 15, 3, 0.5, 2.0, lava_seed + 300)

            # Cratères volcaniques
            crater_noise = fbm(u * 6, v * 6, 4, 0.5, 2.0, rock_seed + 300)

            # Combiner toutes les sources de lave (plus de lave visible!)
            lava_intensity = max(
                lava_rivers * 1.0,
                lava_tributaries * 0.85,
                lava_pools * 0.9,
                lava_fissures * 0.6
            )

            # Seuil de lave plus bas = plus de lave visible
            lava_threshold = 0.50

            if lava_intensity > lava_threshold:
                # LAVE ACTIVE - rouge vif!
                heat = (lava_intensity - lava_threshold) / (1.0 - lava_threshold)
                heat = smoothstep(heat)

                # Gradient de chaleur: rouge sombre -> rouge vif -> orange -> jaune -> blanc
                if heat < 0.25:
                    # Bords de la coulée - rouge sombre
                    base_color = color_lerp(lava_dark, lava_red, heat / 0.25)
                elif heat < 0.5:
                    # Rouge vif intense
                    base_color = color_lerp(lava_red, lava_orange, (heat - 0.25) / 0.25)
                elif heat < 0.75:
                    # Orange
                    base_color = color_lerp(lava_orange, lava_yellow, (heat - 0.5) / 0.25)
                else:
                    # Cœur incandescent
                    base_color = color_lerp(lava_yellow, lava_white, (heat - 0.75) / 0.25)

                # La lave émet sa propre lumière - pas d'éclairage externe
                # Ajouter de la turbulence dans la lave pour le mouvement
                flow_turb = fbm(u * 25, v * 25, 3, 0.5, 2.0, lava_seed + 400)
                brightness = 0.85 + flow_turb * 0.15

                r = min(255, int(base_color[0] * brightness))
                g = min(255, int(base_color[1] * brightness))
                b = min(255, int(base_color[2] * brightness))
                lit_color = (r, g, b, 255)

            else:
                # ROCHE VOLCANIQUE
                # Distance à la lave pour la chaleur
                dist_to_lava = (lava_threshold - lava_intensity) / lava_threshold
                rock_heat = 1.0 - smoothstep(dist_to_lava * 2)

                # Couleur de roche basée sur la proximité de la lave
                if rock_heat > 0.6:
                    # Très proche de la lave - roche incandescente
                    base_color = color_lerp(hot_rock, glowing_rock, (rock_heat - 0.6) / 0.4)
                elif rock_heat > 0.3:
                    # Proche - roche chaude
                    base_color = color_lerp(warm_rock, hot_rock, (rock_heat - 0.3) / 0.3)
                else:
                    # Loin - roche refroidie avec texture
                    rock_var = rock_terrain * 0.5 + rock_detail * 0.5
                    base_color = color_lerp(cooled_rock, warm_rock, rock_var * 0.4)

                # Cratères volcaniques
                if crater_noise < 0.2:
                    crater_depth = (0.2 - crater_noise) / 0.2
                    base_color = color_lerp(base_color, (12, 8, 8), crater_depth * 0.6)

                # Illumination par la lave proche (lueur rouge)
                ambient = 0.08 + rock_heat * 0.25
                lit_color = apply_lighting(base_color, normal, specular_strength=0.15,
                                          ambient=ambient)

                # Teinte rouge de la lueur de lave
                if rock_heat > 0.2:
                    glow_intensity = (rock_heat - 0.2) * 0.4
                    r = min(255, int(lit_color[0] + glow_intensity * 80))
                    g = lit_color[1]
                    b = lit_color[2]
                    lit_color = (r, g, b, 255)

            pixels[x, y] = lit_color

    # Pas de halo
    return img


def generate_barren(seed: int) -> Image.Image:
    """Génère une planète stérile/lunaire CRIBLÉE de cratères d'impact."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)
    terrain_seed = seed
    crater_seed = seed + 1000

    # Palettes grises variées - style lunaire/mercurien avec contraste accentué
    palettes = [
        {  # Gris lunaire classique - contraste fort
            'base': (100, 100, 105),
            'dark': (30, 30, 35),        # Très sombre pour les ombres
            'very_dark': (15, 15, 18),   # Noir quasi-total
            'light': (170, 170, 175),
            'rim': (145, 145, 150),
            'ejecta': (125, 125, 130),
        },
        {  # Gris chaud (astéroïde) - contraste fort
            'base': (110, 100, 90),
            'dark': (35, 30, 25),
            'very_dark': (18, 15, 12),
            'light': (175, 165, 155),
            'rim': (155, 145, 135),
            'ejecta': (135, 125, 115),
        },
        {  # Gris froid (Callisto) - contraste fort
            'base': (90, 95, 105),
            'dark': (25, 28, 35),
            'very_dark': (12, 14, 20),
            'light': (150, 155, 165),
            'rim': (130, 135, 145),
            'ejecta': (110, 115, 125),
        },
    ]
    palette = palettes[seed % len(palettes)]

    # Direction de la lumière pour les ombres de cratères (plus latérale = ombres plus longues)
    light_dir_u = -0.7
    light_dir_v = -0.2

    # Générer ÉNORMÉMENT de cratères - surface criblée d'impacts
    random.seed(crater_seed)

    # Très grands bassins d'impact
    giant_craters = []
    num_giant = 2 + (seed % 2)
    for _ in range(num_giant):
        cu = random.uniform(0, 1)
        cv = random.uniform(0.15, 0.85)
        cr = random.uniform(0.12, 0.20)
        depth = random.uniform(0.7, 0.95)
        age = random.uniform(0.5, 1.0)
        giant_craters.append((cu, cv, cr, depth, age))

    # Grands cratères d'impact
    large_craters = []
    num_large = 6 + (seed % 4)
    for _ in range(num_large):
        cu = random.uniform(0, 1)
        cv = random.uniform(0.1, 0.9)
        cr = random.uniform(0.06, 0.11)
        depth = random.uniform(0.65, 0.9)
        age = random.uniform(0.4, 1.0)
        large_craters.append((cu, cv, cr, depth, age))

    # Cratères moyens - beaucoup plus
    medium_craters = []
    num_medium = 25 + (seed % 15)
    for _ in range(num_medium):
        cu = random.uniform(0, 1)
        cv = random.uniform(0.05, 0.95)
        cr = random.uniform(0.025, 0.055)
        depth = random.uniform(0.55, 0.85)
        age = random.uniform(0.5, 1.0)
        medium_craters.append((cu, cv, cr, depth, age))

    # Petits cratères - TRÈS nombreux
    small_craters = []
    num_small = 100 + (seed % 50)
    for _ in range(num_small):
        cu = random.uniform(0, 1)
        cv = random.uniform(0, 1)
        cr = random.uniform(0.01, 0.024)
        depth = random.uniform(0.5, 0.8)
        age = random.uniform(0.6, 1.0)
        small_craters.append((cu, cv, cr, depth, age))

    # Très petits cratères
    tiny_craters = []
    num_tiny = 150 + (seed % 80)
    for _ in range(num_tiny):
        cu = random.uniform(0, 1)
        cv = random.uniform(0, 1)
        cr = random.uniform(0.005, 0.012)
        depth = random.uniform(0.4, 0.7)
        age = random.uniform(0.7, 1.0)
        tiny_craters.append((cu, cv, cr, depth, age))

    # Micro-cratères pour texture (criblage fin)
    micro_craters = []
    num_micro = 250 + (seed % 100)
    for _ in range(num_micro):
        cu = random.uniform(0, 1)
        cv = random.uniform(0, 1)
        cr = random.uniform(0.002, 0.006)
        depth = random.uniform(0.3, 0.5)
        micro_craters.append((cu, cv, cr, depth))

    # Tous les cratères sauf micro (triés par taille décroissante pour superposition correcte)
    all_craters = giant_craters + large_craters + medium_craters + small_craters + tiny_craters

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            normal = sphere_normal(x, y, RENDER_SIZE)
            if normal is None:
                continue

            u = 0.5 + math.atan2(normal[0], normal[2]) / (2 * math.pi)
            v = 0.5 - math.asin(max(-1, min(1, normal[1]))) / math.pi

            # Terrain de base - très subtil pour laisser les cratères dominer
            base_terrain = fbm(u * 4, v * 4, 3, 0.5, 2.0, terrain_seed) * 0.08

            surface_height = 0.5 + base_terrain
            surface_color_value = surface_height

            # Variables pour accumuler les effets de cratères
            crater_shadow = 0
            crater_highlight = 0
            total_depth_mod = 0

            # Traiter tous les cratères
            for cu, cv, cr, depth, *age_opt in all_craters:
                age = age_opt[0] if age_opt else 0.85

                # Distance au centre (avec wrapping horizontal)
                du = u - cu
                if du > 0.5:
                    du -= 1
                elif du < -0.5:
                    du += 1
                dv = v - cv
                dist = math.sqrt(du * du + dv * dv)

                if dist < cr * 2.0:  # Zone d'influence étendue
                    normalized_dist = dist / cr

                    # Direction du point par rapport au centre du cratère
                    if dist > 0.001:
                        dir_u = du / dist
                        dir_v = dv / dist
                    else:
                        dir_u, dir_v = 0, 0

                    # Calcul de l'ombre - TRÈS prononcé
                    shadow_factor = -(dir_u * light_dir_u + dir_v * light_dir_v)

                    if normalized_dist < 0.6:
                        # Fond du cratère - TRÈS SOMBRE
                        floor_depth = (1 - normalized_dist / 0.6) * depth * age

                        # Le fond est beaucoup plus sombre
                        total_depth_mod += floor_depth * 0.6

                        # Ombre très prononcée sur un côté
                        if shadow_factor > 0:
                            crater_shadow = max(crater_shadow, shadow_factor * floor_depth * 0.9)

                        # Pic central pour les grands cratères
                        if cr > 0.08 and normalized_dist < 0.12:
                            central_peak = (1 - normalized_dist / 0.12) * 0.25 * age
                            surface_color_value += central_peak
                            if shadow_factor < 0:
                                crater_highlight = max(crater_highlight, -shadow_factor * central_peak)

                    elif normalized_dist < 1.0:
                        # Paroi intérieure du cratère - contraste fort
                        wall_pos = (normalized_dist - 0.6) / 0.4

                        if shadow_factor > 0:
                            # Côté ombre - TRÈS sombre
                            shadow_intensity = shadow_factor * (1 - wall_pos) * depth * 0.85
                            crater_shadow = max(crater_shadow, shadow_intensity)
                        else:
                            # Côté éclairé - plus clair
                            highlight_intensity = -shadow_factor * (1 - wall_pos) * depth * 0.5
                            crater_highlight = max(crater_highlight, highlight_intensity)

                    elif normalized_dist < 1.2:
                        # Rebord du cratère (rim) - toujours plus clair
                        rim_pos = (normalized_dist - 1.0) / 0.2
                        rim_height = math.sin(rim_pos * math.pi) * 0.35 * age
                        crater_highlight = max(crater_highlight, rim_height)
                        surface_color_value += rim_height * 0.15

                    elif normalized_dist < 2.0:
                        # Éjecta rayonnants
                        ejecta_dist = (normalized_dist - 1.2) / 0.8
                        ejecta_fade = 1 - smoothstep(ejecta_dist)

                        # Motif rayonnant
                        angle = math.atan2(dv, du)
                        num_rays = 8 + int(cr * 100)
                        ray_pattern = (math.sin(angle * num_rays) * 0.5 + 0.5) * ejecta_fade
                        ray_noise = noise2d(u * 60 + cu * 100, v * 60 + cv * 100, crater_seed) * ejecta_fade

                        ejecta_brightness = (ray_pattern * 0.4 + ray_noise * 0.6) * 0.12 * age
                        surface_color_value += ejecta_brightness

            # Ajouter les micro-cratères (texture très fine - criblage)
            for cu, cv, cr, depth in micro_craters:
                du = u - cu
                if du > 0.5:
                    du -= 1
                elif du < -0.5:
                    du += 1
                dv = v - cv
                dist = math.sqrt(du * du + dv * dv)

                if dist < cr:
                    micro_depth = (1 - dist / cr) * depth * 0.2
                    total_depth_mod += micro_depth

            # Appliquer la profondeur accumulée
            surface_color_value -= total_depth_mod
            surface_color_value = max(0, min(1, surface_color_value))

            # Interpoler dans la palette avec plus de contraste
            if surface_color_value < 0.25:
                # Zones très sombres (fonds de cratères)
                t = surface_color_value / 0.25
                base_color = color_lerp(palette['very_dark'], palette['dark'], t)
            elif surface_color_value < 0.45:
                t = (surface_color_value - 0.25) / 0.2
                base_color = color_lerp(palette['dark'], palette['base'], t)
            elif surface_color_value < 0.6:
                t = (surface_color_value - 0.45) / 0.15
                base_color = color_lerp(palette['base'], palette['rim'], t)
            else:
                t = (surface_color_value - 0.6) / 0.4
                base_color = color_lerp(palette['rim'], palette['light'], t)

            # Appliquer les ombres de cratères - TRÈS prononcées
            if crater_shadow > 0:
                shadow_strength = min(crater_shadow * 1.2, 0.95)
                base_color = color_lerp(base_color, palette['very_dark'], shadow_strength)

            if crater_highlight > 0:
                highlight_strength = min(crater_highlight, 0.6)
                base_color = color_lerp(base_color, palette['light'], highlight_strength)

            # Texture fine de régolithe (poussière)
            regolith = noise2d(u * 200, v * 200, terrain_seed + 300) * 0.05
            r = min(255, max(0, int(base_color[0] * (1 + regolith - 0.025))))
            g = min(255, max(0, int(base_color[1] * (1 + regolith - 0.025))))
            b = min(255, max(0, int(base_color[2] * (1 + regolith - 0.025))))
            base_color = (r, g, b)

            # Éclairage final - ambient très faible pour contraste maximal
            lit_color = apply_lighting(
                base_color, normal,
                ambient=0.06,
                specular_strength=0.1,
                specular_power=12
            )
            pixels[x, y] = lit_color

    # Pas de halo
    return img


def generate_gas(seed: int) -> Image.Image:
    """Génère une géante gazeuse poétique - bandes de gaz fluides, couleurs douces, SANS halo."""
    img = Image.new('RGBA', (RENDER_SIZE, RENDER_SIZE), (0, 0, 0, 0))
    pixels = img.load()

    random.seed(seed)

    cx, cy = RENDER_SIZE / 2, RENDER_SIZE / 2
    # Rayon fixe - pas de halo
    planet_radius = RENDER_SIZE / 2 - 2

    # Palettes poétiques - couleurs douces et harmonieuses
    palettes = [
        # Aurore orangée - coucher de soleil
        {
            'core': [(255, 180, 120), (245, 155, 95), (230, 130, 75), (255, 200, 150)],
            'veils': [(255, 210, 170, 0.6), (255, 175, 130, 0.5), (255, 230, 200, 0.4)],
            'highlight': (255, 240, 220),
        },
        # Crépuscule doré - lumière chaude
        {
            'core': [(250, 210, 150), (235, 185, 120), (220, 165, 100), (255, 225, 175)],
            'veils': [(255, 230, 190, 0.55), (250, 200, 150, 0.45), (255, 240, 210, 0.35)],
            'highlight': (255, 245, 230),
        },
        # Océan céleste - bleu profond
        {
            'core': [(90, 140, 210), (70, 115, 185), (55, 95, 165), (110, 160, 230)],
            'veils': [(130, 175, 240, 0.55), (100, 150, 220, 0.45), (160, 195, 255, 0.35)],
            'highlight': (200, 220, 255),
        },
        # Brume azur - bleu-vert rêveur
        {
            'core': [(95, 170, 200), (75, 145, 175), (60, 125, 160), (115, 185, 215)],
            'veils': [(140, 200, 230, 0.5), (110, 175, 210, 0.4), (170, 220, 245, 0.35)],
            'highlight': (210, 235, 250),
        },
        # Lavande cosmique - violet doux
        {
            'core': [(170, 140, 200), (150, 120, 180), (130, 100, 165), (190, 160, 215)],
            'veils': [(200, 175, 230, 0.5), (175, 150, 210, 0.4), (220, 200, 245, 0.35)],
            'highlight': (235, 225, 255),
        },
        # Rose auroral - magenta tendre
        {
            'core': [(210, 145, 175), (190, 125, 155), (175, 110, 145), (225, 165, 195)],
            'veils': [(235, 180, 210, 0.5), (210, 160, 190, 0.4), (250, 205, 230, 0.35)],
            'highlight': (255, 230, 245),
        },
    ]
    palette = palettes[seed % len(palettes)]

    for y in range(RENDER_SIZE):
        for x in range(RENDER_SIZE):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy)

            # Bord net - pas de halo
            if dist > planet_radius:
                continue

            angle = math.atan2(dy, dx)

            # Position verticale pour les courants
            v = 0.5 + dy / (planet_radius * 2)
            v = max(0, min(1, v))
            u = 0.5 + angle / (2 * math.pi)

            # === COURANTS ATMOSPHÉRIQUES FLUIDES ===
            # Domain warping doux pour des flux organiques
            wu, wv = domain_warp(u * 1.5, v * 3, 0.35, seed + 400)

            # Bandes douces - comme des rubans de soie
            ribbon_freq = 6 + (seed % 4)
            ribbon_flow = fbm(wu * 8, wv * 5, 6, 0.6, 1.8, seed + 500)

            # Pattern de flux principal - sinusoïdes douces
            flow_pattern = math.sin((wv + ribbon_flow * 0.2) * ribbon_freq * math.pi)
            flow_pattern = (flow_pattern + 1) / 2

            # Adoucir avec du bruit supplémentaire
            soft_blend = fbm(u * 12, v * 8, 4, 0.5, 2.0, seed + 600) * 0.25
            flow_pattern = smoothstep(flow_pattern + soft_blend - 0.125)

            # === COULEUR DES COURANTS ===
            n_colors = len(palette['core'])
            color_idx = flow_pattern * (n_colors - 1)
            idx1 = int(color_idx)
            idx2 = min(idx1 + 1, n_colors - 1)
            blend_t = color_idx - idx1

            base_color = color_lerp(palette['core'][idx1], palette['core'][idx2], blend_t)

            # === VOILES DE GAZ ===
            # Couches de voiles pour texture
            for i, (vr, vg, vb, vopacity) in enumerate(palette['veils']):
                veil_wu, veil_wv = domain_warp(u * (2 + i), v * (2 + i * 0.5), 0.4, seed + 700 + i * 100)
                veil_pattern = fbm(veil_wu * 6, veil_wv * 4, 5, 0.55, 2.0, seed + 800 + i * 100)

                veil_threshold = 0.4 + i * 0.1
                if veil_pattern > veil_threshold:
                    veil_strength = smoothstep((veil_pattern - veil_threshold) / 0.3) * vopacity
                    veil_color = (int(vr), int(vg), int(vb))
                    base_color = color_lerp(base_color, veil_color, veil_strength * 0.5)

            # === TOURBILLONS DOUX ===
            num_spirals = 2 + (seed % 2)
            for i in range(num_spirals):
                spiral_u = (seed * 0.13 + i * 0.4) % 1
                spiral_v = 0.25 + (i * 0.25)
                spiral_r = 0.08 + (seed % 3) * 0.015

                su_diff = min(abs(u - spiral_u), 1 - abs(u - spiral_u))
                sv_diff = abs(v - spiral_v)
                spiral_dist = math.sqrt(su_diff**2 + (sv_diff * 1.3)**2)

                if spiral_dist < spiral_r:
                    spiral_t = 1 - spiral_dist / spiral_r
                    spiral_t = smoothstep(spiral_t) ** 1.5

                    rot_angle = math.atan2(sv_diff, su_diff)
                    swirl = fbm(rot_angle * 1.5 + spiral_dist * 8, spiral_dist * 3, 4, 0.5, 2.0, seed + i * 200)

                    swirl_color = color_lerp(base_color, palette['highlight'], swirl * 0.4)
                    base_color = color_lerp(base_color, swirl_color, spiral_t * 0.5)

            # === ÉCLAIRAGE DOUX ===
            # Simuler un éclairage de sphère sans spéculaire dur
            norm_dist = dist / planet_radius
            # Gradient radial subtil
            radial_light = 1.0 - norm_dist * 0.2
            # Légère luminosité directionnelle (lumière venant de la gauche)
            dir_light = 0.5 + (dx / planet_radius) * 0.2 - (dy / planet_radius) * 0.05
            total_light = radial_light * 0.6 + dir_light * 0.4

            brightness = 0.7 + total_light * 0.4

            r = min(255, int(base_color[0] * brightness))
            g = min(255, int(base_color[1] * brightness))
            b = min(255, int(base_color[2] * brightness))

            # Opacité pleine - pas de transparence aux bords
            pixels[x, y] = (r, g, b, 255)

    # Léger flou pour adoucir les bandes
    img = img.filter(ImageFilter.GaussianBlur(radius=1.0))

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
