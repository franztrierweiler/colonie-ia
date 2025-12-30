# Plan de Développement - EPIC 4 : Système Planétaire

## Statut Global

| Phase | Description | Statut |
|-------|-------------|--------|
| 1 | Modèle Planet | ✅ Terminé (EPIC 2) |
| 2 | États des planètes | ✅ Terminé (EPIC 2) |
| 3 | Économie planétaire | ✅ Terminé (EPIC 3) |
| 4 | Budget planétaire | ✅ Terminé (EPIC 3) |
| 5 | Rendements décroissants | ✅ Terminé (EPIC 3) |
| 6 | Terraformation | ✅ Terminé |
| 7 | Abandon de planète | ✅ Terminé |

---

## Vue d'ensemble

L'EPIC 4 gère le système planétaire : caractéristiques, terraformation, économie et abandon.

**Dépendances** : EPIC 2 (modèles), EPIC 3 (économie)

**User Stories couvertes** :
- US 4.1 - Caractéristiques planétaires (température, gravité, métal)
- US 4.2 - Terraformation (modifier température vers 22°C)
- US 4.3 - États des planètes (cycle de vie)
- US 4.4 - Économie planétaire (revenus/coûts)
- US 4.5 - Budget planétaire (slider terraform/minage)
- US 4.6 - Rendements décroissants
- US 4.7 - Abandon de planète

---

## Implémentation

### Déjà implémenté (EPICs précédents)

**Modèle Planet** (`backend/app/models/galaxy.py`) :
- `temperature` / `current_temperature` - Température originale et actuelle
- `gravity` - Gravité (fixe)
- `metal_reserves` / `metal_remaining` - Ressources métal
- `state` - État (PlanetState enum)
- `population` / `max_population` - Population
- `terraform_budget` / `mining_budget` - Allocation budget
- `habitability` - Propriété calculée

**Service Économie** (`backend/app/services/economy.py`) :
- `calculate_planet_income()` - Revenu/coût d'une planète
- `process_planet_mining()` - Extraction de métal
- `diminishing_returns()` - Rendements décroissants

### Nouvelles fonctionnalités (EPIC 4)

**Terraformation** :
```python
# Constantes
IDEAL_TEMPERATURE = 22.0  # °C
BASE_TERRAFORM_RATE = 5.0  # degrés/tour à 100% budget

# Méthodes
EconomyService.calculate_terraform_change(planet) -> float
EconomyService.process_planet_terraformation(planet) -> dict
EconomyService.process_player_terraformation(player) -> dict
```

**Abandon de planète** :
```python
EconomyService.abandon_planet(planet, strip_mine=True) -> dict
# - strip_mine=True : récupère 50% du métal restant
# - Passe l'état à ABANDONED
# - Libère la planète (owner_id = None)
```

---

## API Endpoints

| Méthode | Endpoint | Description | Statut |
|---------|----------|-------------|--------|
| GET | `/api/planets/:id` | Détails d'une planète | ✅ |
| PATCH | `/api/planets/:id/budget` | Modifier budget | ✅ (EPIC 3) |
| POST | `/api/planets/:id/abandon` | Abandonner planète | ✅ |

---

## Intégration fin de tour

La terraformation est exécutée automatiquement à chaque fin de tour :

```python
# Dans TurnService.process_player_turn()
# 4. Process terraformation
terraformation = EconomyService.process_player_terraformation(player)
result["terraformation"] = terraformation
```

---

## Formules

### Terraformation

```
temp_diff = 22 - current_temperature
population_factor = 1 + (population / 200000)
base_change = 5.0 * population_factor
effective_change = diminishing_returns(terraform_budget/100, base_change)
new_temp = current_temp + min(effective_change, temp_diff)
```

### Habitabilité

```
temp_factor = max(0, 1 - |current_temp - 22| / 100)
gravity_factor = max(0, 1 - |gravity - 1.0| / 2)
habitability = temp_factor * gravity_factor
max_population = 1_000_000 * habitability
```

---

## Tests

- [x] Tests unitaires terraformation (6 tests)
- [x] Tests unitaires abandon (6 tests)
- [x] Test intégration fin de tour avec terraformation

---

## Critères d'acceptation

- [x] La température peut être modifiée vers 22°C via terraformation
- [x] La terraformation utilise les rendements décroissants
- [x] La terraformation augmente la capacité de population max
- [x] Une planète peut être abandonnée
- [x] L'abandon récupère 50% du métal restant (strip-mine)
- [x] L'abandon libère la planète pour recolonisation

---

*Document généré pour EPIC 4 - Système Planétaire*
*Projet Colonie-IA*
