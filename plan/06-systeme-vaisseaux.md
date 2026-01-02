# Plan de Développement - EPIC 6 : Système de Vaisseaux

## Statut Global

| Phase | Description | Statut |
|-------|-------------|--------|
| 1 | Modèles de données (Backend) | ✅ Terminé |
| 2 | Service FleetService (Backend) | ✅ Terminé |
| 3 | Déplacement et trajectoires (Backend) | ✅ Terminé |
| 4 | Ravitaillement (Backend) | ✅ Terminé |
| 5 | Démantèlement (Backend) | ✅ Terminé |
| 6 | API Endpoints (Backend) | ✅ Terminé |
| 7 | Tests Backend | ✅ Terminé (17 tests) |
| 8 | Services API Frontend | ✅ Terminé |
| 9 | Panneau de gestion des flottes | ✅ Terminé |
| 10 | Concepteur de vaisseaux | ✅ Terminé |
| 11 | Déplacement par glisser-déposer | ✅ Terminé |
| 12 | Affichage trajectoires | ✅ Terminé |

**Commit Backend** : `b9dd4bb` - EPIC 6 : Système de Vaisseaux - Modèles, Service et API

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

## BACKEND (TERMINÉ)

### Phase 1 : Modèles de données ✅

**Fichier** : `backend/app/models/fleet.py`

#### 1.1 Énumérations

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

#### 1.2 Modèles

- **ShipDesign** : Design personnalisé avec 5 niveaux tech
- **Ship** : Instance de vaisseau avec dégâts
- **Fleet** : Groupe de vaisseaux avec statut et destination

#### 1.3 Caractéristiques par type

| Type | Range Bonus | Speed | Weapons | Shields | Metal Base | Money Base |
|------|-------------|-------|---------|---------|------------|------------|
| Fighter | 0 | 1.0 | 1.0 | 1.0 | 50 | 100 |
| Scout | +3 | 1.2 | 0.3 | 0.3 | 30 | 80 |
| Colony | -1 | 0.5 | 0.1 | 0.5 | 200 | 500 |
| Satellite | 0 (fixe) | 0 | 0.8 | 1.5 | 20 | 30 |
| Tanker | 0 | 0.8 | 0.1 | 0.5 | 100 | 200 |
| Battleship | 0 | 0.7 | 2.0 | 2.0 | 300 | 600 |
| Decoy | 0 | 1.5 | 0 | 0.1 | 5 | 10 |
| Biological | 0 | 1.0 | 1.5 | 0.5 | 0 | 300 |

### Phase 2 : Service FleetService ✅

**Fichier** : `backend/app/services/fleet_service.py`

- `calculate_design_costs()` - Calcul des coûts prototype/production
- `create_design()` - Créer un design de vaisseau
- `build_ships()` - Construire des vaisseaux
- `create_fleet()` - Créer une flotte vide
- `split_fleet()` - Diviser une flotte
- `merge_fleets()` - Fusionner deux flottes

### Phase 3 : Déplacement et trajectoires ✅

- `calculate_travel_time()` - Calcul durée de voyage
- `get_fleet_speed()` - Vitesse = min des vaisseaux
- `get_fleet_range()` - Portée = min des vaisseaux (bonus tanker)
- `move_fleet()` - Déplacer vers une destination
- `process_fleet_movements()` - Traitement fin de tour

### Phase 4 : Ravitaillement ✅

- `can_refuel_at()` - Vérification planète alliée
- `refuel_fleet()` - Ravitaillement manuel
- `process_refueling()` - Ravitaillement automatique fin de tour

### Phase 5 : Démantèlement ✅

- `disband_ship()` - Démanteler un vaisseau (75% métal)
- `disband_fleet()` - Démanteler toute une flotte

### Phase 6 : API Endpoints ✅

**Fichier** : `backend/app/routes/fleet.py`

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/games/:id/designs` | Liste des designs du joueur |
| POST | `/api/games/:id/designs` | Créer un design |
| GET | `/api/games/:id/designs/:id/costs` | Coûts d'un design |
| POST | `/api/games/:id/designs/:id/build` | Construire vaisseau(x) |
| GET | `/api/games/:id/fleets` | Liste des flottes |
| POST | `/api/games/:id/fleets` | Créer une flotte |
| GET | `/api/fleets/:id` | Détails d'une flotte |
| POST | `/api/fleets/:id/move` | Déplacer une flotte |
| POST | `/api/fleets/:id/split` | Diviser une flotte |
| POST | `/api/fleets/:id/merge` | Fusionner des flottes |
| POST | `/api/fleets/:id/disband` | Démanteler une flotte |
| POST | `/api/ships/:id/disband` | Démanteler un vaisseau |

### Phase 7 : Tests Backend ✅

**Fichier** : `backend/tests/test_fleet.py` (17 tests)

---

## FRONTEND (TERMINÉ)

### Phase 8 : Services API Frontend ✅

**Fichier** : `frontend/src/services/api.ts`

Ajouter les méthodes suivantes :

```typescript
// Ship Designs
async getDesigns(gameId: number)
async createDesign(gameId: number, data: CreateDesignData)
async buildShips(gameId: number, designId: number, fleetId: number, count: number)

