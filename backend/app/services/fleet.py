"""
Fleet service.
Handles ship design, construction, fleet management, and movement.
"""
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app import db
from app.models import (
    GamePlayer, Planet, Star, PlanetState,
    Ship, ShipDesign, Fleet,
    ShipType, FleetStatus, SHIP_BASE_STATS,
)


# =============================================================================
# Constants
# =============================================================================

DISBAND_METAL_RECOVERY = 0.75  # 75% metal recovered when disbanding
TANKER_RANGE_BONUS = 1.5  # Tankers extend range by 50%
BASE_FUEL_CAPACITY = 10.0  # Base fuel units
PROTOTYPE_COST_MULTIPLIER = 2  # Prototype costs 2x production


# =============================================================================
# Fleet Service
# =============================================================================

class FleetService:
    """Service for managing ships, designs, and fleets."""

    # -------------------------------------------------------------------------
    # Ship Design Management
    # -------------------------------------------------------------------------

    @staticmethod
    def create_design(
        player: GamePlayer,
        name: str,
        ship_type: ShipType,
        range_level: int = 1,
        speed_level: int = 1,
        weapons_level: int = 1,
        shields_level: int = 1,
        mini_level: int = 1,
    ) -> ShipDesign:
        """
        Create a new ship design.

        Args:
            player: GamePlayer who owns the design
            name: Name for the design
            ship_type: Type of ship
            range_level: Range technology level (1-10+)
            speed_level: Speed technology level
            weapons_level: Weapons technology level
            shields_level: Shields technology level
            mini_level: Miniaturization level

        Returns:
            New ShipDesign instance
        """
        # Validate ship type
        if isinstance(ship_type, str):
            ship_type = ShipType(ship_type)

        # Check if radical tech is required
        base_stats = SHIP_BASE_STATS.get(ship_type)
        if base_stats and base_stats.get("requires_radical"):
            # TODO: Check player has unlocked this via radical research
            pass

        design = ShipDesign(
            player_id=player.id,
            name=name,
            ship_type=ship_type.value,
            range_level=max(1, range_level),
            speed_level=max(1, speed_level),
            weapons_level=max(1, weapons_level),
            shields_level=max(1, shields_level),
            mini_level=max(1, mini_level),
        )

        # Calculate and cache costs
        design.calculate_costs()

        db.session.add(design)
        db.session.flush()  # Get ID
        return design

    @staticmethod
    def get_player_designs(player: GamePlayer) -> List[ShipDesign]:
        """Get all designs owned by a player."""
        return player.ship_designs.all()

    @staticmethod
    def calculate_design_costs(
        ship_type: ShipType,
        range_level: int,
        speed_level: int,
        weapons_level: int,
        shields_level: int,
        mini_level: int,
    ) -> Dict[str, int]:
        """
        Calculate costs for a potential design (without creating it).

        Returns:
            Dictionary with prototype and production costs
        """
        if isinstance(ship_type, str):
            ship_type = ShipType(ship_type)

        base = SHIP_BASE_STATS.get(ship_type, SHIP_BASE_STATS[ShipType.FIGHTER])

        # Technology factor
        tech_factor = (range_level + speed_level + weapons_level + shields_level) / 4

        # Miniaturization effects
        mini_metal_reduction = 1 - (mini_level * 0.08)
        mini_money_increase = 1 + (mini_level * 0.10)

        # Calculate costs
        metal_cost = int(base["base_metal"] * tech_factor * mini_metal_reduction)
        money_cost = int(base["base_money"] * tech_factor * mini_money_increase)

        metal_cost = max(1, metal_cost) if base["base_metal"] > 0 else 0
        money_cost = max(1, money_cost)

        return {
            "prototype_money": money_cost * PROTOTYPE_COST_MULTIPLIER,
            "prototype_metal": metal_cost * PROTOTYPE_COST_MULTIPLIER,
            "production_money": money_cost,
            "production_metal": metal_cost,
        }

    # -------------------------------------------------------------------------
    # Ship Construction
    # -------------------------------------------------------------------------

    @staticmethod
    def build_prototype(
        player: GamePlayer,
        design: ShipDesign,
        fleet: Fleet,
    ) -> Tuple[bool, str, Optional[Ship]]:
        """
        Build the prototype (first ship of a design).
        Costs 2x the normal production cost.

        Args:
            player: Player building the ship
            design: Ship design to build
            fleet: Fleet to add the ship to

        Returns:
            Tuple of (success, message, ship or None)
        """
        if design.is_prototype_built:
            return False, "Prototype already built for this design", None

        if design.player_id != player.id:
            return False, "This design belongs to another player", None

        # Check resources
        if player.money < design.prototype_cost_money:
            return False, f"Not enough money (need {design.prototype_cost_money}, have {player.money})", None

        if player.metal < design.prototype_cost_metal:
            return False, f"Not enough metal (need {design.prototype_cost_metal}, have {player.metal})", None

        # Deduct resources
        player.money -= design.prototype_cost_money
        player.metal -= design.prototype_cost_metal

        # Create ship
        ship = Ship(
            design_id=design.id,
            fleet_id=fleet.id,
        )
        db.session.add(ship)

        # Mark prototype as built
        design.is_prototype_built = True
        design.ships_built = 1

        return True, "Prototype built successfully", ship

    @staticmethod
    def build_ship(
        player: GamePlayer,
        design: ShipDesign,
        fleet: Fleet,
    ) -> Tuple[bool, str, Optional[Ship]]:
        """
        Build a ship from an existing design.

        Args:
            player: Player building the ship
            design: Ship design to build
            fleet: Fleet to add the ship to

        Returns:
            Tuple of (success, message, ship or None)
        """
        if not design.is_prototype_built:
            return FleetService.build_prototype(player, design, fleet)

        if design.player_id != player.id:
            return False, "This design belongs to another player", None

        # Check resources
        if player.money < design.production_cost_money:
            return False, f"Not enough money (need {design.production_cost_money})", None

        if player.metal < design.production_cost_metal:
            return False, f"Not enough metal (need {design.production_cost_metal})", None

        # Deduct resources
        player.money -= design.production_cost_money
        player.metal -= design.production_cost_metal

        # Create ship
        ship = Ship(
            design_id=design.id,
            fleet_id=fleet.id,
        )
        db.session.add(ship)

        design.ships_built += 1

        return True, "Ship built successfully", ship

    @staticmethod
    def build_ships(
        player: GamePlayer,
        design: ShipDesign,
        fleet: Fleet,
        count: int,
    ) -> Tuple[bool, str, List[Ship]]:
        """
        Build multiple ships of the same design.

        Args:
            player: Player building the ships
            design: Ship design to build
            fleet: Fleet to add the ships to
            count: Number of ships to build

        Returns:
            Tuple of (success, message, list of ships)
        """
        if count <= 0:
            return False, "Count must be positive", []

        ships = []
        for i in range(count):
            success, message, ship = FleetService.build_ship(player, design, fleet)
            if not success:
                if ships:
                    return True, f"Built {len(ships)} ships, then: {message}", ships
                return False, message, []
            ships.append(ship)

        return True, f"Built {len(ships)} ships", ships

    # -------------------------------------------------------------------------
    # Fleet Management
    # -------------------------------------------------------------------------

    @staticmethod
    def create_fleet(
        player: GamePlayer,
        name: str,
        star: Star = None,
        planet: Planet = None,
    ) -> Fleet:
        """
        Create a new empty fleet.

        Args:
            player: Player who owns the fleet
            name: Name for the fleet
            star: Star where fleet is stationed (optional)
            planet: Planet the fleet is orbiting (optional)

        Returns:
            New Fleet instance
        """
        fleet = Fleet(
            player_id=player.id,
            name=name,
            current_star_id=star.id if star else None,
            orbiting_planet_id=planet.id if planet else None,
            status=FleetStatus.STATIONED.value,
            fuel_remaining=BASE_FUEL_CAPACITY,
            max_fuel=BASE_FUEL_CAPACITY,
        )
        db.session.add(fleet)
        db.session.flush()  # Get ID
        return fleet

    @staticmethod
    def add_ship_to_fleet(ship: Ship, fleet: Fleet) -> bool:
        """Add a ship to a fleet."""
        if ship.is_destroyed:
            return False

        # Ships can only join fleets at the same location
        if ship.fleet and ship.fleet.current_star_id != fleet.current_star_id:
            return False

        ship.fleet_id = fleet.id
        return True

    @staticmethod
    def remove_ship_from_fleet(ship: Ship) -> bool:
        """Remove a ship from its fleet."""
        if ship.fleet_id is None:
            return False

        ship.fleet_id = None
        return True

    @staticmethod
    def split_fleet(
        fleet: Fleet,
        ship_ids: List[int],
        new_name: str,
    ) -> Tuple[bool, str, Optional[Fleet]]:
        """
        Split a fleet by moving some ships to a new fleet.

        Args:
            fleet: Original fleet
            ship_ids: IDs of ships to move to new fleet
            new_name: Name for the new fleet

        Returns:
            Tuple of (success, message, new fleet or None)
        """
        if fleet.status != FleetStatus.STATIONED.value:
            return False, "Cannot split fleet while in transit", None

        # Validate ships belong to this fleet
        ships_to_move = []
        for ship_id in ship_ids:
            ship = Ship.query.get(ship_id)
            if not ship or ship.fleet_id != fleet.id:
                return False, f"Ship {ship_id} not in this fleet", None
            if ship.is_destroyed:
                continue
            ships_to_move.append(ship)

        if not ships_to_move:
            return False, "No valid ships to move", None

        # Create new fleet at same location
        new_fleet = Fleet(
            player_id=fleet.player_id,
            name=new_name,
            current_star_id=fleet.current_star_id,
            orbiting_planet_id=fleet.orbiting_planet_id,
            status=FleetStatus.STATIONED.value,
            fuel_remaining=fleet.fuel_remaining,
            max_fuel=fleet.max_fuel,
        )
        db.session.add(new_fleet)
        db.session.flush()  # Get ID

        # Move ships
        for ship in ships_to_move:
            ship.fleet_id = new_fleet.id

        return True, f"Split {len(ships_to_move)} ships to new fleet", new_fleet

    @staticmethod
    def merge_fleets(fleet1: Fleet, fleet2: Fleet) -> Tuple[bool, str]:
        """
        Merge two fleets into one (fleet2 ships move to fleet1).

        Args:
            fleet1: Fleet to merge into (keeps name)
            fleet2: Fleet to merge from (will be deleted)

        Returns:
            Tuple of (success, message)
        """
        if fleet1.player_id != fleet2.player_id:
            return False, "Fleets belong to different players"

        if fleet1.current_star_id != fleet2.current_star_id:
            return False, "Fleets must be at the same location"

        if fleet1.status != FleetStatus.STATIONED.value or fleet2.status != FleetStatus.STATIONED.value:
            return False, "Both fleets must be stationed"

        # Move all ships from fleet2 to fleet1
        ships_moved = 0
        for ship in fleet2.ships.filter_by(is_destroyed=False).all():
            ship.fleet_id = fleet1.id
            ships_moved += 1

        # Flush to ensure ship changes are persisted before deleting fleet2
        db.session.flush()

        # Delete empty fleet
        db.session.delete(fleet2)

        return True, f"Merged {ships_moved} ships into {fleet1.name}"

    # -------------------------------------------------------------------------
    # Fleet Movement
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_distance(star1: Star, star2: Star) -> float:
        """Calculate distance between two stars."""
        dx = star2.x - star1.x
        dy = star2.y - star1.y
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def calculate_travel_time(fleet: Fleet, destination: Star) -> int:
        """
        Calculate number of turns to reach destination.

        Args:
            fleet: Fleet to move
            destination: Target star

        Returns:
            Number of turns (0 if at destination)
        """
        if fleet.current_star_id == destination.id:
            return 0

        current_star = Star.query.get(fleet.current_star_id)
        if not current_star:
            return -1

        distance = FleetService.calculate_distance(current_star, destination)
        speed = fleet.fleet_speed

        if speed <= 0:
            return -1  # Cannot move (satellites)

        return math.ceil(distance / speed)

    @staticmethod
    def can_reach(fleet: Fleet, destination: Star) -> Tuple[bool, str]:
        """
        Check if fleet can reach destination with current fuel.

        Args:
            fleet: Fleet to check
            destination: Target star

        Returns:
            Tuple of (can_reach, reason)
        """
        if fleet.status != FleetStatus.STATIONED.value:
            return False, "Fleet is already in transit"

        if fleet.current_star_id == destination.id:
            return False, "Already at destination"

        current_star = Star.query.get(fleet.current_star_id)
        if not current_star:
            return False, "Fleet has no current location"

        distance = FleetService.calculate_distance(current_star, destination)

        if distance > fleet.fleet_range:
            return False, f"Destination too far (distance: {distance:.1f}, range: {fleet.fleet_range:.1f})"

        if distance > fleet.fuel_remaining:
            return False, f"Not enough fuel (need: {distance:.1f}, have: {fleet.fuel_remaining:.1f})"

        # Check for satellites (cannot move)
        for ship in fleet.ships.filter_by(is_destroyed=False):
            if ship.design.ship_type == ShipType.SATELLITE.value:
                return False, "Fleet contains satellites which cannot move"

        return True, "OK"

    @staticmethod
    def move_fleet(
        fleet: Fleet,
        destination: Star,
        current_turn: int,
    ) -> Tuple[bool, str]:
        """
        Start moving a fleet to a destination.

        Args:
            fleet: Fleet to move
            destination: Target star
            current_turn: Current game turn

        Returns:
            Tuple of (success, message)
        """
        can_move, reason = FleetService.can_reach(fleet, destination)
        if not can_move:
            return False, reason

        current_star = Star.query.get(fleet.current_star_id)
        distance = FleetService.calculate_distance(current_star, destination)
        travel_time = FleetService.calculate_travel_time(fleet, destination)

        # Update fleet
        fleet.status = FleetStatus.IN_TRANSIT.value
        fleet.destination_star_id = destination.id
        fleet.departure_turn = current_turn
        fleet.arrival_turn = current_turn + travel_time
        fleet.fuel_remaining -= distance
        fleet.current_star_id = None
        fleet.orbiting_planet_id = None

        return True, f"Fleet departing, will arrive in {travel_time} turns"

    @staticmethod
    def process_fleet_movements(game_id: int, current_turn: int) -> Dict:
        """
        Process all fleet movements for a game (called at end of turn).

        Args:
            game_id: Game ID
            current_turn: Current turn number

        Returns:
            Dictionary with movement results
        """
        from app.models import Game

        game = Game.query.get(game_id)
        if not game:
            return {"error": "Game not found"}

        results = {
            "arrivals": [],
            "in_transit": [],
        }

        # Get all fleets in transit for this game
        for player in game.players:
            for fleet in player.fleets.filter_by(status=FleetStatus.IN_TRANSIT.value):
                if fleet.arrival_turn <= current_turn:
                    # Fleet has arrived
                    fleet.status = FleetStatus.STATIONED.value
                    fleet.current_star_id = fleet.destination_star_id
                    fleet.destination_star_id = None
                    fleet.departure_turn = None
                    fleet.arrival_turn = None

                    results["arrivals"].append({
                        "fleet_id": fleet.id,
                        "fleet_name": fleet.name,
                        "player_id": fleet.player_id,
                        "star_id": fleet.current_star_id,
                    })
                else:
                    results["in_transit"].append({
                        "fleet_id": fleet.id,
                        "fleet_name": fleet.name,
                        "turns_remaining": fleet.arrival_turn - current_turn,
                    })

        return results

    # -------------------------------------------------------------------------
    # Refueling
    # -------------------------------------------------------------------------

    @staticmethod
    def can_refuel_at(fleet: Fleet, planet: Planet) -> bool:
        """
        Check if fleet can refuel at a planet.
        Can refuel at own planets or allied planets.
        """
        if planet.owner_id is None:
            return False

        # Own planet
        if planet.owner_id == fleet.player_id:
            return True

        # Allied planet (TODO: implement alliance system)
        # For now, only own planets
        return False

    @staticmethod
    def refuel_fleet(fleet: Fleet) -> Tuple[bool, str]:
        """
        Refuel a fleet at current location.

        Returns:
            Tuple of (success, message)
        """
        if fleet.status != FleetStatus.STATIONED.value:
            return False, "Fleet must be stationed to refuel"

        # Check if at a planet where we can refuel
        if fleet.orbiting_planet_id:
            planet = Planet.query.get(fleet.orbiting_planet_id)
            if planet and FleetService.can_refuel_at(fleet, planet):
                fleet.fuel_remaining = fleet.max_fuel
                return True, f"Refueled at {planet.name}"

        # Check all planets at current star
        star = Star.query.get(fleet.current_star_id)
        if star:
            for planet in star.planets:
                if FleetService.can_refuel_at(fleet, planet):
                    fleet.fuel_remaining = fleet.max_fuel
                    fleet.orbiting_planet_id = planet.id
                    return True, f"Refueled at {planet.name}"

        return False, "No friendly planet available for refueling"

    @staticmethod
    def process_refueling(game_id: int) -> Dict:
        """
        Process automatic refueling for all fleets (called at end of turn).
        """
        from app.models import Game

        game = Game.query.get(game_id)
        if not game:
            return {"error": "Game not found"}

        results = {"refueled": []}

        for player in game.players:
            for fleet in player.fleets.filter_by(status=FleetStatus.STATIONED.value):
                if fleet.fuel_remaining < fleet.max_fuel:
                    success, message = FleetService.refuel_fleet(fleet)
                    if success:
                        results["refueled"].append({
                            "fleet_id": fleet.id,
                            "fleet_name": fleet.name,
                        })

        return results

    # -------------------------------------------------------------------------
    # Disbanding (Ship Recycling)
    # -------------------------------------------------------------------------

    @staticmethod
    def disband_ship(ship: Ship) -> Tuple[bool, str, int]:
        """
        Disband a single ship, recovering 75% of its metal cost.

        Args:
            ship: Ship to disband

        Returns:
            Tuple of (success, message, metal_recovered)
        """
        if ship.is_destroyed:
            return False, "Ship is already destroyed", 0

        if not ship.fleet:
            return False, "Ship must be in a fleet", 0

        fleet = ship.fleet
        if fleet.status != FleetStatus.STATIONED.value:
            return False, "Cannot disband ships while in transit", 0

        # Must be at a friendly planet
        planet = None
        if fleet.orbiting_planet_id:
            planet = Planet.query.get(fleet.orbiting_planet_id)

        if not planet or planet.owner_id != fleet.player_id:
            return False, "Must be orbiting a friendly planet to disband", 0

        # Calculate metal recovery
        metal_recovered = int(ship.design.production_cost_metal * DISBAND_METAL_RECOVERY)

        # Give metal to player
        player = GamePlayer.query.get(fleet.player_id)
        player.metal += metal_recovered

        # Destroy ship
        ship.is_destroyed = True
        ship.destroyed_at = datetime.utcnow()

        return True, f"Ship disbanded, recovered {metal_recovered} metal", metal_recovered

    @staticmethod
    def disband_fleet(fleet: Fleet) -> Tuple[bool, str, int]:
        """
        Disband all ships in a fleet.

        Args:
            fleet: Fleet to disband

        Returns:
            Tuple of (success, message, total_metal_recovered)
        """
        if fleet.status != FleetStatus.STATIONED.value:
            return False, "Cannot disband fleet while in transit", 0

        total_metal = 0
        ships_disbanded = 0

        for ship in fleet.ships.filter_by(is_destroyed=False):
            success, _, metal = FleetService.disband_ship(ship)
            if success:
                total_metal += metal
                ships_disbanded += 1

        if ships_disbanded == 0:
            return False, "No ships to disband", 0

        # Delete empty fleet
        db.session.delete(fleet)

        return True, f"Disbanded {ships_disbanded} ships, recovered {total_metal} metal", total_metal

    # -------------------------------------------------------------------------
    # Fleet Summary
    # -------------------------------------------------------------------------

    @staticmethod
    def get_player_fleet_summary(player: GamePlayer) -> Dict:
        """Get summary of all fleets for a player."""
        fleets = []
        total_ships = 0

        for fleet in player.fleets:
            fleet_data = fleet.to_dict()
            fleets.append(fleet_data)
            total_ships += fleet_data["ship_count"]

        designs = [d.to_dict() for d in player.ship_designs]

        return {
            "player_id": player.id,
            "total_fleets": len(fleets),
            "total_ships": total_ships,
            "fleets": fleets,
            "designs": designs,
        }
