"""
Economy service.
Handles resource management: money (taxation), metal (mining), and debt.
"""
import math
from typing import Dict, List, Optional, Tuple

from datetime import datetime
from app import db
from app.models import GamePlayer, Planet, PlanetState, ProductionQueue, Ship, Fleet


# =============================================================================
# Economic Constants
# =============================================================================

# Initial resources
INITIAL_MONEY = 10000
INITIAL_METAL = 500

# Debt system
DEBT_MAX_MULTIPLIER = 5  # Max debt = 5x total income
DEBT_INTEREST_RATE = 0.15  # 15% per turn

# Taxation
BASE_TAX_RATE = 0.1  # 10% of population contributes to income
POPULATION_THRESHOLD = 10000  # Below this, colony costs money
COLONY_MAINTENANCE_COST = 100  # Base cost for small colonies

# Mining
BASE_MINING_RATE = 10  # Base metal units per turn at 100% budget
MINING_EFFICIENCY_FACTOR = 0.5  # Logarithmic scaling factor

# Population growth
BASE_GROWTH_RATE = 0.05  # 5% per turn
MAX_GROWTH_RATE = 0.10  # 10% max with ideal conditions

# Terraformation
IDEAL_TEMPERATURE = 22.0  # Ideal temperature in Celsius
BASE_TERRAFORM_RATE = 5.0  # Base degrees change per turn at 100% budget
MIN_TERRAFORM_CHANGE = 0.1  # Minimum temperature change per turn

# Ship Production
BASE_SHIP_PRODUCTION_RATE = 100  # Base production points per turn at 100% budget
PRODUCTION_POPULATION_FACTOR = 50000  # Population per 1x production multiplier


# =============================================================================
# Utility Functions
# =============================================================================

def diminishing_returns(budget_percentage: float, base_output: float) -> float:
    """
    Calculate output with diminishing returns (logarithmic).

    Args:
        budget_percentage: Budget allocation as decimal (0-1)
        base_output: Maximum output at 100% budget

    Returns:
        Effective output after diminishing returns

    Formula: output = base * log(1 + budget) / log(2)
    This gives approximately:
        10% budget -> 26% output
        25% budget -> 49% output
        50% budget -> 74% output
        75% budget -> 91% output
        100% budget -> 100% output
    """
    if budget_percentage <= 0:
        return 0.0

    # Clamp to 0-1 range
    budget_percentage = min(1.0, max(0.0, budget_percentage))

    # Logarithmic diminishing returns
    efficiency = math.log(1 + budget_percentage) / math.log(2)

    return base_output * efficiency


def calculate_habitability_factor(planet: Planet) -> float:
    """
    Calculate habitability factor for economic calculations.

    Args:
        planet: Planet instance

    Returns:
        Habitability factor (0-1)
    """
    return planet.habitability


# =============================================================================
# Economy Service
# =============================================================================

