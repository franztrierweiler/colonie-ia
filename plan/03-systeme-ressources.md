# Plan de Développement - EPIC 3 : Système de Ressources

## Statut Global

| Phase | Description | Statut |
|-------|-------------|--------|
| 1 | Service d'économie | ✅ Terminé |
| 2 | Système de taxation | ✅ Terminé |
| 3 | Système de minage | ✅ Terminé |
| 4 | Système de dette | ✅ Terminé |
| 5 | Intégration fin de tour | ✅ Terminé |
| 6 | API et Frontend | ✅ Backend terminé |

---

## Vue d'ensemble

L'EPIC 3 implémente le système économique du jeu : gestion de l'argent (taxation), du métal (minage) et de la dette.

**Dépendances** : EPIC 2 (modèles Planet, GamePlayer)

**User Stories couvertes** :
- US 3.1 - Gestion de l'argent (taxation des colonies)
- US 3.2 - Gestion du métal (extraction)
- US 3.3 - Épuisement des ressources (métal non-renouvelable)
- US 3.4 - Système de dette (emprunt 5x revenu, 15% intérêt)
- US 3.5 - Disponibilité globale de l'argent

---

## Phase 1 : Service d'économie

### 1.1 Constantes économiques

```python
# Économie globale
INITIAL_MONEY = 10000
INITIAL_METAL = 500
DEBT_MAX_MULTIPLIER = 5  # Max emprunt = 5x revenu
DEBT_INTEREST_RATE = 0.15  # 15% par tour

# Taxation
BASE_TAX_RATE = 0.1  # 10% de la population
POPULATION_THRESHOLD = 10000  # Seuil rentabilité
COLONY_MAINTENANCE_COST = 100  # Coût fixe par colonie

# Minage
BASE_MINING_RATE = 10  # Unités de métal de base par tour
MINING_EFFICIENCY_FACTOR = 0.5  # Facteur logarithmique
```

### 1.2 Formules économiques

**Revenu d'une planète** :
```
if population >= POPULATION_THRESHOLD:
    income = population * BASE_TAX_RATE * habitability
else:
    income = -COLONY_MAINTENANCE_COST * (1 - population/POPULATION_THRESHOLD)
```

**Rendements décroissants (logarithmique)** :
```
effective_output = base_output * log(1 + budget_percentage) / log(2)
```

**Minage** :
```
metal_extracted = min(
    metal_remaining,
    BASE_MINING_RATE * log(1 + mining_budget/50) / log(2)
)
```

### 1.3 Tâches Phase 1

- [ ] T1.1 - Créer `backend/app/services/economy.py`
- [ ] T1.2 - Implémenter constantes économiques
- [ ] T1.3 - Implémenter fonction rendements décroissants
- [ ] T1.4 - Tests unitaires formules

---

## Phase 2 : Système de taxation

### 2.1 Calcul du revenu

Le revenu d'un joueur est la somme des revenus de toutes ses planètes.

```python
class EconomyService:
    @staticmethod
    def calculate_planet_income(planet: Planet) -> int:
        """Calcule le revenu/coût d'une planète."""
        pass

    @staticmethod
    def calculate_player_income(player: GamePlayer) -> int:
        """Calcule le revenu total d'un joueur."""
        pass

    @staticmethod
    def calculate_player_expenses(player: GamePlayer) -> dict:
        """Calcule les dépenses détaillées."""
        pass
```

### 2.2 Tâches Phase 2

- [ ] T2.1 - Implémenter `calculate_planet_income()`
- [ ] T2.2 - Implémenter `calculate_player_income()`
- [ ] T2.3 - Implémenter `calculate_player_expenses()`
- [ ] T2.4 - Ajouter champs `income` et `expenses` à GamePlayer.to_dict()
- [ ] T2.5 - Tests unitaires taxation

---

## Phase 3 : Système de minage

### 3.1 Extraction du métal

```python
class EconomyService:
    @staticmethod
    def calculate_mining_output(planet: Planet, budget_spent: int) -> int:
        """Calcule le métal extrait avec rendements décroissants."""
        pass

    @staticmethod
    def process_planet_mining(planet: Planet) -> int:
        """Exécute le minage et retourne le métal extrait."""
        pass

    @staticmethod
    def process_player_mining(player: GamePlayer) -> dict:
        """Exécute le minage sur toutes les planètes d'un joueur."""
        pass
```

### 3.2 Épuisement des ressources

- Le métal extrait est déduit de `planet.metal_remaining`
- Quand `metal_remaining == 0`, plus d'extraction possible
- Le métal extrait est ajouté au stock global du joueur

### 3.3 Tâches Phase 3

- [ ] T3.1 - Implémenter `calculate_mining_output()`
- [ ] T3.2 - Implémenter `process_planet_mining()`
- [ ] T3.3 - Implémenter `process_player_mining()`
- [ ] T3.4 - Mettre à jour `planet.metal_remaining` après minage
- [ ] T3.5 - Tests unitaires minage

---

## Phase 4 : Système de dette

### 4.1 Mécanisme

- Un joueur peut emprunter jusqu'à 5x son revenu total
- Intérêts de 15% déduits automatiquement chaque tour
- Si le joueur ne peut pas payer les intérêts, il devient négatif

```python
class EconomyService:
    @staticmethod
    def calculate_max_debt(player: GamePlayer) -> int:
        """Calcule la dette maximale autorisée."""
        income = EconomyService.calculate_player_income(player)
        return max(0, income * DEBT_MAX_MULTIPLIER)

    @staticmethod
    def borrow(player: GamePlayer, amount: int) -> bool:
        """Emprunte de l'argent."""
        pass

    @staticmethod
    def repay_debt(player: GamePlayer, amount: int) -> bool:
        """Rembourse une partie de la dette."""
        pass

    @staticmethod
    def process_interest(player: GamePlayer) -> int:
        """Calcule et déduit les intérêts de la dette."""
        pass
```