// Fleets
async getFleets(gameId: number)
async getFleet(fleetId: number)
async createFleet(gameId: number, name: string, planetId?: number)
async moveFleet(fleetId: number, destinationPlanetId: number)
async splitFleet(fleetId: number, shipIds: number[], newFleetName: string)
async mergeFleets(fleetId: number, fleetIdToMerge: number)
async disbandFleet(fleetId: number)
async disbandShip(shipId: number)
```

### Phase 9 : Panneau de gestion des flottes ✅

**Composants créés** :

#### 9.1 FleetPanel.tsx
Panneau latéral affichant :
- Liste des flottes du joueur
- Flotte sélectionnée : détails, vaisseaux, actions
- Boutons : déplacer, diviser, fusionner, démanteler

#### 9.2 FleetList.tsx
Liste compacte des flottes avec :
- Nom et nombre de vaisseaux
- Statut (en orbite, en transit)
- Icône de destination si en transit

#### 9.3 FleetDetails.tsx
Détails d'une flotte :
- Statistiques (vitesse, portée, puissance)
- Liste des vaisseaux par type
- Carburant restant
- Configuration de combat

### Phase 10 : Concepteur de vaisseaux ✅

**Composants créés** (intégrés dans FleetPanel.tsx) :

#### 10.1 ShipDesigner.tsx
Interface de création de design :
- Sélection du type de vaisseau
- 5 sliders pour les niveaux technologiques
- Prévisualisation des coûts (prototype/production)
- Bouton "Créer le design"

#### 10.2 ShipDesignList.tsx
Liste des designs existants :
- Nom, type, niveaux tech
- Coûts de production
- Bouton "Construire"

#### 10.3 BuildShipModal.tsx
Modal de construction :
- Sélection de la flotte cible
- Quantité à construire
- Coût total affiché
- Validation

### Phase 11 : Déplacement par glisser-déposer ✅

**Modifications apportées** :

#### 11.1 GalaxyMap.tsx
- État de drag : flotte source
- Gestionnaires onDragStart, onDragOver, onDrop
- Feedback visuel pendant le drag

#### 11.2 FleetMarker.tsx
- Attribut draggable
- Style pendant le drag
- Annulation si hors carte

#### 11.3 PlanetMarker.tsx
- Zone de drop
- Highlight si destination valide
- Calcul de la portée affichée

### Phase 12 : Affichage des trajectoires ✅

**Modifications apportées** :

#### 12.1 FleetTrajectory.tsx (existant, à améliorer)
- Ligne pointillée entre position actuelle et destination
- Segments par tour (avec graduation)
- Icône de flotte animée sur le trajet
- Indicateur du tour d'arrivée

#### 12.2 GalaxyMap.tsx
- Rendu des trajectoires pour toutes les flottes en transit
- Z-order correct (trajectoires sous les marqueurs)

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

### Backend ✅
- [x] 8 types de vaisseaux disponibles
- [x] Les designs sont personnalisables (5 valeurs tech)
- [x] Prototype coûte 2x, production normale ensuite
- [x] Les flottes se déplacent avec trajectoire fixe
- [x] Ravitaillement automatique sur planètes alliées
- [x] Démantèlement récupère 75% du métal
- [x] La vitesse de flotte = min des vaisseaux
- [x] La portée de flotte = min des vaisseaux

### Frontend ✅
- [x] Le joueur peut créer des designs de vaisseaux
- [x] Le joueur peut construire des vaisseaux
- [x] Le joueur peut voir ses flottes dans un panneau
- [x] Le joueur peut déplacer une flotte par drag & drop
- [x] Les trajectoires des flottes en transit sont visibles
- [x] Le joueur peut diviser/fusionner des flottes
- [x] Le joueur peut démanteler des vaisseaux

---

*Document mis à jour pour EPIC 6 - Système de Vaisseaux*
*Projet Colonie-IA*
