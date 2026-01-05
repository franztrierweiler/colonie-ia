# Plan EPIC 10 : Interface Utilisateur

## Statut Global

| Phase | Description | Statut |
|-------|-------------|--------|
| 1 | Infrastructure (Backend + Base Frontend) | ✅ Terminé |
| 2 | Carte stellaire (US 10.1, 10.2, 10.3) | ✅ Terminé |
| 3 | Panneau planète (US 10.5, 10.6) | ✅ Terminé |
| 4 | Gestion flottes (US 10.4, 10.9) | ✅ Terminé |
| 5 | Rapports et historique (US 10.7, 10.8) | 🟡 Partiel |
| 6 | Finitions (US 10.10) | En attente |

**Commit Phase 1** : `8b1122f` - EPIC 10 Phase 1 : Infrastructure carte de jeu
**Commit Phase 2** : `37e7f67` - EPIC 10 Phase 2 : Carte stellaire interactive
**Commit Phase 3** : `82cf33c` - EPIC 10 Phase 3 : Panneau planète avec sliders budget
**Commit Phase 4** : `d5e8419` - EPIC 10: Interface GameView style Spaceward Ho! + système flottes

### Détail Phase 5 (Partiel)
- ✅ US 10.8 Rapport de tour : CombatReportPanel implémenté (EPIC 7)
- ✅ TechPanel avec comparaison technologique (EPIC 5)
- ❌ US 10.7 Graphique historique : Non implémenté

## Vue d'ensemble

L'EPIC 10 couvre l'interface de jeu principale permettant aux joueurs de visualiser et interagir avec la galaxie, leurs planètes et flottes.

## User Stories

| US | Description | Priorité | Dépendances |
|----|-------------|----------|-------------|
| 10.1 | Carte stellaire 2D | Haute | Backend map endpoint |
| 10.2 | Niveaux de zoom (3 niveaux) | Haute | US 10.1 |
| 10.3 | Représentation visuelle planètes | Haute | US 10.1 |
| 10.4 | Lignes de trajectoire flottes | Moyenne | EPIC 6 (✓ fait) |
| 10.5 | Panneau d'information planète | Haute | EPIC 3, 4 (✓ fait) |
| 10.6 | Graphique budget pseudo-log | Moyenne | US 10.5 |
| 10.7 | Graphique historique | Basse | - |
| 10.8 | Rapport de tour | Moyenne | Turn system |
| 10.9 | Barre latérale gestion flottes | Haute | EPIC 6 (✓ fait) |
| 10.10 | Sauvegarde disposition fenêtres | Basse | - |

## Architecture Frontend

```
frontend/src/
├── pages/
│   └── GameView.tsx              # Page principale de jeu
├── components/game/
│   ├── GalaxyMap.tsx             # Carte stellaire canvas/SVG
│   ├── StarSystem.tsx            # Rendu d'une étoile
│   ├── PlanetMarker.tsx          # Marqueur planète (bicorne/?)
│   ├── FleetMarker.tsx           # Marqueur flotte
│   ├── FleetTrajectory.tsx       # Lignes de trajectoire (en transit)
│   ├── RoutePreview.tsx          # Prévisualisation route (pendant drag)
│   ├── WaypointMarker.tsx        # Marqueur escale suggérée
│   ├── ZoomControls.tsx          # Contrôles de zoom
│   ├── PlanetPanel.tsx           # Panneau info planète
│   ├── BudgetSlider.tsx          # Slider budget avec courbe log
│   ├── FleetSidebar.tsx          # Barre latérale flottes
│   ├── FleetCard.tsx             # Carte d'une flotte
│   ├── FleetSelectionModal.tsx   # Sélection flottes à envoyer
│   ├── TurnReport.tsx            # Rapport de tour
│   ├── HistoryChart.tsx          # Graphique historique
│   └── MiniMap.tsx               # Mini-carte (optionnel)
├── hooks/
│   ├── useGameState.ts           # État global du jeu
│   ├── useMapControls.ts         # Pan, zoom, sélection
│   ├── useDragRoute.ts           # Gestion drag planète→planète
│   └── useWindowLayout.ts        # Sauvegarde disposition
└── services/
    ├── api.ts                    # Endpoints API
    └── RouteCalculator.ts        # Calcul routes côté client (preview)
```

