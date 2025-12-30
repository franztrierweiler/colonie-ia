"""
Tests unitaires pour le système de flottes.
"""
import pytest
from app import db
from app.models import (
    User, Game, GamePlayer, Galaxy, Star, Planet, PlanetState,
    Ship, ShipDesign, Fleet, ShipType, FleetStatus,
)
from app.services.fleet import FleetService, DISBAND_METAL_RECOVERY
from app.services.auth import hash_password


def create_test_user(pseudo: str, email: str) -> User:
    """Helper pour créer un utilisateur de test."""
    return User(
        pseudo=pseudo,
        email=email,
        password_hash=hash_password("password123"),
    )


class TestShipDesign:
    """Tests pour la création de designs de vaisseaux."""

    @pytest.fixture
    def game_setup(self, app):
        """Crée une configuration de jeu de test."""
        with app.app_context():
            user = create_test_user("designer", "designer@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Design Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Designer",
                color="#FF0000",
                money=10000,
                metal=500,
            )
            db.session.add(player)
            db.session.commit()

            yield {"user": user, "game": game, "player": player}

    def test_create_fighter_design(self, app, game_setup):
        """Création d'un design de chasseur."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Designer").first()

            design = FleetService.create_design(
                player=player,
                name="Fighter Mk1",
                ship_type=ShipType.FIGHTER,
                range_level=1,
                speed_level=1,
                weapons_level=1,
                shields_level=1,
                mini_level=1,
            )
            db.session.commit()

            assert design.name == "Fighter Mk1"
            assert design.ship_type == ShipType.FIGHTER.value
            assert design.production_cost_metal > 0
            assert design.production_cost_money > 0
            assert design.prototype_cost_metal == design.production_cost_metal * 2
            assert design.prototype_cost_money == design.production_cost_money * 2
            assert not design.is_prototype_built

    def test_create_scout_design(self, app, game_setup):
        """Création d'un design d'éclaireur avec bonus de portée."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Designer").first()

            design = FleetService.create_design(
                player=player,
                name="Scout Mk1",
                ship_type=ShipType.SCOUT,
            )
            db.session.commit()

            # Scout has +3 range bonus, base range = level * 5
            assert design.effective_range == (1 * 5) + 3  # (range_level * 5) + bonus

    def test_miniaturization_reduces_metal(self, app, game_setup):
        """La miniaturisation réduit le coût en métal."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Designer").first()

            # Design sans miniaturisation
            design_low = FleetService.create_design(
                player=player,
                name="Fighter Low Mini",
                ship_type=ShipType.FIGHTER,
                mini_level=1,
            )

            # Design avec haute miniaturisation
            design_high = FleetService.create_design(
                player=player,
                name="Fighter High Mini",
                ship_type=ShipType.FIGHTER,
                mini_level=5,
            )
            db.session.commit()

            # Miniaturisation réduit le métal, augmente l'argent
            assert design_high.production_cost_metal < design_low.production_cost_metal
            assert design_high.production_cost_money > design_low.production_cost_money

    def test_tech_levels_affect_cost(self, app, game_setup):
        """Niveaux tech plus élevés = coûts plus élevés."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Designer").first()

            design_low = FleetService.create_design(
                player=player,
                name="Fighter Low",
                ship_type=ShipType.FIGHTER,
                range_level=1,
                speed_level=1,
                weapons_level=1,
                shields_level=1,
            )

            design_high = FleetService.create_design(
                player=player,
                name="Fighter High",
                ship_type=ShipType.FIGHTER,
                range_level=5,
                speed_level=5,
                weapons_level=5,
                shields_level=5,
            )
            db.session.commit()

            assert design_high.production_cost_metal > design_low.production_cost_metal
            assert design_high.production_cost_money > design_low.production_cost_money


