"""
Combat routes.
Provides endpoints for combat reports and history.
"""
from flask import jsonify, request

from app.routes import api_bp
from app.models import Game, GamePlayer
from app.models.combat import CombatReport
from app.services.combat import CombatService
from app.services.auth import token_required


# =============================================================================
# Combat Report Routes
# =============================================================================

@api_bp.route("/games/<int:game_id>/combat-reports", methods=["GET"])
@token_required
def get_game_combat_reports(current_user, game_id):
    """
    Get combat reports for a game.

    Query params:
        turn: Filter by specific turn (optional)
        limit: Max number of reports (default 50)

    Returns:
        List of combat report summaries
    """
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Get player in this game
    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not in this game"}), 403

    # Query params
    turn = request.args.get("turn", type=int)
    limit = request.args.get("limit", 50, type=int)
    limit = min(limit, 100)  # Max 100

    # Build query
    query = CombatReport.query.filter_by(game_id=game_id)

    if turn is not None:
        query = query.filter_by(turn=turn)

    reports = query.order_by(CombatReport.turn.desc()).limit(limit).all()

    return jsonify({
        "reports": [r.to_summary_dict() for r in reports],
        "count": len(reports),
    })


@api_bp.route("/games/<int:game_id>/combat-reports/turn/<int:turn>", methods=["GET"])
@token_required
def get_turn_combat_reports(current_user, game_id, turn):
    """
    Get all combat reports for a specific turn.

    Returns:
        List of detailed combat reports
    """
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not in this game"}), 403

    reports = CombatService.get_combat_reports_for_turn(game_id, turn)

    return jsonify({
        "turn": turn,
        "reports": [r.to_dict() for r in reports],
        "count": len(reports),
    })


@api_bp.route("/combat-reports/<int:report_id>", methods=["GET"])
@token_required
def get_combat_report(current_user, report_id):
    """
    Get detailed combat report by ID.

    Returns:
        Full combat report with combat log
    """
    report = CombatReport.query.get(report_id)
    if not report:
        return jsonify({"error": "Combat report not found"}), 404

    # Check access (player must be in the game)
    player = GamePlayer.query.filter_by(
        game_id=report.game_id,
        user_id=current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not in this game"}), 403

    return jsonify(report.to_dict())


@api_bp.route("/games/<int:game_id>/my-battles", methods=["GET"])
@token_required
def get_my_battles(current_user, game_id):
    """
    Get combat history for current player.

    Query params:
        limit: Max number of reports (default 20)

    Returns:
        List of battles involving this player
    """
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not in this game"}), 403

    limit = request.args.get("limit", 20, type=int)
    limit = min(limit, 50)

    reports = CombatService.get_player_combat_history(game_id, player.id, limit)

    # Categorize as offensive or defensive
    battles = []
    for report in reports:
        is_attacker = player.id in (report.attacker_ids or [])
        is_defender = report.defender_id == player.id
        is_winner = report.victor_id == player.id

        battles.append({
            **report.to_summary_dict(),
            "role": "attacker" if is_attacker else "defender",
            "result": "victory" if is_winner else ("draw" if report.is_draw else "defeat"),
        })

    return jsonify({
        "battles": battles,
        "count": len(battles),
    })


@api_bp.route("/games/<int:game_id>/combat-stats", methods=["GET"])
@token_required
def get_combat_stats(current_user, game_id):
    """
    Get combat statistics for current player.

    Returns:
        Combat statistics (wins, losses, ships destroyed, etc.)
    """
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    player = GamePlayer.query.filter_by(
        game_id=game_id,
        user_id=current_user.id
    ).first()

    if not player:
        return jsonify({"error": "You are not in this game"}), 403

    # Get all battles involving player
    from sqlalchemy import or_
    reports = CombatReport.query.filter(
        CombatReport.game_id == game_id,
        or_(
            CombatReport.defender_id == player.id,
            CombatReport.attacker_ids.contains([player.id])
        )
    ).all()

    # Calculate stats
    stats = {
        "total_battles": len(reports),
        "victories": 0,
        "defeats": 0,
        "draws": 0,
        "ships_lost": 0,
        "ships_destroyed": 0,
        "planets_captured": 0,
        "planets_lost": 0,
        "metal_recovered": 0,
    }

    for report in reports:
        is_attacker = player.id in (report.attacker_ids or [])

        # Victory/Defeat
        if report.is_draw:
            stats["draws"] += 1
        elif report.victor_id == player.id:
            stats["victories"] += 1
        else:
            stats["defeats"] += 1

        # Ships lost
        if is_attacker:
            player_losses = (report.attacker_losses or {}).get(str(player.id), {})
            stats["ships_lost"] += sum(player_losses.values())
            # Ships destroyed = defender losses
            stats["ships_destroyed"] += sum((report.defender_losses or {}).values())
        else:
            stats["ships_lost"] += sum((report.defender_losses or {}).values())
            # Ships destroyed = attacker losses
            for losses in (report.attacker_losses or {}).values():
                stats["ships_destroyed"] += sum(losses.values())

        # Planets
        if report.planet_captured or report.planet_colonized:
            if report.victor_id == player.id:
                stats["planets_captured"] += 1
            elif report.defender_id == player.id:
                stats["planets_lost"] += 1

        # Metal
        if report.victor_id == player.id:
            stats["metal_recovered"] += report.metal_recovered

    return jsonify(stats)
