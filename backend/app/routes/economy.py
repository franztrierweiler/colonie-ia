"""
Economy and turn management routes
"""
from flask import request, jsonify, g
from pydantic import BaseModel, Field
from typing import Optional

from app.routes import api_bp
from app.services.auth import token_required
from app.services import EconomyService, TurnService
from app.models import Game, GamePlayer, Planet, GameStatus, ProductionQueue


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
    ships_budget: int = Field(ge=0, le=100)


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
    Modifier le budget d'une planète (terraform/minage/vaisseaux)
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
            - ships_budget
          properties:
            terraform_budget:
              type: integer
              minimum: 0
              maximum: 100
            mining_budget:
              type: integer
              minimum: 0
              maximum: 100
            ships_budget:
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
    total = data.terraform_budget + data.mining_budget + data.ships_budget
    if total != 100:
        return jsonify({"error": f"terraform_budget + mining_budget + ships_budget must equal 100 (got {total})"}), 400

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
    planet.ships_budget = data.ships_budget
    db.session.commit()

    return jsonify({
        "planet_id": planet.id,
        "terraform_budget": planet.terraform_budget,
        "mining_budget": planet.mining_budget,
        "ships_budget": planet.ships_budget,
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


# =============================================================================
# Production Queue Endpoints
# =============================================================================

class AddToQueueSchema(BaseModel):
    """Schema for adding ships to production queue."""
    design_id: int
    fleet_id: Optional[int] = None
    count: int = Field(default=1, ge=1, le=100)


@api_bp.route("/planets/<int:planet_id>/production", methods=["GET"])
@token_required
def get_production_queue(planet_id: int):
    """
    Obtenir la file de production d'une planète
    ---
    tags:
      - Production
    security:
      - Bearer: []
    parameters:
      - in: path
        name: planet_id
        type: integer
        required: true
    responses:
      200:
        description: File de production
      403:
        description: Planète ne vous appartient pas
      404:
        description: Planète non trouvée
    """
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

    # Get queue items
    queue_items = planet.production_queue.filter_by(is_completed=False).order_by(
        ProductionQueue.priority
    ).all()

    # Calculate production stats
    production_output = EconomyService.calculate_ship_production_output(planet)

    return jsonify({
        "planet_id": planet.id,
        "planet_name": planet.name,
        "ships_budget": planet.ships_budget,
        "production_output_per_turn": production_output,
        "ship_production_points": planet.ship_production_points,
        "queue": [item.to_dict() for item in queue_items],
    })


@api_bp.route("/planets/<int:planet_id>/production", methods=["POST"])
@token_required
def add_to_production_queue(planet_id: int):
    """
    Ajouter un vaisseau à la file de production
    ---
    tags:
      - Production
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
            - design_id
          properties:
            design_id:
              type: integer
              description: ID du design de vaisseau
            fleet_id:
              type: integer
              description: ID de la flotte cible (optionnel)
            count:
              type: integer
              default: 1
              minimum: 1
              maximum: 100
              description: Nombre de vaisseaux à ajouter
    responses:
      200:
        description: Vaisseau(x) ajouté(s) à la file
      400:
        description: Erreur
      403:
        description: Planète ne vous appartient pas
      404:
        description: Planète non trouvée
    """
    try:
        data = AddToQueueSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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

    from app import db
    success, message, items = EconomyService.add_to_production_queue(
        planet=planet,
        design_id=data.design_id,
        fleet_id=data.fleet_id,
        count=data.count
    )

    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            "items": [item.to_dict() for item in items],
        })
    else:
        return jsonify({"error": message}), 400


@api_bp.route("/production/<int:queue_id>", methods=["DELETE"])
@token_required
def remove_from_production_queue(queue_id: int):
    """
    Retirer un élément de la file de production
    ---
    tags:
      - Production
    security:
      - Bearer: []
    parameters:
      - in: path
        name: queue_id
        type: integer
        required: true
    responses:
      200:
        description: Élément retiré
      400:
        description: Erreur
      403:
        description: Non autorisé
      404:
        description: Élément non trouvé
    """
    item = ProductionQueue.query.get(queue_id)
    if not item:
        return jsonify({"error": "Queue item not found"}), 404

    # Check ownership
    planet = item.planet
    player = GamePlayer.query.filter_by(
        id=planet.owner_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "This production queue does not belong to you"}), 403

    from app import db
    success, message = EconomyService.remove_from_production_queue(queue_id)

    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
        })
    else:
        return jsonify({"error": message}), 400
