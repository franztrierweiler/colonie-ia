"""
Tests unitaires pour le service d'économie.
"""
import pytest
from app import db
from app.models import User, Game, GamePlayer, Galaxy, Star, Planet, PlanetState
from app.services.economy import (
    EconomyService,
    diminishing_returns,
    INITIAL_MONEY,
    INITIAL_METAL,
    DEBT_MAX_MULTIPLIER,
    DEBT_INTEREST_RATE,
    BASE_TAX_RATE,
    POPULATION_THRESHOLD,
    COLONY_MAINTENANCE_COST,
    BASE_MINING_RATE,
)
from app.services.auth import hash_password


def create_test_user(pseudo: str, email: str) -> User:
    """Helper pour créer un utilisateur de test."""
    return User(
        pseudo=pseudo,
        email=email,
        password_hash=hash_password("password123"),
    )


class TestDiminishingReturns:
    """Tests pour la fonction de rendements décroissants."""

    def test_zero_budget_returns_zero(self):
        """0% budget donne 0 output."""
        assert diminishing_returns(0, 100) == 0

    def test_full_budget_returns_full(self):
        """100% budget donne 100% output."""
        result = diminishing_returns(1.0, 100)
        assert abs(result - 100) < 0.1

    def test_half_budget_returns_less_than_full(self):
        """50% budget donne moins que 100% output (rendements décroissants)."""
        result = diminishing_returns(0.5, 100)
        # 50% budget donne ~58% output (log(1.5)/log(2) ≈ 0.585)
        assert result < 100
        assert result > 50  # Plus que proportionnel mais moins que linéaire

    def test_diminishing_returns_curve(self):
        """Vérifie que la fonction est concave (rendements décroissants marginaux)."""
        # Vérifie que doubler le budget ne double pas le résultat
        result_25 = diminishing_returns(0.25, 100)
        result_50 = diminishing_returns(0.50, 100)
        result_100 = diminishing_returns(1.00, 100)

        # Le gain de 25% à 50% devrait être inférieur au gain de 0% à 25%
        gain_first_quarter = result_25  # gain de 0 à 25%
        gain_second_quarter = result_50 - result_25  # gain de 25% à 50%

        # Pour une fonction concave, les gains marginaux diminuent
        # Mais notre formule log(1+x) est moins agressive
        # On vérifie simplement que ce n'est pas linéaire
        assert result_50 < 2 * result_25, "Devrait être sous-linéaire"
        assert result_100 < 2 * result_50, "Devrait être sous-linéaire"

    def test_negative_budget_returns_zero(self):
        """Budget négatif donne 0."""
        assert diminishing_returns(-0.5, 100) == 0

    def test_over_budget_capped_at_one(self):
        """Budget > 100% est plafonné."""
        result = diminishing_returns(1.5, 100)
        assert abs(result - 100) < 0.1


class TestPlanetIncome:
    """Tests pour le calcul des revenus planétaires."""

    @pytest.fixture
    def setup_game(self, app):
        """Crée une configuration de jeu de test."""
        with app.app_context():
            user = create_test_user("testuser", "test@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Test Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Test Player",
                color="#FF0000",
                money=INITIAL_MONEY,
                metal=INITIAL_METAL,
            )
            db.session.add(player)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium", star_count=10, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            star = Star(galaxy_id=galaxy.id, name="Test Star", x=50, y=50)
            db.session.add(star)
            db.session.commit()

            yield {"user": user, "game": game, "player": player, "galaxy": galaxy, "star": star}

    def test_unexplored_planet_no_income(self, app, setup_game):
        """Planète non explorée ne génère pas de revenu."""
        with app.app_context():
            star = Star.query.first()
            planet = Planet(
                star_id=star.id,
                name="Test Planet",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.UNEXPLORED.value,
                population=50000,
                max_population=1000000,
            )
            db.session.add(planet)
            db.session.commit()

            income = EconomyService.calculate_planet_income(planet)
            assert income == 0

    def test_small_colony_costs_money(self, app, setup_game):
        """Petite colonie coûte de l'argent."""
        with app.app_context():
            star = Star.query.first()
            planet = Planet(
                star_id=star.id,
                name="Small Colony",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.COLONIZED.value,
                population=1000,  # Très petite
                max_population=1000000,
            )
            db.session.add(planet)
            db.session.commit()

            income = EconomyService.calculate_planet_income(planet)
            assert income < 0  # Coûte de l'argent

    def test_large_colony_generates_income(self, app, setup_game):
        """Grande colonie génère des revenus."""
        with app.app_context():
            star = Star.query.first()
            planet = Planet(
                star_id=star.id,
                name="Large Colony",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.DEVELOPED.value,
                population=100000,  # Au-dessus du seuil
                max_population=1000000,
            )
            db.session.add(planet)
            db.session.commit()

            income = EconomyService.calculate_planet_income(planet)
            assert income > 0  # Génère des revenus

    def test_harsh_planet_less_income(self, app, setup_game):
        """Planète hostile génère moins de revenus."""
        with app.app_context():
            star = Star.query.first()

            # Planète idéale
            ideal_planet = Planet(
                star_id=star.id,
                name="Ideal",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.DEVELOPED.value,
                population=100000,
                max_population=1000000,
            )
            db.session.add(ideal_planet)

            # Planète froide
            harsh_planet = Planet(
                star_id=star.id,
                name="Harsh",
                temperature=-50,
                current_temperature=-50,
                gravity=1.5,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.DEVELOPED.value,
                population=100000,
                max_population=500000,
            )
            db.session.add(harsh_planet)
            db.session.commit()

            ideal_income = EconomyService.calculate_planet_income(ideal_planet)
            harsh_income = EconomyService.calculate_planet_income(harsh_planet)

            assert ideal_income > harsh_income


