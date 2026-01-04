# Plan EPIC 7 : Système de Combat

## Vue d'ensemble

Le système de combat est **entièrement automatique** - pas de contrôle tactique du joueur.
Les combats ne se produisent **qu'au-dessus des planètes**, jamais en hyperespace.

### Séquence de combat
```
1. Arrivée des flottes sur une planète
2. Combat orbital (vaisseaux vs vaisseaux/satellites)
3. Bombardement de la colonie (si vaisseaux attaquants survivants)
4. Colonisation possible (si Vaisseau Colonial présent et planète non possédée)
```

---

## User Stories

### US 7.1 - Combat automatique
**Statut : FAIT**

**Description :** Les combats se résolvent automatiquement sans contrôle tactique du joueur.

**Implémentation prévue :**
- Service : `backend/app/services/combat.py` - `CombatService`
- Méthode principale : `resolve_combat(planet_id, attacking_fleets, defending_fleets)`
- Appelé depuis `TurnService.process_fleet_arrivals()`

**Critères d'acceptation :**
- [ ] Combat résolu automatiquement à l'arrivée de flottes hostiles
- [ ] Rapport de combat généré pour chaque bataille
- [ ] Résultat clair : vainqueur, pertes des deux côtés

---

### US 7.2 - Combat orbital uniquement
**Statut : FAIT**

**Description :** Les combats ne se produisent qu'au-dessus des planètes, jamais en hyperespace.

**Implémentation prévue :**
- Condition dans `TurnService` : combats uniquement sur planètes avec flottes hostiles
- Pas de combat si flottes se croisent en transit
- Validation : flottes doivent être `STATIONED` ou `ARRIVING`

**Critères d'acceptation :**
- [ ] Combat déclenché uniquement quand flottes arrivent sur même planète
- [ ] Flottes en transit ne peuvent pas être interceptées
- [ ] Combat possible entre flotte arrivante et satellites défensifs

---

### US 7.3 - Séquence de combat
**Statut : FAIT**

**Description :** Les batailles suivent la séquence : combat orbital → bombardement → colonisation.

**Implémentation prévue :**

```python
class CombatService:
    def resolve_battle(planet, turn):
        # Phase 1: Combat orbital
        orbital_result = self._orbital_combat(planet, attacking_fleets, defending_fleets)

        # Phase 2: Bombardement (si attaquants survivants)
        if orbital_result.attacker_ships_remaining > 0 and planet.owner_id:
            bombardment_result = self._bombardment(planet, orbital_result.attacker_ships)

        # Phase 3: Colonisation (si vaisseau colonial et planète libre)
        if planet.owner_id is None and has_colony_ship:
            colonization_result = self._colonize(planet, colony_ship)

        return CombatReport(...)
```

**Critères d'acceptation :**
- [ ] Phase orbital avant bombardement
- [ ] Bombardement uniquement si attaquants survivants et planète occupée
- [ ] Colonisation uniquement si planète non possédée et vaisseau colonial

---

### US 7.4 - Priorité Vitesse
**Statut : FAIT**

**Description :** La technologie Vitesse détermine qui tire en premier.

**Implémentation prévue :**
```python
def _calculate_initiative(ship):
    """Plus la vitesse est haute, plus le vaisseau tire tôt."""
    design = ship.design
    base_speed = design.speed_level
    ship_mult = design.base_stats["speed_mult"]
    return base_speed * ship_mult

def _orbital_combat(attacking, defending):
    # Ordonner tous les vaisseaux par initiative (vitesse)
    all_ships = attacking + defending
    all_ships.sort(key=lambda s: _calculate_initiative(s), reverse=True)

    for ship in all_ships:
        if ship.is_destroyed:
            continue
        target = self._select_target(ship, enemies)
        self._fire(ship, target)
```

**Critères d'acceptation :**
- [ ] Vaisseaux avec haute Vitesse tirent en premier
- [ ] En cas d'égalité, ordre aléatoire
- [ ] Multiplicateur de type de vaisseau pris en compte (Scout = 1.2x, Battleship = 0.7x)

---

### US 7.5 - Défense au sol
**Statut : FAIT**

**Description :** La population défend avec la meilleure technologie du défenseur.

**Implémentation prévue :**
```python
def _bombardment(planet, attacking_ships):
    # Population défend avec tech du propriétaire
    defender_tech = planet.owner.technology

    # Puissance de défense basée sur population
    defense_power = planet.population * DEFENSE_PER_POP
    defense_tech = max(defender_tech.weapons_level, defender_tech.shields_level)

    # Dégâts infligés aux attaquants
    for ship in attacking_ships:
        damage = defense_power * defense_tech * random()
        ship.take_damage(damage)

    # Dégâts infligés à la population
    bombardment_casualties = sum(ship.attack_power for ship in attacking_ships)
    planet.population -= bombardment_casualties
```

