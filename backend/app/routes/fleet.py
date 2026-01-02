"""
Fleet management routes
"""
from flask import request, jsonify, g
from pydantic import BaseModel, Field
from typing import List, Optional

from app import db
from app.routes import api_bp
from app.services.auth import token_required
from app.services import FleetService
from app.models import (
    Game, GamePlayer, Planet, GameStatus,
    Ship, ShipDesign, Fleet, ShipType, FleetStatus,
)


# =============================================================================
# Pydantic Schemas
# =============================================================================

class CreateDesignSchema(BaseModel):
    """Schema for creating a ship design."""
    name: str = Field(min_length=1, max_length=50)
    ship_type: str
    range_level: int = Field(ge=1, le=20, default=1)
    speed_level: int = Field(ge=1, le=20, default=1)
    weapons_level: int = Field(ge=1, le=20, default=1)
    shields_level: int = Field(ge=1, le=20, default=1)
    mini_level: int = Field(ge=1, le=20, default=1)


class BuildShipsSchema(BaseModel):
    """Schema for building ships."""
    fleet_id: int
    count: int = Field(ge=1, le=100, default=1)


class CreateFleetSchema(BaseModel):
    """Schema for creating a fleet."""
    name: str = Field(min_length=1, max_length=50)
    planet_id: Optional[int] = None


class MoveFleetSchema(BaseModel):
    """Schema for moving a fleet."""
    destination_planet_id: int


class SplitFleetSchema(BaseModel):
    """Schema for splitting a fleet."""
    ship_ids: List[int]
    new_fleet_name: str = Field(min_length=1, max_length=50)


class MergeFleetSchema(BaseModel):
    """Schema for merging fleets."""
    fleet_id_to_merge: int


# =============================================================================
# Helper Functions
# =============================================================================

def get_player_in_game(game_id: int) -> tuple:
    """Get game and player for current user."""
    game = Game.query.get(game_id)
    if not game:
        return None, None, ({"error": "Game not found"}, 404)

    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return game, None, ({"error": "You are not in this game"}, 403)

    return game, player, None


# =============================================================================
# Ship Design Endpoints
# =============================================================================

@api_bp.route("/games/<int:game_id>/designs", methods=["GET"])
@token_required
def get_designs(game_id: int):
    """
    Liste des designs du joueur
    ---
    tags:
      - Vaisseaux
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
    responses:
      200:
        description: Liste des designs
    """
    game, player, error = get_player_in_game(game_id)
    if error:
        return jsonify(error[0]), error[1]

    designs = FleetService.get_player_designs(player)
    return jsonify({
        "designs": [d.to_dict() for d in designs]
    })


@api_bp.route("/games/<int:game_id>/designs", methods=["POST"])
@token_required
def create_design(game_id: int):
    """
    Créer un nouveau design de vaisseau
    ---
    tags:
      - Vaisseaux
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
            - name
            - ship_type
          properties:
            name:
              type: string
            ship_type:
              type: string
              enum: [fighter, scout, colony, satellite, tanker, battleship, decoy, biological]
            range_level:
              type: integer
              default: 1
            speed_level:
              type: integer
              default: 1
            weapons_level:
              type: integer
              default: 1
            shields_level:
              type: integer
              default: 1
            mini_level:
              type: integer
              default: 1
    responses:
      201:
        description: Design créé
      400:
        description: Données invalides
    """
    try:
        data = CreateDesignSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    game, player, error = get_player_in_game(game_id)
    if error:
        return jsonify(error[0]), error[1]

    if game.status != GameStatus.RUNNING.value:
        return jsonify({"error": "Game is not running"}), 400

    # Validate ship type
    try:
        ship_type = ShipType(data.ship_type)
    except ValueError:
        return jsonify({"error": f"Invalid ship type: {data.ship_type}"}), 400

    design = FleetService.create_design(
        player=player,
        name=data.name,
        ship_type=ship_type,
        range_level=data.range_level,
        speed_level=data.speed_level,
        weapons_level=data.weapons_level,
        shields_level=data.shields_level,
        mini_level=data.mini_level,
    )

    db.session.commit()

    return jsonify(design.to_dict()), 201


