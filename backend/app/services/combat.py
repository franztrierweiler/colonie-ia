"""
Combat service.
Handles battle resolution, including orbital combat, bombardment, and colonization.
"""
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from app import db
from app.models import Game, GamePlayer, Planet
from app.models.fleet import Fleet, Ship, ShipDesign, ShipType, FleetStatus, CombatBehavior
from app.models.combat import CombatReport


# =============================================================================
# Combat Constants
# =============================================================================

# Damage calculation
BASE_DAMAGE = 10  # Base damage per weapons level
DAMAGE_VARIANCE = 0.2  # +/- 20% random variance

# Combat behavior modifiers
BEHAVIOR_MODIFIERS = {
    CombatBehavior.AGGRESSIVE.value: {"weapons_mod": 1.2, "shields_mod": 0.8},
    CombatBehavior.DEFENSIVE.value: {"weapons_mod": 0.8, "shields_mod": 1.2},
    CombatBehavior.FOLLOW.value: {"weapons_mod": 0.0, "shields_mod": 1.0},  # Doesn't attack
    CombatBehavior.NORMAL.value: {"weapons_mod": 1.0, "shields_mod": 1.0},
}

# Target priority (higher = targeted first)
TARGET_PRIORITY = {
    ShipType.COLONY.value: 100,      # Priority max - strategic target
    ShipType.TANKER.value: 80,       # Support ships
    ShipType.BATTLESHIP.value: 60,   # High threat
    ShipType.FIGHTER.value: 40,      # Standard threat
    ShipType.BIOLOGICAL.value: 50,   # Medium threat
    ShipType.SCOUT.value: 30,        # Low threat
    ShipType.SATELLITE.value: 20,    # Defense
    ShipType.DECOY.value: 10,        # Lowest priority (but still attracts fire)
}

# Debris and casualties
DEBRIS_RECOVERY_RATE = 0.25  # 25% of destroyed ship metal recovered
DEBRIS_CASUALTY_RATE = 10    # Population killed per debris metal unit
MAX_DEBRIS_CASUALTY_PCT = 0.10  # Max 10% population killed by debris

# Ground defense
GROUND_DEFENSE_PER_1000_POP = 1  # Defense power per 1000 population

# Bombardment
BOMBARDMENT_CASUALTY_PER_WEAPON = 100  # Population killed per weapon level


# =============================================================================
# Combat Service
# =============================================================================

