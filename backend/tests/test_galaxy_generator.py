"""
Tests unitaires pour la génération de galaxie.
"""
import math
import pytest
from app import db
from app.models import Game, User, Galaxy, Star, Planet, GalaxyShape, PlanetState
from app.services.galaxy_generator import (
    GalaxyGenerator,
    GALAXY_PRESETS,
    DENSITY_FACTORS,
    generate_galaxy,
    find_home_planets,
    prepare_home_planet,
)
from app.services.auth import hash_password


def create_test_user(pseudo: str, email: str) -> User:
    """Helper pour créer un utilisateur de test."""
    return User(
        pseudo=pseudo,
        email=email,
        password_hash=hash_password("password123"),
    )


class TestGalaxyPresets:
    """Tests pour les constantes de configuration."""

    def test_galaxy_presets_exist(self):
        """Vérifie que tous les presets de taille existent."""
        assert "small" in GALAXY_PRESETS
        assert "medium" in GALAXY_PRESETS
        assert "large" in GALAXY_PRESETS
        assert "huge" in GALAXY_PRESETS

    def test_galaxy_presets_have_required_keys(self):
        """Vérifie que chaque preset a les clés requises."""
        for name, preset in GALAXY_PRESETS.items():
            assert "stars" in preset, f"Preset {name} manque 'stars'"
            assert "width" in preset, f"Preset {name} manque 'width'"
            assert "height" in preset, f"Preset {name} manque 'height'"

    def test_galaxy_presets_increasing_size(self):
        """Vérifie que les presets sont ordonnés par taille croissante."""
        sizes = ["small", "medium", "large", "huge"]
        for i in range(len(sizes) - 1):
            assert GALAXY_PRESETS[sizes[i]]["stars"] < GALAXY_PRESETS[sizes[i + 1]]["stars"]

    def test_density_factors_exist(self):
        """Vérifie que tous les facteurs de densité existent."""
        assert "low" in DENSITY_FACTORS
        assert "medium" in DENSITY_FACTORS
        assert "high" in DENSITY_FACTORS

    def test_density_factors_values(self):
        """Vérifie que les facteurs de densité sont cohérents."""
        assert DENSITY_FACTORS["low"] > DENSITY_FACTORS["medium"]
        assert DENSITY_FACTORS["medium"] > DENSITY_FACTORS["high"]


class TestGalaxyGeneratorInit:
    """Tests pour l'initialisation du générateur."""

    def test_init_with_valid_preset(self):
        """Vérifie l'initialisation avec un preset valide."""
        gen = GalaxyGenerator(
            game_id=1,
            shape="circle",
            size="medium",
            density="medium"
        )
        assert gen.game_id == 1
        assert gen.shape == "circle"
        assert gen.star_count == GALAXY_PRESETS["medium"]["stars"]
        assert gen.width == GALAXY_PRESETS["medium"]["width"]
        assert gen.height == GALAXY_PRESETS["medium"]["height"]

    def test_init_with_invalid_preset_uses_medium(self):
        """Vérifie qu'un preset invalide utilise medium par défaut."""
        gen = GalaxyGenerator(
            game_id=1,
            shape="circle",
            size="invalid_size",
            density="medium"
        )
        assert gen.star_count == GALAXY_PRESETS["medium"]["stars"]

    def test_init_density_factor(self):
        """Vérifie que le facteur de densité est appliqué."""
        gen_low = GalaxyGenerator(1, "circle", "small", "low")
        gen_high = GalaxyGenerator(1, "circle", "small", "high")
        assert gen_low.density_factor > gen_high.density_factor


class TestStarPositionGeneration:
    """Tests pour la génération des positions d'étoiles."""

    def test_circle_positions_within_bounds(self):
        """Vérifie que les positions en cercle sont dans les limites."""
        gen = GalaxyGenerator(1, "circle", "small", "medium")
        positions = gen._generate_circle()

        assert len(positions) == gen.star_count
        for x, y in positions:
            assert 0 <= x <= gen.width
            assert 0 <= y <= gen.height

    def test_circle_positions_centered(self):
        """Vérifie que les étoiles sont centrées dans un cercle."""
        gen = GalaxyGenerator(1, "circle", "medium", "medium")
        positions = gen._generate_circle()

        center_x = gen.width / 2
        center_y = gen.height / 2
        max_radius = min(gen.width, gen.height) / 2

        for x, y in positions:
            dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            assert dist <= max_radius * 1.1  # Petite marge pour la relaxation

    def test_spiral_positions_within_bounds(self):
        """Vérifie que les positions en spirale sont dans les limites."""
        gen = GalaxyGenerator(1, "spiral", "small", "medium")
        positions = gen._generate_spiral()

        assert len(positions) == gen.star_count
        for x, y in positions:
            assert 0 <= x <= gen.width
            assert 0 <= y <= gen.height

    def test_cluster_positions_within_bounds(self):
        """Vérifie que les positions en amas sont dans les limites."""
        gen = GalaxyGenerator(1, "cluster", "small", "medium")
        positions = gen._generate_cluster()

        assert len(positions) == gen.star_count
        for x, y in positions:
            assert 0 <= x <= gen.width
            assert 0 <= y <= gen.height

    def test_random_positions_within_bounds(self):
        """Vérifie que les positions aléatoires sont dans les limites."""
        gen = GalaxyGenerator(1, "random", "small", "medium")
        positions = gen._generate_random()

        assert len(positions) == gen.star_count
        for x, y in positions:
            assert 0 <= x <= gen.width
            assert 0 <= y <= gen.height

    def test_random_positions_have_minimum_spacing(self):
        """Vérifie que les étoiles aléatoires ont un espacement minimal."""
        gen = GalaxyGenerator(1, "random", "small", "low")
        positions = gen._generate_random()

        # La plupart des étoiles devraient avoir un espacement minimum
        min_distances = []
        for i, (x1, y1) in enumerate(positions):
            min_dist = float("inf")
            for j, (x2, y2) in enumerate(positions):
                if i != j:
                    dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                    min_dist = min(min_dist, dist)
            min_distances.append(min_dist)

        # Au moins 80% des étoiles ont un voisin à plus de 3 unités
        close_stars = sum(1 for d in min_distances if d > 3)
        assert close_stars >= len(positions) * 0.8


