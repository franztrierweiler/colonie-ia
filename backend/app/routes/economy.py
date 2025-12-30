"""
Economy and turn management routes
"""
from flask import request, jsonify, g
from pydantic import BaseModel, Field
from typing import Optional

from app.routes import api_bp
from app.services.auth import token_required
from app.services import EconomyService, TurnService
from app.models import Game, GamePlayer, Planet, GameStatus


# Pydantic schemas
class BorrowSchema(BaseModel):
    """Schema for borrowing money."""
    amount: int = Field(gt=0)


class RepaySchema(BaseModel):
    """Schema for repaying debt."""
    amount: int = Field(gt=0)


class PlanetBudgetSchema(BaseModel):
    """Schema for updating planet budget allocation."""
    terraform_budget: int = Field(ge=0, le=100)
    mining_budget: int = Field(ge=0, le=100)


# =============================================================================
# Economy Endpoints
# =============================================================================

@api_bp.route("/games/<int:game_id>/economy", methods=["GET"])
@token_required
def get_economy(game_id: int):
    """
    Obtenir l'état économique du joueur
    ---
    tags:
      - Économie
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: État économique
      403:
        description: Non membre de la partie
      404:
        description: Partie non trouvée
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

    summary = EconomyService.get_player_economy_summary(player)
    return jsonify(summary)


@api_bp.route("/games/<int:game_id>/borrow", methods=["POST"])
@token_required
def borrow_money(game_id: int):
    """
    Emprunter de l'argent (prendre de la dette)
    ---
    tags:
      - Économie
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
            - amount
          properties:
            amount:
              type: integer
              minimum: 1
              description: Montant à emprunter
    responses:
      200:
        description: Emprunt effectué
      400:
        description: Emprunt impossible
      403:
        description: Non membre de la partie
    """
    try:
        data = BorrowSchema(**request.json)
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

    from app import db
    success, message = EconomyService.borrow(player, data.amount)
    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            "money": player.money,
            "debt": player.debt,
        })
    else:
        return jsonify({"error": message}), 400


@api_bp.route("/games/<int:game_id>/repay", methods=["POST"])
@token_required
def repay_debt(game_id: int):
    """
    Rembourser une partie de la dette
    ---
    tags:
      - Économie
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
            - amount
          properties:
            amount:
              type: integer
              minimum: 1
              description: Montant à rembourser
    responses:
      200:
        description: Remboursement effectué
      400:
        description: Remboursement impossible
    """
    try:
        data = RepaySchema(**request.json)
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

    from app import db
    success, message = EconomyService.repay_debt(player, data.amount)
    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            "money": player.money,
            "debt": player.debt,
        })
    else:
        return jsonify({"error": message}), 400


@api_bp.route("/planets/<int:planet_id>/budget", methods=["PATCH"])
@token_required
def update_planet_budget(planet_id: int):
    """
    Modifier le budget d'une planète (terraform/minage)
    ---
    tags:
      - Économie
    security:
      - Bearer: []
    parameters:
      - in: path
        name: planet_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - terraform_budget
            - mining_budget
          properties:
            terraform_budget:
              type: integer
              minimum: 0
              maximum: 100
            mining_budget:
              type: integer
              minimum: 0
              maximum: 100
    responses:
      200:
        description: Budget mis à jour
      400:
        description: Budget invalide
      403:
        description: Planète ne vous appartient pas
    """
    try:
        data = PlanetBudgetSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Validate that budgets sum to 100
    if data.terraform_budget + data.mining_budget != 100:
        return jsonify({"error": "terraform_budget + mining_budget must equal 100"}), 400

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    # Check ownership
    player = GamePlayer.query.filter_by(
        id=planet.owner_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "This planet does not belong to you"}), 403

    from app import db
    planet.terraform_budget = data.terraform_budget
    planet.mining_budget = data.mining_budget
    db.session.commit()

    return jsonify({
        "planet_id": planet.id,
        "terraform_budget": planet.terraform_budget,
        "mining_budget": planet.mining_budget,
    })


class AbandonPlanetSchema(BaseModel):
    """Schema for abandoning a planet."""
    strip_mine: bool = Field(default=True)


@api_bp.route("/planets/<int:planet_id>/abandon", methods=["POST"])
@token_required
def abandon_planet(planet_id: int):
    """
    Abandonner une planète (optionnellement strip-mine)
    ---
    tags:
      - Planètes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: planet_id
        type: integer
        required: true
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            strip_mine:
              type: boolean
              default: true
              description: Récupérer 50% du métal restant
    responses:
      200:
        description: Planète abandonnée
      400:
        description: Erreur (planète non colonisée)
      403:
        description: Planète ne vous appartient pas
      404:
        description: Planète non trouvée
    """
    data = AbandonPlanetSchema(**(request.json or {}))

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    # Check ownership
    player = GamePlayer.query.filter_by(
        id=planet.owner_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "This planet does not belong to you"}), 403

    # Check game is running
    game = Game.query.get(player.game_id)
    if game.status != GameStatus.RUNNING.value:
        return jsonify({"error": "Game is not running"}), 400

    try:
        from app import db
        result = EconomyService.abandon_planet(planet, strip_mine=data.strip_mine)
        db.session.commit()

        return jsonify({
            "success": True,
            **result,
            "player_metal": player.metal,
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# =============================================================================
# Turn Management Endpoints
# =============================================================================

@api_bp.route("/games/<int:game_id>/turn/status", methods=["GET"])
@token_required
def get_turn_status(game_id: int):
    """
    Obtenir le statut du tour actuel
    ---
    tags:
      - Tours
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Statut du tour
      404:
        description: Partie non trouvée
    """
    try:
        status = TurnService.get_turn_status(game_id)
        return jsonify(status)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@api_bp.route("/games/<int:game_id>/turn/submit", methods=["POST"])
@token_required
def submit_turn(game_id: int):
    """
    Soumettre son tour (signaler qu'on a fini)
    ---
    tags:
      - Tours
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Tour soumis
      400:
        description: Erreur
    """
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

    try:
        all_submitted = TurnService.submit_turn(game_id, player.id)

        response = {
            "submitted": True,
            "all_players_submitted": all_submitted,
        }

        # If all players submitted, process the turn
        if all_submitted:
            turn_results = TurnService.process_turn(game)
            response["turn_processed"] = True
            response["turn_results"] = turn_results

            # Check for victory
            victory = TurnService.check_victory(game)
            if victory:
                response["victory"] = victory

        return jsonify(response)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/games/<int:game_id>/turn/process", methods=["POST"])
@token_required
def force_process_turn(game_id: int):
    """
    Forcer le passage au tour suivant (admin seulement)
    ---
    tags:
      - Tours
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Tour traité
      403:
        description: Non autorisé
    """
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Only admin can force turn
    if game.admin_user_id != g.current_user.id:
        return jsonify({"error": "Only game admin can force turn processing"}), 403

    if game.status != GameStatus.RUNNING.value:
        return jsonify({"error": "Game is not running"}), 400

    try:
        turn_results = TurnService.process_turn(game)

        response = {
            "turn_processed": True,
            "turn_results": turn_results,
        }

        # Check for victory
        victory = TurnService.check_victory(game)
        if victory:
            response["victory"] = victory

        return jsonify(response)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