## Architecture Backend (additions)

```
backend/app/
├── services/
│   └── route.py                  # RouteService - calcul de routes A*
└── routes/
    └── fleet.py                  # + endpoints calculate-route, move-with-waypoints
```

## Nouveaux Endpoints Backend Requis

### GET /api/games/:id/map
Retourne la carte complète avec étoiles, planètes et flottes visibles.

```json
{
  "galaxy": {
    "width": 200,
    "height": 200,
    "shape": "spiral"
  },
  "stars": [
    {
      "id": 1,
      "name": "Austerlitz",
      "x": 50.0,
      "y": 75.0,
      "planets": [
        {
          "id": 1,
          "name": "Austerlitz I",
          "state": "colonized",
          "owner_id": 1,
          "population": 500000
        }
      ]
    }
  ],
  "fleets": [
    {
      "id": 1,
      "name": "1ère Flotte",
      "player_id": 1,
      "current_star_id": 1,
      "status": "stationed",
      "ship_count": 5
    }
  ],
  "my_player_id": 1
}
```

### POST /api/games/:id/calculate-route
Calcule la meilleure route entre deux planètes pour une flotte donnée.

**Request:**
```json
{
  "fleet_id": 1,
  "from_planet_id": 1,
  "to_planet_id": 5
}
```

**Response:**
```json
{
  "reachable": true,
  "direct_route": false,
  "waypoints": [
    {"id": 3, "name": "Marengo", "x": 45.0, "y": 60.0}
  ],
  "segments": [
    {
      "from_id": 1,
      "to_id": 3,
      "distance": 12.5,
      "travel_turns": 2
    },
    {
      "from_id": 3,
      "to_id": 5,
      "distance": 8.3,
      "travel_turns": 1
    }
  ],
  "total_distance": 20.8,
  "total_turns": 3,
  "fleet_range": 15.0
}
```

**Si route impossible:**
```json
{
  "reachable": false,
  "direct_route": false,
  "waypoints": [],
  "segments": [],
  "reason": "No allied planets within range to create a route",
  "fleet_range": 15.0,
  "direct_distance": 45.2
}
```

### POST /api/fleets/:id/move-with-waypoints
Déplace une flotte avec des escales programmées.

**Request:**
```json
{
  "waypoints": [3, 5]  // IDs des planètes dans l'ordre
}
```

**Response:**
```json
{
  "success": true,
  "message": "Fleet departing for Marengo (waypoint 1/2)",
  "fleet": {...},
  "planned_route": [
    {"planet_id": 3, "arrival_turn": 3},
    {"planet_id": 5, "arrival_turn": 5}
  ]
}
```

### GET /api/games/:id/turn-report
Retourne le rapport du dernier tour.

```json
{
  "turn": 5,
  "events": [
    {"type": "construction", "message": "3 Chasseurs construits sur Austerlitz"},
    {"type": "battle", "message": "Bataille orbitale au-dessus de Waterloo"},
    {"type": "economy", "message": "Revenu: +1500 Or, Métal extrait: +200"}
  ],
  "economy_summary": {...},
  "battles": [...]
}
```

## Phases d'Implémentation

### Phase 1 : Infrastructure (Backend + Base Frontend)
1. Créer endpoint GET `/games/:id/map`
2. Créer page `GameView.tsx` avec routing
3. Ajouter méthodes API côté frontend
4. Créer hook `useGameState` pour état global

### Phase 2 : Carte Stellaire (US 10.1, 10.2, 10.3)
1. Implémenter `GalaxyMap.tsx` avec Canvas/SVG
2. Système de pan (drag) et zoom (molette)
3. 3 niveaux de zoom prédéfinis
4. Rendu des étoiles avec `StarSystem.tsx`
5. Marqueurs planètes : bicorne (possédée), ? (inexplorée), vide (explorée)
6. Rendu conditionnel selon zoom (détails à zoom élevé)

