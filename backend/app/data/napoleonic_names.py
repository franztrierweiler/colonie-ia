"""
Napoleonic-themed names for planets, stars, and AI players.
"""

# Star/System names - Major Napoleonic battles and locations
STAR_NAMES = [
    # Major victories
    "Austerlitz",
    "Marengo",
    "Iéna",
    "Wagram",
    "Arcole",
    "Rivoli",
    "Pyramides",
    "Friedland",
    "Ulm",
    "Eylau",
    # Italian campaigns
    "Lodi",
    "Castiglione",
    "Bassano",
    "Mantua",
    "Mondovi",
    "Millesimo",
    # Egyptian campaign
    "Aboukir",
    "Memphis",
    "Alexandrie",
    "Le Caire",
    # German campaigns
    "Ratisbonne",
    "Eckmühl",
    "Essling",
    "Aspern",
    "Landshut",
    # Russian campaign
    "Borodino",
    "Smolensk",
    "Vitebsk",
    "Moscou",
    "Krasnoï",
    "Bérézina",
    # Spanish campaign
    "Madrid",
    "Saragosse",
    "Burgos",
    "Somo Sierra",
    # Final campaigns
    "Leipzig",
    "Dresde",
    "Lützen",
    "Bautzen",
    "Montmirail",
    "Champaubert",
    "Montereau",
    "Craonne",
    "Laon",
    # Hundred Days
    "Waterloo",
    "Ligny",
    "Quatre-Bras",
    # Locations
    "Corse",
    "Ajaccio",
    "Fontainebleau",
    "Malmaison",
    "Saint-Cloud",
    "Compiègne",
    "Tilsit",
    "Erfurt",
    # Islands
    "Elbe",
    "Sainte-Hélène",
    "Capri",
    "Malte",
    # Naval
    "Trafalgar",
    "Nil",
    "Copenhague",
    # Additional locations
    "Toulon",
    "Vendôme",
    "Austerlitz Prime",
    "Marengo II",
    "Nouvelle Corse",
    "Impérial",
    "Gloire",
    "Victoire",
    "Triomphe",
    "Honneur",
    "Aigle",
    "Couronne",
    "Soleil",
    "Étoile",
    "Grognard",
    "Hussard",
    "Cuirassier",
    "Grenadier",
    "Voltigeur",
    "Artillerie",
    "Cavalerie",
    "Infanterie",
    "Garde",
    "Légion",
    "Régiment",
    "Brigade",
    "Division",
    "Corps",
    "Armée",
    "Empire",
]

# Planet suffixes for multiple planets per star
PLANET_SUFFIXES = ["Prime", "Secundus", "Tertius", "Quartus"]

# AI player names - Napoleonic marshals and generals
AI_NAMES = [
    # Marshals of the Empire
    "Maréchal Ney",
    "Maréchal Murat",
    "Maréchal Davout",
    "Maréchal Lannes",
    "Maréchal Masséna",
    "Maréchal Soult",
    "Maréchal Berthier",
    "Maréchal Bernadotte",
    "Maréchal Augereau",
    "Maréchal Bessières",
    "Maréchal Mortier",
    "Maréchal Lefebvre",
    "Maréchal Kellermann",
    "Maréchal Pérignon",
    "Maréchal Sérurier",
    "Maréchal Brune",
    "Maréchal Moncey",
    "Maréchal Jourdan",
    "Maréchal Victor",
    "Maréchal MacDonald",
    "Maréchal Oudinot",
    "Maréchal Marmont",
    "Maréchal Suchet",
    "Maréchal Gouvion Saint-Cyr",
    "Maréchal Poniatowski",
    "Maréchal Grouchy",
    # Enemy generals (for variety)
    "Duc de Wellington",
    "Prince Koutouzov",
    "Général Blücher",
    "Archiduc Charles",
    "Amiral Nelson",
    "Général Moore",
]

# Player colors - Empire-inspired
PLAYER_COLORS = [
    "#1E3A8A",  # Bleu impérial
    "#DC2626",  # Rouge régimentaire
    "#15803D",  # Vert chasseur
    "#CA8A04",  # Or impérial
    "#7C3AED",  # Violet royal
    "#EA580C",  # Orange cuivre
    "#0891B2",  # Cyan marine
    "#78350F",  # Brun cavalerie
]

# Technology names (for future use)
TECH_NAMES = {
    "range": [
        "Longue Vue",
        "Télescope de Cassini",
        "Optique de Campagne",
        "Navigation Stellaire",
        "Cartographie Galactique",
    ],
    "speed": [
        "Charge de Cavalerie",
        "Hussards Volants",
        "Manœuvre d'Ulm",
        "Grande Randonnée",
        "Éclair de Marengo",
    ],
    "weapons": [
        "Canon de 12",
        "Artillerie à Cheval",
        "Batterie de la Garde",
        "Feu de Salve",
        "Grapeshot Impérial",
    ],
    "shields": [
        "Carré d'Infanterie",
        "Cuirasse de Cavalerie",
        "Forteresse Mobile",
        "Bouclier Impérial",
        "Retraite de Russie",
    ],
    "miniaturization": [
        "Artisanat Corse",
        "Manufacture de Sèvres",
        "Ingénierie Polytechnique",
        "Miniature de Campagne",
        "Nanotechnologie Impériale",
    ],
}

