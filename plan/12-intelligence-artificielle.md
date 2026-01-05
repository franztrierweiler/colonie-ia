# Plan EPIC 12 : Intelligence Artificielle

## Vue d'ensemble

L'EPIC 12 implémente un système d'IA capable de jouer de manière compétente au jeu. L'IA doit être suffisamment performante pour offrir un défi intéressant aux joueurs humains, tout en restant battable.

### Objectifs clés
- IA reconnue comme **particulièrement compétente**
- Plusieurs **niveaux de difficulté** (débutant à expert)
- Capable d'utiliser **toutes les fonctionnalités** du jeu (ravitailleurs, biologiques, etc.)
- Attaques **multi-planètes coordonnées**
- Gestion **optimisée du métal** en fin de partie
- Mode **Auto-Play** pour observer les stratégies

---

## User Stories

### US 12.1 - IA compétente
**Statut : À faire**

**Description :** L'IA doit jouer de manière compétente et offrir un défi intéressant.

**Critères d'acceptation :**
- [ ] L'IA prend des décisions logiques à chaque tour
- [ ] L'IA explore, colonise et développe ses planètes
- [ ] L'IA construit des flottes équilibrées
- [ ] L'IA défend ses planètes vulnérables
- [ ] L'IA attaque les cibles opportunes

---

### US 12.2 - Niveaux de difficulté
**Statut : À faire**

**Description :** Le joueur peut choisir parmi plusieurs niveaux de difficulté.

**Niveaux proposés :**
| Niveau | Nom | Description |
|--------|-----|-------------|
| 1 | Conscrit | Erreurs fréquentes, réaction lente |
| 2 | Grenadier | Décisions basiques, pas de tactiques avancées |
| 3 | Capitaine | Jeu équilibré, stratégie standard |
| 4 | Colonel | Bonne stratégie, utilise ravitailleurs |
| 5 | Maréchal | Expert, attaques coordonnées, biologiques |

**Implémentation :**
```python
class AIDifficulty(Enum):
    CONSCRIT = 1      # Facile
    GRENADIER = 2     # Normal-
    CAPITAINE = 3     # Normal
    COLONEL = 4       # Difficile
    MARECHAL = 5      # Expert
```

**Critères d'acceptation :**
- [ ] 5 niveaux de difficulté disponibles
- [ ] Différences perceptibles entre niveaux
- [ ] Configuration à la création de partie

---

### US 12.3 - IA utilisant ravitailleurs et biologiques
**Statut : À faire**

**Description :** L'IA sait utiliser efficacement les vaisseaux avancés.

**Comportements attendus :**
- **Ravitailleurs** : L'IA crée des chaînes de ravitaillement pour atteindre des planètes éloignées
- **Biologiques** : L'IA utilise les vaisseaux biologiques quand débloqués par recherche radicale
- Priorité aux ravitailleurs si beaucoup de planètes hors de portée

**Critères d'acceptation :**
- [ ] L'IA construit des ravitailleurs quand nécessaire
- [ ] L'IA planifie des routes avec ravitaillement
- [ ] L'IA utilise les biologiques si disponibles

---

### US 12.4 - Attaques coordonnées multi-planètes
**Statut : À faire**

**Description :** L'IA lance des attaques sur plusieurs fronts simultanément.

**Stratégie :**
```
Analyse → Identification des cibles → Allocation des forces → Lancement synchronisé
```

**Comportements :**
- Diviser les forces pour attaquer plusieurs planètes faibles
- Concentration sur une planète forte si supériorité écrasante
- Feintes avec leurres/éclaireurs
- Timing des arrivées pour maximiser l'effet de surprise

**Critères d'acceptation :**
- [ ] L'IA attaque parfois plusieurs planètes en même temps
- [ ] Les attaques arrivent au même tour quand possible
- [ ] L'IA n'attaque pas avec des forces insuffisantes

---

### US 12.5 - Gestion optimisée du métal
**Statut : À faire**

**Description :** L'IA gère efficacement le métal, surtout en fin de partie.

