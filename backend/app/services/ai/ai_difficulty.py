"""
AI Difficulty System.

Defines difficulty levels and their modifiers for AI behavior.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any


class AIDifficultyLevel(str, Enum):
    """AI difficulty levels with thematic names."""
    CONSCRIT = "conscrit"      # Level 1 - Easy
    GRENADIER = "grenadier"    # Level 2 - Normal-
    CAPITAINE = "capitaine"    # Level 3 - Normal
    COLONEL = "colonel"        # Level 4 - Hard
    MARECHAL = "marechal"      # Level 5 - Expert


@dataclass
class DifficultyModifiers:
    """
    Modifiers that affect AI behavior based on difficulty level.

    Attributes:
        decision_error_rate: Probability of making suboptimal decisions (0-1)
        reaction_delay: Turns of delay before responding to threats
        attack_threshold: Required force superiority ratio to attack (1.0 = equal)
        economy_efficiency: Multiplier for economic decisions (1.0 = normal)
        can_use_tankers: Whether AI can use tanker ships for extended range
        can_coordinate_attacks: Whether AI can launch multi-planet attacks
        can_use_biologicals: Whether AI can use biological ships
        predictive_defense: Whether AI anticipates enemy movements
        exploration_priority: How aggressively AI explores (0-1)
        tech_focus: How well AI balances research (0-1, higher = smarter)
    """
    decision_error_rate: float
    reaction_delay: int
    attack_threshold: float
    economy_efficiency: float
    can_use_tankers: bool
    can_coordinate_attacks: bool
    can_use_biologicals: bool
    predictive_defense: bool
    exploration_priority: float
    tech_focus: float

    @classmethod
    def for_difficulty(cls, difficulty: AIDifficultyLevel) -> "DifficultyModifiers":
        """Get modifiers for a specific difficulty level."""
        return DIFFICULTY_PRESETS.get(difficulty, DIFFICULTY_PRESETS[AIDifficultyLevel.CAPITAINE])


# Difficulty presets
DIFFICULTY_PRESETS: Dict[AIDifficultyLevel, DifficultyModifiers] = {
    AIDifficultyLevel.CONSCRIT: DifficultyModifiers(
        decision_error_rate=0.30,      # 30% bad decisions
        reaction_delay=2,               # 2 turns delay
        attack_threshold=2.0,           # Only attacks with 2x superiority
        economy_efficiency=0.70,        # 70% efficiency
        can_use_tankers=False,
        can_coordinate_attacks=False,
        can_use_biologicals=False,
        predictive_defense=False,
        exploration_priority=0.3,       # Slow explorer
        tech_focus=0.4,                 # Poor tech balance
    ),
    AIDifficultyLevel.GRENADIER: DifficultyModifiers(
        decision_error_rate=0.15,      # 15% bad decisions
        reaction_delay=1,               # 1 turn delay
        attack_threshold=1.5,           # Attacks with 1.5x superiority
        economy_efficiency=0.85,        # 85% efficiency
        can_use_tankers=False,
        can_coordinate_attacks=False,
        can_use_biologicals=False,
        predictive_defense=False,
        exploration_priority=0.5,
        tech_focus=0.6,
    ),
    AIDifficultyLevel.CAPITAINE: DifficultyModifiers(
        decision_error_rate=0.05,      # 5% bad decisions
        reaction_delay=0,               # No delay
        attack_threshold=1.2,           # Attacks with 1.2x superiority
        economy_efficiency=1.0,         # Normal efficiency
        can_use_tankers=True,
        can_coordinate_attacks=False,
        can_use_biologicals=False,
        predictive_defense=False,
        exploration_priority=0.7,
        tech_focus=0.8,
    ),
    AIDifficultyLevel.COLONEL: DifficultyModifiers(
        decision_error_rate=0.02,      # 2% bad decisions
        reaction_delay=0,
        attack_threshold=1.0,           # Attacks at parity
        economy_efficiency=1.0,
        can_use_tankers=True,
        can_coordinate_attacks=True,    # Can coordinate attacks
        can_use_biologicals=False,
        predictive_defense=True,        # Anticipates attacks
        exploration_priority=0.85,
        tech_focus=0.9,
    ),
    AIDifficultyLevel.MARECHAL: DifficultyModifiers(
        decision_error_rate=0.0,       # No errors
        reaction_delay=0,
        attack_threshold=0.8,           # Attacks even slightly inferior
        economy_efficiency=1.1,         # 110% efficiency (slight bonus)
        can_use_tankers=True,
        can_coordinate_attacks=True,
        can_use_biologicals=True,       # Uses all ship types
        predictive_defense=True,
        exploration_priority=1.0,       # Maximum exploration
        tech_focus=1.0,                 # Perfect tech balance
    ),
}


def map_legacy_difficulty(legacy_difficulty: str) -> AIDifficultyLevel:
    """
    Map legacy difficulty strings to new difficulty levels.

    Args:
        legacy_difficulty: Old difficulty value (easy, medium, hard, expert)

    Returns:
        Corresponding AIDifficultyLevel
    """
    mapping = {
        "easy": AIDifficultyLevel.CONSCRIT,
        "medium": AIDifficultyLevel.CAPITAINE,
        "hard": AIDifficultyLevel.COLONEL,
        "expert": AIDifficultyLevel.MARECHAL,
    }
    return mapping.get(legacy_difficulty, AIDifficultyLevel.CAPITAINE)
