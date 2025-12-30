"""
Game management service.
Handles game creation, player management, and game lifecycle.
"""
from datetime import datetime
from typing import List, Optional

from app import db
from app.models import Game, GamePlayer, GameStatus, AIDifficulty
from app.data import get_random_ai_name, get_player_color, AI_NAMES
from app.services.galaxy_generator import generate_galaxy, find_home_planets, prepare_home_planet


def _notify_lobby_update(game: Game):
    """Helper to emit lobby update via WebSocket."""
    try:
        from app.websocket import emit_lobby_update
        players = [player.to_dict() for player in game.players]
        emit_lobby_update(game.id, players)
    except Exception as e:
        print(f"[WS] Failed to emit lobby_update: {e}")


class GameService:
    """Service for managing games."""

    # Initial resources for players
    INITIAL_MONEY = 10000
    INITIAL_METAL = 500

    @staticmethod
    def create_game(
        creator_id: int,
        name: str,
        galaxy_shape: str = "random",
        galaxy_size: str = "medium",
        galaxy_density: str = "medium",
        max_players: int = 8,
        turn_duration_years: int = 10,
        alliances_enabled: bool = True,
        combat_luck_enabled: bool = True,
    ) -> Game:
        """
        Create a new game and add the creator as the first player.

        Args:
            creator_id: User ID of the game creator
            name: Name of the game
            galaxy_shape: Shape of the galaxy
            galaxy_size: Size preset (small, medium, large, huge)
            galaxy_density: Star density
            max_players: Maximum number of players (2-8)
            turn_duration_years: Years per turn
            alliances_enabled: Whether alliances are allowed
            combat_luck_enabled: Whether combat has random factor

        Returns:
            Created Game instance
        """
        from app.models import User

        # Validate max_players
        max_players = max(2, min(8, max_players))

        # Get creator info
        creator = User.query.get(creator_id)
        if not creator:
            raise ValueError("Creator not found")

        # Create game
        game = Game(
            name=name,
            status=GameStatus.LOBBY.value,
            galaxy_shape=galaxy_shape,
            star_count={"small": 20, "medium": 50, "large": 100, "huge": 200}.get(galaxy_size, 50),
            density={"low": 0.7, "medium": 1.0, "high": 1.3}.get(galaxy_density, 1.0),
            max_players=max_players,
            turn_duration_years=turn_duration_years,
            alliances_enabled=alliances_enabled,
            combat_luck_enabled=combat_luck_enabled,
            admin_user_id=creator_id,
        )
        db.session.add(game)
        db.session.flush()  # Get game ID

        # Add creator as first player
        player = GamePlayer(
            game_id=game.id,
            user_id=creator_id,
            player_name=creator.pseudo,
            color=get_player_color(0),
            is_ai=False,
            money=GameService.INITIAL_MONEY,
            metal=GameService.INITIAL_METAL,
        )
        db.session.add(player)
        db.session.commit()

        return game

    @staticmethod
    def join_game(game_id: int, user_id: int) -> GamePlayer:
        """
        Add a human player to a game.

        Args:
            game_id: ID of the game to join
            user_id: ID of the user joining

        Returns:
            Created GamePlayer instance

        Raises:
            ValueError: If game is full, started, or user already in game
        """
        from app.models import User

        game = Game.query.get(game_id)
        if not game:
            raise ValueError("Game not found")

        if game.status != GameStatus.LOBBY.value:
            raise ValueError("Game has already started")

        # Check if game is full
        current_players = game.players.count()
        if current_players >= game.max_players:
            raise ValueError("Game is full")

        # Check if user is already in game
        existing = GamePlayer.query.filter_by(game_id=game_id, user_id=user_id).first()
        if existing:
            raise ValueError("Already in this game")

        # Get user info
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        # Create player
        player = GamePlayer(
            game_id=game_id,
            user_id=user_id,
            player_name=user.pseudo,
            color=get_player_color(current_players),
            is_ai=False,
            money=GameService.INITIAL_MONEY,
            metal=GameService.INITIAL_METAL,
        )
        db.session.add(player)
        db.session.commit()

        # Notify lobby via WebSocket
        _notify_lobby_update(game)

        return player

    @staticmethod
    def leave_game(game_id: int, user_id: int) -> bool:
        """
        Remove a player from a game lobby.

        Args:
            game_id: ID of the game
            user_id: ID of the user leaving

        Returns:
            True if successful

        Raises:
            ValueError: If game started or user is admin
        """
        game = Game.query.get(game_id)
        if not game:
            raise ValueError("Game not found")

        if game.status != GameStatus.LOBBY.value:
            raise ValueError("Cannot leave a started game")

        # Admin cannot leave (must delete game)
        if game.admin_user_id == user_id:
            raise ValueError("Game admin cannot leave. Delete the game instead.")

        player = GamePlayer.query.filter_by(game_id=game_id, user_id=user_id).first()
        if not player:
            raise ValueError("Not in this game")

        db.session.delete(player)
        db.session.commit()

        # Notify lobby via WebSocket
        _notify_lobby_update(game)

        return True

    @staticmethod
    def add_ai_player(
        game_id: int,
        difficulty: str = "medium",
        name: Optional[str] = None,
    ) -> GamePlayer:
        """
        Add an AI player to a game.

        Args:
            game_id: ID of the game
            difficulty: AI difficulty level
            name: Optional custom name for the AI

        Returns:
            Created GamePlayer instance
        """
        game = Game.query.get(game_id)
        if not game:
            raise ValueError("Game not found")

        if game.status != GameStatus.LOBBY.value:
            raise ValueError("Game has already started")

        current_players = game.players.count()
        if current_players >= game.max_players:
            raise ValueError("Game is full")

        # Get used AI names
        used_names = {p.player_name for p in game.players if p.is_ai}

        # Generate or validate name
        if not name:
            name = get_random_ai_name(used_names)

        # Create AI player
        player = GamePlayer(
            game_id=game_id,
            user_id=None,  # No user for AI
            player_name=name,
            color=get_player_color(current_players),
            is_ai=True,
            ai_difficulty=difficulty,
            is_ready=True,  # AI is always ready
            money=GameService.INITIAL_MONEY,
            metal=GameService.INITIAL_METAL,
        )
        db.session.add(player)
        db.session.commit()

        # Notify lobby via WebSocket
        _notify_lobby_update(game)

        return player

    @staticmethod
    def remove_ai_player(game_id: int, player_id: int) -> bool:
        """
        Remove an AI player from a game.

        Args:
            game_id: ID of the game
            player_id: ID of the AI player to remove

        Returns:
            True if successful
        """
        player = GamePlayer.query.filter_by(id=player_id, game_id=game_id, is_ai=True).first()
        if not player:
            raise ValueError("AI player not found")

        game = Game.query.get(game_id)
        if game.status != GameStatus.LOBBY.value:
            raise ValueError("Cannot modify players in a started game")

        db.session.delete(player)
        db.session.commit()

        # Notify lobby via WebSocket
        _notify_lobby_update(game)

        return True

    @staticmethod
    def set_player_ready(game_id: int, user_id: int, ready: bool = True) -> GamePlayer:
        """
        Set a player's ready status.

        Args:
            game_id: ID of the game
            user_id: ID of the user
            ready: Ready status

        Returns:
            Updated GamePlayer instance
        """
        player = GamePlayer.query.filter_by(game_id=game_id, user_id=user_id).first()
        if not player:
            raise ValueError("Player not found")

        player.is_ready = ready
        db.session.commit()

        # Notify lobby via WebSocket
        game = Game.query.get(game_id)
        if game:
            _notify_lobby_update(game)

        return player

    @staticmethod
    def start_game(game_id: int, admin_user_id: int) -> Game:
        """
        Start a game - generate galaxy and assign home planets.

        Args:
            game_id: ID of the game to start
            admin_user_id: ID of the user starting the game (must be admin)

        Returns:
            Updated Game instance
        """
        game = Game.query.get(game_id)
        if not game:
            raise ValueError("Game not found")

        if game.admin_user_id != admin_user_id:
            raise ValueError("Only the game admin can start the game")

        if game.status != GameStatus.LOBBY.value:
            raise ValueError("Game has already started")

        # Check minimum players
        player_count = game.players.count()
        if player_count < 2:
            raise ValueError("Need at least 2 players to start")

        # Check all human players are ready
        human_players = game.players.filter_by(is_ai=False).all()
        for player in human_players:
            if not player.is_ready and player.user_id != admin_user_id:
                raise ValueError("Not all players are ready")

        # Determine galaxy size from star_count
        size_map = {20: "small", 50: "medium", 100: "large", 200: "huge"}
        galaxy_size = size_map.get(game.star_count, "medium")

        # Determine density from float
        density_map = {0.7: "low", 1.0: "medium", 1.3: "high"}
        galaxy_density = min(density_map.keys(), key=lambda x: abs(x - game.density))
        galaxy_density = density_map[galaxy_density]

        # Generate galaxy
        galaxy = generate_galaxy(
            game_id=game.id,
            shape=game.galaxy_shape,
            size=galaxy_size,
            density=galaxy_density,
        )

        # Find and assign home planets
        players = list(game.players.all())
        home_planets = find_home_planets(galaxy, len(players))

        for player, planet in zip(players, home_planets):
            # Prepare the planet as a home world
            prepare_home_planet(planet)
            planet.owner_id = player.id

            # Update player
            player.home_planet_id = planet.id
            player.planet_count = 1

        # Update game status
        game.status = GameStatus.RUNNING.value
        game.started_at = datetime.utcnow()
        game.current_turn = 1

        db.session.commit()

        # Notify all players via WebSocket that game has started
        try:
            from app.websocket import emit_game_started
            game_data = game.to_dict()
            game_data["players"] = [p.to_dict() for p in game.players]
            emit_game_started(game.id, game_data)
        except Exception as e:
            print(f"[WS] Failed to emit game_started: {e}")

        return game

    @staticmethod
    def delete_game(game_id: int, admin_user_id: int) -> bool:
        """
        Delete a game (only in lobby status).

        Args:
            game_id: ID of the game
            admin_user_id: ID of the admin user

        Returns:
            True if successful
        """
        game = Game.query.get(game_id)
        if not game:
            raise ValueError("Game not found")

        if game.admin_user_id != admin_user_id:
            raise ValueError("Only the game admin can delete the game")

        if game.status not in [GameStatus.LOBBY.value, GameStatus.ABANDONED.value]:
            raise ValueError("Cannot delete a game in progress")

        # Delete all players first
        GamePlayer.query.filter_by(game_id=game_id).delete()

        # Delete galaxy if exists
        if game.galaxy:
            db.session.delete(game.galaxy)

        # Delete game
        db.session.delete(game)
        db.session.commit()

        return True

    @staticmethod
    def update_game(
        game_id: int,
        admin_user_id: int,
        name: Optional[str] = None,
        galaxy_shape: Optional[str] = None,
        galaxy_size: Optional[str] = None,
        galaxy_density: Optional[str] = None,
        max_players: Optional[int] = None,
        turn_duration_years: Optional[int] = None,
        alliances_enabled: Optional[bool] = None,
        combat_luck_enabled: Optional[bool] = None,
    ) -> Game:
        """
        Update game configuration (only in lobby).

        Args:
            game_id: ID of the game to update
            admin_user_id: ID of the user (must be admin)
            name: New game name (optional)
            galaxy_shape: New galaxy shape (optional)
            galaxy_size: New galaxy size preset (optional)
            galaxy_density: New density preset (optional)
            max_players: New max players (optional)
            turn_duration_years: New turn duration (optional)
            alliances_enabled: New alliance setting (optional)
            combat_luck_enabled: New combat luck setting (optional)

        Returns:
            Updated Game instance

        Raises:
            ValueError: If game not found, user not admin, or game started
        """
        game = Game.query.get(game_id)
        if not game:
            raise ValueError("Game not found")

        if game.admin_user_id != admin_user_id:
            raise ValueError("Only the game admin can modify the game")

        if game.status != GameStatus.LOBBY.value:
            raise ValueError("Cannot modify a game that has started")

        # Update fields if provided
        if name is not None:
            game.name = name

        if galaxy_shape is not None:
            game.galaxy_shape = galaxy_shape

        if galaxy_size is not None:
            game.star_count = {"small": 20, "medium": 50, "large": 100, "huge": 200}.get(galaxy_size, 50)

        if galaxy_density is not None:
            game.density = {"low": 0.7, "medium": 1.0, "high": 1.3}.get(galaxy_density, 1.0)

        if max_players is not None:
            # Ensure max_players is valid and >= current player count
            current_players = game.players.count()
            new_max = max(2, min(8, max_players))
            if new_max < current_players:
                raise ValueError(f"Cannot reduce max_players below current player count ({current_players})")
            game.max_players = new_max

        if turn_duration_years is not None:
            game.turn_duration_years = max(10, min(100, turn_duration_years))

        if alliances_enabled is not None:
            game.alliances_enabled = alliances_enabled

        if combat_luck_enabled is not None:
            game.combat_luck_enabled = combat_luck_enabled

        db.session.commit()

        # Notify lobby via WebSocket
        _notify_lobby_update(game)

        return game

    @staticmethod
    def get_lobby_games() -> List[Game]:
        """Get all games in lobby status."""
        return Game.query.filter_by(status=GameStatus.LOBBY.value).order_by(Game.created_at.desc()).all()

    @staticmethod
    def get_game_details(game_id: int) -> Optional[Game]:
        """Get game with all details."""
        return Game.query.get(game_id)
