"""
Game management routes
"""
from flask import request, jsonify, g
from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.routes import api_bp
from app.services.auth import token_required
from app.services import GameService
from app.models import Game, GameStatus


# Pydantic schemas for validation
class CreateGameSchema(BaseModel):
    """Schema for creating a new game."""
    name: str = Field(min_length=3, max_length=100)
    galaxy_shape: Literal["circle", "spiral", "cluster", "random"] = "random"
    galaxy_size: Literal["small", "medium", "large", "huge"] = "medium"
    galaxy_density: Literal["low", "medium", "high"] = "medium"
    max_players: int = Field(default=8, ge=2, le=8)
    turn_duration_years: int = Field(default=10, ge=10, le=100)
    alliances_enabled: bool = True
    combat_luck_enabled: bool = True


class AddAISchema(BaseModel):
    """Schema for adding an AI player."""
    difficulty: Literal["easy", "medium", "hard", "expert"] = "medium"
    name: Optional[str] = Field(default=None, max_length=50)


class SetReadySchema(BaseModel):
    """Schema for setting ready status."""
    ready: bool = True


class UpdateGameSchema(BaseModel):
    """Schema for updating game configuration."""
    name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    galaxy_shape: Optional[Literal["circle", "spiral", "cluster", "random"]] = None
    galaxy_size: Optional[Literal["small", "medium", "large", "huge"]] = None
    galaxy_density: Optional[Literal["low", "medium", "high"]] = None
    max_players: Optional[int] = Field(default=None, ge=2, le=8)
    turn_duration_years: Optional[int] = Field(default=None, ge=10, le=100)
    alliances_enabled: Optional[bool] = None
    combat_luck_enabled: Optional[bool] = None


