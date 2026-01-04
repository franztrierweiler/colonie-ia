"""
Combat models for battle resolution and reports.
"""
from datetime import datetime
from typing import List, Dict, Any

from app import db


class CombatReport(db.Model):
    """
    Report of a battle that occurred on a planet.
    Stores all information about the combat for history and display.
    """
    __tablename__ = "combat_reports"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=False)
    turn = db.Column(db.Integer, nullable=False)

    # Participants (JSON: list of player_ids for attackers)
    attacker_ids = db.Column(db.JSON, nullable=False, default=list)
    defender_id = db.Column(db.Integer, db.ForeignKey("game_players.id"), nullable=True)

    # Result
    victor_id = db.Column(db.Integer, db.ForeignKey("game_players.id"), nullable=True)
    is_draw = db.Column(db.Boolean, default=False, nullable=False)

    # Forces involved (JSON: {player_id: {ship_type: count}})
    attacker_forces = db.Column(db.JSON, nullable=False, default=dict)
    defender_forces = db.Column(db.JSON, nullable=False, default=dict)

    # Losses (JSON: {player_id: {ship_type: count}})
    attacker_losses = db.Column(db.JSON, nullable=False, default=dict)
    defender_losses = db.Column(db.JSON, nullable=False, default=dict)

    # Population casualties from bombardment/debris
    population_casualties = db.Column(db.Integer, default=0, nullable=False)

    # Debris and recovery
    total_debris_metal = db.Column(db.Integer, default=0, nullable=False)
    metal_recovered = db.Column(db.Integer, default=0, nullable=False)

    # Colonization result
    planet_captured = db.Column(db.Boolean, default=False, nullable=False)
    planet_colonized = db.Column(db.Boolean, default=False, nullable=False)
    new_owner_id = db.Column(db.Integer, db.ForeignKey("game_players.id"), nullable=True)

    # Combat phases log (JSON: list of phase descriptions)
    combat_log = db.Column(db.JSON, nullable=False, default=list)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    game = db.relationship("Game", backref=db.backref("combat_reports", lazy="dynamic"))
    planet = db.relationship("Planet", backref=db.backref("combat_reports", lazy="dynamic"))
    defender = db.relationship("GamePlayer", foreign_keys=[defender_id],
                               backref=db.backref("defensive_battles", lazy="dynamic"))
    victor = db.relationship("GamePlayer", foreign_keys=[victor_id])
    new_owner = db.relationship("GamePlayer", foreign_keys=[new_owner_id])

    def __repr__(self):
        return f"<CombatReport {self.id} at planet {self.planet_id} turn {self.turn}>"

    def add_log_entry(self, phase: str, message: str, details: Dict = None):
        """Add an entry to the combat log."""
        if self.combat_log is None:
            self.combat_log = []

        entry = {
            "phase": phase,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if details:
            entry["details"] = details

        # Need to reassign for SQLAlchemy to detect change
        log = list(self.combat_log)
        log.append(entry)
        self.combat_log = log

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "game_id": self.game_id,
            "planet_id": self.planet_id,
            "planet_name": self.planet.name if self.planet else None,
            "turn": self.turn,
            "attacker_ids": self.attacker_ids,
            "defender_id": self.defender_id,
            "victor_id": self.victor_id,
            "is_draw": self.is_draw,
            "attacker_forces": self.attacker_forces,
            "defender_forces": self.defender_forces,
            "attacker_losses": self.attacker_losses,
            "defender_losses": self.defender_losses,
            "population_casualties": self.population_casualties,
            "total_debris_metal": self.total_debris_metal,
            "metal_recovered": self.metal_recovered,
            "planet_captured": self.planet_captured,
            "planet_colonized": self.planet_colonized,
            "new_owner_id": self.new_owner_id,
            "combat_log": self.combat_log,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary (less detail)."""
        total_attacker_losses = sum(
            sum(losses.values()) for losses in (self.attacker_losses or {}).values()
        )
        total_defender_losses = sum((self.defender_losses or {}).values())

        return {
            "id": self.id,
            "planet_id": self.planet_id,
            "planet_name": self.planet.name if self.planet else None,
            "turn": self.turn,
            "victor_id": self.victor_id,
            "attacker_losses": total_attacker_losses,
            "defender_losses": total_defender_losses,
            "planet_captured": self.planet_captured,
            "planet_colonized": self.planet_colonized,
        }