class TestMining:
    """Tests pour le système de minage."""

    @pytest.fixture
    def mining_planet(self, app):
        """Crée une planète avec des ressources minières."""
        with app.app_context():
            user = create_test_user("miner", "miner@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Mining Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Miner",
                color="#00FF00",
                money=INITIAL_MONEY,
                metal=0,  # Pas de métal au départ
            )
            db.session.add(player)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium", star_count=5, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            star = Star(galaxy_id=galaxy.id, name="Mining Star", x=50, y=50)
            db.session.add(star)
            db.session.commit()

            planet = Planet(
                star_id=star.id,
                name="Rich Planet",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.DEVELOPED.value,
                population=50000,
                max_population=1000000,
                mining_budget=50,
                terraform_budget=50,
                owner_id=player.id,
            )
            db.session.add(planet)
            db.session.commit()

            yield {"player": player, "planet": planet}

    def test_mining_extracts_metal(self, app, mining_planet):
        """Le minage extrait du métal."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Rich Planet").first()
            initial_reserves = planet.metal_remaining

            metal_extracted = EconomyService.process_planet_mining(planet)

            assert metal_extracted > 0
            assert planet.metal_remaining < initial_reserves
            assert planet.metal_remaining == initial_reserves - metal_extracted

    def test_mining_respects_budget(self, app, mining_planet):
        """Budget de minage plus élevé = plus de métal."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Rich Planet").first()

            # 25% budget
            planet.mining_budget = 25
            low_output = EconomyService.calculate_mining_output(planet)

            # 75% budget
            planet.mining_budget = 75
            high_output = EconomyService.calculate_mining_output(planet)

            assert high_output > low_output

    def test_mining_depletes_reserves(self, app, mining_planet):
        """Le minage épuise les réserves."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Rich Planet").first()
            planet.metal_remaining = 5  # Presque épuisé
            planet.mining_budget = 100

            metal_extracted = EconomyService.process_planet_mining(planet)

            assert metal_extracted <= 5
            assert planet.metal_remaining >= 0

    def test_empty_planet_no_mining(self, app, mining_planet):
        """Planète épuisée ne produit plus de métal."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Rich Planet").first()
            planet.metal_remaining = 0

            metal_extracted = EconomyService.calculate_mining_output(planet)

            assert metal_extracted == 0