@api_bp.route("/games/<int:game_id>/designs/<int:design_id>/costs", methods=["GET"])
@token_required
def get_design_costs(game_id: int, design_id: int):
    """
    Obtenir les coûts d'un design
    ---
    tags:
      - Vaisseaux
    """
    game, player, error = get_player_in_game(game_id)
    if error:
        return jsonify(error[0]), error[1]

    design = ShipDesign.query.get(design_id)
    if not design or design.player_id != player.id:
        return jsonify({"error": "Design not found"}), 404

    return jsonify({
        "design_id": design.id,
        "name": design.name,
        "prototype_cost_money": design.prototype_cost_money,
        "prototype_cost_metal": design.prototype_cost_metal,
        "production_cost_money": design.production_cost_money,
        "production_cost_metal": design.production_cost_metal,
        "is_prototype_built": design.is_prototype_built,
    })


@api_bp.route("/games/<int:game_id>/designs/<int:design_id>/build", methods=["POST"])
@token_required
def build_ships(game_id: int, design_id: int):
    """
    Construire des vaisseaux à partir d'un design
    ---
    tags:
      - Vaisseaux
    security:
      - Bearer: []
    parameters:
      - in: path
        name: game_id
        type: integer
        required: true
      - in: path
        name: design_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - fleet_id
          properties:
            fleet_id:
              type: integer
            count:
              type: integer
              default: 1
    responses:
      200:
        description: Vaisseaux construits
      400:
        description: Construction impossible
    """
    try:
        data = BuildShipsSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    game, player, error = get_player_in_game(game_id)
    if error:
        return jsonify(error[0]), error[1]

    if game.status != GameStatus.RUNNING.value:
        return jsonify({"error": "Game is not running"}), 400

    design = ShipDesign.query.get(design_id)
    if not design or design.player_id != player.id:
        return jsonify({"error": "Design not found"}), 404

    fleet = Fleet.query.get(data.fleet_id)
    if not fleet or fleet.player_id != player.id:
        return jsonify({"error": "Fleet not found"}), 404

    if fleet.status != FleetStatus.STATIONED.value:
        return jsonify({"error": "Fleet must be stationed to build ships"}), 400

    success, message, ships = FleetService.build_ships(player, design, fleet, data.count)

    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            "ships_built": len(ships),
            "player_money": player.money,
            "player_metal": player.metal,
        })
    else:
        return jsonify({"error": message}), 400


# =============================================================================
# Fleet Management Endpoints
# =============================================================================

@api_bp.route("/games/<int:game_id>/fleets", methods=["GET"])
@token_required
def get_fleets(game_id: int):
    """
    Liste des flottes du joueur
    ---
    tags:
      - Flottes
    security:
      - Bearer: []
    responses:
      200:
        description: Liste des flottes
    """
    game, player, error = get_player_in_game(game_id)
    if error:
        return jsonify(error[0]), error[1]

    summary = FleetService.get_player_fleet_summary(player)
    return jsonify(summary)


@api_bp.route("/games/<int:game_id>/fleets", methods=["POST"])
@token_required
def create_fleet(game_id: int):
    """
    Créer une nouvelle flotte
    ---
    tags:
      - Flottes
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
            planet_id:
              type: integer
    responses:
      201:
        description: Flotte créée
    """
    try:
        data = CreateFleetSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    game, player, error = get_player_in_game(game_id)
    if error:
        return jsonify(error[0]), error[1]

    if game.status != GameStatus.RUNNING.value:
        return jsonify({"error": "Game is not running"}), 400

    planet = None
    if data.planet_id:
        planet = Planet.query.get(data.planet_id)
        if not planet:
            return jsonify({"error": "Planet not found"}), 404
        # Must own the planet to create fleet there
        if planet.owner_id != player.id:
            return jsonify({"error": "You don't own this planet"}), 403

    fleet = FleetService.create_fleet(player, data.name, planet)
    db.session.commit()

    return jsonify(fleet.to_dict()), 201


@api_bp.route("/fleets/<int:fleet_id>", methods=["GET"])
@token_required
def get_fleet(fleet_id: int):
    """
    Détails d'une flotte
    ---
    tags:
      - Flottes
    """
    fleet = Fleet.query.get(fleet_id)
    if not fleet:
        return jsonify({"error": "Fleet not found"}), 404

    # Check ownership
    player = GamePlayer.query.filter_by(
        id=fleet.player_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "This fleet does not belong to you"}), 403

    return jsonify(fleet.to_dict(include_ships=True))


