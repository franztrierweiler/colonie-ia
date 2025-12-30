# Plan de Développement - EPIC 6 : Système de Vaisseaux

## Statut Global

| Phase | Description | Statut |
|-------|-------------|--------|
| 1 | Modèles de données | En cours |
| 2 | Service FleetService | En attente |
| 3 | Déplacement et trajectoires | En attente |
| 4 | Ravitaillement | En attente |
| 5 | Démantèlement | En attente |
| 6 | API Endpoints | En attente |
| 7 | Tests | En attente |

---

## Vue d'ensemble

L'EPIC 6 implémente le système de vaisseaux : types, conception, flottes, déplacement et démantèlement.

**Dépendances** : EPIC 2 (Galaxy, Planet), EPIC 3-4 (économie)

**Dépendances futures** : EPIC 5 (technologies) pour niveaux tech, EPIC 7 (combat)

**User Stories couvertes** :
- US 6.1 - Types de vaisseaux de base
- US 6.2 - Vaisseaux spéciaux (Leurre, Biologique) - partiel, dépend EPIC 5
- US 6.3 - Conception de vaisseaux (5 valeurs tech)
- US 6.4 - Prototype vs Production
- US 6.5 - Déplacement des flottes
- US 6.6 - Trajectoire fixe en hyperespace
- US 6.7 - Ravitaillement automatique
- US 6.8 - Organisation des flottes
- US 6.9 - Démantèlement de vaisseaux (75% métal)
- US 6.10 - Configuration comportement combat

---

## Phase 1 : Modèles de données

### 1.1 Énumérations

```python
class ShipType(str, Enum):
    FIGHTER = "fighter"           # Chasseur - équilibré
    SCOUT = "scout"               # Éclaireur - portée +3
    COLONY = "colony"             # Vaisseau Colonial - 10000 colons
    SATELLITE = "satellite"       # Satellite - défense statique
    TANKER = "tanker"             # Ravitailleur
    BATTLESHIP = "battleship"     # Cuirassé - puissant
    DECOY = "decoy"               # Leurre - cheap (Radical)
    BIOLOGICAL = "biological"     # Biologique (Radical)

class FleetStatus(str, Enum):
    STATIONED = "stationed"       # En orbite
    IN_TRANSIT = "in_transit"     # En hyperespace
    ARRIVING = "arriving"         # Arrivée ce tour
```

### 1.2 Modèle ShipDesign

Design personnalisé d'un type de vaisseau.

```python
class ShipDesign(db.Model):
    id: int (PK)
    player_id: int (FK GamePlayer)
    name: str                     # Nom donné par le joueur
    ship_type: ShipType

    # Niveaux technologiques (0-10+)
    range_level: int = 1
    speed_level: int = 1
    weapons_level: int = 1
    shields_level: int = 1
    mini_level: int = 1

    # Coûts calculés
    prototype_cost_money: int     # Coût prototype en argent
    prototype_cost_metal: int     # Coût prototype en métal
    production_cost_money: int    # Coût production en argent
    production_cost_metal: int    # Coût production en métal

    # État
    is_prototype_built: bool = False
    created_at: datetime
```

### 1.3 Modèle Ship

Instance d'un vaisseau.

```python
class Ship(db.Model):
    id: int (PK)
    design_id: int (FK ShipDesign)
    fleet_id: int (FK Fleet, nullable)

    # État
    damage: int = 0               # Dégâts subis
    is_destroyed: bool = False
```

### 1.4 Modèle Fleet

Groupe de vaisseaux.

```python
class Fleet(db.Model):
    id: int (PK)
    player_id: int (FK GamePlayer)
    name: str

    # Position actuelle
    current_star_id: int (FK Star, nullable)  # null si en transit
    current_planet_id: int (FK Planet, nullable)

    # Déplacement
    status: FleetStatus
    destination_star_id: int (FK Star, nullable)
    departure_turn: int (nullable)
    arrival_turn: int (nullable)

    # Carburant
    fuel_remaining: float         # Distance restante

    # Combat
    combat_behavior: str = "normal"  # normal, aggressive, defensive
```