class TestShipConstruction:
    """Tests pour la construction de vaisseaux."""

    @pytest.fixture
    def construction_setup(self, app):
        """Setup pour les tests de construction."""
        with app.app_context():
            user = create_test_user("builder", "builder@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Build Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Builder",
                color="#00FF00",
                money=10000,
                metal=1000,
            )
            db.session.add(player)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium",
                          star_count=10, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            star = Star(galaxy_id=galaxy.id, name="Home Star", x=50, y=50)
            db.session.add(star)
            db.session.commit()

            planet = Planet(
                star_id=star.id,
                name="Home Planet",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.DEVELOPED.value,
                population=100000,
                max_population=1000000,
                owner_id=player.id,
            )
            db.session.add(planet)
            db.session.commit()

            # Create a design and fleet
            design = FleetService.create_design(
                player=player,
                name="Fighter Mk1",
                ship_type=ShipType.FIGHTER,
            )
            fleet = FleetService.create_fleet(player, "First Fleet", star, planet)
            db.session.commit()

            yield {
                "player": player,
                "design": design,
                "fleet": fleet,
                "planet": planet,
                "star": star,
                "design_id": design.id,
                "fleet_id": fleet.id,
            }

    def test_build_prototype(self, app, construction_setup):
        """Construction du prototype (premier vaisseau)."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Builder").first()
            design = ShipDesign.query.get(construction_setup["design_id"])
            fleet = Fleet.query.get(construction_setup["fleet_id"])

            initial_money = player.money
            initial_metal = player.metal
            proto_money = design.prototype_cost_money
            proto_metal = design.prototype_cost_metal

            success, message, ship = FleetService.build_prototype(player, design, fleet)
            db.session.commit()

            assert success, f"Build failed: {message}"
            assert ship is not None
            assert design.is_prototype_built
            assert player.money == initial_money - proto_money
            assert player.metal == initial_metal - proto_metal

    def test_build_production_after_prototype(self, app, construction_setup):
        """Construction de production après le prototype."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Builder").first()
            design = ShipDesign.query.get(construction_setup["design_id"])
            fleet = Fleet.query.get(construction_setup["fleet_id"])

            # Build prototype first
            FleetService.build_prototype(player, design, fleet)
            db.session.commit()

            initial_money = player.money
            initial_metal = player.metal
            prod_money = design.production_cost_money
            prod_metal = design.production_cost_metal

            # Build production ship
            success, message, ship = FleetService.build_ship(player, design, fleet)
            db.session.commit()

            assert success, f"Build failed: {message}"
            assert player.money == initial_money - prod_money
            assert player.metal == initial_metal - prod_metal

    def test_build_ships_batch(self, app, construction_setup):
        """Construction de plusieurs vaisseaux en lot."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Builder").first()
            design = ShipDesign.query.get(construction_setup["design_id"])
            fleet = Fleet.query.get(construction_setup["fleet_id"])

            success, message, ships = FleetService.build_ships(player, design, fleet, 3)
            db.session.commit()

            assert success, f"Build failed: {message}"
            assert len(ships) == 3

            # Refresh design to get updated count
            design = ShipDesign.query.get(construction_setup["design_id"])
            assert design.ships_built == 3

    def test_build_insufficient_resources(self, app, construction_setup):
        """Construction impossible sans ressources."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Builder").first()
            design = ShipDesign.query.get(construction_setup["design_id"])
            fleet = Fleet.query.get(construction_setup["fleet_id"])

            player.money = 0
            player.metal = 0

            success, message, ship = FleetService.build_ship(player, design, fleet)

            assert not success
            assert "enough" in message.lower()


