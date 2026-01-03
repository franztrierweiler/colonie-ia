# Plan EPIC 5 : Système Technologique

## Vue d'ensemble

Ce plan documente l'implémentation du système de recherche technologique avec 6 domaines :
- **Portée** : distance de vol avant ravitaillement
- **Vitesse** : rapidité de déplacement + priorité au combat
- **Armes** : puissance offensive
- **Boucliers** : résistance aux dégâts
- **Miniaturisation** : réduit coût métal, augmente coût argent
- **Radical** : percées imprévisibles

## User Stories

### US 5.1 - Recherche Portée
**Statut : TERMINÉ**

**Implémentation :**
- Modèle : `backend/app/models/technology.py` - `PlayerTechnology.range_level`, `range_progress`, `range_budget`
- Service : `backend/app/services/technology.py` - `calculate_research_output()`, `process_player_research()`
- Route : `GET /api/games/:id/technology`, `PATCH /api/games/:id/technology/budget`
- Frontend : `frontend/src/components/game/TechPanel.tsx` - barre verticale avec niveau et progression

---

### US 5.2 - Recherche Vitesse
**Statut : TERMINÉ**

**Implémentation :**
- Même structure que US 5.1 avec `speed_level`, `speed_progress`, `speed_budget`

---

### US 5.3 - Recherche Armes
**Statut : TERMINÉ**

**Implémentation :**
- Même structure que US 5.1 avec `weapons_level`, `weapons_progress`, `weapons_budget`

---

### US 5.4 - Recherche Boucliers
**Statut : TERMINÉ**

**Implémentation :**
- Même structure que US 5.1 avec `shields_level`, `shields_progress`, `shields_budget`

---

### US 5.5 - Recherche Miniaturisation
**Statut : TERMINÉ**

**Implémentation :**
- Même structure que US 5.1 avec `mini_level`, `mini_progress`, `mini_budget`

---

### US 5.6 - Recherche Radicale
**Statut : TERMINÉ**

**Implémentation :**
- Modèle : `radical_level`, `radical_progress`, `radical_budget`
- Seuil de percée : `RADICAL_BREAKTHROUGH_THRESHOLD = 500` points
- Déblocages spéciaux : `decoy_unlocked`, `biological_unlocked`
- Bonus temporaires : `temp_*_bonus`, `temp_bonus_expires_turn`

---

### US 5.7 - Mécanisme de percée radicale
**Statut : EN COURS (95%)**

**Ce qui est fait :**
- Modèle `RadicalBreakthrough` avec options, eliminated_option, unlocked_option
- Types de percées (`RadicalBreakthroughType`) :
  - TECH_BONUS_RANGE/SPEED/WEAPONS/SHIELDS : +2 niveaux temporaires
  - TERRAFORM_BOOST : terraformation accélérée
  - SPY_INFO : info planètes ennemies
  - STEAL_TECH : voler technologie
  - UNLOCK_DECOY : débloquer vaisseaux Leurre
  - UNLOCK_BIOLOGICAL : débloquer vaisseaux Biologiques
- Service `_create_radical_breakthrough()` : génère 4 options aléatoires
- Service `eliminate_breakthrough_option()` : joueur élimine 1 option, 1 des 3 restantes débloquée
- Routes API :
  - `GET /api/games/:id/breakthroughs` : percées en attente
  - `POST /api/breakthroughs/:id/eliminate` : résoudre une percée
  - `GET /api/breakthroughs/:id` : détails d'une percée
- Frontend `BreakthroughModal.tsx` :
  - Affiche les 4 options avec icônes et descriptions
  - Sélection de l'option à éliminer
  - Animation de résolution et affichage du résultat
  - Gestion des états de chargement et erreur

**Ce qui reste :**
- [ ] Intégration du modal dans GameView (affichage automatique quand percée en attente)
- [ ] Effets TODO dans `_apply_breakthrough_effect()` :
  - TERRAFORM_BOOST : tracker la durée de boost
  - SPY_INFO : révéler les infos planétaires
  - STEAL_TECH : implémenter le vol de technologie

---

### US 5.8 - Comparaison technologique
**Statut : TERMINÉ**