**Stratégies :**
- **Début** : Minage équilibré sur toutes les planètes
- **Milieu** : Concentration sur les planètes riches, expansion vers nouvelles sources
- **Fin** : Recyclage des vaisseaux obsolètes, récupération des débris, strip-mining

**Critères d'acceptation :**
- [ ] L'IA recycle les vaisseaux obsolètes
- [ ] L'IA exploite intensivement les planètes avant abandon
- [ ] L'IA récupère le métal des débris de combat

---

### US 12.6 - Mode Auto-Play
**Statut : À faire**

**Description :** Le joueur peut laisser l'IA jouer à sa place.

**Fonctionnalités :**
- Bouton "Auto-Play" dans l'interface
- L'IA prend le contrôle temporairement
- Le joueur peut reprendre le contrôle à tout moment
- Observation des décisions de l'IA

**Critères d'acceptation :**
- [ ] Bouton Auto-Play disponible
- [ ] L'IA joue les tours du joueur
- [ ] Le joueur peut reprendre à tout moment
- [ ] Les actions de l'IA sont visibles dans les rapports

---

## Architecture Technique

### Structure des fichiers

```
backend/app/
├── services/
│   └── ai/
│       ├── __init__.py
│       ├── ai_service.py          # Service principal
│       ├── ai_strategy.py         # Stratégies par phase de jeu
│       ├── ai_economy.py          # Décisions économiques
│       ├── ai_military.py         # Décisions militaires
│       ├── ai_expansion.py        # Décisions d'expansion
│       ├── ai_research.py         # Décisions de recherche
│       └── ai_difficulty.py       # Modificateurs de difficulté
├── models/
│   └── ai.py                      # AIPlayer settings
└── routes/
    └── ai.py                      # Routes Auto-Play
```

### AIService (Service principal)

```python
# backend/app/services/ai/ai_service.py

from enum import Enum
from typing import Dict, List, Any, Optional

class AIDifficulty(Enum):
    CONSCRIT = 1
    GRENADIER = 2
    CAPITAINE = 3
    COLONEL = 4
    MARECHAL = 5

class AIService:
    """Service principal de l'IA."""

    @staticmethod
    def process_ai_turn(player: GamePlayer) -> Dict[str, Any]:
        """
        Traite le tour d'un joueur IA.

        Ordre des décisions:
        1. Analyse de la situation
        2. Décisions de recherche
        3. Décisions économiques (budget planètes)
        4. Décisions de construction
        5. Décisions militaires (mouvements flottes)
        """

    @staticmethod
    def analyze_game_state(player: GamePlayer) -> "GameAnalysis":
        """Analyse complète de l'état du jeu."""

    @staticmethod
    def _apply_difficulty_modifier(
        decision: Any,
        difficulty: AIDifficulty
    ) -> Any:
        """Applique les modificateurs de difficulté."""
```

### GameAnalysis (Analyse du jeu)

```python
class GameAnalysis:
    """Résultat de l'analyse de l'état du jeu."""

    # Phase du jeu
    phase: GamePhase  # EARLY, MID, LATE

    # Situation économique
    income: int
    metal_stock: int
    metal_production: int
    debt_ratio: float

    # Situation militaire
    my_fleet_power: float
    enemy_fleet_power: Dict[int, float]  # player_id -> power
    military_advantage: float  # > 1 = supériorité

    # Situation technologique
    my_tech_levels: Dict[str, int]
    tech_comparison: Dict[int, str]  # player_id -> "ahead"/"behind"/"equal"

    # Opportunités
    vulnerable_enemy_planets: List[Planet]
    colonizable_planets: List[Planet]
    planets_needing_defense: List[Planet]

    # Menaces
    incoming_enemy_fleets: List[Fleet]
    planets_under_threat: List[Planet]
```

### AIEconomyService (Décisions économiques)