class TestFleetManagement:
    """Tests pour la gestion des flottes."""

    @pytest.fixture
    def fleet_setup(self, app):
        """Setup pour les tests de flottes."""
        with app.app_context():
            user = create_test_user("admiral", "admiral@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Fleet Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Admiral",
                color="#0000FF",
                money=50000,
                metal=5000,
            )
            db.session.add(player)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium",
                          star_count=10, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            star1 = Star(galaxy_id=galaxy.id, name="Star Alpha", x=10, y=10)
            star2 = Star(galaxy_id=galaxy.id, name="Star Beta", x=50, y=50)
            db.session.add_all([star1, star2])
            db.session.commit()

            planet = Planet(
                star_id=star1.id,
                name="Alpha Prime",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.DEVELOPED.value,
                population=100000,
                max_population=1000000,
                owner_id=player.id,
            )
            db.session.add(planet)
            db.session.commit()

            # Create fleet with ships
            design = FleetService.create_design(player, "Fighter", ShipType.FIGHTER)
            fleet = FleetService.create_fleet(player, "Alpha Fleet", star1, planet)
            FleetService.build_ships(player, design, fleet, 5)
            db.session.commit()

            yield {
                "player_id": player.id,
                "fleet_id": fleet.id,
                "star1_id": star1.id,
                "star2_id": star2.id,
                "planet_id": planet.id,
                "design_id": design.id,
            }

    def test_split_fleet(self, app, fleet_setup):
        """Division d'une flotte."""
        with app.app_context():
            fleet = Fleet.query.get(fleet_setup["fleet_id"])
            ships = list(fleet.ships.filter_by(is_destroyed=False).limit(2))
            ship_ids = [s.id for s in ships]

            success, message, new_fleet = FleetService.split_fleet(
                fleet, ship_ids, "Beta Fleet"
            )
            db.session.commit()

            assert success, f"Split failed: {message}"
            assert new_fleet is not None
            assert new_fleet.name == "Beta Fleet"
            assert new_fleet.ship_count == 2

            # Refresh original fleet
            fleet = Fleet.query.get(fleet_setup["fleet_id"])
            assert fleet.ship_count == 3

    def test_merge_fleets(self, app, fleet_setup):
        """Fusion de deux flottes."""
        with app.app_context():
            player = GamePlayer.query.get(fleet_setup["player_id"])
            fleet1 = Fleet.query.get(fleet_setup["fleet_id"])
            star1 = Star.query.get(fleet_setup["star1_id"])
            design = ShipDesign.query.get(fleet_setup["design_id"])

            initial_count = fleet1.ship_count

            # Create second fleet at same location
            fleet2 = FleetService.create_fleet(player, "Gamma Fleet", star1)
            FleetService.build_ships(player, design, fleet2, 2)
            db.session.commit()

            success, message = FleetService.merge_fleets(fleet1, fleet2)
            db.session.commit()

            assert success, f"Merge failed: {message}"

            # Refresh fleet1
            fleet1 = Fleet.query.get(fleet_setup["fleet_id"])
            assert fleet1.ship_count == initial_count + 2

    def test_fleet_speed_limited_by_slowest(self, app, fleet_setup):
        """La vitesse de flotte est limitée par le vaisseau le plus lent."""
        with app.app_context():
            player = GamePlayer.query.get(fleet_setup["player_id"])
            fleet = Fleet.query.get(fleet_setup["fleet_id"])

            # Get initial speed (fighters only)
            initial_speed = fleet.fleet_speed

            # Create a slow colony ship design
            colony_design = FleetService.create_design(
                player, "Colony Ship", ShipType.COLONY
            )
            FleetService.build_ships(player, colony_design, fleet, 1)
            db.session.commit()

            # Refresh fleet
            fleet = Fleet.query.get(fleet_setup["fleet_id"])

            # Colony ships are slower (0.5 speed multiplier)
            assert fleet.fleet_speed < initial_speed  # Should be limited by colony ship


class TestFleetMovement:
    """Tests pour le déplacement des flottes."""

    @pytest.fixture
    def movement_setup(self, app):
        """Setup pour les tests de mouvement."""
        with app.app_context():
            user = create_test_user("navigator", "navigator@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Movement Game", admin_user_id=user.id, max_players=4,
                       current_turn=1)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Navigator",
                color="#FF00FF",
                money=50000,
                metal=5000,
            )
            db.session.add(player)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium",
                          star_count=10, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            # Two stars at known distance
            star_origin = Star(galaxy_id=galaxy.id, name="Origin", x=0, y=0)
            star_near = Star(galaxy_id=galaxy.id, name="Near", x=5, y=0)  # distance 5
            star_far = Star(galaxy_id=galaxy.id, name="Far", x=50, y=0)  # distance 50
            db.session.add_all([star_origin, star_near, star_far])
            db.session.commit()

            planet = Planet(
                star_id=star_origin.id,
                name="Origin Planet",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.DEVELOPED.value,
                population=100000,
                max_population=1000000,
                owner_id=player.id,
            )
            db.session.add(planet)
            db.session.commit()

            design = FleetService.create_design(player, "Fighter", ShipType.FIGHTER)
            fleet = FleetService.create_fleet(player, "Mobile Fleet", star_origin, planet)
            FleetService.build_ships(player, design, fleet, 3)
            fleet.fuel_remaining = 20  # Enough for near, not for far
            fleet.max_fuel = 20
            db.session.commit()

            yield {
                "game_id": game.id,
                "player_id": player.id,
                "fleet_id": fleet.id,
                "star_origin_id": star_origin.id,
                "star_near_id": star_near.id,
                "star_far_id": star_far.id,
                "planet_id": planet.id,
            }

    def test_move_to_reachable_destination(self, app, movement_setup):
        """Déplacement vers une destination accessible."""
        with app.app_context():
            fleet = Fleet.query.get(movement_setup["fleet_id"])
            star_near = Star.query.get(movement_setup["star_near_id"])
            game = Game.query.get(movement_setup["game_id"])

            success, message = FleetService.move_fleet(fleet, star_near, game.current_turn)
            db.session.commit()

            assert success, f"Move failed: {message}"
            assert fleet.status == FleetStatus.IN_TRANSIT.value
            assert fleet.destination_star_id == star_near.id

    def test_cannot_move_to_unreachable_destination(self, app, movement_setup):
        """Impossible de se déplacer vers une destination hors de portée."""
        with app.app_context():
            fleet = Fleet.query.get(movement_setup["fleet_id"])
            star_far = Star.query.get(movement_setup["star_far_id"])
            game = Game.query.get(movement_setup["game_id"])

            success, message = FleetService.move_fleet(fleet, star_far, game.current_turn)

            assert not success
            assert "fuel" in message.lower() or "far" in message.lower() or "range" in message.lower()

    def test_fleet_arrival(self, app, movement_setup):
        """Arrivée de flotte après trajet."""
        with app.app_context():
            fleet = Fleet.query.get(movement_setup["fleet_id"])
            star_near = Star.query.get(movement_setup["star_near_id"])
            game = Game.query.get(movement_setup["game_id"])

            # Start movement
            success, message = FleetService.move_fleet(fleet, star_near, game.current_turn)
            assert success, f"Move failed: {message}"
            arrival_turn = fleet.arrival_turn
            db.session.commit()

            # Process movements at arrival turn
            results = FleetService.process_fleet_movements(game.id, arrival_turn)

            # Refresh fleet
            fleet = Fleet.query.get(movement_setup["fleet_id"])
            assert len(results["arrivals"]) == 1
            assert fleet.status == FleetStatus.STATIONED.value
            assert fleet.current_star_id == star_near.id