### 1.5 Caractéristiques par type de vaisseau

| Type | Range Bonus | Speed | Weapons | Shields | Metal Base | Money Base | Capacité |
|------|-------------|-------|---------|---------|------------|------------|----------|
| Fighter | 0 | 1.0 | 1.0 | 1.0 | 50 | 100 | - |
| Scout | +3 | 1.2 | 0.3 | 0.3 | 30 | 80 | - |
| Colony | -1 | 0.5 | 0.1 | 0.5 | 200 | 500 | 10000 colons |
| Satellite | 0 (fixe) | 0 | 0.8 | 1.5 | 20 | 30 | - |
| Tanker | 0 | 0.8 | 0.1 | 0.5 | 100 | 200 | Ravitaillement |
| Battleship | 0 | 0.7 | 2.0 | 2.0 | 300 | 600 | - |
| Decoy | 0 | 1.5 | 0 | 0.1 | 5 | 10 | - |
| Biological | 0 | 1.0 | 1.5 | 0.5 | 0 | 300 | Spécial |

---

## Phase 2 : Service FleetService

### 2.1 Calcul des coûts

```python
class FleetService:
    @staticmethod
    def calculate_design_costs(design: ShipDesign) -> dict:
        """Calcule les coûts d'un design."""
        base = SHIP_BASE_COSTS[design.ship_type]

        # Facteurs technologiques
        tech_factor = (
            design.range_level +
            design.speed_level +
            design.weapons_level +
            design.shields_level
        ) / 4

        # Miniaturisation : réduit métal, augmente argent
        mini_factor = 1 - (design.mini_level * 0.08)  # -8% métal par niveau
        money_increase = 1 + (design.mini_level * 0.10)  # +10% argent par niveau

        metal_cost = int(base.metal * tech_factor * mini_factor)
        money_cost = int(base.money * tech_factor * money_increase)

        return {
            "prototype_money": money_cost * 2,  # Prototype = 2x
            "prototype_metal": metal_cost * 2,
            "production_money": money_cost,
            "production_metal": metal_cost,
        }
```

### 2.2 Construction de vaisseaux

```python
    @staticmethod
    def build_prototype(player: GamePlayer, design: ShipDesign) -> Ship:
        """Construit le prototype (premier exemplaire)."""

    @staticmethod
    def build_ship(player: GamePlayer, design: ShipDesign,
                   planet: Planet) -> Ship:
        """Construit un vaisseau à partir d'un design existant."""

    @staticmethod
    def build_ships(player: GamePlayer, design: ShipDesign,
                    planet: Planet, count: int) -> List[Ship]:
        """Construit plusieurs vaisseaux."""
```

### 2.3 Gestion des flottes

```python
    @staticmethod
    def create_fleet(player: GamePlayer, name: str,
                     planet: Planet) -> Fleet:
        """Crée une nouvelle flotte vide."""

    @staticmethod
    def add_ships_to_fleet(fleet: Fleet, ships: List[Ship]):
        """Ajoute des vaisseaux à une flotte."""

    @staticmethod
    def split_fleet(fleet: Fleet, ship_ids: List[int],
                    new_name: str) -> Fleet:
        """Divise une flotte en deux."""

    @staticmethod
    def merge_fleets(fleet1: Fleet, fleet2: Fleet) -> Fleet:
        """Fusionne deux flottes."""
```

---

## Phase 3 : Déplacement et trajectoires

### 3.1 Calcul de distance et durée

```python
    @staticmethod
    def calculate_travel_time(fleet: Fleet,
                              destination: Star) -> int:
        """Calcule le nombre de tours pour atteindre la destination."""
        distance = calculate_distance(fleet.current_star, destination)
        fleet_speed = FleetService.get_fleet_speed(fleet)
        return math.ceil(distance / fleet_speed)

    @staticmethod
    def get_fleet_speed(fleet: Fleet) -> float:
        """Vitesse = min des vitesses des vaisseaux."""

    @staticmethod
    def get_fleet_range(fleet: Fleet) -> float:
        """Portée = min des portées des vaisseaux."""
```