# Barbaric/Strange names for hostile planets (extreme temperature or gravity)
HOSTILE_PLANET_NAMES = [
    # Infernal/volcanic names
    "Xarthog",
    "Malebolge",
    "Pyrrhus-IX",
    "Vulcanis",
    "Infernalis",
    "Gehenna",
    "Phlegethon",
    "Tartare",
    # Frozen/dead names
    "Glacialis",
    "Niflheim",
    "Cryos",
    "Gélidor",
    "Mortuus",
    "Nécrosis",
    "Thanatos",
    # Gaseous/methane names
    "Méthanus",
    "Toxicum",
    "Miasma",
    "Pútridos",
    "Venénum",
    "Noxius",
    "Chaotica",
    # Crushing gravity names
    "Gravis-Prime",
    "Titanis",
    "Colossus",
    "Écraseur",
    "Oppressio",
    # Generic barbaric names
    "Xyloth",
    "Zarthan",
    "Kragoth",
    "Voraxis",
    "Morkhan",
    "Draxul",
    "Skaragg",
    "Thulthos",
    "Gorthak",
    "Vexaris",
    "Xyragos",
    "Krethul",
    "Malvonis",
    "Skorrath",
    "Zulghast",
]

# Special messages for specific planets
SPECIAL_PLANET_MESSAGES = {
    "Elbe": "L'Empereur reviendra...",
    "Sainte-Hélène": "Ici repose un conquérant...",
    "Waterloo": "La Garde meurt mais ne se rend pas !",
    "Austerlitz": "Le soleil d'Austerlitz brille sur cette planète.",
    "Moscou": "L'hiver approche...",
    "Trafalgar": "L'Angleterre attend que chacun fasse son devoir.",
}

# Easter egg dates
EASTER_EGG_DATES = {
    "12-02": {  # 2 décembre - Sacre et Austerlitz
        "name": "Jour du Sacre",
        "effect": "golden_bicorn",
        "message": "En ce jour, l'Empereur fut sacré !",
    },
    "08-15": {  # 15 août - Anniversaire de Napoléon
        "name": "Anniversaire de l'Empereur",
        "effect": "tricolor_cockade",
        "message": "Vive l'Empereur !",
    },
    "10-21": {  # 21 octobre - Trafalgar
        "name": "Jour de Trafalgar",
        "effect": "naval_theme",
        "message": "La mer reste anglaise...",
    },
    "06-18": {  # 18 juin - Waterloo
        "name": "Jour de Waterloo",
        "effect": "somber_theme",
        "message": "La Garde meurt...",
    },
}


def get_random_star_name(used_names: set[str] | None = None) -> str:
    """Get a random unused star name."""
    import random
    available = [name for name in STAR_NAMES if used_names is None or name not in used_names]
    if not available:
        # Generate a numbered name if all are used
        return f"Système-{random.randint(1000, 9999)}"
    return random.choice(available)


def get_random_hostile_name(used_names: set[str] | None = None) -> str:
    """Get a random unused hostile planet name (barbaric/strange)."""
    import random
    available = [name for name in HOSTILE_PLANET_NAMES if used_names is None or name not in used_names]
    if not available:
        # Generate a procedural barbaric name if all are used
        prefixes = ["Xar", "Zul", "Kra", "Mor", "Vor", "Dra", "Ska", "Thr", "Gor", "Mal"]
        suffixes = ["thog", "gast", "rath", "xis", "khan", "thos", "gor", "nis", "vax", "zul"]
        return f"{random.choice(prefixes)}{random.choice(suffixes)}-{random.randint(1, 99)}"
    return random.choice(available)


def get_random_ai_name(used_names: set[str] | None = None) -> str:
    """Get a random unused AI name."""
    import random
    available = [name for name in AI_NAMES if used_names is None or name not in used_names]
    if not available:
        # Generate a numbered name if all are used
        return f"Général #{random.randint(100, 999)}"
    return random.choice(available)


def get_player_color(index: int) -> str:
    """Get player color by index (cycles through colors)."""
    return PLAYER_COLORS[index % len(PLAYER_COLORS)]


# ============================================================================
# Planet History Generator
# ============================================================================

# Prehistoric creature names
PREHISTORIC_CREATURES = [
    "Zorgon", "Macrozon", "Titanex", "Kryptodonte", "Mégazaure",
    "Ferox", "Colossaure", "Primordius", "Ancestrix", "Gigantum",
    "Raptodon", "Thermosaure", "Cryobête", "Vulcanex", "Aérogon",
    "Léviathon", "Béhémoth", "Krakenos", "Serpentix", "Draconis",
]