**Implémentation :**
- Service : `get_technology_comparison()` - retourne position relative (ahead/behind/equal)
- Route : `GET /api/games/:id/technology/comparison`
- Frontend : `frontend/src/components/game/TechComparisonModal.tsx`
  - Tableau avec vos niveaux
  - Comparaison relative avec chaque adversaire
  - Légende : + en avance, = égal, - en retard

---

## Architecture Technique

### Modèles (backend/app/models/technology.py)

```
PlayerTechnology
├── player_id (FK -> game_players)
├── Niveaux : range_level, speed_level, weapons_level, shields_level, mini_level, radical_level
├── Progression : *_progress (float, points vers niveau suivant)
├── Budget : *_budget (int 0-100, total = 100)
├── Déblocages : decoy_unlocked, biological_unlocked
└── Bonus temp : temp_*_bonus, temp_bonus_expires_turn

RadicalBreakthrough
├── player_id (FK -> game_players)
├── options (JSON, 4 types de percée)
├── eliminated_option (choix du joueur)
├── unlocked_option (résultat aléatoire)
├── is_resolved, created_turn, resolved_turn
```

### Service (backend/app/services/technology.py)

```
TechnologyService
├── initialize_player_technology() : init à la création du joueur
├── update_research_budget() : modifier allocation (total = 100)
├── calculate_research_cost() : coût niveau suivant (log scaling)
├── calculate_research_output() : points recherche/tour (diminishing returns)
├── process_player_research() : traitement fin de tour
├── _create_radical_breakthrough() : générer 4 options
├── eliminate_breakthrough_option() : résoudre percée
├── get_technology_comparison() : comparaison relative
├── can_build_ship_type() : vérifier déblocages
├── get_max_tech_levels() : niveaux max pour designs
└── validate_design_tech_levels() : validation conception vaisseaux
```

### Routes API (backend/app/routes/technology.py)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | /games/:id/technology | État technologique complet |
| PATCH | /games/:id/technology/budget | Modifier allocation budget |
| GET | /games/:id/technology/comparison | Comparaison avec adversaires |
| GET | /games/:id/technology/max-levels | Niveaux max pour conception |
| GET | /games/:id/breakthroughs | Percées en attente |
| POST | /breakthroughs/:id/eliminate | Résoudre une percée |
| GET | /breakthroughs/:id | Détails d'une percée |

### Frontend

| Composant | Fichier | Description |
|-----------|---------|-------------|
| TechPanel | TechPanel.tsx | Barres verticales, édition budget |
| TechComparisonModal | TechComparisonModal.tsx | Comparaison adversaires |
| BreakthroughModal | BreakthroughModal.tsx | Choix percée radicale (4 options) |

---

## Formules

### Coût niveau suivant
```
cost = BASE_RESEARCH_COST * (1.5 ^ current_level)
BASE_RESEARCH_COST = 100
```

### Points recherche par tour
```
base_research = income * 0.1
effective_output = diminishing_returns(budget_pct, base_research)
```

### Percée radicale
```
RADICAL_BREAKTHROUGH_THRESHOLD = 500 points
TEMP_BONUS_VALUE = +2 niveaux
TEMP_BONUS_DURATION = 5 tours
```

---

## Migration Base de Données

Fichier : `backend/migrations/versions/765d8d414750_add_technology_system_models.py`

Tables créées :
- `player_technologies`
- `radical_breakthroughs`

---

## Tests

**À faire :**
- [ ] Tests unitaires TechnologyService
- [ ] Tests API routes technology
- [ ] Tests intégration process_player_research avec TurnService

---

## Intégration

### Avec système de tour (turn.py)
- `process_player_research()` appelé à chaque fin de tour
- Expiration des bonus temporaires

### Avec système de vaisseaux (fleet.py)
- `can_build_ship_type()` vérifie déblocages Leurre/Biological
- `get_max_tech_levels()` limite les niveaux tech dans les designs
- `validate_design_tech_levels()` valide les conceptions

---

## Historique

| Date | Changement |
|------|------------|
| 2025-01 | Implémentation initiale backend (modèles, service, routes) |
| 2025-01 | Implémentation frontend (TechPanel, TechComparisonModal) |
| 2025-01 | Documentation rétroactive du plan |
| 2026-01-03 | Création BreakthroughModal.tsx pour choix des percées radicales |