```python
# backend/app/services/ai/ai_economy.py

class AIEconomyService:
    """Gestion de l'économie par l'IA."""

    @staticmethod
    def allocate_planet_budgets(
        player: GamePlayer,
        analysis: GameAnalysis
    ) -> Dict[int, Dict]:
        """
        Détermine les budgets de chaque planète.

        Returns:
            {planet_id: {"terraform": %, "mining": %}}
        """

    @staticmethod
    def allocate_research_budget(
        player: GamePlayer,
        analysis: GameAnalysis
    ) -> Dict[str, int]:
        """
        Détermine le budget de recherche par domaine.

        Returns:
            {"range": %, "speed": %, "weapons": %, ...}
        """

    @staticmethod
    def decide_ship_construction(
        planet: Planet,
        player: GamePlayer,
        analysis: GameAnalysis
    ) -> Optional[Dict]:
        """
        Décide quel vaisseau construire sur une planète.

        Returns:
            {"design_id": int, "quantity": int} or None
        """

    @staticmethod
    def should_take_debt(
        player: GamePlayer,
        amount_needed: int,
        analysis: GameAnalysis
    ) -> bool:
        """Décide si l'IA doit s'endetter."""
```

### AIMilitaryService (Décisions militaires)

```python
# backend/app/services/ai/ai_military.py

class AIMilitaryService:
    """Gestion militaire par l'IA."""

    @staticmethod
    def plan_fleet_movements(
        player: GamePlayer,
        analysis: GameAnalysis
    ) -> List[FleetOrder]:
        """
        Planifie les mouvements de flottes.

        Returns:
            Liste d'ordres de mouvement
        """

    @staticmethod
    def evaluate_attack_target(
        fleet: Fleet,
        target: Planet,
        analysis: GameAnalysis
    ) -> float:
        """
        Évalue l'attractivité d'une cible.

        Returns:
            Score (plus élevé = plus attractif)
        """

    @staticmethod
    def calculate_required_force(
        target: Planet,
        defending_fleets: List[Fleet]
    ) -> int:
        """Calcule la force nécessaire pour prendre une cible."""

    @staticmethod
    def plan_defense(
        player: GamePlayer,
        threats: List[Fleet],
        analysis: GameAnalysis
    ) -> List[FleetOrder]:
        """Planifie la défense contre les menaces."""

    @staticmethod
    def should_retreat(
        fleet: Fleet,
        enemy_force: float
    ) -> bool:
        """Décide si une flotte doit battre en retraite."""
```

### AIExpansionService (Décisions d'expansion)

```python
# backend/app/services/ai/ai_expansion.py

class AIExpansionService:
    """Gestion de l'expansion par l'IA."""

    @staticmethod
    def find_colonization_targets(
        player: GamePlayer,
        analysis: GameAnalysis
    ) -> List[Tuple[Planet, float]]:
        """
        Trouve les planètes à coloniser avec leur priorité.

        Returns:
            Liste de (planète, score_priorité)
        """

    @staticmethod
    def evaluate_planet_value(planet: Planet) -> float:
        """
        Évalue la valeur d'une planète.

        Facteurs:
        - Proximité de 22°C (moins de terraformation)
        - Gravité proche de 1.0g
        - Réserves de métal
        - Position stratégique
        """

    @staticmethod
    def plan_colony_ship_route(
        colony_ship: Fleet,
        target: Planet,
        tankers: List[Fleet]
    ) -> List[FleetOrder]:
        """Planifie la route d'un vaisseau colonial avec ravitaillement."""
```

### AIResearchService (Décisions de recherche)

```python
# backend/app/services/ai/ai_research.py

class AIResearchService:
    """Gestion de la recherche par l'IA."""

    # Priorités par phase
    EARLY_GAME_PRIORITY = {
        "range": 0.35,      # Explorer plus loin
        "speed": 0.25,      # Arriver plus vite
        "weapons": 0.15,
        "shields": 0.10,
        "mini": 0.05,
        "radical": 0.10,
    }

    MID_GAME_PRIORITY = {
        "range": 0.15,
        "speed": 0.25,      # Toujours important
        "weapons": 0.25,    # Combat
        "shields": 0.20,
        "mini": 0.10,
        "radical": 0.05,
    }

    LATE_GAME_PRIORITY = {
        "range": 0.10,
        "speed": 0.20,
        "weapons": 0.30,    # Décisif
        "shields": 0.25,
        "mini": 0.10,
        "radical": 0.05,
    }

    @staticmethod
    def get_research_allocation(
        player: GamePlayer,
        analysis: GameAnalysis
    ) -> Dict[str, int]:
        """Détermine l'allocation de recherche."""

    @staticmethod
    def handle_radical_breakthrough(
        options: List[str],
        player: GamePlayer,
        analysis: GameAnalysis
    ) -> str:
        """Choisit quelle percée éliminer."""
```

