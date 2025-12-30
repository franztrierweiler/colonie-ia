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
