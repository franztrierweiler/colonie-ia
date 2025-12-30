"""
Galaxy generation service.
Generates galaxies with different shapes and distributes stars/planets.
"""
import math
import random
from typing import List, Tuple

from app import db
from app.models import Galaxy, Star, Planet, GalaxyShape, GalaxyDensity, PlanetState
from app.data import STAR_NAMES, PLANET_SUFFIXES, get_random_star_name


# Galaxy size presets
GALAXY_PRESETS = {
    "small": {"stars": 20, "width": 100, "height": 100},
    "medium": {"stars": 50, "width": 200, "height": 200},
    "large": {"stars": 100, "width": 300, "height": 300},
    "huge": {"stars": 200, "width": 500, "height": 500},
}

# Density factors (affects minimum distance between stars)
DENSITY_FACTORS = {
    GalaxyDensity.LOW.value: 1.5,
    GalaxyDensity.MEDIUM.value: 1.0,
    GalaxyDensity.HIGH.value: 0.7,
}


class GalaxyGenerator:
    """Service for generating galaxies."""

    def __init__(self, game_id: int, shape: str, size: str, density: str):
        """
        Initialize generator.

        Args:
            game_id: ID of the game this galaxy belongs to
            shape: Galaxy shape (circle, spiral, cluster, random)
            size: Galaxy size preset (small, medium, large, huge)
            density: Star density (low, medium, high)
        """
        self.game_id = game_id
        self.shape = shape
        self.density = density

        preset = GALAXY_PRESETS.get(size, GALAXY_PRESETS["medium"])
        self.star_count = preset["stars"]
        self.width = preset["width"]
        self.height = preset["height"]

        self.density_factor = DENSITY_FACTORS.get(density, 1.0)
        self.used_star_names: set = set()

    def generate(self) -> Galaxy:
        """Generate the complete galaxy with stars and planets."""
        # Create galaxy record
        galaxy = Galaxy(
            game_id=self.game_id,
            shape=self.shape,
            density=self.density,
            star_count=self.star_count,
            width=self.width,
            height=self.height,
        )
        db.session.add(galaxy)
        db.session.flush()  # Get galaxy ID

        # Generate star positions based on shape
        positions = self._generate_star_positions()

        # Create stars with planets
        for i, (x, y) in enumerate(positions):
            star = self._create_star(galaxy.id, x, y)
            db.session.add(star)
            db.session.flush()  # Get star ID

            # Generate planets for this star
            planets = self._generate_planets(star.id)
            for planet in planets:
                db.session.add(planet)

        db.session.commit()
        return galaxy

    def _generate_star_positions(self) -> List[Tuple[float, float]]:
        """Generate star positions based on galaxy shape."""
        generators = {
            GalaxyShape.CIRCLE.value: self._generate_circle,
            GalaxyShape.SPIRAL.value: self._generate_spiral,
            GalaxyShape.CLUSTER.value: self._generate_cluster,
            GalaxyShape.RANDOM.value: self._generate_random,
        }

        generator = generators.get(self.shape, self._generate_random)
        return generator()

    def _generate_circle(self) -> List[Tuple[float, float]]:
        """Generate stars in a circular distribution."""
        positions = []
        center_x = self.width / 2
        center_y = self.height / 2
        max_radius = min(self.width, self.height) / 2 * 0.9

        for _ in range(self.star_count):
            # Random angle and radius (sqrt for uniform distribution in disk)
            angle = random.uniform(0, 2 * math.pi)
            radius = max_radius * math.sqrt(random.uniform(0, 1))

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions.append((x, y))

        return self._apply_minimum_distance(positions)

    def _generate_spiral(self) -> List[Tuple[float, float]]:
        """Generate stars in a spiral galaxy pattern."""
        positions = []
        center_x = self.width / 2
        center_y = self.height / 2
        max_radius = min(self.width, self.height) / 2 * 0.85

        num_arms = random.randint(2, 4)
        arm_spread = 0.4  # How spread out the arms are
        rotation_factor = 3.0  # How tightly wound the spiral is

        for i in range(self.star_count):
            # Assign to an arm
            arm = i % num_arms
            arm_offset = (2 * math.pi / num_arms) * arm

            # Distance from center (more stars near center)
            t = random.uniform(0, 1)
            radius = max_radius * t

            # Base angle for spiral
            angle = arm_offset + rotation_factor * t

            # Add some randomness
            angle += random.gauss(0, arm_spread)
            radius += random.gauss(0, max_radius * 0.05)

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # Clamp to bounds
            x = max(5, min(self.width - 5, x))
            y = max(5, min(self.height - 5, y))

            positions.append((x, y))

        return self._apply_minimum_distance(positions)

    def _generate_cluster(self) -> List[Tuple[float, float]]:
        """Generate stars in multiple clusters."""
        positions = []

        # Create 3-6 cluster centers
        num_clusters = random.randint(3, 6)
        cluster_centers = []

        for _ in range(num_clusters):
            cx = random.uniform(self.width * 0.2, self.width * 0.8)
            cy = random.uniform(self.height * 0.2, self.height * 0.8)
            cluster_centers.append((cx, cy))

        # Distribute stars among clusters
        stars_per_cluster = self.star_count // num_clusters
        extra_stars = self.star_count % num_clusters

        for i, (cx, cy) in enumerate(cluster_centers):
            # Some clusters get extra stars
            count = stars_per_cluster + (1 if i < extra_stars else 0)

            # Cluster radius
            cluster_radius = min(self.width, self.height) / (num_clusters + 1)

            for _ in range(count):
                # Gaussian distribution around cluster center
                x = random.gauss(cx, cluster_radius / 3)
                y = random.gauss(cy, cluster_radius / 3)

                # Clamp to bounds
                x = max(5, min(self.width - 5, x))
                y = max(5, min(self.height - 5, y))

                positions.append((x, y))

        return self._apply_minimum_distance(positions)

    def _generate_random(self) -> List[Tuple[float, float]]:
        """Generate stars with Poisson disk sampling for even distribution."""
        positions = []
        min_distance = (self.width * self.height / self.star_count) ** 0.5 * 0.5 * self.density_factor

        # Use rejection sampling
        max_attempts = self.star_count * 100
        attempts = 0

        while len(positions) < self.star_count and attempts < max_attempts:
            x = random.uniform(5, self.width - 5)
            y = random.uniform(5, self.height - 5)

            # Check minimum distance from existing stars
            too_close = False
            for px, py in positions:
                dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)
                if dist < min_distance:
                    too_close = True
                    break

            if not too_close:
                positions.append((x, y))

            attempts += 1

        # If we couldn't place all stars, reduce constraints and fill remaining
        while len(positions) < self.star_count:
            x = random.uniform(5, self.width - 5)
            y = random.uniform(5, self.height - 5)
            positions.append((x, y))

        return positions

    def _apply_minimum_distance(self, positions: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Apply Lloyd's relaxation to improve star distribution."""
        min_dist = 8 * self.density_factor
        iterations = 3

        for _ in range(iterations):
            new_positions = []
            for i, (x, y) in enumerate(positions):
                # Find nearby stars
                fx, fy = 0, 0
                for j, (ox, oy) in enumerate(positions):
                    if i != j:
                        dx = x - ox
                        dy = y - oy
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist < min_dist and dist > 0:
                            # Repulsion force
                            force = (min_dist - dist) / dist
                            fx += dx * force * 0.3
                            fy += dy * force * 0.3

                new_x = max(5, min(self.width - 5, x + fx))
                new_y = max(5, min(self.height - 5, y + fy))
                new_positions.append((new_x, new_y))

            positions = new_positions

        return positions

    def _create_star(self, galaxy_id: int, x: float, y: float) -> Star:
        """Create a star at the given position."""
        name = get_random_star_name(self.used_star_names)
        self.used_star_names.add(name)

        # Small chance of being a future nova
        is_future_nova = random.random() < 0.05  # 5% chance

        return Star(
            galaxy_id=galaxy_id,
            name=name,
            x=x,
            y=y,
            is_nova=False,
            nova_turn=random.randint(50, 200) if is_future_nova else None,
        )

    def _generate_planets(self, star_id: int) -> List[Planet]:
        """Generate planets for a star system."""
        planets = []
        num_planets = random.randint(1, 4)

        for orbit_index in range(num_planets):
            planet = self._create_planet(star_id, orbit_index)
            planets.append(planet)

        return planets

    def _create_planet(self, star_id: int, orbit_index: int) -> Planet:
        """Create a planet with random characteristics."""
        # Get the star name for planet naming
        star = Star.query.get(star_id)

        if orbit_index == 0:
            name = star.name
        else:
            suffix = PLANET_SUFFIXES[min(orbit_index, len(PLANET_SUFFIXES) - 1)]
            name = f"{star.name} {suffix}"

        # Temperature: varies by orbit (inner = hotter, outer = colder)
        base_temp = random.gauss(0, 100)  # Base variation
        orbit_effect = (orbit_index - 1.5) * 50  # Inner orbits hotter
        temperature = base_temp - orbit_effect
        temperature = max(-200, min(400, temperature))  # Clamp

        # Gravity: normal distribution around 1.0
        gravity = max(0.1, min(3.0, random.gauss(1.0, 0.4)))

        # Metal reserves: exponential distribution (many poor, few rich)
        base_metal = int(random.expovariate(1/500))
        metal_reserves = min(5000, max(50, base_metal))

        # Calculate max population based on habitability
        temp_factor = max(0, 1 - abs(temperature - 22) / 100)
        gravity_factor = max(0, 1 - abs(gravity - 1.0) / 2)
        habitability = temp_factor * gravity_factor
        max_population = int(1_000_000 * habitability)

        return Planet(
            star_id=star_id,
            name=name,
            orbit_index=orbit_index,
            temperature=round(temperature, 1),
            current_temperature=round(temperature, 1),
            gravity=round(gravity, 2),
            metal_reserves=metal_reserves,
            metal_remaining=metal_reserves,
            state=PlanetState.UNEXPLORED.value,
            population=0,
            max_population=max_population,
        )


def generate_galaxy(game_id: int, shape: str, size: str, density: str) -> Galaxy:
    """
    Convenience function to generate a galaxy.

    Args:
        game_id: ID of the game
        shape: Galaxy shape (circle, spiral, cluster, random)
        size: Size preset (small, medium, large, huge)
        density: Star density (low, medium, high)

    Returns:
        Generated Galaxy instance
    """
    generator = GalaxyGenerator(game_id, shape, size, density)
    return generator.generate()


def find_home_planets(galaxy: Galaxy, num_players: int) -> List[Planet]:
    """
    Find suitable home planets for players, maximizing distance between them.

    Args:
        galaxy: The galaxy to search
        num_players: Number of players needing home planets

    Returns:
        List of Planet instances suitable as home planets
    """
    # Find all planets with decent habitability
    candidates = []
    for star in galaxy.stars:
        for planet in star.planets:
            habitability = planet.habitability
            if habitability > 0.3:  # At least 30% habitable
                candidates.append({
                    "planet": planet,
                    "star": star,
                    "habitability": habitability,
                })

    if len(candidates) < num_players:
        raise ValueError(f"Not enough habitable planets for {num_players} players")

    # Sort by habitability (prefer better planets)
    candidates.sort(key=lambda c: c["habitability"], reverse=True)

    # Select planets maximizing minimum distance between them
    selected = []

    # Start with the most habitable planet
    selected.append(candidates[0])
    candidates = candidates[1:]

    while len(selected) < num_players and candidates:
        # Find the candidate that maximizes minimum distance to selected planets
        best_candidate = None
        best_min_dist = -1

        for candidate in candidates:
            min_dist = float("inf")
            for sel in selected:
                dist = math.sqrt(
                    (candidate["star"].x - sel["star"].x) ** 2 +
                    (candidate["star"].y - sel["star"].y) ** 2
                )
                min_dist = min(min_dist, dist)

            if min_dist > best_min_dist:
                best_min_dist = min_dist
                best_candidate = candidate

        if best_candidate:
            selected.append(best_candidate)
            candidates.remove(best_candidate)

    return [s["planet"] for s in selected]


def prepare_home_planet(planet: Planet) -> None:
    """
    Prepare a planet to be a home planet (terraform to ideal conditions).

    Args:
        planet: Planet to prepare
    """
    planet.current_temperature = 22.0  # Ideal temperature
    planet.state = PlanetState.DEVELOPED.value
    planet.population = 100_000
    planet.max_population = 1_000_000
    planet.is_home_planet = True
    planet.terraform_budget = 30
    planet.mining_budget = 70