### Modificateurs de difficulté

```python
# backend/app/services/ai/ai_difficulty.py

class DifficultyModifiers:
    """Modificateurs selon le niveau de difficulté."""

    MODIFIERS = {
        AIDifficulty.CONSCRIT: {
            "decision_error_rate": 0.30,     # 30% de mauvaises décisions
            "reaction_delay": 2,              # Réagit avec 2 tours de retard
            "attack_threshold": 2.0,          # Attaque seulement si 2x supérieur
            "economy_efficiency": 0.7,        # 70% d'efficacité économique
            "can_use_tankers": False,
            "can_coordinate_attacks": False,
            "can_use_biologicals": False,
        },
        AIDifficulty.GRENADIER: {
            "decision_error_rate": 0.15,
            "reaction_delay": 1,
            "attack_threshold": 1.5,
            "economy_efficiency": 0.85,
            "can_use_tankers": False,
            "can_coordinate_attacks": False,
            "can_use_biologicals": False,
        },
        AIDifficulty.CAPITAINE: {
            "decision_error_rate": 0.05,
            "reaction_delay": 0,
            "attack_threshold": 1.2,
            "economy_efficiency": 1.0,
            "can_use_tankers": True,
            "can_coordinate_attacks": False,
            "can_use_biologicals": False,
        },
        AIDifficulty.COLONEL: {
            "decision_error_rate": 0.02,
            "reaction_delay": 0,
            "attack_threshold": 1.0,
            "economy_efficiency": 1.0,
            "can_use_tankers": True,
            "can_coordinate_attacks": True,
            "can_use_biologicals": False,
        },
        AIDifficulty.MARECHAL: {
            "decision_error_rate": 0.0,
            "reaction_delay": 0,
            "attack_threshold": 0.8,          # Attaque même si légèrement inférieur
            "economy_efficiency": 1.1,        # Bonus d'efficacité
            "can_use_tankers": True,
            "can_coordinate_attacks": True,
            "can_use_biologicals": True,
            "predictive_defense": True,       # Anticipe les attaques
        },
    }
```

---

## Intégration avec TurnService

```python
# Modification de backend/app/services/turn.py

class TurnService:
    @staticmethod
    def process_turn(game: Game) -> Dict[str, Any]:
        # ... code existant ...

        # Avant de traiter les joueurs humains, traiter les IA
        for player in game.players.filter_by(is_eliminated=False, is_ai=True):
            ai_decisions = AIService.process_ai_turn(player)
            results["ai_decisions"][player.id] = ai_decisions

        # ... suite du traitement ...
```

---

## Routes API

### Auto-Play

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/games/:id/auto-play/enable` | Active l'auto-play |
| POST | `/api/games/:id/auto-play/disable` | Désactive l'auto-play |
| GET | `/api/games/:id/auto-play/status` | Statut auto-play |

```python
# backend/app/routes/ai.py

@bp.route('/games/<int:game_id>/auto-play/enable', methods=['POST'])
@jwt_required()
def enable_auto_play(game_id: int):
    """Active l'auto-play pour le joueur courant."""

@bp.route('/games/<int:game_id>/auto-play/disable', methods=['POST'])
@jwt_required()
def disable_auto_play(game_id: int):
    """Désactive l'auto-play."""