### 4.2 Tâches Phase 4

- [ ] T4.1 - Implémenter `calculate_max_debt()`
- [ ] T4.2 - Implémenter `borrow()`
- [ ] T4.3 - Implémenter `repay_debt()`
- [ ] T4.4 - Implémenter `process_interest()`
- [ ] T4.5 - Tests unitaires dette

---

## Phase 5 : Intégration fin de tour

### 5.1 Service de tour

```python
class TurnService:
    @staticmethod
    def process_turn(game: Game) -> dict:
        """Exécute toutes les actions de fin de tour."""
        results = {
            "turn": game.current_turn,
            "players": {}
        }

        for player in game.players:
            player_result = TurnService.process_player_turn(player)
            results["players"][player.id] = player_result

        game.current_turn += 1
        game.current_year += game.turn_duration_years

        return results

    @staticmethod
    def process_player_turn(player: GamePlayer) -> dict:
        """Exécute les actions économiques pour un joueur."""
        # 1. Calculer revenus
        # 2. Calculer intérêts dette
        # 3. Exécuter minage
        # 4. Exécuter terraformation (EPIC 4)
        # 5. Mettre à jour population
        # 6. Appliquer changements
        pass
```

### 5.2 Ordre des opérations de fin de tour

1. **Revenus** : Calculer et ajouter les revenus des colonies
2. **Intérêts** : Déduire les intérêts de la dette
3. **Minage** : Extraire le métal des planètes
4. **Terraformation** : Modifier les températures (EPIC 4)
5. **Population** : Croissance naturelle
6. **Validation** : Vérifier élimination (banqueroute)

### 5.3 Tâches Phase 5

- [ ] T5.1 - Créer `backend/app/services/turn.py`
- [ ] T5.2 - Implémenter `TurnService.process_turn()`
- [ ] T5.3 - Implémenter `process_player_turn()`
- [ ] T5.4 - Implémenter calcul de croissance population
- [ ] T5.5 - Implémenter vérification élimination
- [ ] T5.6 - Tests intégration fin de tour

---

## Phase 6 : API et Frontend

### 6.1 Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/games/:id/economy` | État économique du joueur |
| POST | `/api/games/:id/borrow` | Emprunter de l'argent |
| POST | `/api/games/:id/repay` | Rembourser la dette |
| PATCH | `/api/planets/:id/budget` | Modifier le budget planétaire |
| POST | `/api/games/:id/end-turn` | Terminer son tour |

### 6.2 Schémas API

```python
class BorrowSchema(BaseModel):
    amount: int = Field(gt=0)

class RepaySchema(BaseModel):
    amount: int = Field(gt=0)

class PlanetBudgetSchema(BaseModel):
    terraform_budget: int = Field(ge=0, le=100)
    mining_budget: int = Field(ge=0, le=100)
    # terraform_budget + mining_budget = 100

class EconomyResponse(BaseModel):
    money: int
    metal: int
    debt: int
    income: int
    expenses: int
    max_debt: int
    planets: List[PlanetEconomyResponse]
```

### 6.3 Composants Frontend

```
frontend/src/
├── components/
│   ├── EconomyPanel.tsx       # Vue globale économie
│   ├── PlanetBudgetSlider.tsx # Slider terraform/minage
│   ├── DebtPanel.tsx          # Gestion dette
│   └── IncomeBreakdown.tsx    # Détail revenus
├── hooks/
│   └── useEconomy.ts          # Hook gestion économie
```

### 6.4 Tâches Phase 6

- [ ] T6.1 - Endpoint GET /api/games/:id/economy
- [ ] T6.2 - Endpoint POST /api/games/:id/borrow
- [ ] T6.3 - Endpoint POST /api/games/:id/repay
- [ ] T6.4 - Endpoint PATCH /api/planets/:id/budget
- [ ] T6.5 - Endpoint POST /api/games/:id/end-turn
- [ ] T6.6 - Documentation Swagger
- [ ] T6.7 - Composant EconomyPanel
- [ ] T6.8 - Composant PlanetBudgetSlider
- [ ] T6.9 - Composant DebtPanel
- [ ] T6.10 - Hook useEconomy
- [ ] T6.11 - Tests API

---

## Critères d'acceptation EPIC 3

- [ ] Les revenus sont calculés correctement selon la population
- [ ] Le minage extrait du métal avec rendements décroissants
- [ ] Le métal s'épuise définitivement quand les réserves sont vides
- [ ] La dette est limitée à 5x le revenu
- [ ] Les intérêts de 15% sont déduits chaque tour
- [ ] L'argent est disponible instantanément (pas de logistique)
- [ ] Le slider budget fonctionne correctement
- [ ] La fin de tour exécute toutes les opérations économiques

---

## Risques et mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Formules déséquilibrées | Élevé | Tests avec différents scénarios, ajustement des constantes |
| Boucle infinie dette | Élevé | Plafonner la dette, vérifier chaque tour |
| Performance fin de tour | Moyen | Optimiser requêtes DB, batch updates |

---

## Notes techniques

### Rendements décroissants

La formule logarithmique assure que doubler le budget ne double pas le résultat :

| Budget % | Efficacité relative |
|----------|---------------------|
| 10% | 0.26 |
| 25% | 0.49 |
| 50% | 0.74 |
| 75% | 0.91 |
| 100% | 1.00 |

### Équilibre économique

- Une colonie devient rentable à ~10 000 habitants
- Le minage intensif épuise rapidement les réserves
- La dette permet des investissements risqués mais coûteux

---

*Document généré pour EPIC 3 - Système de Ressources*
*Projet Colonie-IA*