@api_bp.route("/fleets/<int:fleet_id>/move", methods=["POST"])
@token_required
def move_fleet(fleet_id: int):
    """
    Déplacer une flotte vers une planète
    ---
    tags:
      - Flottes
    security:
      - Bearer: []
    parameters:
      - in: path
        name: fleet_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - destination_planet_id
          properties:
            destination_planet_id:
              type: integer
    responses:
      200:
        description: Flotte en mouvement
      400:
        description: Déplacement impossible
    """
    try:
        data = MoveFleetSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    fleet = Fleet.query.get(fleet_id)
    if not fleet:
        return jsonify({"error": "Fleet not found"}), 404

    player = GamePlayer.query.filter_by(
        id=fleet.player_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "This fleet does not belong to you"}), 403

    game = Game.query.get(player.game_id)
    if game.status != GameStatus.RUNNING.value:
        return jsonify({"error": "Game is not running"}), 400

    destination = Planet.query.get(data.destination_planet_id)
    if not destination:
        return jsonify({"error": "Destination planet not found"}), 404

    success, message = FleetService.move_fleet(fleet, destination, game.current_turn)

    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            "fleet": fleet.to_dict(),
        })
    else:
        return jsonify({"error": message}), 400


@api_bp.route("/fleets/<int:fleet_id>/split", methods=["POST"])
@token_required
def split_fleet(fleet_id: int):
    """
    Diviser une flotte en deux
    ---
    tags:
      - Flottes
    """
    try:
        data = SplitFleetSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    fleet = Fleet.query.get(fleet_id)
    if not fleet:
        return jsonify({"error": "Fleet not found"}), 404

    player = GamePlayer.query.filter_by(
        id=fleet.player_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "This fleet does not belong to you"}), 403

    success, message, new_fleet = FleetService.split_fleet(fleet, data.ship_ids, data.new_fleet_name)

    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            "original_fleet": fleet.to_dict(),
            "new_fleet": new_fleet.to_dict() if new_fleet else None,
        })
    else:
        return jsonify({"error": message}), 400


@api_bp.route("/fleets/<int:fleet_id>/merge", methods=["POST"])
@token_required
def merge_fleet(fleet_id: int):
    """
    Fusionner deux flottes
    ---
    tags:
      - Flottes
    """
    try:
        data = MergeFleetSchema(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    fleet1 = Fleet.query.get(fleet_id)
    fleet2 = Fleet.query.get(data.fleet_id_to_merge)

    if not fleet1 or not fleet2:
        return jsonify({"error": "Fleet not found"}), 404

    player = GamePlayer.query.filter_by(
        id=fleet1.player_id,
        user_id=g.current_user.id
    ).first()

    if not player or fleet2.player_id != player.id:
        return jsonify({"error": "Fleets must belong to you"}), 403

    success, message = FleetService.merge_fleets(fleet1, fleet2)

    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            "fleet": fleet1.to_dict(),
        })
    else:
        return jsonify({"error": message}), 400


@api_bp.route("/fleets/<int:fleet_id>/disband", methods=["POST"])
@token_required
def disband_fleet(fleet_id: int):
    """
    Démanteler une flotte entière (récupère 75% du métal)
    ---
    tags:
      - Flottes
    """
    fleet = Fleet.query.get(fleet_id)
    if not fleet:
        return jsonify({"error": "Fleet not found"}), 404

    player = GamePlayer.query.filter_by(
        id=fleet.player_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "This fleet does not belong to you"}), 403

    success, message, metal_recovered = FleetService.disband_fleet(fleet)

    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            "metal_recovered": metal_recovered,
            "player_metal": player.metal,
        })
    else:
        return jsonify({"error": message}), 400


@api_bp.route("/ships/<int:ship_id>/disband", methods=["POST"])
@token_required
def disband_ship(ship_id: int):
    """
    Démanteler un vaisseau (récupère 75% du métal)
    ---
    tags:
      - Vaisseaux
    """
    ship = Ship.query.get(ship_id)
    if not ship:
        return jsonify({"error": "Ship not found"}), 404

    if not ship.fleet:
        return jsonify({"error": "Ship must be in a fleet"}), 400

    player = GamePlayer.query.filter_by(
        id=ship.fleet.player_id,
        user_id=g.current_user.id
    ).first()

    if not player:
        return jsonify({"error": "This ship does not belong to you"}), 403

    success, message, metal_recovered = FleetService.disband_ship(ship)

    if success:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": message,
            "metal_recovered": metal_recovered,
            "player_metal": player.metal,
        })
    else:
        return jsonify({"error": message}), 400