### Phase 3 : Panneau Planète (US 10.5, 10.6)
1. Panneau latéral `PlanetPanel.tsx` au clic sur planète
2. Affichage caractéristiques (temp, gravité, métal, pop)
3. `BudgetSlider.tsx` avec visualisation courbe logarithmique
4. Intégration API pour modification budget
5. Bouton abandon planète

### Phase 4 : Gestion Flottes (US 10.4, 10.9)
1. `FleetSidebar.tsx` - liste des flottes du joueur
2. `FleetCard.tsx` - résumé d'une flotte
3. `FleetMarker.tsx` - icône sur la carte
4. `FleetTrajectory.tsx` - lignes de trajectoire (voir système ci-dessous)
5. `RouteCalculator.ts` - calcul des routes avec escales
6. Drag & drop **planète → planète** pour déplacement
7. Actions : split, merge, disband

#### Système de déplacement par glisser-déposer (style Spaceward Ho!)

**Interaction utilisateur :**
1. Glisser depuis une planète possédée (avec flottes)
2. Pendant le glissement, afficher la ligne de trajectoire
3. Relâcher sur la planète destination

**Feedback visuel selon la portée :**

| Situation | Affichage |
|-----------|-----------|
| Portée suffisante | Ligne **continue** avec flèche → |
| Portée insuffisante mais route possible | Ligne continue avec **escales suggérées** (points intermédiaires) |
| Aucune route possible | Ligne **discontinue** (pointillés rouges) |

**Calcul de route avec escales :**
```typescript
interface RouteResult {
  reachable: boolean;
  directRoute: boolean;      // true si portée directe
  waypoints: Planet[];       // planètes intermédiaires (escales)
  totalDistance: number;
  segments: RouteSegment[];  // pour affichage
}

interface RouteSegment {
  from: Planet;
  to: Planet;
  distance: number;
  travelTurns: number;
}
```

**Algorithme de recherche de route :**
```
1. Calculer distance directe source → destination
2. Si distance <= portée_flotte → route directe OK
3. Sinon, chercher chemin via planètes intermédiaires :
   - Planètes alliées/possédées uniquement (pour ravitaillement)
   - Algorithme A* ou Dijkstra
   - Contrainte : chaque segment <= portée_flotte
4. Si aucun chemin trouvé → route impossible
```

**Composants à créer :**
- `useDragRoute.ts` - hook pour gérer le drag & drop
- `RoutePreview.tsx` - affichage de la route pendant le drag
- `WaypointMarker.tsx` - marqueur d'escale suggérée

### Phase 5 : Rapports et Historique (US 10.7, 10.8)
1. Endpoint GET `/games/:id/turn-report`
2. `TurnReport.tsx` - modal ou panneau
3. `HistoryChart.tsx` - graphique évolution (Chart.js/Recharts)
4. Métriques : population, planètes, flottes, technologie

### Phase 6 : Finitions (US 10.10)
1. `useWindowLayout.ts` - sauvegarde localStorage
2. Positions et tailles des panneaux
3. Préférences de zoom par défaut

## Composants UI Détaillés

### GalaxyMap.tsx
```typescript
interface GalaxyMapProps {
  stars: Star[];
  fleets: Fleet[];
  selectedStarId?: number;
  onStarClick: (starId: number) => void;
  onFleetClick: (fleetId: number) => void;
}

// États de zoom
const ZOOM_LEVELS = {
  galaxy: 0.5,    // Vue globale
  region: 1.0,    // Vue régionale
  system: 2.0,    // Vue système
};
```

### PlanetPanel.tsx
```typescript
interface PlanetPanelProps {
  planet: Planet;
  onBudgetChange: (terraform: number, mining: number) => void;
  onAbandon: () => void;
}
```

### FleetSidebar.tsx
```typescript
interface FleetSidebarProps {
  fleets: Fleet[];
  selectedFleetId?: number;
  onFleetSelect: (fleetId: number) => void;
  onFleetMove: (fleetId: number, destStarId: number) => void;
  onFleetSplit: (fleetId: number, shipIds: number[]) => void;
  onFleetMerge: (fleetId1: number, fleetId2: number) => void;
}
```

