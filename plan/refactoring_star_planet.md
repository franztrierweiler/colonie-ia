# Plan de Refactorisation : Fusion Star/Planet

**Date** : 2025-12-31
**Objectif** : Simplifier le modèle de données en fusionnant `Star` et `Planet` en un seul modèle `Planet`
**Branche de sauvegarde** : `mini_sys_solaire` (conserve l'ancien modèle)

## Contexte

Le modèle actuel utilise une hiérarchie `Galaxy → Star → Planet` (1-4 planètes par étoile).
Dans Spaceward Ho!, chaque point sur la carte est directement une planète colonisable.
Cette refactorisation simplifie le modèle pour coller au gameplay original.

## Impact des fichiers

### Backend (7 fichiers)

| Fichier | Impact | Description |
|---------|--------|-------------|
| `backend/app/models/galaxy.py` | **MAJEUR** | Supprimer `Star`, modifier `Planet`, adapter `Galaxy` |
| `backend/app/models/fleet.py` | **MAJEUR** | Remplacer `star_id` par `planet_id` |
| `backend/app/models/__init__.py` | Mineur | Supprimer export de `Star` |
| `backend/app/services/galaxy_generator.py` | **MAJEUR** | Réécrire génération (plus de stars intermédiaires) |
| `backend/app/services/game_service.py` | Modéré | Adapter `find_home_planets` |
| `backend/app/routes/games.py` | Modéré | Adapter `get_game_map` (retourner planets au lieu de stars) |
| `backend/app/data/__init__.py` | Mineur | PLANET_SUFFIXES devient inutile |

### Frontend (6 fichiers)

| Fichier | Impact | Description |
|---------|--------|-------------|
| `frontend/src/hooks/useGameState.ts` | **MAJEUR** | Supprimer type `Star`, adapter `Planet`, renommer helpers |
| `frontend/src/components/game/GalaxyMap.tsx` | **MAJEUR** | Utiliser `Planet[]` au lieu de `Star[]` |
| `frontend/src/components/game/StarSystem.tsx` | **SUPPRIMER** | Remplacé par `PlanetMarker` étendu |
| `frontend/src/components/game/PlanetMarker.tsx` | **MAJEUR** | Fusionner avec logique de StarSystem |
| `frontend/src/components/game/PlanetPanel.tsx` | Modéré | Supprimer références à star_id |
| `frontend/src/services/api.ts` | Mineur | Adapter types si nécessaire |

### Base de données

- Migration destructive requise (drop tables stars, planets + recreate planets)
- Perte des parties de développement existantes (acceptable)

---

## Plan d'exécution détaillé

### Phase 1 : Backend - Modèles (priorité haute)

#### 1.1 Modifier `backend/app/models/galaxy.py`

**Avant** :
```python
class Galaxy → stars (relationship)
class Star → planets (relationship), x, y, name, is_nova
class Planet → star_id, orbit_index, ...
```

**Après** :
```python
class Galaxy → planets (relationship)
class Planet → galaxy_id, x, y, name, is_nova, temperature, gravity, ...
```

**Actions** :
- [ ] Supprimer la classe `Star`
- [ ] Ajouter à `Planet` : `galaxy_id`, `x`, `y`, `is_nova`, `nova_turn`
- [ ] Supprimer de `Planet` : `star_id`, `orbit_index`
- [ ] Modifier `Galaxy.stars` → `Galaxy.planets`
- [ ] Adapter les méthodes `to_dict()`

#### 1.2 Modifier `backend/app/models/fleet.py`

**Actions** :
- [ ] Renommer `current_star_id` → `current_planet_id`
- [ ] Renommer `destination_star_id` → `destination_planet_id`
- [ ] Adapter les relationships
- [ ] Adapter `to_dict()`

#### 1.3 Modifier `backend/app/models/__init__.py`

**Actions** :
- [ ] Supprimer l'import/export de `Star`

---

### Phase 2 : Backend - Services

#### 2.1 Réécrire `backend/app/services/galaxy_generator.py`

**Avant** :
```python
generate() → crée Stars → pour chaque Star, crée 1-4 Planets
_create_star() → Star(galaxy_id, x, y, name)
_generate_planets() → [Planet(star_id, orbit_index, ...)]
```

**Après** :
```python
generate() → crée Planets directement
_create_planet() → Planet(galaxy_id, x, y, name, temperature, gravity, ...)
```

**Actions** :
- [ ] Supprimer `_create_star()`
- [ ] Supprimer `_generate_planets()`
- [ ] Fusionner la logique dans `_create_planet()`
- [ ] Adapter la méthode `generate()` pour créer des planètes directement
- [ ] Conserver la logique de génération de positions (cercle, spiral, cluster, random)
- [ ] Renommer variables `star_count` → `planet_count`

#### 2.2 Adapter `backend/app/services/game_service.py`

**Actions** :
- [ ] Adapter `find_home_planets()` : plus de double boucle stars→planets
- [ ] Simplifier l'accès aux planètes (direct depuis galaxy.planets)

---

### Phase 3 : Backend - Routes

#### 3.1 Adapter `backend/app/routes/games.py`

**Avant** (route `/games/<id>/map`) :
```python
stars_data = []
for star in galaxy.stars:
    star_dict = star.to_dict()
    star_dict["planets"] = [planet.to_dict() for planet in star.planets]
    stars_data.append(star_dict)
return {"stars": stars_data, ...}
```

**Après** :
```python
planets_data = [planet.to_dict() for planet in galaxy.planets]
return {"planets": planets_data, ...}
```

**Actions** :
- [ ] Simplifier `get_game_map()` pour retourner `planets` au lieu de `stars`
- [ ] Supprimer la clé `stars` de la réponse JSON
- [ ] Supprimer `star_count` de galaxy (ou le renommer en `planet_count`)

---

### Phase 4 : Frontend - Types et État

#### 4.1 Modifier `frontend/src/hooks/useGameState.ts`

**Avant** :
```typescript
interface Planet { star_id, orbit_index, ... }
interface Star { id, name, x, y, is_nova, planets: Planet[] }
interface GameState { stars: Star[], ... }
```

**Après** :
```typescript
interface Planet { id, name, x, y, is_nova, temperature, gravity, ... }
interface GameState { planets: Planet[], ... }
```

**Actions** :
- [ ] Supprimer l'interface `Star`
- [ ] Ajouter `x`, `y`, `is_nova`, `nova_turn` à `Planet`
- [ ] Supprimer `star_id`, `orbit_index` de `Planet`
- [ ] Renommer `GameState.stars` → `GameState.planets`
- [ ] Adapter `refreshMap()` pour utiliser `data.planets`
- [ ] Renommer `getStarById` → `getPlanetById`
- [ ] Renommer `getFleetsAtStar` → `getFleetsAtPlanet`
- [ ] Renommer `selectedStarId` → `selectedPlanetId`

---

### Phase 5 : Frontend - Composants

#### 5.1 Fusionner `StarSystem.tsx` dans `PlanetMarker.tsx`

Le composant `StarSystem` affiche actuellement :
- Le halo de l'étoile
- Le coeur de l'étoile
- Les indicateurs de possession
- Les planètes en orbite (via PlanetMarker)
- Le nom de l'étoile

Le nouveau `PlanetMarker` doit :
- Afficher un point pour la planète
- Indicateur de possession (cercle coloré)
- Nom de la planète
- Gestion du clic

**Actions** :
- [ ] Créer nouveau `PlanetMarker.tsx` avec la logique fusionnée
- [ ] Supprimer `StarSystem.tsx`
- [ ] Simplifier (pas d'orbites, pas de planètes multiples)

#### 5.2 Adapter `GalaxyMap.tsx`

**Avant** :
```tsx
{stars.map((star) => (
  <StarSystem key={star.id} star={star} ... />
))}
```

**Après** :
```tsx
{planets.map((planet) => (
  <PlanetMarker key={planet.id} planet={planet} ... />
))}
```

**Actions** :
- [ ] Renommer props `stars` → `planets`
- [ ] Utiliser `PlanetMarker` au lieu de `StarSystem`
- [ ] Adapter les trajectoires de flottes (utiliser planet.x, planet.y)
- [ ] Adapter `onStarClick` → `onPlanetClick`

#### 5.3 Adapter `PlanetPanel.tsx`

**Actions** :
- [ ] Supprimer les références à `star_id`
- [ ] Vérifier que le reste fonctionne avec le nouveau modèle

---

### Phase 6 : Migration de base de données

#### 6.1 Procédure de migration

**Option 1 : Réinitialisation complète (recommandé pour dev)**
```bash
# Supprimer la base SQLite existante
rm -f backend/instance/dev.db

# Recréer avec les nouvelles migrations
cd backend
flask db upgrade
```

**Option 2 : Migration Alembic**
Créer un fichier `migrations/versions/xxx_refactor_star_planet.py` avec :
- Suppression des tables `planets` et `stars`
- Recréation de `planets` avec les colonnes x, y, is_nova, galaxy_id
- Modification de `fleets` : renommer `current_star_id` → `current_planet_id`
- Modification de `galaxies` : renommer `star_count` → `planet_count`

**Statut** : ✅ Terminé (backend adapté, migration à faire par l'utilisateur)

---

### Phase 7 : Tests et validation

- [ ] Lancer le backend et vérifier qu'il démarre sans erreur
- [ ] Créer une nouvelle partie et vérifier la génération de galaxie
- [ ] Vérifier l'affichage de la carte dans le frontend
- [ ] Tester la sélection de planète
- [ ] Tester le panneau de planète
- [ ] Vérifier les flottes (si implémentées)

---

## Ordre d'exécution recommandé

1. **Phase 1.1** - Modèle Galaxy/Planet (backend)
2. **Phase 1.2** - Modèle Fleet (backend)
3. **Phase 1.3** - Exports __init__ (backend)
4. **Phase 2.1** - Galaxy Generator (backend)
5. **Phase 2.2** - Game Service (backend)
6. **Phase 3.1** - Routes (backend)
7. **Phase 6.1** - Migration BDD
8. **Test backend** - Vérifier que l'API fonctionne
9. **Phase 4.1** - Types frontend
10. **Phase 5.1** - PlanetMarker
11. **Phase 5.2** - GalaxyMap
12. **Phase 5.3** - PlanetPanel
13. **Phase 7** - Tests finaux

---

## Risques et mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Perte de données | Faible | Projet en dev, pas de données importantes |
| Régression frontend | Moyen | Tester chaque composant après modification |
| API breaking change | Moyen | Modifier frontend et backend ensemble |
| Confusion star/planet | Faible | Renommer systématiquement partout |

---

## Checklist finale

- [x] Toutes les références à `Star` supprimées du backend
- [x] Toutes les références à `Star` supprimées du frontend
- [x] Toutes les références à `star_id` remplacées par `planet_id`
- [x] Compilation TypeScript sans erreur
- [x] Syntaxe Python valide
- [x] Tests manuels passants
- [ ] Commit final sur `main`

---

## Statut d'exécution

| Phase | Statut |
|-------|--------|
| 1.1 Modèle Galaxy/Planet | ✅ Terminé |
| 1.2 Modèle Fleet | ✅ Terminé |
| 1.3 Exports __init__ | ✅ Terminé |
| 2.1 Galaxy Generator | ✅ Terminé |
| 2.2 Game Service | ✅ Terminé |
| 3.1 Routes games/fleet | ✅ Terminé |
| 4.1 Types frontend | ✅ Terminé |
| 5.1 PlanetMarker | ✅ Terminé |
| 5.2 GalaxyMap | ✅ Terminé |
| 5.3 PlanetPanel/GameView | ✅ Terminé |
| 6.1 Migration BDD | ✅ Terminé |
| 7 Tests validation | ✅ Terminé |

**Date de complétion** : 2025-12-31

---

## Notes de migration

La migration Alembic `df6c67f4dfd5_refactor_star_planet_fusion.py` a été créée et appliquée avec succès.

Procédure appliquée :
1. Suppression des volumes Docker (`docker compose down -v`)
2. Redémarrage des containers (`docker compose up -d`)
3. Application des migrations (`flask db upgrade`)

Tests validés :
- Création d'utilisateurs
- Création de partie avec 2 joueurs
- Génération de 50 planètes avec coordonnées x, y directes
- Attribution des home planets aux joueurs
- API `/games/{id}/map` retourne `planets[]` au lieu de `stars[]`
