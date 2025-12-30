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