class TestDisbanding:
    """Tests pour le démantèlement de vaisseaux."""

    @pytest.fixture
    def disband_setup(self, app):
        """Setup pour les tests de démantèlement."""
        with app.app_context():
            user = create_test_user("scrapper", "scrapper@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Disband Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Scrapper",
                color="#FFFF00",
                money=50000,
                metal=1000,
            )
            db.session.add(player)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium",
                          star_count=10, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            star = Star(galaxy_id=galaxy.id, name="Scrap Star", x=50, y=50)
            db.session.add(star)
            db.session.commit()

            planet = Planet(
                star_id=star.id,
                name="Scrap Planet",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.DEVELOPED.value,
                population=100000,
                max_population=1000000,
                owner_id=player.id,
            )
            db.session.add(planet)
            db.session.commit()

            design = FleetService.create_design(player, "Scrappable", ShipType.FIGHTER)
            fleet = FleetService.create_fleet(player, "Scrap Fleet", star, planet)
            FleetService.build_ships(player, design, fleet, 3)
            db.session.commit()

            yield {
                "player_id": player.id,
                "fleet_id": fleet.id,
                "design_id": design.id,
                "planet_id": planet.id,
            }

    def test_disband_ship_recovers_metal(self, app, disband_setup):
        """Démantèlement récupère 75% du métal."""
        with app.app_context():
            player = GamePlayer.query.get(disband_setup["player_id"])
            fleet = Fleet.query.get(disband_setup["fleet_id"])
            design = ShipDesign.query.get(disband_setup["design_id"])
            ship = fleet.ships.filter_by(is_destroyed=False).first()

            assert ship is not None, "No ships in fleet"

            initial_metal = player.metal
            expected_recovery = int(design.production_cost_metal * DISBAND_METAL_RECOVERY)

            success, message, metal_recovered = FleetService.disband_ship(ship)
            db.session.commit()

            assert success, f"Disband failed: {message}"
            assert metal_recovered == expected_recovery
            assert player.metal == initial_metal + expected_recovery
            assert ship.is_destroyed

    def test_disband_fleet(self, app, disband_setup):
        """Démantèlement de toute la flotte."""
        with app.app_context():
            player = GamePlayer.query.get(disband_setup["player_id"])
            fleet = Fleet.query.get(disband_setup["fleet_id"])

            initial_metal = player.metal
            ship_count = fleet.ship_count

            success, message, total_metal = FleetService.disband_fleet(fleet)
            db.session.commit()

            assert success, f"Disband failed: {message}"
            assert total_metal > 0
            assert player.metal == initial_metal + total_metal
            assert str(ship_count) in message

    def test_cannot_disband_in_transit(self, app, disband_setup):
        """Impossible de démanteler en transit."""
        with app.app_context():
            fleet = Fleet.query.get(disband_setup["fleet_id"])
            fleet.status = FleetStatus.IN_TRANSIT.value
            db.session.commit()

            ship = fleet.ships.filter_by(is_destroyed=False).first()
            assert ship is not None, "No ships in fleet"

            success, message, metal = FleetService.disband_ship(ship)

            assert not success
            assert "transit" in message.lower()