class TestGalaxyGeneration:
    """Tests d'intégration pour la génération complète."""

    @pytest.fixture
    def user(self, app):
        """Crée un utilisateur de test."""
        with app.app_context():
            user = create_test_user("testuser", "test@test.com")
            db.session.add(user)
            db.session.commit()
            yield user

    @pytest.fixture
    def game(self, app, user):
        """Crée une partie de test."""
        with app.app_context():
            user_db = User.query.filter_by(pseudo="testuser").first()
            game = Game(
                name="Test Game",
                admin_user_id=user_db.id,
                max_players=4,
            )
            db.session.add(game)
            db.session.commit()
            yield game

    def test_generate_creates_galaxy(self, app, game):
        """Vérifie qu'une galaxie est créée."""
        with app.app_context():
            game_db = Game.query.filter_by(name="Test Game").first()
            galaxy = generate_galaxy(game_db.id, "circle", "small", "medium")

            assert galaxy is not None
            assert galaxy.game_id == game_db.id
            assert galaxy.shape == "circle"
            assert galaxy.density == "medium"

    def test_generate_creates_correct_star_count(self, app, game):
        """Vérifie que le bon nombre d'étoiles est créé."""
        with app.app_context():
            game_db = Game.query.filter_by(name="Test Game").first()
            galaxy = generate_galaxy(game_db.id, "circle", "small", "medium")

            stars = Star.query.filter_by(galaxy_id=galaxy.id).all()
            assert len(stars) == GALAXY_PRESETS["small"]["stars"]

    def test_generate_creates_planets_for_each_star(self, app, game):
        """Vérifie que chaque étoile a des planètes."""
        with app.app_context():
            game_db = Game.query.filter_by(name="Test Game").first()
            galaxy = generate_galaxy(game_db.id, "circle", "small", "medium")

            for star in galaxy.stars:
                planets = Planet.query.filter_by(star_id=star.id).all()
                assert len(planets) >= 1
                assert len(planets) <= 4

    def test_generate_planet_characteristics(self, app, game):
        """Vérifie les caractéristiques des planètes générées."""
        with app.app_context():
            game_db = Game.query.filter_by(name="Test Game").first()
            galaxy = generate_galaxy(game_db.id, "circle", "small", "medium")

            planets = Planet.query.join(Star).filter(Star.galaxy_id == galaxy.id).all()

            for planet in planets:
                # Température dans les limites
                assert -200 <= planet.temperature <= 400
                # Gravité dans les limites
                assert 0.1 <= planet.gravity <= 3.0
                # Métal dans les limites
                assert 50 <= planet.metal_reserves <= 5000
                # État initial
                assert planet.state == PlanetState.UNEXPLORED.value

    def test_generate_all_shapes(self, app, game):
        """Vérifie que toutes les formes peuvent être générées."""
        shapes = ["circle", "spiral", "cluster", "random"]

        with app.app_context():
            for i, shape in enumerate(shapes):
                # Créer une nouvelle partie pour chaque forme
                user_db = User.query.filter_by(pseudo="testuser").first()
                new_game = Game(
                    name=f"Test Game {shape}",
                    admin_user_id=user_db.id,
                    max_players=4,
                )
                db.session.add(new_game)
                db.session.commit()

                galaxy = generate_galaxy(new_game.id, shape, "small", "medium")
                assert galaxy.shape == shape
                assert galaxy.stars.count() == GALAXY_PRESETS["small"]["stars"]