@api_bp.route("/games", methods=["POST"])
@token_required
def create_game():
    """
    Créer une nouvelle partie
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              description: Nom de la partie
              example: "Campagne d'Austerlitz"
            galaxy_shape:
              type: string
              enum: [circle, spiral, cluster, random]
              default: random
            galaxy_size:
              type: string
              enum: [small, medium, large, huge]
              default: medium
            galaxy_density:
              type: string
              enum: [low, medium, high]
              default: medium
            max_players:
              type: integer
              minimum: 2
              maximum: 8
              default: 8
            turn_duration_years:
              type: integer
              minimum: 10
              maximum: 100
              default: 10
            alliances_enabled:
              type: boolean
              default: true
            combat_luck_enabled:
              type: boolean
              default: true
    responses:
      201:
        description: Partie créée
      400:
        description: Données invalides
    """
    try:
        data = CreateGameSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        game = GameService.create_game(
            creator_id=g.current_user.id,
            name=data.name,
            galaxy_shape=data.galaxy_shape,
            galaxy_size=data.galaxy_size,
            galaxy_density=data.galaxy_density,
            max_players=data.max_players,
            turn_duration_years=data.turn_duration_years,
            alliances_enabled=data.alliances_enabled,
            combat_luck_enabled=data.combat_luck_enabled,
        )
        return jsonify(game.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/games", methods=["GET"])
@token_required
def list_games():
    """
    Lister les parties en attente (lobby)
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    responses:
      200:
        description: Liste des parties
        schema:
          type: object
          properties:
            games:
              type: array
              items:
                type: object
    """
    games = GameService.get_lobby_games()
    return jsonify({
        "games": [game.to_dict() for game in games]
    })


@api_bp.route("/games/<int:game_id>", methods=["GET"])
@token_required
def get_game(game_id: int):
    """
    Obtenir les détails d'une partie
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Détails de la partie
      404:
        description: Partie non trouvée
    """
    try:
        game = GameService.get_game_details(game_id)
        if not game:
            return jsonify({"error": "Game not found"}), 404

        # Include players in response
        response = game.to_dict()
        response["players"] = [player.to_dict() for player in game.players]

        # Include galaxy info if game has started
        if game.galaxy:
            response["galaxy"] = game.galaxy.to_dict()

        return jsonify(response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/games/<int:game_id>", methods=["PATCH"])
@token_required
def update_game(game_id: int):
    """
    Modifier la configuration d'une partie (admin seulement, lobby uniquement)
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
              description: Nouveau nom de la partie
            galaxy_shape:
              type: string
              enum: [circle, spiral, cluster, random]
            galaxy_size:
              type: string
              enum: [small, medium, large, huge]
            galaxy_density:
              type: string
              enum: [low, medium, high]
            max_players:
              type: integer
              minimum: 2
              maximum: 8
            turn_duration_years:
              type: integer
              minimum: 10
              maximum: 100
            alliances_enabled:
              type: boolean
            combat_luck_enabled:
              type: boolean
    responses:
      200:
        description: Partie modifiée
      400:
        description: Données invalides
      403:
        description: Non autorisé
      404:
        description: Partie non trouvée
    """
    try:
        data = UpdateGameSchema(**(request.json or {}))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        game = GameService.update_game(
            game_id=game_id,
            admin_user_id=g.current_user.id,
            name=data.name,
            galaxy_shape=data.galaxy_shape,
            galaxy_size=data.galaxy_size,
            galaxy_density=data.galaxy_density,
            max_players=data.max_players,
            turn_duration_years=data.turn_duration_years,
            alliances_enabled=data.alliances_enabled,
            combat_luck_enabled=data.combat_luck_enabled,
        )
        response = game.to_dict()
        response["players"] = [player.to_dict() for player in game.players]
        return jsonify(response)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify({"error": error_msg}), 404
        if "admin" in error_msg.lower():
            return jsonify({"error": error_msg}), 403
        return jsonify({"error": error_msg}), 400


@api_bp.route("/games/<int:game_id>", methods=["DELETE"])
@token_required
def delete_game(game_id: int):
    """
    Supprimer une partie (admin seulement)
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Partie supprimée
      403:
        description: Non autorisé
      404:
        description: Partie non trouvée
    """
    try:
        GameService.delete_game(game_id, g.current_user.id)
        return jsonify({"message": "Game deleted"})
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify({"error": error_msg}), 404
        if "admin" in error_msg.lower():
            return jsonify({"error": error_msg}), 403
        return jsonify({"error": error_msg}), 400


@api_bp.route("/games/<int:game_id>/join", methods=["POST"])
@token_required
def join_game(game_id: int):
    """
    Rejoindre une partie
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Rejoint la partie
      400:
        description: Impossible de rejoindre
      404:
        description: Partie non trouvée
    """
    try:
        player = GameService.join_game(game_id, g.current_user.id)
        return jsonify(player.to_dict())
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify({"error": error_msg}), 404
        return jsonify({"error": error_msg}), 400


@api_bp.route("/games/<int:game_id>/leave", methods=["POST"])
@token_required
def leave_game(game_id: int):
    """
    Quitter une partie
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Partie quittée
      400:
        description: Impossible de quitter
    """
    try:
        GameService.leave_game(game_id, g.current_user.id)
        return jsonify({"message": "Left game"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/games/<int:game_id>/ai", methods=["POST"])
@token_required
def add_ai_player(game_id: int):
    """
    Ajouter un joueur IA
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            difficulty:
              type: string
              enum: [easy, medium, hard, expert]
              default: medium
            name:
              type: string
              description: Nom personnalisé (optionnel)
    responses:
      201:
        description: IA ajoutée
      400:
        description: Impossible d'ajouter l'IA
    """
    try:
        data = AddAISchema(**(request.json or {}))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Check if user is admin of the game
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    if game.admin_user_id != g.current_user.id:
        return jsonify({"error": "Only game admin can add AI players"}), 403

    try:
        player = GameService.add_ai_player(
            game_id=game_id,
            difficulty=data.difficulty,
            name=data.name,
        )
        return jsonify(player.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/games/<int:game_id>/ai/<int:player_id>", methods=["DELETE"])
@token_required
def remove_ai_player(game_id: int, player_id: int):
    """
    Retirer un joueur IA
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
      - in: path
        name: player_id
        type: integer
        required: true
    responses:
      200:
        description: IA retirée
      400:
        description: Erreur
      403:
        description: Non autorisé
    """
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    if game.admin_user_id != g.current_user.id:
        return jsonify({"error": "Only game admin can remove AI players"}), 403

    try:
        GameService.remove_ai_player(game_id, player_id)
        return jsonify({"message": "AI player removed"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/games/<int:game_id>/ready", methods=["POST"])
@token_required
def set_ready(game_id: int):
    """
    Définir le statut prêt du joueur
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            ready:
              type: boolean
              default: true
    responses:
      200:
        description: Statut mis à jour
      400:
        description: Erreur
    """
    try:
        data = SetReadySchema(**(request.json or {}))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        player = GameService.set_player_ready(game_id, g.current_user.id, data.ready)
        return jsonify(player.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/games/<int:game_id>/start", methods=["POST"])
@token_required
def start_game(game_id: int):
    """
    Démarrer une partie (admin seulement)
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Partie démarrée
      400:
        description: Impossible de démarrer
      403:
        description: Non autorisé
    """
    try:
        game = GameService.start_game(game_id, g.current_user.id)
        response = game.to_dict()
        response["players"] = [player.to_dict() for player in game.players]
        if game.galaxy:
            response["galaxy"] = game.galaxy.to_dict()
        return jsonify(response)
    except ValueError as e:
        error_msg = str(e)
        if "admin" in error_msg.lower():
            return jsonify({"error": error_msg}), 403
        return jsonify({"error": error_msg}), 400


@api_bp.route("/games/<int:game_id>/map", methods=["GET"])
@token_required
def get_game_map(game_id: int):
    """
    Obtenir la carte complète d'une partie
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Carte avec étoiles, planètes et flottes
      403:
        description: Non participant à cette partie
      404:
        description: Partie non trouvée
    """
    from app.models import GamePlayer, Fleet

    # Vérifier que la partie existe
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Vérifier que l'utilisateur participe à cette partie
    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not a player in this game"}), 403

    # Vérifier que la partie a démarré
    if game.status != GameStatus.RUNNING.value:
        return jsonify({"error": "Game has not started yet"}), 400

    # Construire la réponse
    galaxy = game.galaxy
    if not galaxy:
        return jsonify({"error": "Galaxy not generated"}), 500

    # Étoiles avec leurs planètes
    stars_data = []
    for star in galaxy.stars:
        star_dict = star.to_dict()
        star_dict["planets"] = [planet.to_dict() for planet in star.planets]
        stars_data.append(star_dict)

    # Flottes visibles (les siennes + celles sur ses planètes)
    # Pour l'instant, on retourne toutes les flottes du jeu (fog of war à implémenter plus tard)
    all_fleets = Fleet.query.join(GamePlayer).filter(
        GamePlayer.game_id == game_id
    ).all()

    fleets_data = [fleet.to_dict() for fleet in all_fleets]

    # Tous les joueurs (pour les couleurs)
    players_data = [p.to_dict() for p in game.players]

    return jsonify({
        "game_id": game_id,
        "turn": game.current_turn,
        "my_player_id": player.id,
        "galaxy": {
            "id": galaxy.id,
            "width": galaxy.width,
            "height": galaxy.height,
            "shape": galaxy.shape,
            "star_count": galaxy.star_count,
        },
        "stars": stars_data,
        "fleets": fleets_data,
        "players": players_data,
    })


@api_bp.route("/games/my", methods=["GET"])
@token_required
def my_games():
    """
    Lister mes parties (en cours et terminées)
    ---
    tags:
      - Parties
    security:
      - Bearer: []
    responses:
      200:
        description: Liste des parties du joueur
    """
    from app.models import GamePlayer

    # Get all games where user is a player
    player_entries = GamePlayer.query.filter_by(user_id=g.current_user.id).all()
    games = []

    for player in player_entries:
        game_data = player.game.to_dict()
        game_data["my_player"] = player.to_dict()
        games.append(game_data)

    return jsonify({"games": games})
