"""
Main AI Service for Colonie-IA.

This service orchestrates all AI decision-making for computer-controlled players.
It uses GameAnalysis to understand the situation and applies difficulty-based
modifiers to make appropriate decisions.
"""
import random
import logging
from typing import Dict, List, Any, Optional

from app import db
from app.models import (
    GamePlayer, Planet, Fleet, Game,
    PlanetState, FleetStatus, ShipType, ShipDesign,
)
from app.services.ai.ai_difficulty import (
    AIDifficultyLevel, DifficultyModifiers, map_legacy_difficulty
)
from app.services.ai.game_analysis import GameAnalysis, GamePhase

logger = logging.getLogger(__name__)


class AIService:
    """
    Main AI service that processes AI player turns.

    The AI makes decisions in the following order:
    1. Analyze game state
    2. Handle pending radical breakthroughs
    3. Allocate research budget
    4. Allocate planet budgets (terraform/mining/ships)
    5. Queue ship production
    6. Plan and execute fleet movements

    Each decision is modified by the AI's difficulty level.
    """

    @staticmethod
    def process_ai_turn(player: GamePlayer) -> Dict[str, Any]:
        """
        Process a complete turn for an AI player.

        This is the main entry point called by TurnService.

        Args:
            player: The AI GamePlayer to process

        Returns:
            Dictionary containing all decisions made
        """
        if not player.is_ai:
            raise ValueError(f"Player {player.id} is not an AI player")

        # Get difficulty modifiers
        difficulty = AIService._get_difficulty(player)
        modifiers = DifficultyModifiers.for_difficulty(difficulty)

        # Analyze game state
        analysis = GameAnalysis.analyze(player)

        logger.info(
            f"[AI-{difficulty.value}] Turn {analysis.current_turn}: "
            f"Processing player {player.player_name}"
        )
        logger.debug(f"[AI] Analysis summary: {analysis.get_summary()}")

        # Initialize results
        results = {
            "player_id": player.id,
            "player_name": player.player_name,
            "difficulty": difficulty.value,
            "decisions": {
                "research": {},
                "planet_budgets": {},
                "production": [],
                "fleet_movements": [],
            },
            "analysis_summary": analysis.get_summary(),
        }

        # Apply decision error rate (skip some decisions on lower difficulties)
        if random.random() < modifiers.decision_error_rate:
            logger.debug(f"[AI] Decision error triggered - suboptimal turn")
            # On error, just skip most decisions
            return results

        try:
            # 1. Handle pending radical breakthroughs
            AIService._handle_radical_breakthroughs(player, analysis, modifiers, results)

            # 2. Allocate research budget
            AIService._allocate_research(player, analysis, modifiers, results)

            # 3. Allocate planet budgets
            AIService._allocate_planet_budgets(player, analysis, modifiers, results)

            # 4. Queue ship production
            AIService._plan_production(player, analysis, modifiers, results)

            # 5. Plan fleet movements
            AIService._plan_fleet_movements(player, analysis, modifiers, results)

            db.session.commit()

        except Exception as e:
            logger.error(f"[AI] Error processing turn for player {player.id}: {e}")
            db.session.rollback()
            results["error"] = str(e)

        return results

    @staticmethod
    def _get_difficulty(player: GamePlayer) -> AIDifficultyLevel:
        """Get the difficulty level for an AI player."""
        if player.ai_difficulty:
            # Try to match new difficulty levels
            try:
                return AIDifficultyLevel(player.ai_difficulty)
            except ValueError:
                # Fall back to legacy mapping
                return map_legacy_difficulty(player.ai_difficulty)
        return AIDifficultyLevel.CAPITAINE

    @staticmethod
    def _handle_radical_breakthroughs(
        player: GamePlayer,
        analysis: GameAnalysis,
        modifiers: DifficultyModifiers,
        results: Dict
    ):
        """
        Handle any pending radical breakthroughs.

        The AI chooses which breakthrough to eliminate based on current needs.
        """
        pending = player.radical_breakthroughs.filter_by(is_resolved=False).all()

        for breakthrough in pending:
            if not breakthrough.options or len(breakthrough.options) < 4:
                continue

            # Choose option to eliminate based on what we need LEAST
            options = list(breakthrough.options)

            # Determine least needed option
            # Higher difficulty = smarter elimination
            if modifiers.tech_focus > 0.7:
                # Smart choice: eliminate what we need least
                least_needed = AIService._choose_least_needed_breakthrough(
                    options, player, analysis
                )
            else:
                # Random choice on lower difficulties
                least_needed = random.choice(options)

            breakthrough.eliminated_option = least_needed

            # Resolve: pick randomly from remaining
            remaining = [o for o in options if o != least_needed]
            breakthrough.unlocked_option = random.choice(remaining)
            breakthrough.is_resolved = True
            breakthrough.resolved_turn = analysis.current_turn

            results["decisions"]["radical_breakthrough"] = {
                "eliminated": least_needed,
                "unlocked": breakthrough.unlocked_option,
            }

            logger.debug(
                f"[AI] Resolved breakthrough: eliminated {least_needed}, "
                f"got {breakthrough.unlocked_option}"
            )

    @staticmethod
    def _choose_least_needed_breakthrough(
        options: List[str],
        player: GamePlayer,
        analysis: GameAnalysis
    ) -> str:
        """Choose the breakthrough option we need least."""
        tech = player.technology

        # Score each option (lower = less needed)
        scores = {}

        for option in options:
            score = 50  # Base score

            if "RANGE" in option.upper():
                # Less needed if we have high range or few colonizable planets
                score -= tech.range_level * 2 if tech else 0
                if len(analysis.colonizable_planets) == 0:
                    score -= 20
            elif "SPEED" in option.upper():
                # Always somewhat useful
                score += 10
            elif "WEAPONS" in option.upper():
                # Less needed if no enemies or high military advantage
                if analysis.military_advantage > 2.0:
                    score -= 20
            elif "SHIELDS" in option.upper():
                # More needed if under threat
                if analysis.incoming_threats:
                    score += 20
            elif "DECOY" in option.upper():
                # Less needed early game
                if analysis.phase == GamePhase.EARLY:
                    score -= 30
            elif "BIOLOGICAL" in option.upper():
                # Advanced option, less needed early
                if analysis.phase == GamePhase.EARLY:
                    score -= 30
            elif "SPY" in option.upper():
                # Less useful late game
                if analysis.phase == GamePhase.LATE:
                    score -= 20
            elif "STEAL" in option.upper():
                # More useful if behind in tech
                behind_count = sum(
                    1 for v in analysis.enemy_tech_comparison.values()
                    if v == "behind"
                )
                if behind_count > 0:
                    score += 20

            scores[option] = score

        # Return option with lowest score
        return min(scores.keys(), key=lambda k: scores[k])

    @staticmethod
    def _allocate_research(
        player: GamePlayer,
        analysis: GameAnalysis,
        modifiers: DifficultyModifiers,
        results: Dict
    ):
        """
        Allocate research budget across technology domains.

        Strategy varies by game phase and difficulty.
        """
        tech = player.technology
        if not tech:
            return

        # Base allocation by phase
        if analysis.phase == GamePhase.EARLY:
            allocation = {
                "range": 35,
                "speed": 25,
                "weapons": 15,
                "shields": 10,
                "mini": 5,
                "radical": 10,
            }
        elif analysis.phase == GamePhase.MID:
            allocation = {
                "range": 15,
                "speed": 25,
                "weapons": 25,
                "shields": 20,
                "mini": 10,
                "radical": 5,
            }
        else:  # LATE
            allocation = {
                "range": 10,
                "speed": 20,
                "weapons": 30,
                "shields": 25,
                "mini": 10,
                "radical": 5,
            }

        # Adjust based on situation
        if analysis.incoming_threats:
            # More shields if under attack
            allocation["shields"] += 10
            allocation["range"] -= 5
            allocation["mini"] -= 5

        if analysis.needs_expansion and len(analysis.colonizable_planets) > 0:
            # More range for expansion
            allocation["range"] += 10
            allocation["weapons"] -= 5
            allocation["shields"] -= 5

        # Apply tech focus modifier (lower focus = more random)
        if modifiers.tech_focus < 0.8:
            # Add randomness
            for key in allocation:
                allocation[key] += random.randint(-5, 5)

        # Normalize to 100
        total = sum(allocation.values())
        if total > 0:
            for key in allocation:
                allocation[key] = max(0, int(allocation[key] * 100 / total))

        # Ensure sum is 100
        diff = 100 - sum(allocation.values())
        allocation["speed"] += diff  # Speed is always useful

        # Apply to player technology
        tech.range_budget = allocation["range"]
        tech.speed_budget = allocation["speed"]
        tech.weapons_budget = allocation["weapons"]
        tech.shields_budget = allocation["shields"]
        tech.mini_budget = allocation["mini"]
        tech.radical_budget = allocation["radical"]

        results["decisions"]["research"] = allocation
        logger.debug(f"[AI] Research allocation: {allocation}")

    @staticmethod
    def _allocate_planet_budgets(
        player: GamePlayer,
        analysis: GameAnalysis,
        modifiers: DifficultyModifiers,
        results: Dict
    ):
        """
        Allocate budgets for each owned planet.

        Balance between terraforming, mining, and ship production.
        """
        for planet in analysis.my_planets:
            # Default balanced allocation
            terraform = 34
            mining = 33
            ships = 33

            # Adjust based on planet state
            temp_diff = abs(planet.current_temperature - 22)

            if temp_diff > 30:
                # Planet needs significant terraforming
                terraform = 60
                mining = 20
                ships = 20
            elif temp_diff > 10:
                # Moderate terraforming needed
                terraform = 45
                mining = 30
                ships = 25
            elif planet.metal_remaining > 5000:
                # Rich in metal
                terraform = 20
                mining = 50
                ships = 30
            elif planet.metal_remaining < 500:
                # Low metal, focus on ships if we have any
                terraform = 30
                mining = 10
                ships = 60

            # Late game: more ships
            if analysis.phase == GamePhase.LATE:
                ships += 15
                terraform -= 10
                mining -= 5

            # Under threat: more ships
            if planet in analysis.vulnerable_planets:
                ships += 20
                terraform -= 10
                mining -= 10

            # Apply economy efficiency modifier
            effectiveness = modifiers.economy_efficiency
            # Lower efficiency = slightly suboptimal allocation
            if effectiveness < 1.0:
                terraform += random.randint(-10, 10)
                mining += random.randint(-10, 10)
                ships = 100 - terraform - mining

            # Normalize
            total = terraform + mining + ships
            terraform = max(0, min(100, int(terraform * 100 / total)))
            mining = max(0, min(100, int(mining * 100 / total)))
            ships = 100 - terraform - mining

            # Apply to planet
            planet.terraform_budget = terraform
            planet.mining_budget = mining
            planet.ships_budget = ships

            results["decisions"]["planet_budgets"][planet.id] = {
                "planet_name": planet.name,
                "terraform": terraform,
                "mining": mining,
                "ships": ships,
            }

        logger.debug(f"[AI] Planet budgets allocated for {len(analysis.my_planets)} planets")

    @staticmethod
    def _plan_production(
        player: GamePlayer,
        analysis: GameAnalysis,
        modifiers: DifficultyModifiers,
        results: Dict
    ):
        """
        Plan and queue ship production across planets.

        Decides what ships to build based on current needs and queues them.
        Only queues if player has resources and queue is not too full.
        """
        from app.services.economy import EconomyService
        from app.models import ProductionQueue

        # Ensure player has ship designs
        AIService._ensure_ship_designs(player)

        # Check current queue size - don't queue more if already have pending items
        current_queue_size = 0
        for planet in analysis.my_planets:
            current_queue_size += ProductionQueue.query.filter_by(
                planet_id=planet.id,
                is_completed=False
            ).count()

        # Limit queue to 3 items per planet
        max_queue = len(analysis.my_planets) * 3
        if current_queue_size >= max_queue:
            logger.debug(f"[AI] Queue full ({current_queue_size}/{max_queue}), skipping production")
            results["decisions"]["production"] = []
            return

        # Determine what we need
        need_scouts = analysis.phase == GamePhase.EARLY and len(analysis.colonizable_planets) > 0
        need_colony = analysis.needs_expansion and len(analysis.colonizable_planets) > 0
        need_fighters = analysis.incoming_threats or analysis.attack_opportunities
        need_defense = len(analysis.vulnerable_planets) > 0

        # Get all designs by type
        designs = {}
        for d in player.ship_designs.all():
            designs[d.ship_type] = d

        production_plan = []

        # Determine production priority (only one type per turn to avoid resource exhaustion)
        production_need = None

        if need_colony and ShipType.COLONY.value in designs:
            # Check if we already have colony ships available or in production
            has_colony_ship = any(f.can_colonize for f in analysis.available_fleets)
            colony_in_queue = ProductionQueue.query.filter(
                ProductionQueue.design_id == designs[ShipType.COLONY.value].id,
                ProductionQueue.is_completed == False
            ).count() > 0

            if not has_colony_ship and not colony_in_queue:
                production_need = (ShipType.COLONY.value, "high", 1)

        if production_need is None and need_fighters and ShipType.FIGHTER.value in designs:
            production_need = (ShipType.FIGHTER.value, "medium", 1)

        if production_need is None and need_scouts and ShipType.SCOUT.value in designs:
            production_need = (ShipType.SCOUT.value, "medium", 1)

        if production_need is None and need_defense and ShipType.SATELLITE.value in designs:
            production_need = (ShipType.SATELLITE.value, "low", 1)

        if production_need is None:
            results["decisions"]["production"] = []
            return

        ship_type, priority, count = production_need
        design = designs[ship_type]

        # Check if player can afford the FULL cost
        if design.is_prototype_built:
            cost_money = design.production_cost_money
            cost_metal = design.production_cost_metal
        else:
            cost_money = design.prototype_cost_money
            cost_metal = design.prototype_cost_metal

        if player.money < cost_money or player.metal < cost_metal:
            logger.debug(
                f"[AI] Cannot afford {ship_type} (need {cost_money}$/{cost_metal}M, "
                f"have {player.money}$/{player.metal}M)"
            )
            results["decisions"]["production"] = []
            return

        # Queue production on planets with capacity
        planets_with_capacity = [
            p for p in analysis.my_planets
            if p.ships_budget > 20 and p.population > 5000
        ]

        if not planets_with_capacity and analysis.my_planets:
            planets_with_capacity = analysis.my_planets[:1]

        if planets_with_capacity:
            planet = planets_with_capacity[0]

            # Queue production
            success, msg, items = EconomyService.add_to_production_queue(
                planet=planet,
                design_id=design.id,
                count=count
            )

            if success:
                production_plan.append({
                    "type": ship_type,
                    "priority": priority,
                    "count": count,
                    "planet_id": planet.id,
                    "planet_name": planet.name,
                })
                logger.debug(f"[AI] Queued {count}x {ship_type} on {planet.name}")

        results["decisions"]["production"] = production_plan

    @staticmethod
    def _ensure_ship_designs(player: GamePlayer):
        """
        Ensure the AI player has basic ship designs.

        Creates default designs if none exist.
        """
        from app.services.fleet import FleetService

        existing_types = {d.ship_type for d in player.ship_designs.all()}

        # Default designs for AI
        default_designs = [
            (f"Chasseur {player.player_name[:3]}", ShipType.FIGHTER),
            (f"Éclaireur {player.player_name[:3]}", ShipType.SCOUT),
            (f"Colonisateur {player.player_name[:3]}", ShipType.COLONY),
            (f"Satellite {player.player_name[:3]}", ShipType.SATELLITE),
        ]

        for name, ship_type in default_designs:
            if ship_type.value not in existing_types:
                try:
                    FleetService.create_design(
                        player=player,
                        name=name,
                        ship_type=ship_type,
                        range_level=1,
                        speed_level=1,
                        weapons_level=1,
                        shields_level=1,
                        mini_level=1,
                    )
                    logger.debug(f"[AI] Created design {name} for {player.player_name}")
                except Exception as e:
                    logger.warning(f"[AI] Failed to create design {name}: {e}")

    @staticmethod
    def _plan_fleet_movements(
        player: GamePlayer,
        analysis: GameAnalysis,
        modifiers: DifficultyModifiers,
        results: Dict
    ):
        """
        Plan fleet movements for the turn.

        Considers defense, expansion, and attack opportunities.
        """
        movements = []

        # Check reaction delay
        if modifiers.reaction_delay > 0:
            # On lower difficulties, don't react immediately to threats
            logger.debug(f"[AI] Reaction delay: {modifiers.reaction_delay} turns")
            # Still do some basic movements

        # 1. Defense: Move fleets to threatened planets
        for threat in analysis.incoming_threats[:3]:  # Handle top 3 threats
            target = threat.target_planet

            # Find available fleet to defend
            for fleet in analysis.available_fleets:
                if fleet.current_planet_id == target.id:
                    continue  # Already there

                # Simple distance check (would need proper pathfinding)
                current = fleet.current_planet
                if current:
                    dx = current.x - target.x
                    dy = current.y - target.y
                    distance = (dx*dx + dy*dy) ** 0.5

                    # Can we reach in time?
                    turns_to_arrive = int(distance / max(1, fleet.fleet_speed)) + 1
                    if turns_to_arrive <= (threat.arrival_turn - analysis.current_turn + 1):
                        movements.append({
                            "fleet_id": fleet.id,
                            "fleet_name": fleet.name,
                            "destination_id": target.id,
                            "destination_name": target.name,
                            "reason": "defense",
                        })
                        analysis.available_fleets.remove(fleet)
                        break

        # 2. Expansion: Send colony ships to colonizable planets
        if analysis.colonizable_planets and modifiers.exploration_priority > 0.5:
            from app.services.fleet import FleetService

            for fleet in analysis.available_fleets[:]:
                if fleet.can_colonize:
                    # Find best REACHABLE colonization target
                    for target in analysis.colonizable_planets:
                        # Check if fleet can actually reach this target
                        can_reach, reason = FleetService.can_reach(fleet, target.planet)
                        if can_reach:
                            movements.append({
                                "fleet_id": fleet.id,
                                "fleet_name": fleet.name,
                                "destination_id": target.planet.id,
                                "destination_name": target.planet.name,
                                "reason": "colonization",
                            })
                            analysis.available_fleets.remove(fleet)
                            break

        # 3. Attack: Launch attacks on opportunity targets
        if analysis.attack_opportunities and len(analysis.available_fleets) > 0:
            for opportunity in analysis.attack_opportunities[:3]:
                # Check if we have enough force
                required_power = opportunity.defense_power * modifiers.attack_threshold

                # Find fleet with enough power
                for fleet in analysis.available_fleets[:]:
                    fleet_power = fleet.total_weapons + fleet.total_shields
                    if fleet_power >= required_power:
                        movements.append({
                            "fleet_id": fleet.id,
                            "fleet_name": fleet.name,
                            "destination_id": opportunity.target_planet.id,
                            "destination_name": opportunity.target_planet.name,
                            "reason": "attack",
                        })
                        analysis.available_fleets.remove(fleet)
                        break

        results["decisions"]["fleet_movements"] = movements
        logger.debug(f"[AI] Fleet movements planned: {len(movements)}")

        # Note: Actual fleet movement execution should be done via FleetService
        # This is just the decision phase

    @staticmethod
    def execute_fleet_movements(player: GamePlayer, movements: List[Dict]) -> List[Dict]:
        """
        Execute the planned fleet movements.

        This should be called after planning to actually move the fleets.

        Args:
            player: The player whose fleets to move
            movements: List of movement decisions from planning

        Returns:
            List of execution results
        """
        from app.services.fleet import FleetService

        results = []
        game = player.game

        for movement in movements:
            fleet_id = movement.get("fleet_id")
            destination_id = movement.get("destination_id")

            try:
                # Get fleet and destination objects
                fleet = Fleet.query.get(fleet_id)
                destination = Planet.query.get(destination_id)

                if not fleet or not destination:
                    raise ValueError(f"Fleet {fleet_id} or destination {destination_id} not found")

                if fleet.player_id != player.id:
                    raise ValueError(f"Fleet {fleet_id} does not belong to player")

                # Use FleetService to move fleet
                success, message = FleetService.move_fleet(
                    fleet=fleet,
                    destination=destination,
                    current_turn=game.current_turn,
                )

                results.append({
                    "fleet_id": fleet_id,
                    "success": success,
                    "message": message,
                    "reason": movement.get("reason"),
                })

                if success:
                    logger.debug(
                        f"[AI] Fleet {fleet.name} moving to {destination.name} "
                        f"({movement.get('reason')})"
                    )

            except Exception as e:
                logger.warning(f"[AI] Failed to move fleet {fleet_id}: {e}")
                results.append({
                    "fleet_id": fleet_id,
                    "success": False,
                    "error": str(e),
                })

        return results

    @staticmethod
    def process_colonization_on_arrival(fleet: Fleet, planet: Planet) -> bool:
        """
        Check and execute colonization when a fleet arrives at a planet.

        Called after fleet movement processing to handle automatic colonization.

        Args:
            fleet: Fleet that just arrived
            planet: Planet where fleet arrived

        Returns:
            True if colonization happened
        """
        from app.services.ai.ai_expansion import AIExpansionService

        # Only AI players auto-colonize
        if not fleet.owner.is_ai:
            return False

        # Check if planet is uncolonized and fleet can colonize
        if planet.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
            return False

        if not fleet.can_colonize:
            return False

        # Execute colonization
        success, message = AIExpansionService.execute_colonization(fleet, planet)

        if success:
            logger.info(f"[AI] Auto-colonization: {message}")

        return success
