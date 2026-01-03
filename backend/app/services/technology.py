"""
Technology service.
Handles research spending, progression, and radical breakthroughs.
"""
import math
import random
from typing import Dict, List, Optional, Tuple, Any

from app import db
from app.models import GamePlayer, Game
from app.models.technology import (
    PlayerTechnology, RadicalBreakthrough,
    TechDomain, RadicalBreakthroughType,
)
from app.services.economy import diminishing_returns


# =============================================================================
# Research Constants
# =============================================================================

# Research costs per level (logarithmic scaling)
BASE_RESEARCH_COST = 100  # Points needed for level 1->2
RESEARCH_COST_SCALING = 1.5  # Each level costs 1.5x more

# Research output from income
RESEARCH_OUTPUT_FACTOR = 0.1  # 10% of income goes to research

# Radical breakthrough threshold
RADICAL_BREAKTHROUGH_THRESHOLD = 500  # Points needed to trigger breakthrough

# Temporary bonus from radical breakthroughs
TEMP_BONUS_VALUE = 2  # +2 levels
TEMP_BONUS_DURATION = 5  # Turns

# All possible radical breakthroughs
ALL_BREAKTHROUGHS = list(RadicalBreakthroughType)

# Breakthrough descriptions (for frontend)
BREAKTHROUGH_DESCRIPTIONS = {
    RadicalBreakthroughType.TECH_BONUS_RANGE.value: "Bonus temporaire de Portee (+2 niveaux)",
    RadicalBreakthroughType.TECH_BONUS_SPEED.value: "Bonus temporaire de Vitesse (+2 niveaux)",
    RadicalBreakthroughType.TECH_BONUS_WEAPONS.value: "Bonus temporaire d'Armes (+2 niveaux)",
    RadicalBreakthroughType.TECH_BONUS_SHIELDS.value: "Bonus temporaire de Boucliers (+2 niveaux)",
    RadicalBreakthroughType.TERRAFORM_BOOST.value: "Terraformation acceleree (x2 pendant 3 tours)",
    RadicalBreakthroughType.SPY_INFO.value: "Information sur les planetes ennemies",
    RadicalBreakthroughType.STEAL_TECH.value: "Voler une technologie a un adversaire",
    RadicalBreakthroughType.UNLOCK_DECOY.value: "Debloquer les vaisseaux Leurre",
    RadicalBreakthroughType.UNLOCK_BIOLOGICAL.value: "Debloquer les vaisseaux Biologiques",
}


# =============================================================================
# Technology Service
# =============================================================================

