#!/usr/bin/env python3
"""
Test script for running a complete AI game.

Usage:
    docker compose exec backend python scripts/test_ai_game.py [--turns N]
"""
import sys
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, '/app')

from app import create_app, db
from app.models import User, Game, GamePlayer, GameStatus, Planet, PlanetState, ShipType
from app.services import GameService, TurnService, FleetService
from app.services.ai import AIService, GameAnalysis


def create_test_user():
    """Create or get a test user."""
    user = User.query.filter_by(email="test-ai@colonie.local").first()
    if not user:
        user = User(
            email="test-ai@colonie.local",
            pseudo="TestAdmin",
            password_hash="not-a-real-hash",
            is_verified=True,
        )
        db.session.add(user)
        db.session.commit()
        print(f"[+] Created test user: {user.pseudo} (id={user.id})")
    else:
        print(f"[*] Using existing test user: {user.pseudo} (id={user.id})")
    return user


def create_ai_game(admin_user, num_ai_players=3, galaxy_size="small"):
    """Create a new game with AI players."""
    print(f"\n[+] Creating game with {num_ai_players} AI players...")

    # Create game
    game = GameService.create_game(
        creator_id=admin_user.id,
        name=f"AI Test Game {datetime.now().strftime('%H:%M')}",
        galaxy_shape="random",
        galaxy_size=galaxy_size,
        galaxy_density="medium",
        max_players=num_ai_players + 1,
        turn_duration_years=10,
        alliances_enabled=False,
        combat_luck_enabled=True,
    )
    print(f"    Game created: {game.name} (id={game.id})")

    # Add AI players with different difficulties
    difficulties = ["conscrit", "capitaine", "marechal", "colonel", "grenadier"]
    for i in range(num_ai_players):
        difficulty = difficulties[i % len(difficulties)]
        ai_player = GameService.add_ai_player(
            game_id=game.id,
            difficulty=difficulty,
        )
        print(f"    Added AI: {ai_player.player_name} ({difficulty})")

    return game


def create_default_designs(player):
    """Create default ship designs for a player."""
    designs_created = []

    # Basic designs using player's tech levels (all at 1 for new game)
    default_designs = [
        ("Chasseur Mk1", ShipType.FIGHTER),
        ("Éclaireur Mk1", ShipType.SCOUT),
        ("Colonisateur", ShipType.COLONY),
        ("Satellite Défensif", ShipType.SATELLITE),
    ]

    for name, ship_type in default_designs:
        try:
            design = FleetService.create_design(
                player=player,
                name=name,
                ship_type=ship_type,
                range_level=1,
                speed_level=1,
                weapons_level=1,
                shields_level=1,
                mini_level=1,
            )
            designs_created.append(design)
        except Exception as e:
            print(f"    Warning: Could not create {name}: {e}")

    return designs_created


def start_game(game, admin_user):
    """Start the game."""
    print(f"\n[+] Starting game...")

    # Set admin ready
    admin_player = GamePlayer.query.filter_by(game_id=game.id, user_id=admin_user.id).first()
    admin_player.is_ready = True
    db.session.commit()

    # Start game
    game = GameService.start_game(game.id, admin_user.id)
    print(f"    Game started! Turn {game.current_turn}, Year {game.current_year}")
    print(f"    Galaxy: {game.galaxy.planet_count} planets")

    # Create default ship designs for all players
    print(f"    Creating default ship designs...")
    for player in game.players:
        designs = create_default_designs(player)
        print(f"      {player.player_name}: {len(designs)} designs")

    db.session.commit()
    return game


def show_game_state(game):
    """Display current game state."""
    print(f"\n{'='*60}")
    print(f"TURN {game.current_turn} - YEAR {game.current_year}")
    print(f"{'='*60}")

    players = list(game.players.filter_by(is_eliminated=False).all())
    players.sort(key=lambda p: p.planet_count, reverse=True)

    print(f"\n{'Player':<20} {'Planets':<10} {'Money':<10} {'Metal':<10} {'Fleets':<10}")
    print("-" * 60)

    for player in players:
        fleet_count = player.fleets.count()
        ai_marker = f" [{player.ai_difficulty}]" if player.is_ai else " [HUMAN]"
        print(f"{player.player_name:<20} {player.planet_count:<10} {player.money:<10} {player.metal:<10} {fleet_count:<10}{ai_marker}")

    # Show eliminated players
    eliminated = list(game.players.filter_by(is_eliminated=True).all())
    if eliminated:
        print(f"\nEliminated: {', '.join(p.player_name for p in eliminated)}")