class EconomyService:
    """Service for managing game economy."""

    # -------------------------------------------------------------------------
    # Income Calculations (US 3.1, US 3.5)
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_planet_income(planet: Planet) -> int:
        """
        Calculate the income (or cost) of a single planet.

        - High population planets generate income (taxation)
        - Low population planets cost money (maintenance)

        Args:
            planet: Planet instance

        Returns:
            Income (positive) or cost (negative) in money units
        """
        if planet.state not in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
            return 0

        population = planet.population
        habitability = calculate_habitability_factor(planet)

        if population >= POPULATION_THRESHOLD:
            # Profitable colony: income based on population and habitability
            income = int(population * BASE_TAX_RATE * habitability / 100)
            return income
        else:
            # Small colony: maintenance cost
            population_ratio = population / POPULATION_THRESHOLD
            cost = int(COLONY_MAINTENANCE_COST * (1 - population_ratio))
            return -cost

    @staticmethod
    def calculate_player_income(player: GamePlayer) -> int:
        """
        Calculate total income for a player (sum of all planets).

        Args:
            player: GamePlayer instance

        Returns:
            Total income (can be negative if colonies cost more than they produce)
        """
        total_income = 0

        for planet in player.planets:
            total_income += EconomyService.calculate_planet_income(planet)

        return total_income

    @staticmethod
    def calculate_player_expenses(player: GamePlayer) -> Dict[str, int]:
        """
        Calculate detailed expenses breakdown for a player.

        Args:
            player: GamePlayer instance

        Returns:
            Dictionary with expense categories
        """
        colony_costs = 0
        colony_income = 0

        for planet in player.planets:
            income = EconomyService.calculate_planet_income(planet)
            if income > 0:
                colony_income += income
            else:
                colony_costs += abs(income)

        interest = EconomyService.calculate_interest(player)

        return {
            "colony_income": colony_income,
            "colony_costs": colony_costs,
            "debt_interest": interest,
            "net_income": colony_income - colony_costs - interest,
        }

    # -------------------------------------------------------------------------
    # Mining Calculations (US 3.2, US 3.3)
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_mining_output(
        planet: Planet,
        money_spent: int = 0
    ) -> int:
        """
        Calculate metal extraction with diminishing returns.

        Args:
            planet: Planet instance
            money_spent: Money allocated to mining (optional, uses budget if 0)

        Returns:
            Metal units that would be extracted (capped by remaining reserves)
        """
        if planet.metal_remaining <= 0:
            return 0

        if planet.state not in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
            return 0

        # Use planet's mining budget percentage
        budget_percentage = planet.mining_budget / 100.0

        # Calculate base output with diminishing returns
        base_output = BASE_MINING_RATE * (1 + planet.population / 100000)
        effective_output = diminishing_returns(budget_percentage, base_output)

        # Cap by remaining reserves
        metal_extracted = min(int(effective_output), planet.metal_remaining)

        return metal_extracted

    @staticmethod
    def process_planet_mining(planet: Planet) -> int:
        """
        Execute mining on a planet and update reserves.

        Args:
            planet: Planet instance

        Returns:
            Metal actually extracted
        """
        metal_extracted = EconomyService.calculate_mining_output(planet)

        if metal_extracted > 0:
            planet.metal_remaining -= metal_extracted
            planet.metal_remaining = max(0, planet.metal_remaining)

        return metal_extracted

    @staticmethod
    def process_player_mining(player: GamePlayer) -> Dict[str, any]:
        """
        Execute mining on all planets owned by a player.

        Args:
            player: GamePlayer instance

        Returns:
            Dictionary with mining results per planet and total
        """
        results = {
            "planets": {},
            "total_metal": 0,
        }

        for planet in player.planets:
            metal = EconomyService.process_planet_mining(planet)
            results["planets"][planet.id] = {
                "name": planet.name,
                "extracted": metal,
                "remaining": planet.metal_remaining,
            }
            results["total_metal"] += metal

        # Add to player's metal stock
        player.metal += results["total_metal"]

        return results

    # -------------------------------------------------------------------------
    # Debt System (US 3.4)
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_max_debt(player: GamePlayer) -> int:
        """
        Calculate maximum allowed debt (5x total income).

        Args:
            player: GamePlayer instance

        Returns:
            Maximum debt amount
        """
        income = EconomyService.calculate_player_income(player)

        # Only positive income counts for debt limit
        if income <= 0:
            return 0

        return income * DEBT_MAX_MULTIPLIER

    @staticmethod
    def calculate_interest(player: GamePlayer) -> int:
        """
        Calculate interest due on current debt.

        Args:
            player: GamePlayer instance

        Returns:
            Interest amount (15% of debt)
        """
        if player.debt <= 0:
            return 0

        return int(player.debt * DEBT_INTEREST_RATE)

    @staticmethod
    def borrow(player: GamePlayer, amount: int) -> Tuple[bool, str]:
        """
        Borrow money (take on debt).

        Args:
            player: GamePlayer instance
            amount: Amount to borrow

        Returns:
            Tuple of (success, message)
        """
        if amount <= 0:
            return False, "Amount must be positive"

        max_debt = EconomyService.calculate_max_debt(player)
        current_debt = player.debt

        if current_debt + amount > max_debt:
            available = max_debt - current_debt
            if available <= 0:
                return False, "Maximum debt limit reached"
            return False, f"Can only borrow {available} more (max debt: {max_debt})"

        player.debt += amount
        player.money += amount

        return True, f"Borrowed {amount}. New debt: {player.debt}"

    @staticmethod
    def repay_debt(player: GamePlayer, amount: int) -> Tuple[bool, str]:
        """
        Repay some or all debt.

        Args:
            player: GamePlayer instance
            amount: Amount to repay

        Returns:
            Tuple of (success, message)
        """
        if amount <= 0:
            return False, "Amount must be positive"

        if player.debt <= 0:
            return False, "No debt to repay"

        if amount > player.money:
            return False, f"Not enough money (have: {player.money})"

        # Cap repayment at current debt
        actual_repayment = min(amount, player.debt)

        player.money -= actual_repayment
        player.debt -= actual_repayment

        return True, f"Repaid {actual_repayment}. Remaining debt: {player.debt}"

    @staticmethod
    def process_interest(player: GamePlayer) -> int:
        """
        Calculate and deduct interest from player's money.

        Args:
            player: GamePlayer instance

        Returns:
            Interest amount deducted
        """
        interest = EconomyService.calculate_interest(player)

        if interest > 0:
            player.money -= interest
            # Money can go negative (player in financial trouble)

        return interest

    # -------------------------------------------------------------------------
    # Population Growth
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_population_growth(planet: Planet) -> int:
        """
        Calculate population growth for a planet.

        Growth depends on:
        - Current population
        - Habitability (temperature/gravity)
        - Available space (max_population)

        Args:
            planet: Planet instance

        Returns:
            Population change (can be negative for harsh conditions)
        """
        if planet.state not in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
            return 0

        if planet.population <= 0:
            return 0

        habitability = calculate_habitability_factor(planet)

        # Growth rate modified by habitability
        growth_rate = BASE_GROWTH_RATE * habitability

        # Logistic growth (slows as approaching max)
        capacity_factor = 1 - (planet.population / max(1, planet.max_population))
        capacity_factor = max(0, capacity_factor)

        effective_rate = growth_rate * capacity_factor

        # Calculate growth
        growth = int(planet.population * effective_rate)

        # Minimum growth of 100 for small colonies with good conditions
        if growth < 100 and habitability > 0.5 and planet.population < planet.max_population:
            growth = 100

        # Cap at max population
        new_population = planet.population + growth
        if new_population > planet.max_population:
            growth = planet.max_population - planet.population

        return growth

    @staticmethod
    def process_population_growth(planet: Planet) -> int:
        """
        Apply population growth to a planet.

        Args:
            planet: Planet instance

        Returns:
            Population change applied
        """
        growth = EconomyService.calculate_population_growth(planet)
        planet.population += growth
        planet.population = max(0, min(planet.population, planet.max_population))

        return growth

    # -------------------------------------------------------------------------
    # Terraformation (US 4.2)
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_terraform_change(planet: Planet) -> float:
        """
        Calculate temperature change from terraformation.

        Terraformation moves current_temperature towards IDEAL_TEMPERATURE (22°C).
        Uses diminishing returns based on terraform_budget.

        Args:
            planet: Planet instance

        Returns:
            Temperature change (positive = warming, negative = cooling)
        """
        if planet.state not in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
            return 0.0

        # Already at ideal temperature
        temp_diff = IDEAL_TEMPERATURE - planet.current_temperature
        if abs(temp_diff) < MIN_TERRAFORM_CHANGE:
            return 0.0

        # Use planet's terraform budget percentage
        budget_percentage = planet.terraform_budget / 100.0

        # Calculate base change with diminishing returns
        # More population = faster terraformation
        population_factor = 1 + (planet.population / 200000)
        base_change = BASE_TERRAFORM_RATE * population_factor
        effective_change = diminishing_returns(budget_percentage, base_change)

        # Direction: towards ideal temperature
        if temp_diff > 0:
            # Need to warm up
            change = min(effective_change, temp_diff)
        else:
            # Need to cool down
            change = max(-effective_change, temp_diff)

        return change

    @staticmethod
    def process_planet_terraformation(planet: Planet) -> dict:
        """
        Apply terraformation to a planet.

        Args:
            planet: Planet instance

        Returns:
            Dictionary with terraformation results
        """
        old_temp = planet.current_temperature
        old_max_pop = planet.max_population

        change = EconomyService.calculate_terraform_change(planet)

        if abs(change) >= MIN_TERRAFORM_CHANGE:
            planet.current_temperature += change
            # Recalculate max population based on new habitability
            planet.max_population = planet.calculate_max_population()

        return {
            "old_temperature": old_temp,
            "new_temperature": planet.current_temperature,
            "change": change,
            "old_max_population": old_max_pop,
            "new_max_population": planet.max_population,
        }

    @staticmethod
    def process_player_terraformation(player: GamePlayer) -> dict:
        """
        Apply terraformation to all planets owned by a player.

        Args:
            player: GamePlayer instance

        Returns:
            Dictionary with terraformation results per planet
        """
        results = {
            "planets": {},
            "total_temp_change": 0.0,
        }

        for planet in player.planets:
            if planet.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
                result = EconomyService.process_planet_terraformation(planet)
                results["planets"][planet.id] = {
                    "name": planet.name,
                    **result,
                }
                results["total_temp_change"] += abs(result["change"])

        return results

    # -------------------------------------------------------------------------
    # Planet Abandonment (US 4.7)
    # -------------------------------------------------------------------------

    @staticmethod
    def abandon_planet(planet: Planet, strip_mine: bool = True) -> dict:
        """
        Abandon a planet, optionally strip-mining remaining resources.

        Args:
            planet: Planet instance
            strip_mine: If True, extract all remaining metal before abandoning

        Returns:
            Dictionary with abandonment results
        """
        if planet.state not in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
            raise ValueError("Cannot abandon a planet that is not colonized")

        result = {
            "planet_id": planet.id,
            "planet_name": planet.name,
            "metal_recovered": 0,
            "population_lost": planet.population,
        }

        # Strip mine if requested
        if strip_mine and planet.metal_remaining > 0:
            # Recover 50% of remaining metal (rushed extraction is less efficient)
            result["metal_recovered"] = planet.metal_remaining // 2
            planet.metal_remaining = 0

        # Get the owner before clearing
        owner = planet.owner

        # Clear planet ownership and state
        planet.owner_id = None
        planet.state = PlanetState.ABANDONED.value
        planet.population = 0

        # Add recovered metal to player if owner exists
        if owner and result["metal_recovered"] > 0:
            owner.metal += result["metal_recovered"]

        # Update player's planet count
        if owner:
            owner.planet_count = len([p for p in owner.planets
                                      if p.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]])

        return result

    # -------------------------------------------------------------------------
    # Economic Summary
    # -------------------------------------------------------------------------

    @staticmethod
    def get_player_economy_summary(player: GamePlayer) -> Dict[str, any]:
        """
        Get complete economic summary for a player.

        Args:
            player: GamePlayer instance

        Returns:
            Dictionary with all economic data
        """
        income = EconomyService.calculate_player_income(player)
        expenses = EconomyService.calculate_player_expenses(player)
        max_debt = EconomyService.calculate_max_debt(player)
        interest = EconomyService.calculate_interest(player)

        planets_economy = []
        for planet in player.planets:
            planets_economy.append({
                "id": planet.id,
                "name": planet.name,
                "income": EconomyService.calculate_planet_income(planet),
                "mining_output": EconomyService.calculate_mining_output(planet),
                "ship_production_output": EconomyService.calculate_ship_production_output(planet),
                "metal_remaining": planet.metal_remaining,
                "population": planet.population,
                "max_population": planet.max_population,
                "habitability": round(planet.habitability, 2),
                "terraform_budget": planet.terraform_budget,
                "mining_budget": planet.mining_budget,
                "ships_budget": planet.ships_budget,
            })

        return {
            "money": player.money,
            "metal": player.metal,
            "debt": player.debt,
            "income": income,
            "expenses": expenses,
            "max_debt": max_debt,
            "interest_per_turn": interest,
            "can_borrow": max_debt - player.debt,
            "planets": planets_economy,
        }

    # -------------------------------------------------------------------------
    # Ship Production (US 6.4)
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_ship_production_output(planet: Planet) -> float:
        """
        Calculate ship production points with diminishing returns.

        Production depends on:
        - ships_budget percentage
        - Population (more pop = more workers)
        - Habitability

        Args:
            planet: Planet instance

        Returns:
            Production points generated this turn
        """
        if planet.state not in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
            return 0.0

        # Use planet's ships budget percentage
        budget_percentage = planet.ships_budget / 100.0 if planet.ships_budget else 0

        if budget_percentage <= 0:
            return 0.0

        # Population factor: more population = more production capacity
        population_mult = 1 + (planet.population / PRODUCTION_POPULATION_FACTOR)

        # Habitability affects productivity
        habitability_factor = 0.5 + (planet.habitability * 0.5)

        # Calculate base output with diminishing returns
        base_output = BASE_SHIP_PRODUCTION_RATE * population_mult * habitability_factor
        effective_output = diminishing_returns(budget_percentage, base_output)

        return effective_output

    @staticmethod
    def process_planet_ship_production(planet: Planet) -> dict:
        """
        Process ship production on a planet.

        1. Calculate production points generated
        2. Apply to first item in queue
        3. If ship is completed, create it and deduct resources
        4. Continue to next item if there's remaining production

        Args:
            planet: Planet instance

        Returns:
            Dictionary with production results
        """
        result = {
            "planet_id": planet.id,
            "planet_name": planet.name,
            "production_generated": 0.0,
            "ships_completed": [],
            "ships_in_progress": [],
        }

        production_points = EconomyService.calculate_ship_production_output(planet)
        result["production_generated"] = production_points

        if production_points <= 0:
            return result

        # Get queue items ordered by priority
        queue_items = planet.production_queue.filter_by(is_completed=False).order_by(
            ProductionQueue.priority
        ).all()

        if not queue_items:
            # No ships to build, accumulate points on planet
            planet.ship_production_points += production_points
            return result

        remaining_points = production_points

        for item in queue_items:
            if remaining_points <= 0:
                break

            # Check if player has resources for this ship
            player = planet.owner
            if not player:
                continue

            design = item.design
            if not design:
                continue

            # Determine cost (prototype vs production)
            if design.is_prototype_built:
                metal_cost = design.production_cost_metal
                money_cost = design.production_cost_money
            else:
                metal_cost = design.prototype_cost_metal
                money_cost = design.prototype_cost_money

            # Check resources before investing more production
            if player.metal < metal_cost or player.money < money_cost:
                result["ships_in_progress"].append({
                    "design_name": design.name,
                    "progress": item.production_progress,
                    "blocked": "insufficient_resources",
                })
                continue

            # Apply production points
            points_needed = item.production_required - item.production_invested
            points_to_apply = min(remaining_points, points_needed)
            item.production_invested += points_to_apply
            remaining_points -= points_to_apply

            # Check if ship is complete
            if item.is_ready:
                # Deduct resources
                player.metal -= metal_cost
                player.money -= money_cost

                # Create the ship
                ship = EconomyService._create_ship_from_queue(item)

                if ship:
                    item.is_completed = True
                    item.completed_at = datetime.utcnow()
                    design.ships_built += 1

                    if not design.is_prototype_built:
                        design.is_prototype_built = True

                    result["ships_completed"].append({
                        "design_name": design.name,
                        "ship_id": ship.id,
                        "fleet_id": ship.fleet_id,
                    })
            else:
                result["ships_in_progress"].append({
                    "design_name": design.name,
                    "progress": item.production_progress,
                })

        return result

    @staticmethod
    def _create_ship_from_queue(queue_item: ProductionQueue) -> Optional[Ship]:
        """
        Create a ship from a completed queue item.

        Args:
            queue_item: ProductionQueue instance

        Returns:
            Created Ship or None
        """
        design = queue_item.design
        fleet = queue_item.fleet

        # If no fleet specified, find or create one at this planet
        if not fleet:
            planet = queue_item.planet
            player = planet.owner

            if not player:
                return None

            # Find existing fleet at this planet
            fleet = Fleet.query.filter_by(
                player_id=player.id,
                current_planet_id=planet.id,
                status='stationed'
            ).first()

            # Create new fleet if none exists
            if not fleet:
                fleet = Fleet(
                    player_id=player.id,
                    name=f"Flotte de {planet.name}",
                    current_planet_id=planet.id,
                    status='stationed',
                )
                db.session.add(fleet)
                db.session.flush()

        # Create the ship
        ship = Ship(
            design_id=design.id,
            fleet_id=fleet.id,
        )
        db.session.add(ship)

        return ship

    @staticmethod
    def process_player_ship_production(player: GamePlayer) -> dict:
        """
        Process ship production on all planets owned by a player.

        Args:
            player: GamePlayer instance

        Returns:
            Dictionary with production results per planet
        """
        results = {
            "planets": {},
            "total_ships_completed": 0,
        }

        for planet in player.planets:
            if planet.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
                result = EconomyService.process_planet_ship_production(planet)
                results["planets"][planet.id] = result
                results["total_ships_completed"] += len(result["ships_completed"])

        return results

    @staticmethod
    def add_to_production_queue(
        planet: Planet,
        design_id: int,
        fleet_id: Optional[int] = None,
        count: int = 1
    ) -> Tuple[bool, str, List[ProductionQueue]]:
        """
        Add ships to a planet's production queue.

        Args:
            planet: Planet to build at
            design_id: Ship design to build
            fleet_id: Target fleet (optional)
            count: Number of ships to queue

        Returns:
            Tuple of (success, message, list of queue items)
        """
        from app.models import ShipDesign

        # Verify planet is owned and colonized
        if not planet.owner:
            return False, "Planet has no owner", []

        if planet.state not in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
            return False, "Planet is not colonized", []

        # Verify design belongs to planet owner
        design = ShipDesign.query.get(design_id)
        if not design:
            return False, "Design not found", []

        if design.player_id != planet.owner_id:
            return False, "Design does not belong to planet owner", []

        # Verify fleet if specified
        if fleet_id:
            fleet = Fleet.query.get(fleet_id)
            if not fleet:
                return False, "Fleet not found", []
            if fleet.player_id != planet.owner_id:
                return False, "Fleet does not belong to planet owner", []
            if fleet.current_planet_id != planet.id:
                return False, "Fleet is not at this planet", []

        # Get current max priority
        max_priority = db.session.query(db.func.max(ProductionQueue.priority)).filter_by(
            planet_id=planet.id,
            is_completed=False
        ).scalar() or 0

        # Add items to queue
        items = []
        for i in range(count):
            item = ProductionQueue(
                planet_id=planet.id,
                design_id=design_id,
                fleet_id=fleet_id,
                priority=max_priority + i + 1,
            )
            db.session.add(item)
            items.append(item)

        db.session.flush()

        return True, f"Added {count} ship(s) to production queue", items

    @staticmethod
    def remove_from_production_queue(queue_id: int) -> Tuple[bool, str]:
        """
        Remove an item from the production queue.

        Args:
            queue_id: ProductionQueue ID

        Returns:
            Tuple of (success, message)
        """
        item = ProductionQueue.query.get(queue_id)
        if not item:
            return False, "Queue item not found"

        if item.is_completed:
            return False, "Cannot remove completed item"

        db.session.delete(item)
        return True, "Item removed from queue"

    @staticmethod
    def reorder_production_queue(planet_id: int, queue_ids: List[int]) -> Tuple[bool, str]:
        """
        Reorder production queue items.

        Args:
            planet_id: Planet ID
            queue_ids: List of queue IDs in desired order

        Returns:
            Tuple of (success, message)
        """
        items = ProductionQueue.query.filter(
            ProductionQueue.id.in_(queue_ids),
            ProductionQueue.planet_id == planet_id,
            ProductionQueue.is_completed == False
        ).all()

        if len(items) != len(queue_ids):
            return False, "Some queue items not found"

        # Update priorities
        for i, queue_id in enumerate(queue_ids):
            for item in items:
                if item.id == queue_id:
                    item.priority = i
                    break

        return True, "Queue reordered"