**Critères d'acceptation :**
- [ ] Population utilise meilleure tech du joueur défenseur
- [ ] Défense proportionnelle à la population
- [ ] Population diminue sous bombardement

---

### US 7.6 - Ciblage IA des Vaisseaux Coloniaux
**Statut : FAIT**

**Description :** L'IA cible prioritairement les Vaisseaux Coloniaux adverses.

**Implémentation prévue :**
```python
# Priorité de ciblage
TARGET_PRIORITY = {
    ShipType.COLONY: 100,      # Priorité max
    ShipType.TANKER: 80,       # Soutien
    ShipType.BATTLESHIP: 60,   # Menace
    ShipType.FIGHTER: 40,      # Standard
    ShipType.SCOUT: 30,        # Faible menace
    ShipType.SATELLITE: 20,    # Défense
    ShipType.DECOY: 10,        # Leurre (piège!)
    ShipType.BIOLOGICAL: 50,
}

def _select_target(attacker, enemies):
    # Trier par priorité décroissante
    enemies.sort(key=lambda e: TARGET_PRIORITY[e.ship_type], reverse=True)
    return enemies[0] if enemies else None
```

**Critères d'acceptation :**
- [ ] Vaisseaux Coloniaux ciblés en priorité
- [ ] Ravitailleurs en second
- [ ] Leurres ont la plus basse priorité (mais distraient quand même)

---

### US 7.7 - Récupération de débris
**Statut : FAIT**

**Description :** Récupérer une partie du métal des vaisseaux détruits au-dessus de ses planètes.

**Implémentation prévue :**
```python
DEBRIS_RECOVERY_RATE = 0.25  # 25% du métal récupéré

def _process_debris(planet, destroyed_ships):
    if planet.owner_id is None:
        return 0  # Pas de récupération sans colonie

    total_metal = sum(ship.design.metal_cost for ship in destroyed_ships)
    recovered = int(total_metal * DEBRIS_RECOVERY_RATE)

    # Ajouter au stock du joueur
    planet.owner.add_metal(recovered)

    return recovered
```

**Critères d'acceptation :**
- [ ] 25% du métal des vaisseaux détruits récupéré
- [ ] Uniquement sur planètes contrôlées par un joueur
- [ ] Inclut vaisseaux ennemis et alliés détruits

---

### US 7.8 - Dégâts collatéraux des débris
**Statut : FAIT**

**Description :** Les débris qui tombent peuvent tuer des habitants.

**Implémentation prévue :**
```python
DEBRIS_CASUALTY_RATE = 10  # Habitants tués par unité de métal tombé

def _process_debris_casualties(planet, destroyed_ships):
    if planet.population == 0:
        return 0

    total_debris = sum(ship.design.metal_cost for ship in destroyed_ships)
    casualties = min(
        int(total_debris * DEBRIS_CASUALTY_RATE * random()),
        planet.population * 0.1  # Max 10% de la pop
    )

    planet.population -= casualties
    return casualties
```

**Critères d'acceptation :**
- [ ] Débris tuent des habitants proportionnellement au métal
- [ ] Maximum 10% de la population par bataille
- [ ] Appliqué même si le défenseur gagne

---

## Architecture Technique

### Modèles (à créer)

```python
# backend/app/models/combat.py

class CombatReport(db.Model):
    """Rapport d'une bataille."""
    __tablename__ = "combat_reports"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"))
    turn = db.Column(db.Integer)

    # Participants
    attacker_ids = db.Column(db.JSON)  # Liste player_ids
    defender_id = db.Column(db.Integer, db.ForeignKey("game_players.id"))

    # Résultat
    victor_id = db.Column(db.Integer, db.ForeignKey("game_players.id"))

    # Pertes
    attacker_ships_lost = db.Column(db.JSON)  # {player_id: count}
    defender_ships_lost = db.Column(db.Integer, default=0)
    population_casualties = db.Column(db.Integer, default=0)

    # Débris
    metal_recovered = db.Column(db.Integer, default=0)

    # Colonisation
    planet_captured = db.Column(db.Boolean, default=False)
    planet_colonized = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Service (à créer)

```python
# backend/app/services/combat.py