### 3.2 Mouvement

```python
    @staticmethod
    def move_fleet(fleet: Fleet, destination: Star) -> dict:
        """Envoie une flotte vers une destination."""
        # Vérifie la portée
        # Vérifie le carburant
        # Définit la trajectoire (fixe, pas de changement)

    @staticmethod
    def process_fleet_movements(game: Game):
        """Traite les mouvements de toutes les flottes (fin de tour)."""
        # Avance chaque flotte d'un tour
        # Détecte les arrivées
```

---

## Phase 4 : Ravitaillement

```python
    @staticmethod
    def can_refuel_at(fleet: Fleet, planet: Planet) -> bool:
        """Vérifie si la flotte peut se ravitailler."""
        # Planète du joueur ou allié

    @staticmethod
    def refuel_fleet(fleet: Fleet, planet: Planet):
        """Ravitaille une flotte."""
        # Remet le carburant au max

    @staticmethod
    def process_refueling(game: Game):
        """Ravitaillement automatique en fin de tour."""
```

---

## Phase 5 : Démantèlement

```python
    @staticmethod
    def disband_ship(ship: Ship, planet: Planet) -> int:
        """Démantèle un vaisseau, récupère 75% du métal."""
        metal_recovered = int(ship.design.production_cost_metal * 0.75)
        planet.owner.metal += metal_recovered
        ship.is_destroyed = True
        return metal_recovered

    @staticmethod
    def disband_fleet(fleet: Fleet, planet: Planet) -> int:
        """Démantèle toute une flotte."""
```

---

## Phase 6 : API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/games/:id/designs` | Liste des designs du joueur |
| POST | `/api/games/:id/designs` | Créer un design |
| POST | `/api/games/:id/designs/:id/build` | Construire vaisseau(x) |
| GET | `/api/games/:id/fleets` | Liste des flottes |
| POST | `/api/games/:id/fleets` | Créer une flotte |
| PATCH | `/api/fleets/:id` | Modifier une flotte |
| POST | `/api/fleets/:id/move` | Déplacer une flotte |
| POST | `/api/fleets/:id/split` | Diviser une flotte |
| POST | `/api/fleets/:id/merge` | Fusionner des flottes |
| POST | `/api/fleets/:id/disband` | Démanteler une flotte |
| POST | `/api/ships/:id/disband` | Démanteler un vaisseau |

---

## Phase 7 : Tests

- [ ] Tests calcul des coûts
- [ ] Tests construction prototype vs production
- [ ] Tests création/gestion flottes
- [ ] Tests déplacement et trajectoires
- [ ] Tests ravitaillement
- [ ] Tests démantèlement (75% métal)
- [ ] Tests API endpoints

---

## Formules

### Coût de production

```
metal_cost = base_metal * tech_factor * (1 - mini_level * 0.08)
money_cost = base_money * tech_factor * (1 + mini_level * 0.10)
prototype_cost = production_cost * 2
```

### Vitesse de flotte

```
fleet_speed = min(ship.speed for ship in fleet.ships)
travel_turns = ceil(distance / fleet_speed)
```

### Portée effective

```
base_range = min(ship.range for ship in fleet.ships)
effective_range = base_range + tanker_bonus (si ravitailleur présent)
```

---

## Critères d'acceptation

- [ ] 8 types de vaisseaux disponibles
- [ ] Les designs sont personnalisables (5 valeurs tech)
- [ ] Prototype coûte 2x, production normale ensuite
- [ ] Les flottes se déplacent avec trajectoire fixe
- [ ] Ravitaillement automatique sur planètes alliées
- [ ] Démantèlement récupère 75% du métal
- [ ] La vitesse de flotte = min des vaisseaux
- [ ] La portée de flotte = min des vaisseaux

---

*Document généré pour EPIC 6 - Système de Vaisseaux*
*Projet Colonie-IA*
