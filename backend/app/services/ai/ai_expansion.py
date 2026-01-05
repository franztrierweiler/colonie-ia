"""
AI Expansion Service for Colonie-IA.

Handles colonization decisions and expansion strategy.
"""
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from app import db
from app.models import (
    GamePlayer, Planet, Fleet, PlanetState, FleetStatus, ShipType
)

logger = logging.getLogger(__name__)


@dataclass
class ColonizationTarget:
    """A potential colonization target with its evaluation score."""
    planet: Planet
    score: float
    distance: float
    reachable: bool
    needs_tanker: bool = False


class AIExpansionService:
    """
    Service for AI expansion decisions.

    Handles:
    - Finding colonization targets
    - Evaluating planet value
    - Planning colony ship routes
    - Executing colonization
    """

    # Scoring weights for planet evaluation
    TEMP_WEIGHT = 40  # Max points for temperature
    GRAVITY_WEIGHT = 20  # Max points for gravity
    METAL_WEIGHT = 25  # Max points for metal
    DISTANCE_WEIGHT = 15  # Max points for distance

    @staticmethod
    def find_colonization_targets(
        player: GamePlayer,
        max_targets: int = 5
    ) -> List[ColonizationTarget]:
        """
        Find the best colonization targets for a player.

        Args:
            player: The player looking for targets
            max_targets: Maximum number of targets to return

        Returns:
            List of ColonizationTarget sorted by score (best first)
        """
        from app.services.fleet import FleetService

        targets = []

        # Get player's home planet for distance calculations
        home_planet = AIExpansionService._get_home_planet(player)
        if not home_planet:
            return []

        # Get player's fleet range
        max_range = AIExpansionService._get_max_fleet_range(player)

        # Get all uncolonized planets in the game
        game = player.game
        if not game or not game.galaxy:
            return []

        for planet in game.galaxy.planets:
            # Skip already owned planets
            if planet.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
                continue

            # Calculate distance from nearest owned planet
            distance, nearest = AIExpansionService._get_nearest_distance(player, planet)

            # Skip if unreachable
            if distance > max_range * 2:  # Allow for tanker chains
                continue

            # Evaluate planet value
            score = AIExpansionService.evaluate_planet_value(planet, player, distance)

            # Determine if reachable directly or needs tanker
            reachable = distance <= max_range
            needs_tanker = not reachable and distance <= max_range * 1.5

            targets.append(ColonizationTarget(
                planet=planet,
                score=score,
                distance=distance,
                reachable=reachable,
                needs_tanker=needs_tanker,
            ))

        # Sort by score (highest first) and return top targets
        targets.sort(key=lambda t: t.score, reverse=True)
        return targets[:max_targets]

    @staticmethod
    def evaluate_planet_value(
        planet: Planet,
        player: GamePlayer,
        distance: float = 0
    ) -> float:
        """
        Evaluate a planet's value for colonization.

        Considers:
        - Temperature proximity to 22°C (ideal)
        - Gravity proximity to 1.0g (ideal)
        - Metal reserves
        - Distance from player's territory

        Args:
            planet: Planet to evaluate
            player: Player considering colonization
            distance: Distance from player's nearest planet

        Returns:
            Score from 0 to 100
        """
        score = 0.0

        # Temperature score (40 points max)
        # Closer to 22°C = better
        temp_diff = abs(planet.base_temperature - 22)
        temp_score = max(0, AIExpansionService.TEMP_WEIGHT - temp_diff)
        score += temp_score

        # Gravity score (20 points max)
        # Closer to 1.0g = better
        grav_diff = abs(planet.gravity - 1.0)
        grav_score = max(0, AIExpansionService.GRAVITY_WEIGHT - grav_diff * 20)
        score += grav_score

        # Metal score (25 points max)
        # More metal = better
        metal_score = min(AIExpansionService.METAL_WEIGHT, planet.metal_remaining / 1000)
        score += metal_score

        # Distance score (15 points max)
        # Closer = better
        if distance > 0:
            distance_score = max(0, AIExpansionService.DISTANCE_WEIGHT - distance / 10)
            score += distance_score
        else:
            score += AIExpansionService.DISTANCE_WEIGHT

        return score

    @staticmethod
    def get_available_colony_ships(player: GamePlayer) -> List[Fleet]:
        """
        Get all fleets with colony ships that can colonize.

        Returns:
            List of fleets that can colonize
        """
        colony_fleets = []

        for fleet in player.fleets.filter_by(status=FleetStatus.STATIONED.value):
            if fleet.can_colonize:
                colony_fleets.append(fleet)

        return colony_fleets

    @staticmethod
    def plan_colonization(
        player: GamePlayer,
        targets: List[ColonizationTarget]
    ) -> List[Dict]:
        """
        Plan colonization missions.

        Matches available colony ships to best targets.

        Args:
            player: Player planning colonization
            targets: List of potential targets

        Returns:
            List of colonization orders
        """
        from app.services.fleet import FleetService

        orders = []
        colony_fleets = AIExpansionService.get_available_colony_ships(player)

        if not colony_fleets or not targets:
            return orders

        # Match fleets to targets
        for fleet in colony_fleets[:]:
            if not targets:
                break

            # Find best reachable target for this fleet
            for target in targets[:]:
                if not target.reachable:
                    continue

                # Check if fleet can actually reach
                can_reach, _ = FleetService.can_reach(fleet, target.planet)
                if can_reach:
                    orders.append({
                        "fleet_id": fleet.id,
                        "fleet_name": fleet.name,
                        "destination_id": target.planet.id,
                        "destination_name": target.planet.name,
                        "reason": "colonization",
                        "target_score": target.score,
                    })
                    targets.remove(target)
                    break

        return orders

    @staticmethod
    def execute_colonization(fleet: Fleet, planet: Planet) -> Tuple[bool, str]:
        """
        Execute colonization when a colony ship arrives at an uncolonized planet.

        Args:
            fleet: Fleet containing colony ship
            planet: Planet to colonize

        Returns:
            Tuple of (success, message)
        """
        # Verify fleet can colonize
        if not fleet.can_colonize:
            return False, "Fleet has no colony ship"

        # Verify planet is not already colonized
        if planet.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
            return False, "Planet is already colonized"

        # Find and consume the colony ship
        colony_ship = None
        for ship in fleet.ships.filter_by(is_destroyed=False):
            if ship.design.ship_type == ShipType.COLONY.value:
                colony_ship = ship
                break

        if not colony_ship:
            return False, "No colony ship found in fleet"

        # Colonize the planet
        player = fleet.player

        planet.owner_id = player.id
        planet.state = PlanetState.COLONIZED.value
        planet.population = 10000  # Starting population from colony ship
        planet.max_population = planet.calculate_max_population()

        # Default budgets
        planet.terraform_budget = 34
        planet.mining_budget = 33
        planet.ships_budget = 33

        # Destroy colony ship (settlers disembark)
        from datetime import datetime
        colony_ship.is_destroyed = True
        colony_ship.destroyed_at = datetime.utcnow()

        # Update player stats
        player.planet_count += 1

        logger.info(
            f"[AI] {player.player_name} colonized {planet.name} "
            f"(pop: {planet.population}, temp: {planet.current_temperature}°C)"
        )

        return True, f"Successfully colonized {planet.name}"

    @staticmethod
    def _get_home_planet(player: GamePlayer) -> Optional[Planet]:
        """Get the player's home planet (first colonized planet)."""
        for planet in player.planets:
            if planet.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
                return planet
        return None

    @staticmethod
    def _get_nearest_distance(player: GamePlayer, target: Planet) -> Tuple[float, Optional[Planet]]:
        """
        Get distance from nearest owned planet to target.

        Returns:
            Tuple of (distance, nearest_planet)
        """
        import math

        min_distance = float('inf')
        nearest = None

        for planet in player.planets:
            if planet.state not in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
                continue

            dx = target.x - planet.x
            dy = target.y - planet.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < min_distance:
                min_distance = distance
                nearest = planet

        return min_distance if nearest else float('inf'), nearest

    @staticmethod
    def _get_max_fleet_range(player: GamePlayer) -> float:
        """Get the maximum range of player's fleets."""
        max_range = 10.0  # Base range

        # Check technology
        if player.technology:
            max_range += player.technology.range_level * 2

        # Check actual fleets
        for fleet in player.fleets:
            if fleet.fleet_range > max_range:
                max_range = fleet.fleet_range

        return max_range