## Représentation Visuelle

### Icônes Planètes (selon état et propriétaire)
- **Possédée par moi** : Bicorne napoléonien (couleur joueur)
- **Possédée par autre** : Bicorne (couleur adversaire)
- **Explorée non colonisée** : Cercle vide
- **Inexplorée** : Point d'interrogation "?"
- **Abandonnée** : Cercle barré

### Icônes Flottes
- Petit vaisseau stylisé avec couleur du joueur
- Nombre de vaisseaux affiché
- Animation de pulsation si sélectionnée

### Trajectoires
- Ligne pointillée couleur du joueur
- Segments marqués pour chaque tour
- Point d'arrivée avec cercle

## Dépendances Techniques

### Frontend
- React 18+
- Canvas API ou SVG (préférer SVG pour interactivité)
- Recharts ou Chart.js pour graphiques
- CSS Grid/Flexbox pour layout

### Backend
- Endpoint map avec fog of war (optionnel futur)
- Endpoint turn-report

## Critères d'Acceptation

### US 10.1 - Carte stellaire 2D
- [x] Affiche toutes les étoiles de la galaxie
- [x] Positions correctes selon coordonnées x, y
- [x] Cliquable pour sélectionner

### US 10.2 - Niveaux de zoom
- [x] 3 niveaux accessibles (boutons ou molette)
- [x] Transition fluide entre niveaux
- [x] Pan possible à tous les niveaux

### US 10.3 - Représentation planètes
- [x] Bicorne sur planètes possédées
- [x] "?" sur planètes inexplorées
- [x] Couleur du propriétaire visible

### US 10.4 - Trajectoires flottes et déplacement
**Système de déplacement (style Spaceward Ho!) :**
- [ ] Glisser-déposer de planète source vers planète destination
- [ ] Ligne **continue** avec flèche si portée suffisante
- [ ] Ligne continue avec **escales suggérées** si portée insuffisante mais route possible
- [ ] Ligne **discontinue** (pointillés rouges) si aucune route possible
- [ ] Calcul automatique du meilleur chemin via planètes alliées

**Affichage des flottes en transit :**
- [ ] Lignes visibles pour flottes en transit
- [ ] Segments par tour marqués
- [ ] Escales intermédiaires affichées
- [ ] Destination finale claire

### US 10.5 - Panneau info planète
- [x] Affiche temp, gravité, métal, population
- [x] Sliders budget fonctionnels
- [x] Mise à jour en temps réel

### US 10.6 - Graphique budget
- [x] Visualisation courbe logarithmique
- [x] Montre rendement attendu
- [x] Interactif avec slider

### US 10.7 - Graphique historique
- [ ] Évolution dans le temps
- [ ] Plusieurs métriques
- [ ] Comparaison joueurs

### US 10.8 - Rapport de tour
- [ ] Liste événements du tour
- [ ] Catégorisé (éco, combat, construction)
- [ ] Accessible après chaque tour

### US 10.9 - Barre flottes
- [ ] Liste toutes les flottes
- [ ] Actions disponibles (move, split, merge)
- [ ] État visible (stationed, in_transit)

### US 10.10 - Sauvegarde layout
- [ ] Positions panneaux sauvegardées
- [ ] Restaurées au rechargement
- [ ] Reset possible

## Estimation

| Phase | Complexité |
|-------|------------|
| Phase 1 (Infrastructure) | Moyenne |
| Phase 2 (Carte) | Haute |
| Phase 3 (Panneau planète) | Moyenne |
| Phase 4 (Flottes) | Haute |
| Phase 5 (Rapports) | Moyenne |
| Phase 6 (Finitions) | Basse |

## Notes

- Privilégier SVG pour la carte (meilleure gestion des événements)
- Utiliser React Context pour l'état global du jeu
- Penser responsive mais desktop-first
- Le thème napoléonien sera affiné dans l'EPIC 13
