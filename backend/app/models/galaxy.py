"""
Galaxy and Planet models
"""
from datetime import datetime
from enum import Enum
from app import db


class GalaxyShape(str, Enum):
    """Galaxy shape options."""
    CIRCLE = "circle"
    SPIRAL = "spiral"
    CLUSTER = "cluster"
    RANDOM = "random"


class GalaxyDensity(str, Enum):
    """Galaxy density options."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PlanetState(str, Enum):
    """Planet state enumeration."""
    UNEXPLORED = "unexplored"
    EXPLORED = "explored"
    COLONIZED = "colonized"
    DEVELOPED = "developed"
    HOSTILE = "hostile"
    ABANDONED = "abandoned"


class Galaxy(db.Model):
    """Galaxy model - contains all planets for a game."""

    __tablename__ = "galaxies"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False, unique=True)

    # Configuration
    shape = db.Column(db.String(20), default=GalaxyShape.RANDOM.value, nullable=False)
    density = db.Column(db.String(20), default=GalaxyDensity.MEDIUM.value, nullable=False)
    planet_count = db.Column(db.Integer, default=50, nullable=False)

    # Dimensions (unites de jeu)
    width = db.Column(db.Float, default=200.0, nullable=False)
    height = db.Column(db.Float, default=200.0, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    game = db.relationship("Game", back_populates="galaxy")
    planets = db.relationship("Planet", back_populates="galaxy", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Galaxy {self.id} ({self.shape}, {self.planet_count} planets)>"

    def to_dict(self, include_planets=False):
        """Serialize galaxy to dictionary."""
        data = {
            "id": self.id,
            "game_id": self.game_id,
            "shape": self.shape,
            "density": self.density,
            "planet_count": self.planet_count,
            "width": self.width,
            "height": self.height,
        }
        if include_planets:
            data["planets"] = [planet.to_dict() for planet in self.planets]
        return data


class Planet(db.Model):
    """Planet model - a colonizable world in the galaxy."""

    __tablename__ = "planets"

    id = db.Column(db.Integer, primary_key=True)
    galaxy_id = db.Column(db.Integer, db.ForeignKey("galaxies.id"), nullable=False)

    # Identity
    name = db.Column(db.String(50), nullable=False)

    # Position in galaxy (previously on Star)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)

    # Nova event (previously on Star)
    is_nova = db.Column(db.Boolean, default=False, nullable=False)
    nova_turn = db.Column(db.Integer, nullable=True)

    # Physical characteristics (fixed)
    temperature = db.Column(db.Float, nullable=False)  # Celsius, ideal = 22
    gravity = db.Column(db.Float, nullable=False)  # g, ideal = 1.0

    # Resources
    metal_reserves = db.Column(db.Integer, default=0, nullable=False)  # Initial reserves
    metal_remaining = db.Column(db.Integer, default=0, nullable=False)  # Current reserves

    # State
    state = db.Column(db.String(20), default=PlanetState.UNEXPLORED.value, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("game_players.id"), nullable=True)

    # Population
    population = db.Column(db.Integer, default=0, nullable=False)
    max_population = db.Column(db.Integer, default=0, nullable=False)  # Based on temp/gravity

    # Terraformation progress (temperature modification)
    current_temperature = db.Column(db.Float, nullable=False)  # Current temp after terraforming

    # Economy (per turn allocations in %)
    # Note: terraform_budget + mining_budget + ships_budget = 100
    terraform_budget = db.Column(db.Integer, default=34)  # 0-100
    mining_budget = db.Column(db.Integer, default=33)  # 0-100
    ships_budget = db.Column(db.Integer, default=33)  # 0-100

    # Ship production accumulator
    ship_production_points = db.Column(db.Float, default=0.0)  # Accumulated production

    # Flags
    is_home_planet = db.Column(db.Boolean, default=False)

    # History (generated upon exploration)
    history_line1 = db.Column(db.String(200), nullable=True)
    history_line2 = db.Column(db.String(200), nullable=True)

    # Visual appearance (fixed at creation)
    texture_type = db.Column(db.String(20), nullable=True)  # habitable, desert, ice, volcanic, barren, gas
    texture_index = db.Column(db.Integer, nullable=True)  # 1-100 for texture variety

    # Timestamps
    colonized_at = db.Column(db.DateTime, nullable=True)
    explored_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    galaxy = db.relationship("Galaxy", back_populates="planets")
    owner = db.relationship("GamePlayer", back_populates="planets", foreign_keys=[owner_id])

    def __repr__(self):
        return f"<Planet {self.name} at ({self.x:.1f}, {self.y:.1f}) ({self.state})>"

    @property
    def habitability(self):
        """Calculate habitability score (0-1) based on temperature and gravity."""
        # Temperature factor: ideal at 22C, drops off with distance
        temp_diff = abs(self.current_temperature - 22)
        temp_factor = max(0, 1 - (temp_diff / 100))

        # Gravity factor: ideal at 1.0g
        gravity_diff = abs(self.gravity - 1.0)
        gravity_factor = max(0, 1 - (gravity_diff / 2))

        return temp_factor * gravity_factor

    def calculate_max_population(self):
        """Calculate max population based on habitability."""
        base_population = 1_000_000  # 1 million base
        return int(base_population * self.habitability)

    def to_dict(self):
        """Serialize planet to dictionary."""
        return {
            "id": self.id,
            "galaxy_id": self.galaxy_id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "is_nova": self.is_nova,
            "nova_turn": self.nova_turn,
            "temperature": self.temperature,
            "current_temperature": self.current_temperature,
            "gravity": self.gravity,
            "metal_reserves": self.metal_reserves,
            "metal_remaining": self.metal_remaining,
            "state": self.state,
            "owner_id": self.owner_id,
            "population": self.population,
            "max_population": self.max_population,
            "habitability": round(self.habitability, 2),
            "terraform_budget": self.terraform_budget,
            "mining_budget": self.mining_budget,
            "ships_budget": self.ships_budget,
            "ship_production_points": self.ship_production_points,
            "is_home_planet": self.is_home_planet,
            "history_line1": self.history_line1,
            "history_line2": self.history_line2,
            "texture_type": self.texture_type,
            "texture_index": self.texture_index,
        }