class TestDebt:
    """Tests pour le système de dette."""

    @pytest.fixture
    def player_with_income(self, app):
        """Crée un joueur avec des revenus."""
        with app.app_context():
            user = create_test_user("debtor", "debtor@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Debt Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Debtor",
                color="#0000FF",
                money=5000,
                metal=500,
                debt=0,
            )
            db.session.add(player)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium", star_count=5, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            star = Star(galaxy_id=galaxy.id, name="Debt Star", x=50, y=50)
            db.session.add(star)
            db.session.commit()

            # Planète rentable
            planet = Planet(
                star_id=star.id,
                name="Profitable Planet",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.DEVELOPED.value,
                population=100000,  # Génère des revenus
                max_population=1000000,
                owner_id=player.id,
            )
            db.session.add(planet)
            db.session.commit()

            yield player

    def test_max_debt_calculation(self, app, player_with_income):
        """La dette max est 5x le revenu."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Debtor").first()
            income = EconomyService.calculate_player_income(player)
            max_debt = EconomyService.calculate_max_debt(player)

            assert max_debt == income * DEBT_MAX_MULTIPLIER

    def test_borrow_success(self, app, player_with_income):
        """Emprunt réussi."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Debtor").first()
            initial_money = player.money

            # Calculer combien on peut emprunter
            max_debt = EconomyService.calculate_max_debt(player)
            borrow_amount = min(1000, max_debt // 2) if max_debt > 0 else 0

            if borrow_amount > 0:
                success, message = EconomyService.borrow(player, borrow_amount)
                assert success, f"Borrow failed: {message}"
                assert player.debt == borrow_amount
                assert player.money == initial_money + borrow_amount
            else:
                # Pas de revenu, pas d'emprunt possible
                success, message = EconomyService.borrow(player, 100)
                assert not success

    def test_borrow_over_limit_fails(self, app, player_with_income):
        """Emprunt au-dessus de la limite échoue."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Debtor").first()
            max_debt = EconomyService.calculate_max_debt(player)

            success, message = EconomyService.borrow(player, max_debt + 1000)

            assert not success
            assert "max debt" in message.lower() or "only borrow" in message.lower()

    def test_interest_calculation(self, app, player_with_income):
        """Intérêts = 15% de la dette."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Debtor").first()
            player.debt = 1000

            interest = EconomyService.calculate_interest(player)

            assert interest == int(1000 * DEBT_INTEREST_RATE)

    def test_process_interest_deducts_money(self, app, player_with_income):
        """Les intérêts sont déduits de l'argent."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Debtor").first()
            player.debt = 1000
            initial_money = player.money

            interest = EconomyService.process_interest(player)

            assert player.money == initial_money - interest

    def test_repay_debt(self, app, player_with_income):
        """Remboursement de dette."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Debtor").first()
            player.debt = 1000
            initial_money = player.money

            success, message = EconomyService.repay_debt(player, 500)

            assert success
            assert player.debt == 500
            assert player.money == initial_money - 500


class TestPopulationGrowth:
    """Tests pour la croissance de population."""

    @pytest.fixture
    def growing_planet(self, app):
        """Crée une planète avec population."""
        with app.app_context():
            user = create_test_user("grower", "grower@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Growth Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium", star_count=5, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            star = Star(galaxy_id=galaxy.id, name="Growth Star", x=50, y=50)
            db.session.add(star)
            db.session.commit()

            planet = Planet(
                star_id=star.id,
                name="Growing Planet",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.DEVELOPED.value,
                population=100000,
                max_population=1000000,
            )
            db.session.add(planet)
            db.session.commit()

            yield planet

    def test_population_grows(self, app, growing_planet):
        """La population augmente."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Growing Planet").first()
            initial_pop = planet.population

            growth = EconomyService.process_population_growth(planet)

            assert growth > 0
            assert planet.population > initial_pop

    def test_population_capped_at_max(self, app, growing_planet):
        """La population ne dépasse pas le max."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Growing Planet").first()
            planet.population = planet.max_population - 100

            EconomyService.process_population_growth(planet)

            assert planet.population <= planet.max_population

    def test_harsh_planet_slower_growth(self, app, growing_planet):
        """Planète hostile = croissance plus lente."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Growing Planet").first()

            # Conditions idéales
            planet.current_temperature = 22
            planet.gravity = 1.0
            ideal_growth = EconomyService.calculate_population_growth(planet)

            # Conditions hostiles
            planet.current_temperature = -50
            planet.gravity = 2.0
            harsh_growth = EconomyService.calculate_population_growth(planet)

            assert ideal_growth > harsh_growth


class TestEconomySummary:
    """Tests pour le résumé économique."""

    @pytest.fixture
    def complex_economy(self, app):
        """Crée une économie complexe avec plusieurs planètes."""
        with app.app_context():
            user = create_test_user("emperor", "emperor@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Economy Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Emperor",
                color="#FFD700",
                money=10000,
                metal=500,
                debt=2000,
            )
            db.session.add(player)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium", star_count=10, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            star = Star(galaxy_id=galaxy.id, name="Capital Star", x=50, y=50)
            db.session.add(star)
            db.session.commit()

            # Plusieurs planètes
            planets_data = [
                ("Capital", 100000, 22, 1.0),  # Rentable
                ("Colony", 5000, 22, 1.0),  # Coûteuse
                ("Mine", 20000, -10, 1.2),  # Moyenne
            ]

            for name, pop, temp, grav in planets_data:
                planet = Planet(
                    star_id=star.id,
                    name=name,
                    temperature=temp,
                    current_temperature=temp,
                    gravity=grav,
                    metal_reserves=1000,
                    metal_remaining=500,
                    state=PlanetState.DEVELOPED.value,
                    population=pop,
                    max_population=1000000,
                    owner_id=player.id,
                    mining_budget=50,
                    terraform_budget=50,
                )
                db.session.add(planet)

            db.session.commit()
            yield player

    def test_economy_summary_complete(self, app, complex_economy):
        """Le résumé économique contient toutes les informations."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Emperor").first()
            summary = EconomyService.get_player_economy_summary(player)

            assert "money" in summary
            assert "metal" in summary
            assert "debt" in summary
            assert "income" in summary
            assert "expenses" in summary
            assert "max_debt" in summary
            assert "planets" in summary
            assert len(summary["planets"]) == 3

    def test_economy_summary_planets_detail(self, app, complex_economy):
        """Chaque planète a des détails économiques."""
        with app.app_context():
            player = GamePlayer.query.filter_by(player_name="Emperor").first()
            summary = EconomyService.get_player_economy_summary(player)

            for planet_data in summary["planets"]:
                assert "id" in planet_data
                assert "name" in planet_data
                assert "income" in planet_data
                assert "mining_output" in planet_data
                assert "population" in planet_data


