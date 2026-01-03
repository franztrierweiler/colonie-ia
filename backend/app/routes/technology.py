"""
Technology management routes
"""
from flask import request, jsonify, g
from pydantic import BaseModel, Field

from app import db
from app.routes import api_bp
from app.services.auth import token_required
from app.services.technology import TechnologyService
from app.models import Game, GamePlayer, GameStatus
from app.models.technology import RadicalBreakthrough


# =============================================================================
# Pydantic Schemas
# =============================================================================

class ResearchBudgetSchema(BaseModel):
    """Schema for research budget allocation."""
    range_budget: int = Field(ge=0, le=100)
    speed_budget: int = Field(ge=0, le=100)
    weapons_budget: int = Field(ge=0, le=100)
    shields_budget: int = Field(ge=0, le=100)
    mini_budget: int = Field(ge=0, le=100)
    radical_budget: int = Field(ge=0, le=100)


class EliminateBreakthroughSchema(BaseModel):
    """Schema for eliminating a breakthrough option."""
    option: str


# =============================================================================
# Technology Endpoints
# =============================================================================

@api_bp.route("/games/<int:game_id>/technology", methods=["GET"])
@token_required
def get_technology(game_id: int):
    """
    Obtenir les niveaux technologiques du joueur
    ---
    tags:
      - Technologie
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Etat technologique complet
      403:
        description: Non membre de la partie
      404:
        description: Partie non trouvee
    """
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not in this game"}), 403

    summary = TechnologyService.get_player_tech_summary(player)
    db.session.commit()  # Commit in case tech was created

    return jsonify(summary)


@api_bp.route("/games/<int:game_id>/technology/budget", methods=["PATCH"])
@token_required
def update_research_budget(game_id: int):
    """
    Modifier l'allocation du budget de recherche
    ---
    tags:
      - Technologie
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - range_budget
            - speed_budget
            - weapons_budget
            - shields_budget
            - mini_budget
            - radical_budget
          properties:
            range_budget:
              type: integer
              minimum: 0
              maximum: 100
            speed_budget:
              type: integer
              minimum: 0
              maximum: 100
            weapons_budget:
              type: integer
              minimum: 0
              maximum: 100
            shields_budget:
              type: integer
              minimum: 0
              maximum: 100
            mini_budget:
              type: integer
              minimum: 0
              maximum: 100
            radical_budget:
              type: integer
              minimum: 0
              maximum: 100
    responses:
      200:
        description: Budget mis a jour
      400:
        description: Budget invalide (doit totaliser 100)
      403:
        description: Non membre de la partie
    """
    try:
        data = ResearchBudgetSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if game.status != GameStatus.RUNNING.value:
        return jsonify({"error": "Game is not running"}), 400

    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not in this game"}), 403

    if player.is_eliminated:
        return jsonify({"error": "You have been eliminated"}), 400

    success, message = TechnologyService.update_research_budget(
        player,
        data.range_budget,
        data.speed_budget,
        data.weapons_budget,
        data.shields_budget,
        data.mini_budget,
        data.radical_budget,
    )

    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            "budget": player.technology.to_dict()["budget"],
        })
    else:
        return jsonify({"error": message}), 400


@api_bp.route("/games/<int:game_id>/technology/comparison", methods=["GET"])
@token_required
def get_technology_comparison(game_id: int):
    """
    Obtenir la comparaison technologique avec les adversaires
    ---
    tags:
      - Technologie
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Comparaison relative (ahead/behind/equal)
      403:
        description: Non membre de la partie
      404:
        description: Partie non trouvee
    """
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not in this game"}), 403

    comparison = TechnologyService.get_technology_comparison(game, player)
    return jsonify(comparison)


@api_bp.route("/games/<int:game_id>/technology/max-levels", methods=["GET"])
@token_required
def get_max_tech_levels(game_id: int):
    """
    Obtenir les niveaux technologiques max pour la conception de vaisseaux
    ---
    tags:
      - Technologie
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Niveaux max par domaine
      403:
        description: Non membre de la partie
    """
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not in this game"}), 403

    max_levels = TechnologyService.get_max_tech_levels(player)
    return jsonify({"max_levels": max_levels})


# =============================================================================
# Radical Breakthrough Endpoints
# =============================================================================

@api_bp.route("/games/<int:game_id>/breakthroughs", methods=["GET"])
@token_required
def get_pending_breakthroughs(game_id: int):
    """
    Obtenir les percees radicales en attente du joueur
    ---
    tags:
      - Technologie
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Liste des percees en attente
      403:
        description: Non membre de la partie
    """
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not in this game"}), 403

    pending = RadicalBreakthrough.query.filter_by(
        player_id=player.id,
        is_resolved=False
    ).all()

    return jsonify({
        "pending": [b.to_dict() for b in pending],
    })


@api_bp.route("/breakthroughs/<int:breakthrough_id>/eliminate", methods=["POST"])
@token_required
def eliminate_breakthrough_option(breakthrough_id: int):
    """
    Eliminer une option de percee radicale (1 sur 4)
    ---
    tags:
      - Technologie
    security:
      - Bearer: []
    parameters:
      - in: path
        name: breakthrough_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - option
          properties:
            option:
              type: string
              description: Option a eliminer
    responses:
      200:
        description: Percee resolue, une des 3 options restantes deverrouillee
      400:
        description: Option invalide ou deja resolue
      403:
        description: Percee ne vous appartient pas
      404:
        description: Percee non trouvee
    """
    try:
        data = EliminateBreakthroughSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    breakthrough = RadicalBreakthrough.query.get(breakthrough_id)
    if not breakthrough:
        return jsonify({"error": "Breakthrough not found"}), 404

    # Find the player who owns this breakthrough
    player = GamePlayer.query.filter_by(
        id=breakthrough.player_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "This breakthrough does not belong to you"}), 403

    # Get current game turn
    game = Game.query.get(player.game_id)

    success, message, result = TechnologyService.eliminate_breakthrough_option(
        player,
        breakthrough_id,
        data.option,
        game.current_turn,
    )

    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            **result,
        })
    else:
        return jsonify({"error": message}), 400


@api_bp.route("/breakthroughs/<int:breakthrough_id>", methods=["GET"])
@token_required
def get_breakthrough(breakthrough_id: int):
    """
    Obtenir les details d'une percee radicale
    ---
    tags:
      - Technologie
    security:
      - Bearer: []
    parameters:
      - in: path
        name: breakthrough_id
        type: integer
        required: true
    responses:
      200:
        description: Details de la percee
      403:
        description: Percee ne vous appartient pas
      404:
        description: Percee non trouvee
    """
    breakthrough = RadicalBreakthrough.query.get(breakthrough_id)
    if not breakthrough:
        return jsonify({"error": "Breakthrough not found"}), 404

    # Check ownership
    player = GamePlayer.query.filter_by(
        id=breakthrough.player_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "This breakthrough does not belong to you"}), 403

    return jsonify(breakthrough.to_dict())