# Extinct civilization names
EXTINCT_CIVILIZATIONS = [
    "les Anciens", "les Premiers Hommes", "la civilisation Xéna",
    "les Bâtisseurs", "le peuple Oublié", "les Architectes",
    "les Précurseurs", "la dynastie Éternelle", "les Voyageurs",
    "les Gardiens", "les Éveillés", "le Conseil des Sages",
]

# Planet age descriptions
PLANET_AGES = [
    ("jeune", "800 millions", "1.2 milliard"),
    ("mature", "3 milliards", "5 milliards"),
    ("ancienne", "7 milliards", "9 milliards"),
    ("primordiale", "10 milliards", "12 milliards"),
]

# Origin types
PLANET_ORIGINS = [
    "accrétion de poussières stellaires",
    "collision de protoplanètes",
    "capture gravitationnelle",
    "éjection d'une géante gazeuse",
    "condensation d'un nuage moléculaire",
    "fusion de planétésimaux",
    "résidu d'une supernova",
]


def generate_planet_history(temperature: float, gravity: float, metal_reserves: int) -> tuple[str, str]:
    """
    Generate two lines of history for a planet based on its characteristics.

    Args:
        temperature: Current temperature in Celsius
        gravity: Surface gravity in g
        metal_reserves: Metal reserves amount

    Returns:
        Tuple of (line1, line2) describing the planet's history
    """
    import random

    lines = []

    # Determine planet type for context
    is_cold = temperature < -30
    is_hot = temperature > 60
    is_temperate = -10 <= temperature <= 40
    is_heavy_gravity = gravity > 1.5
    is_low_gravity = gravity < 0.5
    is_metal_rich = metal_reserves > 1000

    # Line 1: Geological/biological history
    line1_options = []

    # Prehistoric life traces (more likely on temperate planets)
    if is_temperate or random.random() < 0.3:
        creature = random.choice(PREHISTORIC_CREATURES)
        trait = random.choice([
            "herbivore géant", "prédateur redoutable", "animal nocturne",
            "créature amphibie", "bête volante", "reptile cuirassé",
            "mammifère primitif", "insecte colossal", "vermiforme souterrain"
        ])
        line1_options.append(f"Traces de {creature}, {trait} préhistorique.")

    # Extinct human presence (rare)
    if random.random() < 0.15:
        civ = random.choice(EXTINCT_CIVILIZATIONS)
        era = random.choice([
            "il y a 50 000 ans", "il y a 100 000 ans", "à l'ère pré-stellaire",
            "avant l'Exode", "durant l'Âge Sombre", "à l'époque des Pionniers"
        ])
        line1_options.append(f"Présence humaine détectée ({civ}), éteinte {era}.")

    # Geological events based on conditions
    if is_cold:
        line1_options.extend([
            "Anciennes mers gelées sous la surface cratérisée.",
            "Glaciation totale survenue il y a 2 milliards d'années.",
            "Vestiges de geysers cryovolcaniques inactifs.",
        ])
    elif is_hot:
        line1_options.extend([
            "Coulées de lave fossilisées couvrant 40% de la surface.",
            "Anciennes chaînes volcaniques encore fumantes.",
            "Océans de magma solidifiés formant des plaines basaltiques.",
        ])

    if is_heavy_gravity:
        line1_options.extend([
            "Noyau ultra-dense composé de métaux lourds.",
            "Compression gravitationnelle ayant écrasé toute vie ancienne.",
        ])
    elif is_low_gravity:
        line1_options.extend([
            "Atmosphère dissipée dans l'espace il y a des millions d'années.",
            "Structure interne poreuse, possible corps poreux.",
            "Résidu d'une explosion planétaire cataclysmique.",
            "Fragment d'une géante gazeuse détruite par collision.",
            "Nuage de méthane condensé après destruction d'un corps massif.",
        ])

    if is_metal_rich:
        line1_options.extend([
            "Gisements de métaux rares formés par impact d'astéroïde.",
            "Sous-sol riche en minerais d'origine volcanique profonde.",
        ])

    # Fallback options
    line1_options.extend([
        "Aucune trace de vie passée détectée.",
        "Formations rocheuses suggérant une activité sismique ancienne.",
        "Surface marquée par des impacts météoritiques millénaires.",
    ])

    line1 = random.choice(line1_options)

    # Line 2: Age and origin
    age_type, min_age, max_age = random.choice(PLANET_AGES)
    origin = random.choice(PLANET_ORIGINS)

    line2_options = [
        f"Planète {age_type}, née il y a environ {min_age} d'années par {origin}.",
        f"Âge estimé : {min_age} à {max_age} d'années. Origine : {origin}.",
        f"Formation datée de {min_age} d'années, issue de {origin}.",
    ]

    # Special cases for extreme planets
    if is_hot and random.random() < 0.4:
        line2_options.append("Rapprochement progressif de son étoile détecté. Durée de vie limitée.")
    if is_cold and random.random() < 0.4:
        line2_options.append("Éloignement orbital progressif. Refroidissement irréversible en cours.")
    if metal_reserves > 2000:
        line2_options.append(f"Richesse minérale exceptionnelle : cœur métallique exposé par érosion.")

    line2 = random.choice(line2_options)

    return (line1, line2)