```

---

## Algorithmes Clés

### 1. Évaluation d'une planète pour colonisation

```python
def evaluate_planet_value(planet: Planet, player: GamePlayer) -> float:
    """
    Score de 0 à 100 pour une planète.
    """
    score = 0

    # Température (40 points max)
    temp_diff = abs(planet.temperature - 22)
    score += max(0, 40 - temp_diff)

    # Gravité (20 points max)
    grav_diff = abs(planet.gravity - 1.0)
    score += max(0, 20 - grav_diff * 20)

    # Métal (25 points max)
    score += min(25, planet.metal_remaining / 1000)

    # Distance (15 points max, plus proche = mieux)
    distance = calculate_distance(player.home_planet, planet)
    score += max(0, 15 - distance / 10)

    return score
```

### 2. Évaluation d'une cible d'attaque

```python
def evaluate_attack_target(target: Planet, player: GamePlayer) -> float:
    """
    Score d'attractivité pour une attaque.
    """
    score = 0

    # Valeur économique
    score += target.population / 10000
    score += target.metal_remaining / 500

    # Faiblesse défensive
    defenders = get_defending_ships(target)
    if not defenders:
        score += 50  # Bonus si pas de défense
    else:
        defense_power = sum(ship.combat_power for ship in defenders)
        my_nearby_power = get_nearby_fleet_power(player, target)
        if my_nearby_power > defense_power * 1.5:
            score += 30  # Bonus si supériorité

    # Valeur stratégique (position, accès à d'autres planètes)
    score += len(get_reachable_planets(target)) * 2

    return score
```

### 3. Planification d'attaque coordonnée

```python
def plan_coordinated_attack(
    player: GamePlayer,
    targets: List[Planet]
) -> List[FleetOrder]:
    """
    Planifie des attaques pour arriver simultanément.
    """
    orders = []

    # Calculer le temps d'arrivée maximum
    max_travel_time = 0
    for target in targets:
        fleet = select_fleet_for_target(player, target)
        travel_time = calculate_travel_time(fleet, target)
        max_travel_time = max(max_travel_time, travel_time)

    # Planifier les départs pour arrivée synchronisée
    for target in targets:
        fleet = select_fleet_for_target(player, target)
        travel_time = calculate_travel_time(fleet, target)
        delay = max_travel_time - travel_time

        orders.append(FleetOrder(
            fleet=fleet,
            destination=target,
            delay_turns=delay,  # Attendre avant de partir
        ))

    return orders
```

---

## Frontend

### Composants à créer

| Composant | Fichier | Description |
|-----------|---------|-------------|
| AutoPlayButton | AutoPlayButton.tsx | Bouton activation/désactivation |
| AIIndicator | AIIndicator.tsx | Indicateur joueur IA |
| DifficultySelector | DifficultySelector.tsx | Sélection niveau IA |

### Intégration GameView

```typescript
// Dans GameView.tsx

const [autoPlayEnabled, setAutoPlayEnabled] = useState(false);