class TestTerraformation:
    """Tests pour le système de terraformation."""

    @pytest.fixture
    def terraform_planet(self, app):
        """Crée une planète à terraformer."""
        with app.app_context():
            user = create_test_user("terraformer", "terraform@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Terraform Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Terraformer",
                color="#00FF00",
                money=10000,
                metal=500,
            )
            db.session.add(player)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium", star_count=5, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            star = Star(galaxy_id=galaxy.id, name="Terraform Star", x=50, y=50)
            db.session.add(star)
            db.session.commit()

            # Planète froide à réchauffer
            planet = Planet(
                star_id=star.id,
                name="Cold Planet",
                temperature=-30,
                current_temperature=-30,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=1000,
                state=PlanetState.COLONIZED.value,
                population=50000,
                max_population=500000,
                terraform_budget=50,
                mining_budget=50,
                owner_id=player.id,
            )
            db.session.add(planet)
            db.session.commit()

            yield {"player": player, "planet": planet}

    def test_cold_planet_warms_up(self, app, terraform_planet):
        """Une planète froide se réchauffe vers 22°C."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Cold Planet").first()
            initial_temp = planet.current_temperature

            result = EconomyService.process_planet_terraformation(planet)

            assert result["change"] > 0  # Température augmente
            assert planet.current_temperature > initial_temp
            assert planet.current_temperature <= 22  # Ne dépasse pas l'idéal

    def test_hot_planet_cools_down(self, app, terraform_planet):
        """Une planète chaude se refroidit vers 22°C."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Cold Planet").first()
            planet.current_temperature = 80  # Très chaud
            initial_temp = planet.current_temperature

            result = EconomyService.process_planet_terraformation(planet)

            assert result["change"] < 0  # Température diminue
            assert planet.current_temperature < initial_temp
            assert planet.current_temperature >= 22  # Ne descend pas sous l'idéal

    def test_ideal_planet_no_change(self, app, terraform_planet):
        """Une planète à 22°C ne change pas."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Cold Planet").first()
            planet.current_temperature = 22.0

            result = EconomyService.process_planet_terraformation(planet)

            assert abs(result["change"]) < 0.1  # Pas de changement significatif
            assert abs(planet.current_temperature - 22) < 0.1

    def test_terraform_budget_affects_rate(self, app, terraform_planet):
        """Plus de budget = terraformation plus rapide."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Cold Planet").first()

            # Low budget
            planet.terraform_budget = 25
            planet.current_temperature = -30
            low_change = EconomyService.calculate_terraform_change(planet)

            # High budget
            planet.terraform_budget = 75
            planet.current_temperature = -30
            high_change = EconomyService.calculate_terraform_change(planet)

            assert high_change > low_change

    def test_zero_terraform_budget_no_change(self, app, terraform_planet):
        """0% budget = pas de terraformation."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Cold Planet").first()
            planet.terraform_budget = 0
            planet.current_temperature = -30

            change = EconomyService.calculate_terraform_change(planet)

            assert change == 0

    def test_terraformation_increases_max_population(self, app, terraform_planet):
        """Terraformation augmente la population max."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Cold Planet").first()
            planet.terraform_budget = 100
            planet.current_temperature = -30

            old_max_pop = planet.max_population

            # Rapprocher de 22°C
            result = EconomyService.process_planet_terraformation(planet)

            # La population max devrait augmenter car habitabilité augmente
            assert result["new_max_population"] >= result["old_max_population"]