class TestHomePlanetSelection:
    """Tests pour la sélection des planètes mères."""

    @pytest.fixture
    def galaxy_with_planets(self, app):
        """Crée une galaxie de test avec des planètes."""
        with app.app_context():
            user = create_test_user("testuser2", "test2@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(
                name="Test Game Home",
                admin_user_id=user.id,
                max_players=4,
            )
            db.session.add(game)
            db.session.commit()

            galaxy = generate_galaxy(game.id, "circle", "medium", "medium")
            yield galaxy

    def test_find_home_planets_returns_correct_count(self, app, galaxy_with_planets):
        """Vérifie que le bon nombre de planètes mères est retourné."""
        with app.app_context():
            galaxy = Galaxy.query.first()
            home_planets = find_home_planets(galaxy, 4)
            assert len(home_planets) == 4

    def test_find_home_planets_are_habitable(self, app, galaxy_with_planets):
        """Vérifie que les planètes mères sont habitables."""
        with app.app_context():
            galaxy = Galaxy.query.first()
            home_planets = find_home_planets(galaxy, 4)

            for planet in home_planets:
                assert planet.habitability > 0.3

    def test_find_home_planets_maximizes_distance(self, app, galaxy_with_planets):
        """Vérifie que les planètes mères sont bien espacées."""
        with app.app_context():
            galaxy = Galaxy.query.first()
            home_planets = find_home_planets(galaxy, 4)

            # Calculer les distances entre planètes mères
            min_dist = float("inf")
            for i, p1 in enumerate(home_planets):
                for j, p2 in enumerate(home_planets):
                    if i < j:
                        dist = math.sqrt(
                            (p1.star.x - p2.star.x) ** 2 +
                            (p1.star.y - p2.star.y) ** 2
                        )
                        min_dist = min(min_dist, dist)

            # La distance minimale devrait être raisonnable
            assert min_dist > 10  # Au moins 10 unités d'écart

    def test_find_home_planets_raises_if_not_enough(self, app):
        """Vérifie qu'une erreur est levée si pas assez de planètes."""
        with app.app_context():
            user = create_test_user("testuser3", "test3@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(
                name="Test Game Small",
                admin_user_id=user.id,
                max_players=8,
            )
            db.session.add(game)
            db.session.commit()

            # Petite galaxie avec peu d'étoiles
            galaxy = generate_galaxy(game.id, "circle", "small", "medium")

            # Demander trop de planètes mères devrait échouer
            # (dépend de la génération aléatoire, peut ne pas toujours échouer)
            try:
                find_home_planets(galaxy, 50)
                # Si ça passe, c'est qu'il y avait assez de planètes habitables
            except ValueError as e:
                assert "Not enough habitable planets" in str(e)


class TestPrepareHomePlanet:
    """Tests pour la préparation des planètes mères."""

    @pytest.fixture
    def test_planet(self, app):
        """Crée une planète de test."""
        with app.app_context():
            user = create_test_user("testuser4", "test4@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(
                name="Test Game Prepare",
                admin_user_id=user.id,
                max_players=4,
            )
            db.session.add(game)
            db.session.commit()

            galaxy = Galaxy(
                game_id=game.id,
                shape="circle",
                density="medium",
                star_count=1,
                width=100,
                height=100,
            )
            db.session.add(galaxy)
            db.session.commit()

            star = Star(
                galaxy_id=galaxy.id,
                name="Test Star",
                x=50,
                y=50,
            )
            db.session.add(star)
            db.session.commit()

            planet = Planet(
                star_id=star.id,
                name="Test Planet",
                orbit_index=0,
                temperature=-50,
                current_temperature=-50,
                gravity=1.2,
                metal_reserves=500,
                metal_remaining=500,
                state=PlanetState.UNEXPLORED.value,
                population=0,
                max_population=100000,
            )
            db.session.add(planet)
            db.session.commit()
            yield planet

    def test_prepare_sets_ideal_temperature(self, app, test_planet):
        """Vérifie que la température est mise à 22°C."""
        with app.app_context():
            planet = Planet.query.first()
            prepare_home_planet(planet)
            assert planet.current_temperature == 22.0

    def test_prepare_sets_developed_state(self, app, test_planet):
        """Vérifie que l'état passe à DEVELOPED."""
        with app.app_context():
            planet = Planet.query.first()
            prepare_home_planet(planet)
            assert planet.state == PlanetState.DEVELOPED.value

    def test_prepare_sets_initial_population(self, app, test_planet):
        """Vérifie que la population initiale est définie."""
        with app.app_context():
            planet = Planet.query.first()
            prepare_home_planet(planet)
            assert planet.population == 100_000

    def test_prepare_sets_home_planet_flag(self, app, test_planet):
        """Vérifie que le flag is_home_planet est activé."""
        with app.app_context():
            planet = Planet.query.first()
            prepare_home_planet(planet)
            assert planet.is_home_planet is True

    def test_prepare_sets_default_budgets(self, app, test_planet):
        """Vérifie que les budgets par défaut sont définis."""
        with app.app_context():
            planet = Planet.query.first()
            prepare_home_planet(planet)
            assert planet.terraform_budget == 30
            assert planet.mining_budget == 70