class TechnologyService:
    """Service for managing technology research."""

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    @staticmethod
    def initialize_player_technology(player: GamePlayer) -> PlayerTechnology:
        """
        Create initial technology state for a new player.
        Called when player joins a game or game starts.

        Args:
            player: GamePlayer instance

        Returns:
            New PlayerTechnology instance
        """
        tech = PlayerTechnology(player_id=player.id)
        db.session.add(tech)
        db.session.flush()
        return tech

    @staticmethod
    def get_or_create_technology(player: GamePlayer) -> PlayerTechnology:
        """
        Get player's technology record, creating if it doesn't exist.

        Args:
            player: GamePlayer instance

        Returns:
            PlayerTechnology instance
        """
        if player.technology:
            return player.technology
        return TechnologyService.initialize_player_technology(player)

    # -------------------------------------------------------------------------
    # Research Budget Management
    # -------------------------------------------------------------------------

    @staticmethod
    def update_research_budget(
        player: GamePlayer,
        range_budget: int,
        speed_budget: int,
        weapons_budget: int,
        shields_budget: int,
        mini_budget: int,
        radical_budget: int,
    ) -> Tuple[bool, str]:
        """
        Update research budget allocation.
        All values must be 0-100 and sum to 100.

        Args:
            player: GamePlayer instance
            range_budget: Allocation for Range research (0-100)
            speed_budget: Allocation for Speed research (0-100)
            weapons_budget: Allocation for Weapons research (0-100)
            shields_budget: Allocation for Shields research (0-100)
            mini_budget: Allocation for Miniaturization research (0-100)
            radical_budget: Allocation for Radical research (0-100)

        Returns:
            Tuple of (success, message)
        """
        total = range_budget + speed_budget + weapons_budget + shields_budget + mini_budget + radical_budget
        if total != 100:
            return False, f"Budget must sum to 100 (got {total})"

        for name, val in [
            ("range", range_budget),
            ("speed", speed_budget),
            ("weapons", weapons_budget),
            ("shields", shields_budget),
            ("mini", mini_budget),
            ("radical", radical_budget),
        ]:
            if val < 0 or val > 100:
                return False, f"Budget value for {name} must be 0-100 (got {val})"

        tech = TechnologyService.get_or_create_technology(player)

        tech.range_budget = range_budget
        tech.speed_budget = speed_budget
        tech.weapons_budget = weapons_budget
        tech.shields_budget = shields_budget
        tech.mini_budget = mini_budget
        tech.radical_budget = radical_budget

        return True, "Research budget updated"

    # -------------------------------------------------------------------------
    # Research Calculations
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_research_cost(current_level: int) -> float:
        """
        Calculate research points needed to advance from current_level to next.
        Uses logarithmic scaling: cost = BASE * 1.5^level

        Args:
            current_level: Current technology level

        Returns:
            Points needed for next level
        """
        return BASE_RESEARCH_COST * (RESEARCH_COST_SCALING ** current_level)

    @staticmethod
    def calculate_research_output(
        player: GamePlayer,
        domain: TechDomain,
    ) -> float:
        """
        Calculate research points generated this turn for a domain.
        Uses diminishing returns based on budget allocation.

        Args:
            player: GamePlayer instance
            domain: Technology domain

        Returns:
            Research points generated
        """
        from app.services.economy import EconomyService

        tech = player.technology
        if not tech:
            return 0.0

        # Get player's total income
        income = EconomyService.calculate_player_income(player)
        if income <= 0:
            # Minimum research even with no income
            income = 100

        # Base research points from income
        base_research = income * RESEARCH_OUTPUT_FACTOR

        # Get budget allocation for this domain
        budget_map = {
            TechDomain.RANGE: tech.range_budget,
            TechDomain.SPEED: tech.speed_budget,
            TechDomain.WEAPONS: tech.weapons_budget,
            TechDomain.SHIELDS: tech.shields_budget,
            TechDomain.MINI: tech.mini_budget,
            TechDomain.RADICAL: tech.radical_budget,
        }
        budget_pct = budget_map.get(domain, 0) / 100.0

        # Apply diminishing returns
        effective_output = diminishing_returns(budget_pct, base_research)

        return effective_output

    # -------------------------------------------------------------------------
    # Research Processing (Turn End)
    # -------------------------------------------------------------------------

    @staticmethod
    def process_player_research(player: GamePlayer, current_turn: int) -> Dict[str, Any]:
        """
        Process research for a player at end of turn.

        1. Calculate research output for each domain
        2. Apply progress towards next level
        3. Handle level-ups
        4. Check for radical breakthroughs
        5. Expire temporary bonuses

        Args:
            player: GamePlayer instance
            current_turn: Current game turn number

        Returns:
            Dict with research output, level-ups, and breakthroughs
        """
        tech = TechnologyService.get_or_create_technology(player)

        result = {
            "player_id": player.id,
            "research_output": {},
            "level_ups": [],
            "radical_breakthrough": None,
        }

        # Process each non-radical domain
        for domain in [TechDomain.RANGE, TechDomain.SPEED, TechDomain.WEAPONS,
                       TechDomain.SHIELDS, TechDomain.MINI]:
            output = TechnologyService.calculate_research_output(player, domain)
            result["research_output"][domain.value] = round(output, 2)

            # Add to progress
            progress_attr = f"{domain.value}_progress"
            level_attr = f"{domain.value}_level"

            current_progress = getattr(tech, progress_attr)
            current_level = getattr(tech, level_attr)

            new_progress = current_progress + output
            cost_to_level = TechnologyService.calculate_research_cost(current_level)

            # Check for level up (can level up multiple times if enough points)
            while new_progress >= cost_to_level:
                new_progress -= cost_to_level
                current_level += 1
                result["level_ups"].append({
                    "domain": domain.value,
                    "new_level": current_level,
                })
                cost_to_level = TechnologyService.calculate_research_cost(current_level)

            setattr(tech, progress_attr, new_progress)
            setattr(tech, level_attr, current_level)

        # Process Radical research separately
        radical_output = TechnologyService.calculate_research_output(player, TechDomain.RADICAL)
        result["research_output"]["radical"] = round(radical_output, 2)

        tech.radical_progress += radical_output

        # Check for radical breakthrough
        if tech.radical_progress >= RADICAL_BREAKTHROUGH_THRESHOLD:
            # Check if player already has a pending breakthrough
            pending = RadicalBreakthrough.query.filter_by(
                player_id=player.id,
                is_resolved=False
            ).first()

            if not pending:
                breakthrough = TechnologyService._create_radical_breakthrough(player, current_turn)
                tech.radical_progress -= RADICAL_BREAKTHROUGH_THRESHOLD
                tech.radical_level += 1
                result["radical_breakthrough"] = breakthrough.to_dict()

        # Expire temporary bonuses
        if tech.temp_bonus_expires_turn and tech.temp_bonus_expires_turn <= current_turn:
            tech.temp_range_bonus = 0
            tech.temp_speed_bonus = 0
            tech.temp_weapons_bonus = 0
            tech.temp_shields_bonus = 0
            tech.temp_bonus_expires_turn = None

        return result

    @staticmethod
    def _create_radical_breakthrough(
        player: GamePlayer,
        current_turn: int,
    ) -> RadicalBreakthrough:
        """
        Create a new radical breakthrough with 4 random options.

        Args:
            player: GamePlayer instance
            current_turn: Current game turn

        Returns:
            New RadicalBreakthrough instance
        """
        # Filter out already unlocked breakthroughs
        tech = player.technology
        available = list(ALL_BREAKTHROUGHS)

        if tech and tech.decoy_unlocked:
            available = [b for b in available if b != RadicalBreakthroughType.UNLOCK_DECOY]
        if tech and tech.biological_unlocked:
            available = [b for b in available if b != RadicalBreakthroughType.UNLOCK_BIOLOGICAL]

        # Ensure we have at least 4 options (duplicate if needed)
        while len(available) < 4:
            available.append(random.choice(ALL_BREAKTHROUGHS))

        # Select 4 random unique breakthroughs
        options = random.sample(available, 4)
        option_values = [o.value for o in options]

        breakthrough = RadicalBreakthrough(
            player_id=player.id,
            options=option_values,
            created_turn=current_turn,
        )
        db.session.add(breakthrough)
        db.session.flush()

        return breakthrough

    # -------------------------------------------------------------------------
    # Radical Breakthrough Resolution
    # -------------------------------------------------------------------------

    @staticmethod
    def eliminate_breakthrough_option(
        player: GamePlayer,
        breakthrough_id: int,
        eliminated_option: str,
        current_turn: int,
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Player eliminates one of the 4 breakthrough options.
        One of the remaining 3 is randomly unlocked.

        Args:
            player: GamePlayer instance
            breakthrough_id: RadicalBreakthrough ID
            eliminated_option: Option to eliminate
            current_turn: Current game turn

        Returns:
            Tuple of (success, message, result_dict)
        """
        breakthrough = RadicalBreakthrough.query.get(breakthrough_id)
        if not breakthrough:
            return False, "Breakthrough not found", None

        if breakthrough.player_id != player.id:
            return False, "This breakthrough does not belong to you", None

        if breakthrough.is_resolved:
            return False, "Breakthrough already resolved", None

        if eliminated_option not in breakthrough.options:
            return False, f"Invalid option to eliminate: {eliminated_option}", None

        # Remove eliminated option
        remaining = [o for o in breakthrough.options if o != eliminated_option]

        # Randomly select one of the remaining 3
        unlocked = random.choice(remaining)

        # Update breakthrough
        breakthrough.eliminated_option = eliminated_option
        breakthrough.unlocked_option = unlocked
        breakthrough.is_resolved = True
        breakthrough.resolved_turn = current_turn

        # Apply the breakthrough effect
        effect_result = TechnologyService._apply_breakthrough_effect(
            player, unlocked, current_turn
        )

        return True, f"Breakthrough resolved: {unlocked}", {
            "breakthrough": breakthrough.to_dict(),
            "effect": effect_result,
        }

    @staticmethod
    def _apply_breakthrough_effect(
        player: GamePlayer,
        breakthrough_type: str,
        current_turn: int,
    ) -> Dict[str, Any]:
        """
        Apply the effect of an unlocked radical breakthrough.

        Args:
            player: GamePlayer instance
            breakthrough_type: RadicalBreakthroughType value
            current_turn: Current game turn

        Returns:
            Dict describing the effect applied
        """
        tech = TechnologyService.get_or_create_technology(player)
        effect: Dict[str, Any] = {
            "type": breakthrough_type,
            "description": BREAKTHROUGH_DESCRIPTIONS.get(breakthrough_type, "Unknown effect"),
        }

        bt = RadicalBreakthroughType(breakthrough_type)

        if bt == RadicalBreakthroughType.UNLOCK_DECOY:
            tech.decoy_unlocked = True
            effect["unlock"] = "decoy"

        elif bt == RadicalBreakthroughType.UNLOCK_BIOLOGICAL:
            tech.biological_unlocked = True
            effect["unlock"] = "biological"

        elif bt in [RadicalBreakthroughType.TECH_BONUS_RANGE,
                    RadicalBreakthroughType.TECH_BONUS_SPEED,
                    RadicalBreakthroughType.TECH_BONUS_WEAPONS,
                    RadicalBreakthroughType.TECH_BONUS_SHIELDS]:
            # Apply temporary bonus
            expires = current_turn + TEMP_BONUS_DURATION

            if bt == RadicalBreakthroughType.TECH_BONUS_RANGE:
                tech.temp_range_bonus = TEMP_BONUS_VALUE
            elif bt == RadicalBreakthroughType.TECH_BONUS_SPEED:
                tech.temp_speed_bonus = TEMP_BONUS_VALUE
            elif bt == RadicalBreakthroughType.TECH_BONUS_WEAPONS:
                tech.temp_weapons_bonus = TEMP_BONUS_VALUE
            elif bt == RadicalBreakthroughType.TECH_BONUS_SHIELDS:
                tech.temp_shields_bonus = TEMP_BONUS_VALUE

            tech.temp_bonus_expires_turn = expires
            effect["bonus_value"] = TEMP_BONUS_VALUE
            effect["expires_turn"] = expires

        elif bt == RadicalBreakthroughType.TERRAFORM_BOOST:
            # TODO: Implement terraform boost tracking
            effect["duration"] = 3

        elif bt == RadicalBreakthroughType.SPY_INFO:
            # TODO: Implement spy info reveal
            effect["revealed"] = True

        elif bt == RadicalBreakthroughType.STEAL_TECH:
            # TODO: Implement tech stealing
            effect["stolen"] = False

        return effect

    # -------------------------------------------------------------------------
    # Technology Comparison (US 5.8)
    # -------------------------------------------------------------------------

    @staticmethod
    def get_technology_comparison(game: Game, player: GamePlayer) -> Dict[str, Any]:
        """
        Get technology comparison between player and opponents.
        Shows relative position without revealing exact enemy levels.

        Args:
            game: Game instance
            player: GamePlayer instance

        Returns:
            Dict with player's levels and relative position to opponents
        """
        player_tech = TechnologyService.get_or_create_technology(player)

        comparison: Dict[str, Any] = {
            "your_levels": player_tech.to_dict()["levels"],
            "opponents": [],
        }

        for opponent in game.players:
            if opponent.id == player.id:
                continue
            if opponent.is_eliminated:
                continue

            opp_tech = opponent.technology
            if not opp_tech:
                continue

            # Calculate relative position (ahead/behind/equal)
            relative = {}
            for domain in ["range", "speed", "weapons", "shields", "mini"]:
                player_level = getattr(player_tech, f"{domain}_level")
                opp_level = getattr(opp_tech, f"{domain}_level")

                if player_level > opp_level:
                    relative[domain] = "ahead"
                elif player_level < opp_level:
                    relative[domain] = "behind"
                else:
                    relative[domain] = "equal"

            comparison["opponents"].append({
                "player_id": opponent.id,
                "player_name": opponent.player_name,
                "color": opponent.color,
                "relative": relative,
            })

        return comparison

    # -------------------------------------------------------------------------
    # Integration with Ship Design
    # -------------------------------------------------------------------------

    @staticmethod
    def can_build_ship_type(player: GamePlayer, ship_type: str) -> Tuple[bool, str]:
        """
        Check if player can build a specific ship type.
        Decoy and Biological require radical unlocks.

        Args:
            player: GamePlayer instance
            ship_type: ShipType value

        Returns:
            Tuple of (can_build, reason)
        """
        from app.models.fleet import ShipType

        tech = player.technology
        if not tech:
            # If no tech record, only basic ships available
            if ship_type in [ShipType.DECOY.value, ShipType.BIOLOGICAL.value]:
                return False, f"{ship_type} ships require radical research breakthrough"
            return True, "OK"

        if ship_type == ShipType.DECOY.value:
            if not tech.decoy_unlocked:
                return False, "Decoy ships require radical research breakthrough"

        elif ship_type == ShipType.BIOLOGICAL.value:
            if not tech.biological_unlocked:
                return False, "Biological ships require radical research breakthrough"

        return True, "OK"

    @staticmethod
    def get_max_tech_levels(player: GamePlayer) -> Dict[str, int]:
        """
        Get the maximum tech levels a player can use in ship designs.
        Includes effective levels (with temporary bonuses).

        Args:
            player: GamePlayer instance

        Returns:
            Dict with max level for each domain
        """
        tech = player.technology
        if not tech:
            return {
                "range": 1,
                "speed": 1,
                "weapons": 1,
                "shields": 1,
                "mini": 1,
            }

        return {
            "range": tech.effective_range,
            "speed": tech.effective_speed,
            "weapons": tech.effective_weapons,
            "shields": tech.effective_shields,
            "mini": tech.mini_level,
        }

    @staticmethod
    def validate_design_tech_levels(
        player: GamePlayer,
        range_level: int,
        speed_level: int,
        weapons_level: int,
        shields_level: int,
        mini_level: int,
    ) -> Tuple[bool, str, Dict[str, int]]:
        """
        Validate that requested tech levels don't exceed player's current tech.
        Returns clamped values if they exceed.

        Args:
            player: GamePlayer instance
            range_level: Requested range level
            speed_level: Requested speed level
            weapons_level: Requested weapons level
            shields_level: Requested shields level
            mini_level: Requested miniaturization level

        Returns:
            Tuple of (is_valid, message, clamped_levels)
        """
        max_levels = TechnologyService.get_max_tech_levels(player)

        clamped = {
            "range": min(range_level, max_levels["range"]),
            "speed": min(speed_level, max_levels["speed"]),
            "weapons": min(weapons_level, max_levels["weapons"]),
            "shields": min(shields_level, max_levels["shields"]),
            "mini": min(mini_level, max_levels["mini"]),
        }

        warnings = []
        if clamped["range"] < range_level:
            warnings.append(f"Range clamped to {clamped['range']}")
        if clamped["speed"] < speed_level:
            warnings.append(f"Speed clamped to {clamped['speed']}")
        if clamped["weapons"] < weapons_level:
            warnings.append(f"Weapons clamped to {clamped['weapons']}")
        if clamped["shields"] < shields_level:
            warnings.append(f"Shields clamped to {clamped['shields']}")
        if clamped["mini"] < mini_level:
            warnings.append(f"Mini clamped to {clamped['mini']}")

        if warnings:
            return False, "; ".join(warnings), clamped

        return True, "OK", clamped

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------

    @staticmethod
    def get_player_tech_summary(player: GamePlayer) -> Dict[str, Any]:
        """
        Get complete technology summary for a player.

        Args:
            player: GamePlayer instance

        Returns:
            Dict with all technology data
        """
        tech = TechnologyService.get_or_create_technology(player)

        # Calculate progress percentages
        progress_pct = {}
        for domain in ["range", "speed", "weapons", "shields", "mini"]:
            level = getattr(tech, f"{domain}_level")
            progress = getattr(tech, f"{domain}_progress")
            cost = TechnologyService.calculate_research_cost(level)
            progress_pct[domain] = round(progress / cost * 100, 1) if cost > 0 else 0

        # Radical progress
        radical_progress_pct = round(
            tech.radical_progress / RADICAL_BREAKTHROUGH_THRESHOLD * 100, 1
        )

        # Pending breakthroughs
        pending_breakthroughs = RadicalBreakthrough.query.filter_by(
            player_id=player.id,
            is_resolved=False
        ).all()

        return {
            **tech.to_dict(),
            "progress_percentages": {
                **progress_pct,
                "radical": radical_progress_pct,
            },
            "pending_breakthroughs": [b.to_dict() for b in pending_breakthroughs],
            "breakthrough_threshold": RADICAL_BREAKTHROUGH_THRESHOLD,
        }