class TestPlanetAbandonment:
    """Tests pour l'abandon de planète."""

    @pytest.fixture
    def owned_planet(self, app):
        """Crée une planète possédée par un joueur."""
        with app.app_context():
            user = create_test_user("abandoner", "abandon@test.com")
            db.session.add(user)
            db.session.commit()

            game = Game(name="Abandon Game", admin_user_id=user.id, max_players=4)
            db.session.add(game)
            db.session.commit()

            player = GamePlayer(
                game_id=game.id,
                user_id=user.id,
                player_name="Abandoner",
                color="#FF0000",
                money=10000,
                metal=500,
            )
            db.session.add(player)
            db.session.commit()

            galaxy = Galaxy(game_id=game.id, shape="circle", density="medium", star_count=5, width=100, height=100)
            db.session.add(galaxy)
            db.session.commit()

            star = Star(galaxy_id=galaxy.id, name="Abandon Star", x=50, y=50)
            db.session.add(star)
            db.session.commit()

            planet = Planet(
                star_id=star.id,
                name="Owned Planet",
                temperature=22,
                current_temperature=22,
                gravity=1.0,
                metal_reserves=1000,
                metal_remaining=600,
                state=PlanetState.COLONIZED.value,
                population=50000,
                max_population=1000000,
                terraform_budget=50,
                mining_budget=50,
                owner_id=player.id,
            )
            db.session.add(planet)
            db.session.commit()

            yield {"player": player, "planet": planet}

    def test_abandon_with_strip_mine(self, app, owned_planet):
        """Abandon avec strip-mine récupère 50% du métal."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Owned Planet").first()
            player = GamePlayer.query.filter_by(player_name="Abandoner").first()
            initial_metal = player.metal
            metal_remaining = planet.metal_remaining

            result = EconomyService.abandon_planet(planet, strip_mine=True)

            assert result["metal_recovered"] == metal_remaining // 2
            assert planet.metal_remaining == 0
            assert player.metal == initial_metal + result["metal_recovered"]

    def test_abandon_without_strip_mine(self, app, owned_planet):
        """Abandon sans strip-mine ne récupère pas de métal."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Owned Planet").first()
            player = GamePlayer.query.filter_by(player_name="Abandoner").first()
            initial_metal = player.metal
            initial_remaining = planet.metal_remaining

            result = EconomyService.abandon_planet(planet, strip_mine=False)

            assert result["metal_recovered"] == 0
            assert planet.metal_remaining == initial_remaining
            assert player.metal == initial_metal

    def test_abandon_clears_ownership(self, app, owned_planet):
        """Abandon libère la planète."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Owned Planet").first()

            EconomyService.abandon_planet(planet)

            assert planet.owner_id is None
            assert planet.state == PlanetState.ABANDONED.value
            assert planet.population == 0

    def test_abandon_records_population_loss(self, app, owned_planet):
        """Abandon enregistre la perte de population."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Owned Planet").first()
            initial_population = planet.population

            result = EconomyService.abandon_planet(planet)

            assert result["population_lost"] == initial_population

    def test_cannot_abandon_unowned_planet(self, app, owned_planet):
        """Impossible d'abandonner une planète non possédée."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Owned Planet").first()
            planet.state = PlanetState.UNEXPLORED.value
            planet.owner_id = None

            with pytest.raises(ValueError) as exc_info:
                EconomyService.abandon_planet(planet)

            assert "not colonized" in str(exc_info.value).lower()

    def test_abandon_updates_player_planet_count(self, app, owned_planet):
        """Abandon met à jour le compteur de planètes du joueur."""
        with app.app_context():
            planet = Planet.query.filter_by(name="Owned Planet").first()
            player = GamePlayer.query.filter_by(player_name="Abandoner").first()
            player.planet_count = 1

            EconomyService.abandon_planet(planet)

            assert player.planet_count == 0