def show_ai_analysis(player):
    """Show AI analysis for a player."""
    if not player.is_ai:
        return

    analysis = GameAnalysis.analyze(player)
    summary = analysis.get_summary()

    print(f"\n  [{player.player_name}] Analysis:")
    print(f"    Phase: {summary['phase']}")
    print(f"    Military advantage: {summary['military']['advantage']:.2f}")
    print(f"    Threats: {summary['threats']}, Opportunities: {summary['opportunities']}")
    print(f"    Metal scarcity: {summary['metal_scarcity']:.0%}")


def run_turn(game, verbose=True):
    """Process one turn."""
    print(f"\n[>] Processing turn {game.current_turn}...")

    # Show AI analysis before turn
    if verbose:
        for player in game.players.filter_by(is_eliminated=False, is_ai=True):
            show_ai_analysis(player)

    # Process turn
    results = TurnService.process_turn(game)

    # Refresh game from DB
    db.session.refresh(game)

    # Show results summary
    if results.get("combats"):
        print(f"    Combats: {len(results['combats'])}")
        for combat in results["combats"]:
            print(f"      - {combat.get('planet_name', '?')}: {combat.get('result', '?')}")

    if results.get("eliminations"):
        print(f"    Eliminations: {[e['player_name'] for e in results['eliminations']]}")

    # Show AI decisions
    if verbose and results.get("ai_decisions"):
        for player_id, ai_result in results["ai_decisions"].items():
            decisions = ai_result.get("decisions", {})
            movements = decisions.get("fleet_movements", [])
            if movements:
                player = GamePlayer.query.get(player_id)
                print(f"    [{player.player_name}] Fleet movements: {len(movements)}")

    return results


def check_victory(game):
    """Check if there's a winner."""
    result = TurnService.check_victory(game)
    if result:
        if result.get("winner"):
            print(f"\n{'*'*60}")
            print(f"VICTORY! {result['winner']['name']} wins!")
            print(f"Final turn: {result['final_turn']}, Year: {result['final_year']}")
            print(f"{'*'*60}")
        elif result.get("draw"):
            print(f"\n{'*'*60}")
            print(f"DRAW - Everyone eliminated!")
            print(f"{'*'*60}")
        return True
    return False


def run_game(num_turns=20, num_ai=3, galaxy_size="small", verbose=True):
    """Run a complete test game."""
    print("\n" + "="*60)
    print("COLONIE-IA - AI GAME TEST")
    print("="*60)

    # Create test user
    admin = create_test_user()

    # Create and start game
    game = create_ai_game(admin, num_ai_players=num_ai, galaxy_size=galaxy_size)
    game = start_game(game, admin)

    # Show initial state
    show_game_state(game)

    # Run turns
    for turn in range(num_turns):
        run_turn(game, verbose=verbose)
        show_game_state(game)

        # Check for victory
        if check_victory(game):
            break

        # Check if only one player left
        active_players = game.players.filter_by(is_eliminated=False).count()
        if active_players <= 1:
            check_victory(game)
            break

    print(f"\n[*] Test completed after {game.current_turn} turns")
    return game


def main():
    parser = argparse.ArgumentParser(description="Test AI game simulation")
    parser.add_argument("--turns", type=int, default=10, help="Number of turns to simulate")
    parser.add_argument("--ai", type=int, default=3, help="Number of AI players")
    parser.add_argument("--size", choices=["small", "medium", "large"], default="small", help="Galaxy size")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    # Create Flask app context
    app = create_app()

    with app.app_context():
        try:
            run_game(
                num_turns=args.turns,
                num_ai=args.ai,
                galaxy_size=args.size,
                verbose=not args.quiet,
            )
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