class CombatService:
    """Service for resolving combat between fleets."""

    # -------------------------------------------------------------------------
    # Combat Detection
    # -------------------------------------------------------------------------

    @staticmethod
    def check_for_combat(planet: Planet) -> bool:
        """
        Check if combat should occur on a planet.
        Combat occurs when hostile fleets are present.

        Args:
            planet: Planet to check

        Returns:
            True if combat should occur
        """
        # Get all fleets at this planet (stationed or just arrived)
        fleets = Fleet.query.filter(
            Fleet.current_planet_id == planet.id,
            Fleet.status.in_([FleetStatus.STATIONED.value, FleetStatus.ARRIVING.value])
        ).all()

        if len(fleets) < 2:
            # Need at least 2 fleets or fleet + defender
            if planet.owner_id is None:
                return False
            # Check if any hostile fleet against planet owner
            for fleet in fleets:
                if fleet.player_id != planet.owner_id:
                    return True
            return False

        # Check if any fleets belong to different players who are hostile
        player_ids = set(f.player_id for f in fleets)
        if planet.owner_id:
            player_ids.add(planet.owner_id)

        # For now, all different players are hostile (no alliance system yet)
        return len(player_ids) > 1

    # -------------------------------------------------------------------------
    # Main Combat Resolution
    # -------------------------------------------------------------------------

    @staticmethod
    def resolve_battle(planet: Planet, current_turn: int) -> Optional[CombatReport]:
        """
        Resolve a complete battle on a planet.

        Sequence:
        1. Identify attackers and defenders
        2. Orbital combat (ship vs ship)
        3. Bombardment (if attackers survive and planet has owner)
        4. Colonization (if colony ship and planet unowned after battle)

        Args:
            planet: Planet where battle occurs
            current_turn: Current game turn

        Returns:
            CombatReport if battle occurred, None otherwise
        """
        if not CombatService.check_for_combat(planet):
            return None

        # Get game
        game = planet.star.game

        # Identify participants
        defender_id = planet.owner_id
        attacker_fleets, defender_fleets = CombatService._identify_participants(
            planet, defender_id
        )

        if not attacker_fleets and not defender_fleets:
            return None

        # Create combat report
        report = CombatReport(
            game_id=game.id,
            planet_id=planet.id,
            turn=current_turn,
            defender_id=defender_id,
            attacker_ids=[f.player_id for f in attacker_fleets],
        )

        # Record initial forces
        report.attacker_forces = CombatService._count_forces(attacker_fleets)
        report.defender_forces = CombatService._count_forces(defender_fleets)

        report.add_log_entry("start", f"Combat commence sur {planet.name}")

        # Phase 1: Orbital Combat
        orbital_result = CombatService._orbital_combat(
            attacker_fleets, defender_fleets, report
        )

        # Phase 2: Ground Defense (if planet has population)
        if planet.owner_id and planet.population > 0:
            CombatService._ground_defense(planet, attacker_fleets, report)

        # Phase 3: Bombardment (if attackers survive)
        surviving_attackers = [f for f in attacker_fleets if f.ship_count > 0]
        if surviving_attackers and planet.owner_id:
            CombatService._bombardment(planet, surviving_attackers, report)

        # Process debris
        all_destroyed = orbital_result["destroyed_ships"]
        CombatService._process_debris(planet, all_destroyed, report)

        # Determine victor
        CombatService._determine_victor(
            planet, attacker_fleets, defender_fleets, report
        )

        # Phase 4: Colonization (if attackers won and have colony ship)
        if report.victor_id and report.victor_id != defender_id:
            CombatService._attempt_colonization(planet, surviving_attackers, report)

        # Record losses
        report.attacker_losses = CombatService._count_losses(
            report.attacker_forces, attacker_fleets
        )
        report.defender_losses = CombatService._count_losses_single(
            report.defender_forces, defender_fleets
        )

        report.add_log_entry("end", f"Combat termine - Vainqueur: {report.victor_id or 'aucun'}")

        db.session.add(report)
        return report

    # -------------------------------------------------------------------------
    # Participant Identification
    # -------------------------------------------------------------------------

    @staticmethod
    def _identify_participants(
        planet: Planet,
        defender_id: Optional[int]
    ) -> Tuple[List[Fleet], List[Fleet]]:
        """
        Identify attacker and defender fleets.

        Args:
            planet: Planet where battle occurs
            defender_id: Player ID of planet owner (defender)

        Returns:
            Tuple of (attacker_fleets, defender_fleets)
        """
        fleets = Fleet.query.filter(
            Fleet.current_planet_id == planet.id,
            Fleet.status.in_([FleetStatus.STATIONED.value, FleetStatus.ARRIVING.value])
        ).all()

        attacker_fleets = []
        defender_fleets = []

        for fleet in fleets:
            if fleet.ship_count == 0:
                continue

            if defender_id and fleet.player_id == defender_id:
                defender_fleets.append(fleet)
            else:
                attacker_fleets.append(fleet)

        return attacker_fleets, defender_fleets

    # -------------------------------------------------------------------------
    # Orbital Combat Phase
    # -------------------------------------------------------------------------

    @staticmethod
    def _orbital_combat(
        attacker_fleets: List[Fleet],
        defender_fleets: List[Fleet],
        report: CombatReport
    ) -> Dict[str, Any]:
        """
        Resolve orbital combat between ships.
        Ships fire in order of speed (initiative).

        Args:
            attacker_fleets: List of attacking fleets
            defender_fleets: List of defending fleets
            report: Combat report to log to

        Returns:
            Dict with combat results
        """
        report.add_log_entry("orbital", "Phase de combat orbital")

        # Collect all ships
        attacker_ships = []
        for fleet in attacker_fleets:
            attacker_ships.extend(
                fleet.ships.filter_by(is_destroyed=False).all()
            )

        defender_ships = []
        for fleet in defender_fleets:
            defender_ships.extend(
                fleet.ships.filter_by(is_destroyed=False).all()
            )

        # All ships participate
        all_ships = [(ship, "attacker") for ship in attacker_ships] + \
                    [(ship, "defender") for ship in defender_ships]

        # Sort by initiative (speed)
        all_ships.sort(key=lambda x: CombatService._calculate_initiative(x[0]), reverse=True)

        destroyed_ships = []
        rounds = 0
        max_rounds = 100  # Prevent infinite loops

        # Combat rounds until one side is eliminated
        while attacker_ships and defender_ships and rounds < max_rounds:
            rounds += 1

            for ship, side in all_ships:
                if ship.is_destroyed:
                    continue

                # Determine enemies
                if side == "attacker":
                    enemies = [s for s in defender_ships if not s.is_destroyed]
                else:
                    enemies = [s for s in attacker_ships if not s.is_destroyed]

                if not enemies:
                    break

                # Check if ship can attack (FOLLOW behavior doesn't attack)
                behavior = ship.fleet.combat_behavior if ship.fleet else CombatBehavior.NORMAL.value
                if behavior == CombatBehavior.FOLLOW.value:
                    continue

                # Select target and fire
                target = CombatService._select_target(enemies)
                if target:
                    destroyed = CombatService._fire(ship, target, behavior, report)
                    if destroyed:
                        destroyed_ships.append(target)

            # Remove destroyed ships from lists
            attacker_ships = [s for s in attacker_ships if not s.is_destroyed]
            defender_ships = [s for s in defender_ships if not s.is_destroyed]

        report.add_log_entry(
            "orbital_end",
            f"Combat orbital termine apres {rounds} rounds",
            {"attacker_remaining": len(attacker_ships), "defender_remaining": len(defender_ships)}
        )

        return {
            "rounds": rounds,
            "attacker_remaining": len(attacker_ships),
            "defender_remaining": len(defender_ships),
            "destroyed_ships": destroyed_ships,
        }

    @staticmethod
    def _calculate_initiative(ship: Ship) -> float:
        """
        Calculate ship's initiative (combat order).
        Higher speed = fires first.
        """
        if not ship.design:
            return 0

        base_speed = ship.design.effective_speed
        # Add small random factor to break ties
        return base_speed + random.random() * 0.5

    @staticmethod
    def _select_target(enemies: List[Ship]) -> Optional[Ship]:
        """
        Select a target from enemy ships based on priority.
        Colony ships are targeted first.
        """
        if not enemies:
            return None

        # Sort by priority
        enemies_sorted = sorted(
            enemies,
            key=lambda s: TARGET_PRIORITY.get(s.design.ship_type, 0) if s.design else 0,
            reverse=True
        )

        # Target highest priority that's not destroyed
        for enemy in enemies_sorted:
            if not enemy.is_destroyed:
                return enemy

        return None

    @staticmethod
    def _fire(
        attacker: Ship,
        target: Ship,
        behavior: str,
        report: CombatReport
    ) -> bool:
        """
        Fire from attacker to target.
        Returns True if target is destroyed.
        """
        if not attacker.design or not target.design:
            return False

        # Get behavior modifiers
        mods = BEHAVIOR_MODIFIERS.get(behavior, BEHAVIOR_MODIFIERS[CombatBehavior.NORMAL.value])

        # Calculate damage
        weapon_power = attacker.design.effective_weapons * mods["weapons_mod"]
        variance = 1 + (random.random() * 2 - 1) * DAMAGE_VARIANCE
        raw_damage = weapon_power * BASE_DAMAGE * variance

        # Calculate damage reduction from shields
        shield_power = target.design.effective_shields
        target_behavior = target.fleet.combat_behavior if target.fleet else CombatBehavior.NORMAL.value
        target_mods = BEHAVIOR_MODIFIERS.get(target_behavior, BEHAVIOR_MODIFIERS[CombatBehavior.NORMAL.value])
        effective_shields = shield_power * target_mods["shields_mod"]

        # Damage reduction (shields absorb damage)
        damage_reduction = effective_shields * 2  # Each shield level reduces 2 damage
        final_damage = max(1, int(raw_damage - damage_reduction))

        # Apply damage
        destroyed = target.take_damage(final_damage)

        if destroyed:
            report.add_log_entry(
                "ship_destroyed",
                f"{attacker.design.ship_type} detruit {target.design.ship_type}",
                {"attacker_type": attacker.design.ship_type, "target_type": target.design.ship_type}
            )

        return destroyed

    # -------------------------------------------------------------------------
    # Ground Defense Phase
    # -------------------------------------------------------------------------

    @staticmethod
    def _ground_defense(
        planet: Planet,
        attacker_fleets: List[Fleet],
        report: CombatReport
    ):
        """
        Population defends with owner's best technology.
        """
        if not planet.owner or planet.population <= 0:
            return

        report.add_log_entry("ground", "Defense au sol")

        # Get defender technology
        defender_tech = planet.owner.technology
        if not defender_tech:
            return

        # Defense power based on population and tech
        defense_level = max(defender_tech.weapons_level, defender_tech.shields_level)
        pop_in_thousands = planet.population / 1000
        defense_power = pop_in_thousands * GROUND_DEFENSE_PER_1000_POP * defense_level

        # Distribute damage among attacking ships
        for fleet in attacker_fleets:
            if fleet.ship_count == 0:
                continue

            ships = list(fleet.ships.filter_by(is_destroyed=False).all())
            if not ships:
                continue

            # Damage per ship
            damage_per_ship = defense_power / len(ships)

            for ship in ships:
                variance = random.random() * 0.5 + 0.75  # 75% to 125%
                damage = int(damage_per_ship * variance)
                destroyed = ship.take_damage(damage)

                if destroyed:
                    report.add_log_entry(
                        "ground_kill",
                        f"Defense au sol detruit {ship.design.ship_type}",
                    )

    # -------------------------------------------------------------------------
    # Bombardment Phase
    # -------------------------------------------------------------------------

    @staticmethod
    def _bombardment(
        planet: Planet,
        attacker_fleets: List[Fleet],
        report: CombatReport
    ):
        """
        Surviving attackers bombard the planet's population.
        """
        if planet.population <= 0:
            return

        report.add_log_entry("bombardment", "Phase de bombardement")

        # Calculate total bombardment power
        total_weapons = 0
        for fleet in attacker_fleets:
            for ship in fleet.ships.filter_by(is_destroyed=False):
                if ship.design:
                    total_weapons += ship.design.effective_weapons

        # Calculate casualties
        base_casualties = int(total_weapons * BOMBARDMENT_CASUALTY_PER_WEAPON)
        variance = random.random() * 0.4 + 0.8  # 80% to 120%
        casualties = int(base_casualties * variance)

        # Apply casualties
        old_pop = planet.population
        planet.population = max(0, planet.population - casualties)
        actual_casualties = old_pop - planet.population

        report.population_casualties += actual_casualties
        report.add_log_entry(
            "bombardment_result",
            f"Bombardement: {actual_casualties} victimes",
            {"casualties": actual_casualties, "remaining_population": planet.population}
        )

        # If population wiped out, planet becomes unowned
        if planet.population <= 0:
            planet.owner_id = None
            report.planet_captured = True
            report.add_log_entry("planet_captured", f"{planet.name} capture (population eliminee)")

    # -------------------------------------------------------------------------
    # Debris Processing
    # -------------------------------------------------------------------------

    @staticmethod
    def _process_debris(
        planet: Planet,
        destroyed_ships: List[Ship],
        report: CombatReport
    ):
        """
        Process debris from destroyed ships.
        - Recover metal (if planet is owned)
        - Cause casualties from falling debris
        """
        if not destroyed_ships:
            return

        # Calculate total debris metal
        total_metal = 0
        for ship in destroyed_ships:
            if ship.design:
                total_metal += ship.design.production_cost_metal

        report.total_debris_metal = total_metal

        # Recovery (only if planet has owner after battle)
        if planet.owner_id and total_metal > 0:
            recovered = int(total_metal * DEBRIS_RECOVERY_RATE)
            report.metal_recovered = recovered

            # Add to owner's metal stockpile
            planet.owner.metal += recovered

            report.add_log_entry(
                "debris_recovery",
                f"Debris recuperes: {recovered} metal",
                {"total_debris": total_metal, "recovered": recovered}
            )

        # Casualties from debris
        if planet.population > 0 and total_metal > 0:
            max_casualties = int(planet.population * MAX_DEBRIS_CASUALTY_PCT)
            debris_casualties = min(
                int(total_metal * DEBRIS_CASUALTY_RATE * random.random()),
                max_casualties
            )

            if debris_casualties > 0:
                planet.population = max(0, planet.population - debris_casualties)
                report.population_casualties += debris_casualties

                report.add_log_entry(
                    "debris_casualties",
                    f"Debris: {debris_casualties} victimes civiles",
                )

    # -------------------------------------------------------------------------
    # Victory Determination
    # -------------------------------------------------------------------------

    @staticmethod
    def _determine_victor(
        planet: Planet,
        attacker_fleets: List[Fleet],
        defender_fleets: List[Fleet],
        report: CombatReport
    ):
        """
        Determine the battle's victor.
        """
        attacker_ships_remaining = sum(f.ship_count for f in attacker_fleets)
        defender_ships_remaining = sum(f.ship_count for f in defender_fleets)

        if attacker_ships_remaining > 0 and defender_ships_remaining == 0:
            # Attackers won
            # Find attacker with most ships remaining
            if attacker_fleets:
                winner = max(attacker_fleets, key=lambda f: f.ship_count)
                report.victor_id = winner.player_id
        elif defender_ships_remaining > 0 and attacker_ships_remaining == 0:
            # Defenders won
            report.victor_id = report.defender_id
        elif attacker_ships_remaining == 0 and defender_ships_remaining == 0:
            # Draw - mutual destruction
            report.is_draw = True
        else:
            # Both have ships remaining - shouldn't happen normally
            # Victor is side with more ships
            if attacker_ships_remaining > defender_ships_remaining:
                winner = max(attacker_fleets, key=lambda f: f.ship_count)
                report.victor_id = winner.player_id
            else:
                report.victor_id = report.defender_id

    # -------------------------------------------------------------------------
    # Colonization Phase
    # -------------------------------------------------------------------------

    @staticmethod
    def _attempt_colonization(
        planet: Planet,
        attacker_fleets: List[Fleet],
        report: CombatReport
    ):
        """
        Attempt to colonize planet with a colony ship.
        """
        # Check if planet is now unowned
        if planet.owner_id is not None:
            return

        # Find a colony ship
        colony_ship = None
        colony_fleet = None

        for fleet in attacker_fleets:
            for ship in fleet.ships.filter_by(is_destroyed=False):
                if ship.design and ship.design.ship_type == ShipType.COLONY.value:
                    colony_ship = ship
                    colony_fleet = fleet
                    break
            if colony_ship:
                break

        if not colony_ship:
            return

        # Colonize!
        planet.owner_id = colony_fleet.player_id
        planet.population = 10000  # Colony ship carries 10000 colonists

        # Destroy the colony ship (used up)
        colony_ship.is_destroyed = True
        colony_ship.destroyed_at = datetime.utcnow()

        report.planet_colonized = True
        report.new_owner_id = colony_fleet.player_id

        report.add_log_entry(
            "colonization",
            f"{planet.name} colonisee par joueur {colony_fleet.player_id}",
            {"new_population": 10000}
        )

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    @staticmethod
    def _count_forces(fleets: List[Fleet]) -> Dict[int, Dict[str, int]]:
        """Count ships by type for each player."""
        forces = {}
        for fleet in fleets:
            player_id = fleet.player_id
            if player_id not in forces:
                forces[player_id] = {}

            for ship in fleet.ships.filter_by(is_destroyed=False):
                if ship.design:
                    ship_type = ship.design.ship_type
                    forces[player_id][ship_type] = forces[player_id].get(ship_type, 0) + 1

        return forces

    @staticmethod
    def _count_losses(
        initial_forces: Dict[int, Dict[str, int]],
        fleets: List[Fleet]
    ) -> Dict[int, Dict[str, int]]:
        """Calculate losses by comparing initial to current forces."""
        current = CombatService._count_forces(fleets)
        losses = {}

        for player_id, ships in initial_forces.items():
            losses[player_id] = {}
            current_ships = current.get(player_id, {})

            for ship_type, count in ships.items():
                current_count = current_ships.get(ship_type, 0)
                lost = count - current_count
                if lost > 0:
                    losses[player_id][ship_type] = lost

        return losses

    @staticmethod
    def _count_losses_single(
        initial_forces: Dict[int, Dict[str, int]],
        fleets: List[Fleet]
    ) -> Dict[str, int]:
        """Calculate losses for defender (single player)."""
        current = {}
        for fleet in fleets:
            for ship in fleet.ships.filter_by(is_destroyed=False):
                if ship.design:
                    ship_type = ship.design.ship_type
                    current[ship_type] = current.get(ship_type, 0) + 1

        # Get initial forces (flatten if nested)
        initial = {}
        for player_ships in initial_forces.values():
            for ship_type, count in player_ships.items():
                initial[ship_type] = initial.get(ship_type, 0) + count

        losses = {}
        for ship_type, count in initial.items():
            current_count = current.get(ship_type, 0)
            lost = count - current_count
            if lost > 0:
                losses[ship_type] = lost

        return losses

    # -------------------------------------------------------------------------
    # Query Methods
    # -------------------------------------------------------------------------

    @staticmethod
    def get_combat_reports_for_turn(game_id: int, turn: int) -> List[CombatReport]:
        """Get all combat reports for a specific turn."""
        return CombatReport.query.filter_by(
            game_id=game_id,
            turn=turn
        ).all()

    @staticmethod
    def get_player_combat_history(
        game_id: int,
        player_id: int,
        limit: int = 20
    ) -> List[CombatReport]:
        """Get combat history involving a specific player."""
        return CombatReport.query.filter(
            CombatReport.game_id == game_id,
            db.or_(
                CombatReport.defender_id == player_id,
                CombatReport.attacker_ids.contains([player_id])
            )
        ).order_by(CombatReport.turn.desc()).limit(limit).all()
