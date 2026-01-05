"""
Game State Analysis for AI decision making.

This module provides comprehensive analysis of the current game state,
identifying opportunities, threats, and strategic situations.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math

from app.models import (
    GamePlayer, Planet, Fleet, Game,
    PlanetState, FleetStatus, ShipType,
)


class GamePhase(str, Enum):
    """Game phase based on turn and situation."""
    EARLY = "early"      # Turns 0-20: Exploration and colonization
    MID = "mid"          # Turns 20-50: Expansion and conflict
    LATE = "late"        # Turns 50+: Resource scarcity and endgame


@dataclass
class ThreatInfo:
    """Information about an incoming threat."""
    fleet: Fleet
    target_planet: Planet
    arrival_turn: int
    estimated_power: float


@dataclass
class OpportunityInfo:
    """Information about an attack opportunity."""
    target_planet: Planet
    owner_id: Optional[int]
    defense_power: float
    value_score: float
    distance: float


@dataclass
class ColonizationTarget:
    """Information about a potential colonization target."""
    planet: Planet
    value_score: float
    distance: float
    travel_turns: int


@dataclass
class GameAnalysis:
    """
    Comprehensive analysis of the game state from a player's perspective.

    This class encapsulates all the information an AI needs to make decisions.
    """
    # Reference info
    player_id: int
    game_id: int
    current_turn: int

    # Game phase
    phase: GamePhase = GamePhase.EARLY

    # Economic situation
    money: int = 0
    metal: int = 0
    debt: int = 0
    income: int = 0
    metal_production: int = 0
    debt_ratio: float = 0.0  # debt / income

    # Planet counts
    my_planet_count: int = 0
    total_planets: int = 0
    colonizable_planets_count: int = 0

    # Military power
    my_fleet_power: float = 0.0
    my_ship_count: int = 0
    enemy_fleet_powers: Dict[int, float] = field(default_factory=dict)
    military_advantage: float = 1.0  # my_power / avg_enemy_power

    # Technology comparison
    my_tech_total: int = 0
    enemy_tech_comparison: Dict[int, str] = field(default_factory=dict)  # "ahead", "behind", "equal"

    # Strategic lists
    my_planets: List[Planet] = field(default_factory=list)
    vulnerable_planets: List[Planet] = field(default_factory=list)  # My planets at risk
    colonizable_planets: List[ColonizationTarget] = field(default_factory=list)
    attack_opportunities: List[OpportunityInfo] = field(default_factory=list)
    incoming_threats: List[ThreatInfo] = field(default_factory=list)

    # Fleet info
    my_fleets: List[Fleet] = field(default_factory=list)
    available_fleets: List[Fleet] = field(default_factory=list)  # Stationed, not empty
    fleets_in_transit: List[Fleet] = field(default_factory=list)

    # Resource scarcity indicators
    metal_scarcity: float = 0.0  # 0 = abundant, 1 = critical
    needs_expansion: bool = False

    @classmethod
    def analyze(cls, player: GamePlayer) -> "GameAnalysis":
        """
        Perform complete analysis of game state for a player.

        Args:
            player: The GamePlayer to analyze for

        Returns:
            Complete GameAnalysis instance
        """
        game = player.game
        analysis = cls(
            player_id=player.id,
            game_id=game.id,
            current_turn=game.current_turn,
        )

        # Determine game phase
        analysis.phase = cls._determine_phase(game)

        # Economic analysis
        analysis._analyze_economy(player)

        # Military analysis
        analysis._analyze_military(player, game)

        # Technology analysis
        analysis._analyze_technology(player, game)

        # Strategic analysis
        analysis._analyze_planets(player, game)
        analysis._analyze_threats(player, game)
        analysis._analyze_opportunities(player, game)

        # Resource scarcity
        analysis._analyze_scarcity(player, game)

        return analysis

    @staticmethod
    def _determine_phase(game: Game) -> GamePhase:
        """Determine current game phase based on turn and situation."""
        turn = game.current_turn

        if turn < 20:
            return GamePhase.EARLY
        elif turn < 50:
            return GamePhase.MID
        else:
            return GamePhase.LATE

    def _analyze_economy(self, player: GamePlayer):
        """Analyze player's economic situation."""
        self.money = player.money
        self.metal = player.metal
        self.debt = player.debt

        # Calculate income from planets
        income = 0
        metal_prod = 0
        for planet in player.planets:
            if planet.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
                # Estimate income based on population
                income += max(0, planet.population // 1000 - 50)
                # Estimate metal production
                if planet.metal_remaining > 0:
                    metal_prod += min(planet.metal_remaining, 100)

        self.income = income
        self.metal_production = metal_prod
        self.debt_ratio = self.debt / max(1, self.income)

    def _analyze_military(self, player: GamePlayer, game: Game):
        """Analyze military situation."""
        # My fleets
        self.my_fleets = list(player.fleets.all())
        self.my_fleet_power = 0.0
        self.my_ship_count = 0

        for fleet in self.my_fleets:
            self.my_fleet_power += fleet.total_weapons + fleet.total_shields
            self.my_ship_count += fleet.ship_count

            if fleet.status == FleetStatus.STATIONED.value and not fleet.is_empty:
                self.available_fleets.append(fleet)
            elif fleet.status == FleetStatus.IN_TRANSIT.value:
                self.fleets_in_transit.append(fleet)

        # Enemy fleet powers
        total_enemy_power = 0.0
        enemy_count = 0

        for other_player in game.players.filter_by(is_eliminated=False):
            if other_player.id == player.id:
                continue

            enemy_power = 0.0
            for fleet in other_player.fleets:
                enemy_power += fleet.total_weapons + fleet.total_shields

            self.enemy_fleet_powers[other_player.id] = enemy_power
            total_enemy_power += enemy_power
            enemy_count += 1

        # Calculate military advantage
        if enemy_count > 0 and total_enemy_power > 0:
            avg_enemy_power = total_enemy_power / enemy_count
            self.military_advantage = self.my_fleet_power / max(1, avg_enemy_power)
        else:
            self.military_advantage = float('inf') if self.my_fleet_power > 0 else 1.0

    def _analyze_technology(self, player: GamePlayer, game: Game):
        """Analyze technology situation."""
        tech = player.technology
        if not tech:
            return

        self.my_tech_total = (
            tech.range_level +
            tech.speed_level +
            tech.weapons_level +
            tech.shields_level +
            tech.mini_level
        )

        # Compare with other players
        for other_player in game.players.filter_by(is_eliminated=False):
            if other_player.id == player.id:
                continue

            other_tech = other_player.technology
            if not other_tech:
                continue

            other_total = (
                other_tech.range_level +
                other_tech.speed_level +
                other_tech.weapons_level +
                other_tech.shields_level +
                other_tech.mini_level
            )

            diff = self.my_tech_total - other_total
            if diff > 2:
                self.enemy_tech_comparison[other_player.id] = "ahead"
            elif diff < -2:
                self.enemy_tech_comparison[other_player.id] = "behind"
            else:
                self.enemy_tech_comparison[other_player.id] = "equal"

    def _analyze_planets(self, player: GamePlayer, game: Game):
        """Analyze planet situation."""
        galaxy = game.galaxy
        if not galaxy:
            return

        self.my_planets = []
        colonizable = []
        home_planet = player.home_planet

        for planet in galaxy.planets:
            self.total_planets += 1

            # My planets
            if planet.owner_id == player.id:
                self.my_planet_count += 1
                self.my_planets.append(planet)
            # Colonizable planets (unowned, not already colonized)
            elif planet.owner_id is None and planet.state not in [
                PlanetState.COLONIZED.value,
                PlanetState.DEVELOPED.value,
                PlanetState.HOSTILE.value
            ]:
                value = self._evaluate_planet_value(planet)
                distance = self._calculate_distance(home_planet, planet) if home_planet else 100

                # Estimate travel turns (assuming average speed of 3)
                travel_turns = int(distance / 3) + 1

                colonizable.append(ColonizationTarget(
                    planet=planet,
                    value_score=value,
                    distance=distance,
                    travel_turns=travel_turns,
                ))

        # Sort colonizable by value/distance ratio
        colonizable.sort(key=lambda t: t.value_score / max(1, t.distance), reverse=True)
        self.colonizable_planets = colonizable[:10]  # Top 10
        self.colonizable_planets_count = len(colonizable)

    def _analyze_threats(self, player: GamePlayer, game: Game):
        """Identify incoming threats to player's planets."""
        for other_player in game.players.filter_by(is_eliminated=False):
            if other_player.id == player.id:
                continue

            for fleet in other_player.fleets:
                # Check if fleet is heading to one of my planets
                if fleet.status == FleetStatus.IN_TRANSIT.value and fleet.destination_planet_id:
                    dest_planet = fleet.destination_planet
                    if dest_planet and dest_planet.owner_id == player.id:
                        threat = ThreatInfo(
                            fleet=fleet,
                            target_planet=dest_planet,
                            arrival_turn=fleet.arrival_turn or (game.current_turn + 1),
                            estimated_power=fleet.total_weapons + fleet.total_shields,
                        )
                        self.incoming_threats.append(threat)
                        if dest_planet not in self.vulnerable_planets:
                            self.vulnerable_planets.append(dest_planet)

        # Sort threats by arrival time
        self.incoming_threats.sort(key=lambda t: t.arrival_turn)

    def _analyze_opportunities(self, player: GamePlayer, game: Game):
        """Identify attack opportunities."""
        galaxy = game.galaxy
        if not galaxy:
            return

        home_planet = player.home_planet
        opportunities = []

        for planet in galaxy.planets:
            # Skip my own planets
            if planet.owner_id == player.id:
                continue

            # Skip unexplored planets
            if planet.state == PlanetState.UNEXPLORED.value:
                continue

            # Calculate defense power
            defense_power = 0.0

            # Satellites and stationed fleets
            for fleet in planet.stationed_fleets:
                if fleet.player_id != player.id:
                    defense_power += fleet.total_weapons + fleet.total_shields

            # Population defense
            if planet.owner_id and planet.population > 0:
                defense_power += planet.population / 10000  # 1 power per 10k pop

            # Calculate value
            value = self._evaluate_planet_value(planet)
            if planet.owner_id:
                value *= 1.5  # Bonus for taking enemy planet

            distance = self._calculate_distance(home_planet, planet) if home_planet else 100

            opportunity = OpportunityInfo(
                target_planet=planet,
                owner_id=planet.owner_id,
                defense_power=defense_power,
                value_score=value,
                distance=distance,
            )
            opportunities.append(opportunity)

        # Sort by value/defense ratio (best opportunities first)
        opportunities.sort(
            key=lambda o: o.value_score / max(1, o.defense_power + o.distance),
            reverse=True
        )
        self.attack_opportunities = opportunities[:15]  # Top 15

    def _analyze_scarcity(self, player: GamePlayer, game: Game):
        """Analyze resource scarcity situation."""
        # Metal scarcity based on remaining reserves
        total_remaining = 0
        total_initial = 0

        for planet in player.planets:
            total_remaining += planet.metal_remaining
            total_initial += planet.metal_reserves

        if total_initial > 0:
            self.metal_scarcity = 1.0 - (total_remaining / total_initial)
        else:
            self.metal_scarcity = 1.0 if self.metal < 100 else 0.5

        # Need expansion if few planets or declining income
        self.needs_expansion = (
            self.my_planet_count < 3 or
            self.colonizable_planets_count > 0 and self.my_planet_count < 5 or
            self.metal_scarcity > 0.7
        )

    @staticmethod
    def _evaluate_planet_value(planet: Planet) -> float:
        """
        Calculate the strategic value of a planet (0-100).

        Factors:
        - Temperature proximity to 22C (ideal)
        - Gravity proximity to 1.0g
        - Metal reserves
        - Population (if colonized)
        """
        score = 0.0

        # Temperature factor (40 points max)
        temp_diff = abs(planet.current_temperature - 22)
        score += max(0, 40 - temp_diff)

        # Gravity factor (20 points max)
        grav_diff = abs(planet.gravity - 1.0)
        score += max(0, 20 - grav_diff * 20)

        # Metal factor (25 points max)
        score += min(25, planet.metal_remaining / 1000)

        # Population bonus (15 points max)
        if planet.population > 0:
            score += min(15, planet.population / 100000)

        return score

    @staticmethod
    def _calculate_distance(p1: Optional[Planet], p2: Planet) -> float:
        """Calculate distance between two planets."""
        if not p1:
            return 100.0

        dx = p1.x - p2.x
        dy = p1.y - p2.y
        return math.sqrt(dx * dx + dy * dy)

    def get_summary(self) -> Dict:
        """Get a summary of the analysis for logging/debugging."""
        return {
            "phase": self.phase.value,
            "economy": {
                "money": self.money,
                "metal": self.metal,
                "debt": self.debt,
                "income": self.income,
            },
            "military": {
                "fleet_power": round(self.my_fleet_power, 1),
                "ship_count": self.my_ship_count,
                "advantage": round(self.military_advantage, 2),
            },
            "planets": {
                "owned": self.my_planet_count,
                "colonizable": len(self.colonizable_planets),
            },
            "threats": len(self.incoming_threats),
            "opportunities": len(self.attack_opportunities),
            "metal_scarcity": round(self.metal_scarcity, 2),
            "needs_expansion": self.needs_expansion,
        }
