"""
Technology models for the research system.

This module handles:
- Player technology levels (6 domains)
- Research budget allocation
- Radical breakthrough mechanics
"""
from datetime import datetime
from enum import Enum
from app import db


class TechDomain(str, Enum):
    """Technology research domains."""
    RANGE = "range"           # Portee - flight distance
    SPEED = "speed"           # Vitesse - movement + combat priority
    WEAPONS = "weapons"       # Armes - offensive power
    SHIELDS = "shields"       # Boucliers - damage resistance
    MINI = "mini"             # Miniaturisation - reduce metal, increase money
    RADICAL = "radical"       # Recherche Radicale - unpredictable breakthroughs


class RadicalBreakthroughType(str, Enum):
    """Types of radical research breakthroughs."""
    TECH_BONUS_RANGE = "tech_bonus_range"       # Temporary +2 to Range
    TECH_BONUS_SPEED = "tech_bonus_speed"       # Temporary +2 to Speed
    TECH_BONUS_WEAPONS = "tech_bonus_weapons"   # Temporary +2 to Weapons
    TECH_BONUS_SHIELDS = "tech_bonus_shields"   # Temporary +2 to Shields
    TERRAFORM_BOOST = "terraform_boost"         # Faster terraformation
    SPY_INFO = "spy_info"                       # Info on distant planets
    STEAL_TECH = "steal_tech"                   # Steal tech from opponent
    UNLOCK_DECOY = "unlock_decoy"               # Unlock Decoy ships
    UNLOCK_BIOLOGICAL = "unlock_biological"     # Unlock Biological ships


