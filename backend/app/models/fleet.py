"""
Fleet and Ship models for the space fleet system.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from app import db


# =============================================================================
# Enumerations
# =============================================================================

class ShipType(str, Enum):
    """Types of ships available in the game."""
    FIGHTER = "fighter"           # Chasseur - balanced combat
    SCOUT = "scout"               # Éclaireur - long range, weak combat
    COLONY = "colony"             # Vaisseau Colonial - carries 10000 colonists
    SATELLITE = "satellite"       # Satellite - static defense, no movement
    TANKER = "tanker"             # Ravitailleur - extends fleet range
    BATTLESHIP = "battleship"     # Cuirassé - heavy combat
    DECOY = "decoy"               # Leurre - cheap distraction (Radical tech)
    BIOLOGICAL = "biological"     # Biologique - special (Radical tech)


class FleetStatus(str, Enum):
    """Status of a fleet."""
    STATIONED = "stationed"       # Orbiting a planet/star
    IN_TRANSIT = "in_transit"     # Traveling in hyperspace
    ARRIVING = "arriving"         # Arriving this turn


class CombatBehavior(str, Enum):
    """Combat behavior configuration."""
    AGGRESSIVE = "aggressive"     # Attack first, prioritize offense
    DEFENSIVE = "defensive"       # Protect, prioritize shields
    FOLLOW = "follow"             # Follow fleet leader
    NORMAL = "normal"             # Balanced approach


# =============================================================================
# Ship Type Base Statistics
# =============================================================================

SHIP_BASE_STATS = {
    ShipType.FIGHTER: {
        "range_bonus": 0,
        "speed_mult": 1.0,
        "weapons_mult": 1.0,
        "shields_mult": 1.0,
        "base_metal": 50,
        "base_money": 100,
        "special": None,
    },
    ShipType.SCOUT: {
        "range_bonus": 3,
        "speed_mult": 1.2,
        "weapons_mult": 0.3,
        "shields_mult": 0.3,
        "base_metal": 30,
        "base_money": 80,
        "special": None,
    },
    ShipType.COLONY: {
        "range_bonus": -1,
        "speed_mult": 0.5,
        "weapons_mult": 0.1,
        "shields_mult": 0.5,
        "base_metal": 200,
        "base_money": 500,
        "special": "colonists_10000",
    },
    ShipType.SATELLITE: {
        "range_bonus": 0,
        "speed_mult": 0,  # Cannot move
        "weapons_mult": 0.8,
        "shields_mult": 1.5,
        "base_metal": 20,
        "base_money": 30,
        "special": "stationary",
    },
    ShipType.TANKER: {
        "range_bonus": 0,
        "speed_mult": 0.8,
        "weapons_mult": 0.1,
        "shields_mult": 0.5,
        "base_metal": 100,
        "base_money": 200,
        "special": "refuel",
    },
    ShipType.BATTLESHIP: {
        "range_bonus": 0,
        "speed_mult": 0.7,
        "weapons_mult": 2.0,
        "shields_mult": 2.0,
        "base_metal": 300,
        "base_money": 600,
        "special": None,
    },
    ShipType.DECOY: {
        "range_bonus": 0,
        "speed_mult": 1.5,
        "weapons_mult": 0,
        "shields_mult": 0.1,
        "base_metal": 5,
        "base_money": 10,
        "special": "decoy",
        "requires_radical": True,
    },
    ShipType.BIOLOGICAL: {
        "range_bonus": 0,
        "speed_mult": 1.0,
        "weapons_mult": 1.5,
        "shields_mult": 0.5,
        "base_metal": 0,  # No metal, organic
        "base_money": 300,
        "special": "biological",
        "requires_radical": True,
    },
}


# =============================================================================
# ShipDesign Model
# =============================================================================

class ShipDesign(db.Model):
    """
    A ship design created by a player.
    Defines the technology levels and type for a class of ships.
    """
    __tablename__ = "ship_designs"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("game_players.id"), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    ship_type = db.Column(db.String(20), nullable=False)

    # Technology levels (1-10+, based on player's research)
    range_level = db.Column(db.Integer, default=1, nullable=False)
    speed_level = db.Column(db.Integer, default=1, nullable=False)
    weapons_level = db.Column(db.Integer, default=1, nullable=False)
    shields_level = db.Column(db.Integer, default=1, nullable=False)
    mini_level = db.Column(db.Integer, default=1, nullable=False)

    # Cached costs (calculated on creation)
    prototype_cost_money = db.Column(db.Integer, default=0, nullable=False)
    prototype_cost_metal = db.Column(db.Integer, default=0, nullable=False)
    production_cost_money = db.Column(db.Integer, default=0, nullable=False)
    production_cost_metal = db.Column(db.Integer, default=0, nullable=False)

    # State
    is_prototype_built = db.Column(db.Boolean, default=False, nullable=False)
    ships_built = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player = db.relationship("GamePlayer", backref=db.backref("ship_designs", lazy="dynamic"))
    ships = db.relationship("Ship", backref="design", lazy="dynamic")

    def __repr__(self):
        return f"<ShipDesign {self.name} ({self.ship_type})>"

    @property
    def base_stats(self):
        """Get base stats for this ship type."""
        return SHIP_BASE_STATS.get(ShipType(self.ship_type), SHIP_BASE_STATS[ShipType.FIGHTER])

    @property
    def effective_range(self) -> float:
        """Calculate effective range based on tech level and ship type."""
        base = self.base_stats
        # Base range is 5 units per range level, plus type bonus
        return (self.range_level * 5) + base["range_bonus"]

    @property
    def effective_speed(self) -> float:
        """Calculate effective speed based on tech level and ship type."""
        base = self.base_stats
        return self.speed_level * base["speed_mult"]

    @property
    def effective_weapons(self) -> float:
        """Calculate effective weapons based on tech level and ship type."""
        base = self.base_stats
        return self.weapons_level * base["weapons_mult"]

    @property
    def effective_shields(self) -> float:
        """Calculate effective shields based on tech level and ship type."""
        base = self.base_stats
        return self.shields_level * base["shields_mult"]

    def calculate_costs(self):
        """Calculate and cache production costs."""
        base = self.base_stats

        # Technology factor (average of all tech levels)
        tech_factor = (
            self.range_level +
            self.speed_level +
            self.weapons_level +
            self.shields_level
        ) / 4

        # Miniaturization: reduces metal, increases money
        mini_metal_reduction = 1 - (self.mini_level * 0.08)  # -8% metal per level
        mini_money_increase = 1 + (self.mini_level * 0.10)   # +10% money per level

        # Base costs
        metal_cost = int(base["base_metal"] * tech_factor * mini_metal_reduction)
        money_cost = int(base["base_money"] * tech_factor * mini_money_increase)

        # Minimum costs
        metal_cost = max(1, metal_cost) if base["base_metal"] > 0 else 0
        money_cost = max(1, money_cost)

        # Set costs
        self.production_cost_metal = metal_cost
        self.production_cost_money = money_cost
        self.prototype_cost_metal = metal_cost * 2
        self.prototype_cost_money = money_cost * 2

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "name": self.name,
            "ship_type": self.ship_type,
            "range_level": self.range_level,
            "speed_level": self.speed_level,
            "weapons_level": self.weapons_level,
            "shields_level": self.shields_level,
            "mini_level": self.mini_level,
            "effective_range": self.effective_range,
            "effective_speed": self.effective_speed,
            "effective_weapons": self.effective_weapons,
            "effective_shields": self.effective_shields,
            "prototype_cost_money": self.prototype_cost_money,
            "prototype_cost_metal": self.prototype_cost_metal,
            "production_cost_money": self.production_cost_money,
            "production_cost_metal": self.production_cost_metal,
            "is_prototype_built": self.is_prototype_built,
            "ships_built": self.ships_built,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# =============================================================================
# Fleet Model
# =============================================================================

class Fleet(db.Model):
    """
    A group of ships belonging to a player.
    """
    __tablename__ = "fleets"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("game_players.id"), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    # Current position (null if in transit)
    current_planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=True)

    # Movement
    status = db.Column(db.String(20), default=FleetStatus.STATIONED.value, nullable=False)
    destination_planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=True)
    departure_turn = db.Column(db.Integer, nullable=True)
    arrival_turn = db.Column(db.Integer, nullable=True)

    # Travel path (stored as JSON: list of planet IDs for multi-hop journeys)
    travel_path = db.Column(db.JSON, nullable=True)

    # Fuel (distance units remaining before needing refuel)
    fuel_remaining = db.Column(db.Float, default=10.0, nullable=False)
    max_fuel = db.Column(db.Float, default=10.0, nullable=False)

    # Combat configuration
    combat_behavior = db.Column(db.String(20), default=CombatBehavior.NORMAL.value, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player = db.relationship("GamePlayer", backref=db.backref("fleets", lazy="dynamic"))
    current_planet = db.relationship("Planet", foreign_keys=[current_planet_id],
                                     backref=db.backref("stationed_fleets", lazy="dynamic"))
    destination_planet = db.relationship("Planet", foreign_keys=[destination_planet_id])
    ships = db.relationship("Ship", backref="fleet", lazy="dynamic")

    def __repr__(self):
        return f"<Fleet {self.name} ({self.ship_count} ships)>"

    @property
    def ship_count(self) -> int:
        """Number of ships in the fleet."""
        return self.ships.filter_by(is_destroyed=False).count()

    @property
    def is_empty(self) -> bool:
        """Check if fleet has no active ships."""
        return self.ship_count == 0

    @property
    def fleet_speed(self) -> float:
        """Fleet speed is limited by slowest ship."""
        ships = self.ships.filter_by(is_destroyed=False).all()
        if not ships:
            return 0
        return min(ship.design.effective_speed for ship in ships)

    @property
    def fleet_range(self) -> float:
        """Fleet range is limited by shortest-range ship."""
        ships = self.ships.filter_by(is_destroyed=False).all()
        if not ships:
            return 0

        base_range = min(ship.design.effective_range for ship in ships)

        # Tanker bonus: extends range by 50%
        has_tanker = any(ship.design.ship_type == ShipType.TANKER.value for ship in ships)
        if has_tanker:
            return base_range * 1.5

        return base_range

    @property
    def total_weapons(self) -> float:
        """Total fleet weapons power."""
        ships = self.ships.filter_by(is_destroyed=False).all()
        return sum(ship.design.effective_weapons for ship in ships)

    @property
    def total_shields(self) -> float:
        """Total fleet shields."""
        ships = self.ships.filter_by(is_destroyed=False).all()
        return sum(ship.design.effective_shields for ship in ships)

    @property
    def can_colonize(self) -> bool:
        """Check if fleet has a colony ship."""
        return self.ships.filter_by(is_destroyed=False).join(ShipDesign).filter(
            ShipDesign.ship_type == ShipType.COLONY.value
        ).count() > 0

    def get_ships_by_type(self) -> dict:
        """Get ship count by type."""
        ships = self.ships.filter_by(is_destroyed=False).all()
        counts = {}
        for ship in ships:
            ship_type = ship.design.ship_type
            counts[ship_type] = counts.get(ship_type, 0) + 1
        return counts

    def to_dict(self, include_ships: bool = False):
        """Convert to dictionary."""
        data = {
            "id": self.id,
            "player_id": self.player_id,
            "name": self.name,
            "status": self.status,
            "current_planet_id": self.current_planet_id,
            "destination_planet_id": self.destination_planet_id,
            "departure_turn": self.departure_turn,
            "arrival_turn": self.arrival_turn,
            "fuel_remaining": self.fuel_remaining,
            "max_fuel": self.max_fuel,
            "combat_behavior": self.combat_behavior,
            "ship_count": self.ship_count,
            "fleet_speed": self.fleet_speed,
            "fleet_range": self.fleet_range,
            "total_weapons": self.total_weapons,
            "total_shields": self.total_shields,
            "can_colonize": self.can_colonize,
            "ships_by_type": self.get_ships_by_type(),
        }

        if include_ships:
            data["ships"] = [ship.to_dict() for ship in self.ships.filter_by(is_destroyed=False)]

        return data


# =============================================================================
# Ship Model
# =============================================================================

class Ship(db.Model):
    """
    An individual ship instance.
    """
    __tablename__ = "ships"

    id = db.Column(db.Integer, primary_key=True)
    design_id = db.Column(db.Integer, db.ForeignKey("ship_designs.id"), nullable=False)
    fleet_id = db.Column(db.Integer, db.ForeignKey("fleets.id"), nullable=True)

    # State
    damage = db.Column(db.Integer, default=0, nullable=False)
    is_destroyed = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    destroyed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Ship {self.id} ({self.design.ship_type if self.design else 'unknown'})>"

    @property
    def health_percent(self) -> float:
        """Current health as percentage."""
        max_health = self.design.effective_shields * 10
        current_health = max(0, max_health - self.damage)
        return (current_health / max_health) * 100 if max_health > 0 else 0

    @property
    def is_damaged(self) -> bool:
        """Check if ship has taken damage."""
        return self.damage > 0

    def take_damage(self, amount: int) -> bool:
        """
        Apply damage to ship.
        Returns True if ship is destroyed.
        """
        self.damage += amount
        max_health = self.design.effective_shields * 10

        if self.damage >= max_health:
            self.is_destroyed = True
            self.destroyed_at = datetime.utcnow()
            return True

        return False

    def repair(self, amount: int = None):
        """Repair ship damage."""
        if amount is None:
            self.damage = 0
        else:
            self.damage = max(0, self.damage - amount)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "design_id": self.design_id,
            "design_name": self.design.name if self.design else None,
            "ship_type": self.design.ship_type if self.design else None,
            "fleet_id": self.fleet_id,
            "damage": self.damage,
            "health_percent": self.health_percent,
            "is_destroyed": self.is_destroyed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# =============================================================================
# Production Queue Model
# =============================================================================

class ProductionQueue(db.Model):
    """
    Tracks ships being built at a planet.
    Each entry represents a ship design being produced.
    """
    __tablename__ = "production_queue"

    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=False)
    design_id = db.Column(db.Integer, db.ForeignKey("ship_designs.id"), nullable=False)
    fleet_id = db.Column(db.Integer, db.ForeignKey("fleets.id"), nullable=True)  # Target fleet

    # Queue order (lower = higher priority)
    priority = db.Column(db.Integer, default=0, nullable=False)

    # Production state
    production_invested = db.Column(db.Float, default=0.0, nullable=False)  # Points already invested
    is_completed = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    planet = db.relationship("Planet", backref=db.backref("production_queue", lazy="dynamic",
                             order_by="ProductionQueue.priority"))
    design = db.relationship("ShipDesign")
    fleet = db.relationship("Fleet")

    def __repr__(self):
        return f"<ProductionQueue {self.id}: {self.design.name if self.design else '?'} at planet {self.planet_id}>"

    @property
    def production_required(self) -> float:
        """Total production points required to complete this ship."""
        if not self.design:
            return 0
        # Production cost = metal + money (combined metric)
        # First ship of a design costs 2x (prototype)
        if not self.design.is_prototype_built:
            return self.design.prototype_cost_metal + self.design.prototype_cost_money
        return self.design.production_cost_metal + self.design.production_cost_money

    @property
    def production_progress(self) -> float:
        """Progress as percentage (0-100)."""
        required = self.production_required
        if required <= 0:
            return 100
        return min(100, (self.production_invested / required) * 100)

    @property
    def is_ready(self) -> bool:
        """Check if production is complete."""
        return self.production_invested >= self.production_required

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "planet_id": self.planet_id,
            "design_id": self.design_id,
            "design_name": self.design.name if self.design else None,
            "ship_type": self.design.ship_type if self.design else None,
            "fleet_id": self.fleet_id,
            "priority": self.priority,
            "production_invested": self.production_invested,
            "production_required": self.production_required,
            "production_progress": self.production_progress,
            "is_completed": self.is_completed,
            "is_ready": self.is_ready,
        }
