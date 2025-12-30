"""
Turn processing service.
Handles end-of-turn calculations and state updates.
"""
from datetime import datetime
from typing import Dict, List, Any

from app import db
from app.models import Game, GamePlayer, Planet, GameStatus, PlanetState
from app.services.economy import EconomyService


class TurnService:
    """Service for processing game turns."""

    @staticmethod
    def process_turn(game: Game) -> Dict[str, Any]:
        """
        Process end of turn for all players in a game.

        Order of operations:
        1. Calculate and apply income for all players
        2. Deduct debt interest
        3. Process mining on all planets
        4. Process terraformation (if implemented)
        5. Process population growth
        6. Check for eliminations
        7. Advance turn counter

        Args:
            game: Game instance

        Returns:
            Dictionary with turn results for all players
        """
        if game.status != GameStatus.RUNNING.value:
            raise ValueError("Game is not running")

        results = {
            "turn": game.current_turn,
            "year": game.current_year,
            "players": {},
            "eliminations": [],
        }

        # Process each player
        for player in game.players.filter_by(is_eliminated=False):
            player_result = TurnService.process_player_turn(player)
            results["players"][player.id] = player_result

            # Check for elimination (bankruptcy or no planets)
            if TurnService.check_elimination(player):
                results["eliminations"].append({
                    "player_id": player.id,
                    "player_name": player.player_name,
                    "reason": "bankruptcy" if player.money < -10000 else "no_planets",
                })

        # Advance turn
        game.current_turn += 1
        game.current_year += game.turn_duration_years

        # Reset turn submission flags
        for player in game.players:
            player.turn_submitted = False

        db.session.commit()

        # Add new turn info to results
        results["new_turn"] = game.current_turn
        results["new_year"] = game.current_year

        # Notify via WebSocket
        TurnService._notify_turn_end(game, results)

        return results

    @staticmethod
    def process_player_turn(player: GamePlayer) -> Dict[str, Any]:
        """
        Process end of turn for a single player.

        Args:
            player: GamePlayer instance

        Returns:
            Dictionary with player's turn results
        """
        result = {
            "player_id": player.id,
            "player_name": player.player_name,
            "before": {
                "money": player.money,
                "metal": player.metal,
                "debt": player.debt,
            },
            "income": 0,
            "interest": 0,
            "mining": {"total": 0, "planets": {}},
            "population_growth": {"total": 0, "planets": {}},
            "after": {},
        }

        # 1. Calculate and apply income
        income = EconomyService.calculate_player_income(player)
        player.money += income
        result["income"] = income

        # 2. Deduct debt interest
        interest = EconomyService.process_interest(player)
        result["interest"] = interest

        # 3. Process mining on all planets
        for planet in player.planets:
            if planet.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
                metal_extracted = EconomyService.process_planet_mining(planet)
                result["mining"]["planets"][planet.id] = {
                    "name": planet.name,
                    "extracted": metal_extracted,
                    "remaining": planet.metal_remaining,
                }
                result["mining"]["total"] += metal_extracted

        # Add mined metal to player stock
        player.metal += result["mining"]["total"]

        # 4. Process terraformation
        terraformation_results = EconomyService.process_player_terraformation(player)
        result["terraformation"] = terraformation_results

        # 5. Process population growth on all planets
        for planet in player.planets:
            if planet.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]:
                growth = EconomyService.process_population_growth(planet)
                result["population_growth"]["planets"][planet.id] = {
                    "name": planet.name,
                    "growth": growth,
                    "population": planet.population,
                }
                result["population_growth"]["total"] += growth

        # Update planet count
        player.planet_count = len([p for p in player.planets
                                   if p.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]])

        # Record final state
        result["after"] = {
            "money": player.money,
            "metal": player.metal,
            "debt": player.debt,
            "planet_count": player.planet_count,
        }

        return result

    @staticmethod
    def check_elimination(player: GamePlayer) -> bool:
        """
        Check if a player should be eliminated.

        Elimination conditions:
        - Severe bankruptcy (money < -10000)
        - No planets remaining

        Args:
            player: GamePlayer instance

        Returns:
            True if player should be eliminated
        """
        # Already eliminated
        if player.is_eliminated:
            return False

        # Check bankruptcy
        if player.money < -10000:
            TurnService._eliminate_player(player, "bankruptcy")
            return True

        # Check no planets
        owned_planets = [p for p in player.planets
                        if p.state in [PlanetState.COLONIZED.value, PlanetState.DEVELOPED.value]]
        if len(owned_planets) == 0:
            TurnService._eliminate_player(player, "no_planets")
            return True

        return False

    @staticmethod
    def _eliminate_player(player: GamePlayer, reason: str):
        """
        Mark a player as eliminated.

        Args:
            player: GamePlayer instance
            reason: Reason for elimination
        """
        player.is_eliminated = True
        player.is_active = False
        player.eliminated_at = datetime.utcnow()

        # Release all planets
        for planet in player.planets:
            planet.owner_id = None
            planet.state = PlanetState.ABANDONED.value

    @staticmethod
    def submit_turn(game_id: int, player_id: int) -> bool:
        """
        Mark a player as having submitted their turn.

        Args:
            game_id: Game ID
            player_id: Player ID

        Returns:
            True if all players have submitted (turn should process)
        """
        player = GamePlayer.query.filter_by(
            game_id=game_id,
            id=player_id,
            is_eliminated=False
        ).first()

        if not player:
            raise ValueError("Player not found or eliminated")

        player.turn_submitted = True
        db.session.commit()

        # Check if all players have submitted
        return TurnService.all_players_submitted(game_id)

    @staticmethod
    def all_players_submitted(game_id: int) -> bool:
        """
        Check if all active players have submitted their turn.

        Args:
            game_id: Game ID

        Returns:
            True if all players have submitted
        """
        game = Game.query.get(game_id)
        if not game:
            return False

        active_players = game.players.filter_by(is_eliminated=False).all()

        for player in active_players:
            # AI players are always "submitted"
            if player.is_ai:
                continue
            if not player.turn_submitted:
                return False

        return True

    @staticmethod
    def get_turn_status(game_id: int) -> Dict[str, Any]:
        """
        Get current turn status for a game.

        Args:
            game_id: Game ID

        Returns:
            Dictionary with turn status info
        """
        game = Game.query.get(game_id)
        if not game:
            raise ValueError("Game not found")

        players_status = []
        for player in game.players.filter_by(is_eliminated=False):
            players_status.append({
                "id": player.id,
                "name": player.player_name,
                "is_ai": player.is_ai,
                "submitted": player.turn_submitted or player.is_ai,
            })

        return {
            "game_id": game.id,
            "current_turn": game.current_turn,
            "current_year": game.current_year,
            "all_submitted": TurnService.all_players_submitted(game_id),
            "players": players_status,
        }

    @staticmethod
    def _notify_turn_end(game: Game, results: Dict[str, Any]):
        """
        Send WebSocket notification for turn end.

        Args:
            game: Game instance
            results: Turn results
        """
        try:
            from app.websocket import emit_turn_end
            emit_turn_end(game.id, {
                "turn": results["new_turn"],
                "year": results["new_year"],
                "eliminations": results["eliminations"],
            })
        except Exception as e:
            print(f"[WS] Failed to emit turn_end: {e}")

    @staticmethod
    def check_victory(game: Game) -> Dict[str, Any]:
        """
        Check if there's a winner.

        Victory condition: Only one player remaining

        Args:
            game: Game instance

        Returns:
            Dictionary with victory info (empty if no winner)
        """
        active_players = game.players.filter_by(is_eliminated=False).all()

        if len(active_players) == 1:
            winner = active_players[0]
            game.status = GameStatus.FINISHED.value
            game.finished_at = datetime.utcnow()
            db.session.commit()

            return {
                "winner": {
                    "id": winner.id,
                    "name": winner.player_name,
                    "is_ai": winner.is_ai,
                },
                "final_turn": game.current_turn,
                "final_year": game.current_year,
            }

        if len(active_players) == 0:
            # Draw - everyone eliminated
            game.status = GameStatus.FINISHED.value
            game.finished_at = datetime.utcnow()
            db.session.commit()

            return {
                "winner": None,
                "draw": True,
                "final_turn": game.current_turn,
                "final_year": game.current_year,
            }

        return {}