const toggleAutoPlay = async () => {
    if (autoPlayEnabled) {
        await api.disableAutoPlay(gameId);
    } else {
        await api.enableAutoPlay(gameId);
    }
    setAutoPlayEnabled(!autoPlayEnabled);
};
```

---

## Tests

### Tests unitaires

- [ ] Test analyse de situation correcte
- [ ] Test décisions économiques cohérentes
- [ ] Test évaluation des cibles
- [ ] Test planification des routes avec ravitaillement
- [ ] Test modificateurs de difficulté
- [ ] Test attaques coordonnées

### Tests d'intégration

- [ ] Test partie IA vs IA complète
- [ ] Test auto-play activation/désactivation
- [ ] Test transitions entre niveaux de difficulté

### Tests de performance

- [ ] Test temps de décision < 1 seconde
- [ ] Test partie 8 joueurs IA fluide

---

## Phases d'Implémentation

### Phase 1 : Infrastructure (Priorité haute) ✅ FAIT
1. ✅ Créer la structure de fichiers `services/ai/`
2. ✅ Implémenter `GameAnalysis`
3. ✅ Créer le modèle de difficulté
4. ✅ Intégrer avec `TurnService`

**Fichiers créés :**
- `backend/app/services/ai/__init__.py`
- `backend/app/services/ai/ai_difficulty.py` - 5 niveaux (Conscrit→Maréchal)
- `backend/app/services/ai/game_analysis.py` - Analyse complète du jeu
- `backend/app/services/ai/ai_service.py` - Service principal

### Phase 2 : Décisions de base (Priorité haute) ✅ FAIT
1. ✅ Implémenter `AIEconomyService` (budgets, construction)
2. ✅ Implémenter `AIResearchService` (intégré dans ai_service.py)
3. ✅ Implémenter `AIExpansionService` (colonisation)

**Fichiers créés/modifiés :**
- `backend/app/services/ai/ai_expansion.py` - Service de colonisation
- `backend/app/services/ai/ai_service.py` - Production et mouvements de flottes
- `backend/app/services/fleet.py` - Auto-colonisation à l'arrivée
- `backend/app/models/fleet.py` - Ajustement portée (35/level) et vitesse (x5)

**Fonctionnalités implémentées :**
- Production automatique de vaisseaux (chasseurs, éclaireurs, coloniaux)
- Création automatique de designs de vaisseaux pour l'IA
- Envoi de flottes coloniales vers planètes accessibles
- Colonisation automatique à l'arrivée
- Vérification de portée/carburant avant mouvement
- Ravitaillement automatique avec mise à jour de la capacité

### Phase 3 : Décisions militaires (Priorité moyenne) 🔄 EN COURS
1. ✅ Implémenter `AIMilitaryService` (attaques simples - intégré)
2. ✅ Ajouter la défense (basique)
3. ⏳ Ajouter l'évaluation des cibles (à améliorer)

### Phase 4 : Fonctionnalités avancées (Priorité moyenne)
1. Attaques coordonnées multi-planètes
2. Utilisation des ravitailleurs
3. Gestion des percées radicales

### Phase 5 : Auto-Play (Priorité basse)
1. Routes API auto-play
2. Composants frontend
3. Gestion de l'état auto-play

### Phase 6 : Polissage (Priorité basse)
1. Affiner les modificateurs de difficulté
2. Tests et équilibrage
3. Optimisation performances

---

## Dépendances

### Requiert (déjà implémenté)
- EPIC 1 : Plateforme (modèles, services)
- EPIC 3 : Système de ressources
- EPIC 4 : Système planétaire
- EPIC 5 : Système technologique
- EPIC 6 : Système de vaisseaux
- EPIC 7 : Système de combat

### Requis par
- EPIC 2 : Configuration de partie (sélection difficulté)
- EPIC 11 : Mode multijoueur (joueurs IA dans parties)

---

## Estimation de complexité

| Phase | Complexité | Description |
|-------|------------|-------------|
| Phase 1 | Moyenne | Structure et analyse |
| Phase 2 | Haute | Logique économique |
| Phase 3 | Haute | Logique militaire |
| Phase 4 | Très haute | Coordination avancée |
| Phase 5 | Basse | Auto-play simple |
| Phase 6 | Moyenne | Équilibrage |

---

## Notes de conception

### Personnalité de l'IA

L'IA devrait avoir des "personnalités" légèrement différentes :
- **Expansionniste** : Priorité colonisation
- **Militariste** : Priorité flottes
- **Technologique** : Priorité recherche
- **Équilibré** : Approche standard

Ces personnalités peuvent être assignées aléatoirement ou configurées.

### Éviter les comportements frustrants

- L'IA ne doit pas "tricher" (pas d'info cachée)
- L'IA ne doit pas cibler un joueur spécifique injustement
- L'IA doit sembler "rationnelle" dans ses décisions

### Debug et observation

Ajouter un mode "debug IA" pour voir les décisions :
```
[IA-Maréchal] Tour 15: Décision d'attaquer Austerlitz
  - Force disponible: 45 vaisseaux
  - Défense estimée: 12 vaisseaux
  - Score cible: 78/100
  - Décision: ATTAQUER
```

---

## Historique

| Date | Changement |
|------|------------|
| 2026-01-05 | Création du plan |
| 2026-01-05 | Phase 1 complète : Infrastructure IA |
| 2026-01-05 | Phase 2 complète : Production, colonisation, mouvements de flottes |
| 2026-01-05 | Ajustements : portée vaisseaux (35/level), vitesse (x5), carburant (100) |