class CombatService:
    """Service de résolution des combats."""

    @staticmethod
    def check_for_combat(planet_id: int) -> bool:
        """Vérifie si un combat doit avoir lieu sur cette planète."""

    @staticmethod
    def resolve_battle(planet_id: int, current_turn: int) -> CombatReport:
        """Résout une bataille complète sur une planète."""

    @staticmethod
    def _orbital_combat(attackers: List[Ship], defenders: List[Ship]) -> dict:
        """Phase de combat orbital."""

    @staticmethod
    def _bombardment(planet: Planet, ships: List[Ship]) -> dict:
        """Phase de bombardement."""

    @staticmethod
    def _colonize(planet: Planet, colony_ship: Ship) -> bool:
        """Phase de colonisation."""

    @staticmethod
    def _calculate_damage(attacker: Ship, defender: Ship) -> float:
        """Calcule les dégâts infligés."""

    @staticmethod
    def _process_debris(planet: Planet, destroyed: List[Ship]) -> dict:
        """Traite les débris et récupération de métal."""
```

### Intégration avec TurnService

```python
# Dans backend/app/services/turn.py

def process_turn(game_id: int):
    # ... existant ...

    # 1. Déplacer les flottes
    fleet_arrivals = FleetService.process_fleet_movements(game)

    # 2. Résoudre les combats sur chaque planète avec flottes hostiles
    for planet in game.planets:
        if CombatService.check_for_combat(planet.id):
            report = CombatService.resolve_battle(planet.id, game.current_turn)
            combat_reports.append(report)

    # 3. Suite du traitement...
```

### Routes API (à créer)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | /games/:id/combat-reports | Rapports de combat du tour |
| GET | /combat-reports/:id | Détail d'un rapport |
| GET | /games/:id/combat-history | Historique des batailles |

---

## Formules de Combat

### Dégâts
```
damage = attacker_weapons * weapons_mult * random(0.8, 1.2)
effective_damage = max(0, damage - defender_shields * shields_mult)
```

### Initiative (ordre de tir)
```
initiative = speed_level * speed_mult + random(0, 1)
```

### Défense au sol
```
ground_defense = population / 1000 * max(weapons_level, shields_level)
```

### Débris
```
recovered_metal = destroyed_ship_metal * 0.25
casualties = debris_metal * 10 * random(0, 1)  # max 10% pop
```

---

## Options tactiques par vaisseau

### CombatBehavior (déjà défini)
```python
class CombatBehavior(str, Enum):
    OFFENSIVE = "offensive"   # +20% armes, -20% boucliers
    DEFENSIVE = "defensive"   # -20% armes, +20% boucliers
    FOLLOW = "follow"         # Attend fin du combat (Colony ships)
```

### Application
```python
def _apply_behavior_modifiers(ship):
    behavior = ship.combat_behavior
    if behavior == CombatBehavior.OFFENSIVE:
        return {"weapons_mod": 1.2, "shields_mod": 0.8}
    elif behavior == CombatBehavior.DEFENSIVE:
        return {"weapons_mod": 0.8, "shields_mod": 1.2}
    else:  # FOLLOW
        return {"weapons_mod": 0, "shields_mod": 1.0}  # Ne tire pas
```

---

## Frontend

### Composants à créer

| Composant | Fichier | Description |
|-----------|---------|-------------|
| CombatReport | CombatReport.tsx | Affichage rapport de bataille |
| CombatAnimation | CombatAnimation.tsx | Animation simplifiée du combat |
| BattleHistory | BattleHistory.tsx | Liste des batailles passées |

### Intégration GameView

- Notification quand combat résolu
- Affichage du rapport dans les "Rapports"
- Icône de bataille sur les planètes concernées

---

## Tests

- [ ] Test combat 1v1 simple
- [ ] Test priorité vitesse
- [ ] Test ciblage vaisseaux coloniaux
- [ ] Test bombardement
- [ ] Test colonisation après victoire
- [ ] Test récupération débris
- [ ] Test dégâts collatéraux
- [ ] Test combat multi-joueurs (alliances)
- [ ] Test combat avec satellites défensifs

---

## Dépendances

### Requiert (déjà implémenté)
- EPIC 4 : Système planétaire (planètes, population)
- EPIC 5 : Système technologique (niveaux tech)
- EPIC 6 : Système de vaisseaux (flottes, ships, designs)

### Requis par (EPICs futurs)
- EPIC 8 : Système d'alliances (combat conjoint)
- EPIC 12 : IA (décisions de combat)

---

## Estimation de complexité

| User Story | Complexité | Priorité |
|------------|------------|----------|
| US 7.1 Combat auto | Haute | 1 |
| US 7.2 Combat orbital | Basse | 1 |
| US 7.3 Séquence | Moyenne | 1 |
| US 7.4 Priorité vitesse | Moyenne | 2 |
| US 7.5 Défense sol | Moyenne | 2 |
| US 7.6 Ciblage Colony | Basse | 3 |
| US 7.7 Débris | Basse | 3 |
| US 7.8 Dégâts coll. | Basse | 3 |

---

## Historique

| Date | Changement |
|------|------------|
| 2026-01-03 | Création du plan |