class PlayerTechnology(db.Model):
    """
    Technology levels and research state for a player.

    Each player has one PlayerTechnology record that tracks:
    - Current levels in each domain (1+)
    - Progress towards next level (0.0 to cost_for_next_level)
    - Budget allocation across domains (must sum to 100)
    - Unlocked special ships (Decoy, Biological)
    - Temporary bonuses from radical breakthroughs
    """
    __tablename__ = "player_technologies"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(
        db.Integer,
        db.ForeignKey("game_players.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    # Current technology levels (start at 1, except radical at 0)
    range_level = db.Column(db.Integer, default=1, nullable=False)
    speed_level = db.Column(db.Integer, default=1, nullable=False)
    weapons_level = db.Column(db.Integer, default=1, nullable=False)
    shields_level = db.Column(db.Integer, default=1, nullable=False)
    mini_level = db.Column(db.Integer, default=1, nullable=False)
    radical_level = db.Column(db.Integer, default=0, nullable=False)

    # Research progress (accumulated points towards next level)
    range_progress = db.Column(db.Float, default=0.0, nullable=False)
    speed_progress = db.Column(db.Float, default=0.0, nullable=False)
    weapons_progress = db.Column(db.Float, default=0.0, nullable=False)
    shields_progress = db.Column(db.Float, default=0.0, nullable=False)
    mini_progress = db.Column(db.Float, default=0.0, nullable=False)
    radical_progress = db.Column(db.Float, default=0.0, nullable=False)

    # Research budget allocation (0-100 each, must sum to 100)
    range_budget = db.Column(db.Integer, default=17, nullable=False)
    speed_budget = db.Column(db.Integer, default=17, nullable=False)
    weapons_budget = db.Column(db.Integer, default=17, nullable=False)
    shields_budget = db.Column(db.Integer, default=17, nullable=False)
    mini_budget = db.Column(db.Integer, default=16, nullable=False)
    radical_budget = db.Column(db.Integer, default=16, nullable=False)

    # Radical unlocks (special ship types)
    decoy_unlocked = db.Column(db.Boolean, default=False, nullable=False)
    biological_unlocked = db.Column(db.Boolean, default=False, nullable=False)

    # Temporary bonuses from radical breakthroughs
    temp_range_bonus = db.Column(db.Integer, default=0, nullable=False)
    temp_speed_bonus = db.Column(db.Integer, default=0, nullable=False)
    temp_weapons_bonus = db.Column(db.Integer, default=0, nullable=False)
    temp_shields_bonus = db.Column(db.Integer, default=0, nullable=False)
    temp_bonus_expires_turn = db.Column(db.Integer, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship
    player = db.relationship(
        "GamePlayer",
        backref=db.backref("technology", uselist=False, cascade="all, delete-orphan")
    )

    def __repr__(self):
        return f"<PlayerTechnology player={self.player_id} R{self.range_level}/S{self.speed_level}/W{self.weapons_level}/Sh{self.shields_level}/M{self.mini_level}>"

    # -------------------------------------------------------------------------
    # Effective levels (including temporary bonuses)
    # -------------------------------------------------------------------------

    @property
    def effective_range(self) -> int:
        """Range level including temporary bonuses."""
        return self.range_level + self.temp_range_bonus

    @property
    def effective_speed(self) -> int:
        """Speed level including temporary bonuses."""
        return self.speed_level + self.temp_speed_bonus

    @property
    def effective_weapons(self) -> int:
        """Weapons level including temporary bonuses."""
        return self.weapons_level + self.temp_weapons_bonus

    @property
    def effective_shields(self) -> int:
        """Shields level including temporary bonuses."""
        return self.shields_level + self.temp_shields_bonus

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self):
        """Serialize technology state to dictionary."""
        return {
            "player_id": self.player_id,
            "levels": {
                "range": self.range_level,
                "speed": self.speed_level,
                "weapons": self.weapons_level,
                "shields": self.shields_level,
                "mini": self.mini_level,
                "radical": self.radical_level,
            },
            "effective_levels": {
                "range": self.effective_range,
                "speed": self.effective_speed,
                "weapons": self.effective_weapons,
                "shields": self.effective_shields,
            },
            "progress": {
                "range": self.range_progress,
                "speed": self.speed_progress,
                "weapons": self.weapons_progress,
                "shields": self.shields_progress,
                "mini": self.mini_progress,
                "radical": self.radical_progress,
            },
            "budget": {
                "range": self.range_budget,
                "speed": self.speed_budget,
                "weapons": self.weapons_budget,
                "shields": self.shields_budget,
                "mini": self.mini_budget,
                "radical": self.radical_budget,
            },
            "unlocks": {
                "decoy": self.decoy_unlocked,
                "biological": self.biological_unlocked,
            },
            "temp_bonuses": {
                "range": self.temp_range_bonus,
                "speed": self.temp_speed_bonus,
                "weapons": self.temp_weapons_bonus,
                "shields": self.temp_shields_bonus,
                "expires_turn": self.temp_bonus_expires_turn,
            },
        }


class RadicalBreakthrough(db.Model):
    """
    Pending or resolved radical breakthrough for a player.

    When radical research accumulates enough points, a breakthrough is triggered:
    1. Four random options are presented
    2. Player eliminates one option
    3. One of the remaining three is randomly unlocked
    """
    __tablename__ = "radical_breakthroughs"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(
        db.Integer,
        db.ForeignKey("game_players.id", ondelete="CASCADE"),
        nullable=False
    )

    # The 4 potential breakthroughs (JSON list of RadicalBreakthroughType values)
    options = db.Column(db.JSON, nullable=False)

    # The one eliminated by player (null until chosen)
    eliminated_option = db.Column(db.String(50), nullable=True)

    # The one that was unlocked (null until resolved)
    unlocked_option = db.Column(db.String(50), nullable=True)

    # State tracking
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)
    created_turn = db.Column(db.Integer, nullable=False)
    resolved_turn = db.Column(db.Integer, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    player = db.relationship(
        "GamePlayer",
        backref=db.backref("radical_breakthroughs", lazy="dynamic", cascade="all, delete-orphan")
    )

    def __repr__(self):
        status = "resolved" if self.is_resolved else "pending"
        return f"<RadicalBreakthrough {self.id} player={self.player_id} {status}>"

    def to_dict(self):
        """Serialize breakthrough to dictionary."""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "options": self.options,
            "eliminated_option": self.eliminated_option,
            "unlocked_option": self.unlocked_option,
            "is_resolved": self.is_resolved,
            "created_turn": self.created_turn,
            "resolved_turn": self.resolved_turn,
        }
