"""
Game and GamePlayer models
"""
from datetime import datetime
from enum import Enum
from app import db


class GameStatus(str, Enum):
    """Game status enumeration."""

    LOBBY = "lobby"  # Waiting for players
    RUNNING = "running"  # Game in progress
    PAUSED = "paused"  # Game paused
    FINISHED = "finished"  # Game completed
    ABANDONED = "abandoned"  # Game abandoned


class AIDifficulty(str, Enum):
    """AI difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class Game(db.Model):
    """Game instance model."""

    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default=GameStatus.LOBBY.value, nullable=False)

    # Galaxy configuration
    star_count = db.Column(db.Integer, default=50, nullable=False)
    galaxy_shape = db.Column(db.String(20), default=GalaxyShape.RANDOM.value)
    density = db.Column(db.Float, default=1.0)  # Stellar density

    # Game settings
    max_players = db.Column(db.Integer, default=8, nullable=False)
    turn_duration_years = db.Column(db.Integer, default=10)  # Years per turn
    turn_timer_seconds = db.Column(db.Integer, nullable=True)  # Optional timer
    current_turn = db.Column(db.Integer, default=0)
    current_year = db.Column(db.Integer, default=2200)

    # Options
    alliances_enabled = db.Column(db.Boolean, default=True)
    combat_luck_enabled = db.Column(db.Boolean, default=True)
    ai_difficulty = db.Column(db.String(20), default="medium")

    # Admin
    admin_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    admin = db.relationship("User", foreign_keys=[admin_user_id])
    players = db.relationship("GamePlayer", back_populates="game", lazy="dynamic")
    galaxy = db.relationship("Galaxy", back_populates="game", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game {self.name} ({self.status})>"

    def to_dict(self):
        """Serialize game to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "star_count": self.star_count,
            "galaxy_shape": self.galaxy_shape,
            "max_players": self.max_players,
            "current_turn": self.current_turn,
            "current_year": self.current_year,
            "player_count": self.players.count(),
            "admin_id": self.admin_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class GamePlayer(db.Model):
    """Association between User and Game (player in a game)."""

    __tablename__ = "game_players"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # Nullable for AI players

    # Player info
    player_name = db.Column(db.String(50), nullable=False)  # In-game name
    color = db.Column(db.String(7), nullable=False)  # Hex color #RRGGBB
    is_ai = db.Column(db.Boolean, default=False)
    ai_difficulty = db.Column(db.String(20), nullable=True)  # Only for AI players
    is_active = db.Column(db.Boolean, default=True)  # Still in game
    is_eliminated = db.Column(db.Boolean, default=False)
    is_ready = db.Column(db.Boolean, default=False)  # Ready in lobby

    # Player state (denormalized for quick access)
    money = db.Column(db.Integer, default=1000)
    metal = db.Column(db.Integer, default=500)
    debt = db.Column(db.Integer, default=0)
    planet_count = db.Column(db.Integer, default=1)

    # Turn management
    turn_submitted = db.Column(db.Boolean, default=False)

    # Timestamps
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    eliminated_at = db.Column(db.DateTime, nullable=True)

    # Home planet reference
    home_planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=True)

    # Relationships
    game = db.relationship("Game", back_populates="players")
    user = db.relationship("User", back_populates="games")
    planets = db.relationship("Planet", back_populates="owner", foreign_keys="Planet.owner_id")
    home_planet = db.relationship("Planet", foreign_keys=[home_planet_id], post_update=True)

    # Unique constraint: one user per game
    __table_args__ = (
        db.UniqueConstraint("game_id", "user_id", name="unique_user_per_game"),
    )

    def __repr__(self):
        return f"<GamePlayer {self.player_name} in Game {self.game_id}>"

    def to_dict(self):
        """Serialize player to dictionary."""
        return {
            "id": self.id,
            "player_name": self.player_name,
            "color": self.color,
            "is_ai": self.is_ai,
            "ai_difficulty": self.ai_difficulty,
            "is_active": self.is_active,
            "is_ready": self.is_ready,
            "is_eliminated": self.is_eliminated,
            "planet_count": self.planet_count,
            "money": self.money,
            "metal": self.metal,
            "user_id": self.user_id,
        }
