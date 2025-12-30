# Plan de Développement - EPIC 2 : Configuration de Partie

## Statut Global

| Phase | Description | Statut |
|-------|-------------|--------|
| 1 | Modèles de données | ⏳ À faire |
| 2 | Génération de galaxie | ⏳ À faire |
| 3 | API Configuration | ⏳ À faire |
| 4 | Gestion des joueurs | ⏳ À faire |
| 5 | Frontend Lobby | ⏳ À faire |
| 6 | Initialisation de partie | ⏳ À faire |

---

## Vue d'ensemble

L'EPIC 2 permet aux joueurs de configurer et lancer une partie : paramètres de galaxie, choix des adversaires et initialisation du jeu.

**Dépendances** : EPIC 1 (authentification, API de base)

**User Stories couvertes** :
- US 2.1 - Configuration de la galaxie
- US 2.2 - Choix des adversaires
- US 2.3 - Niveau de difficulté IA
- US 2.4 - Durée des tours
- US 2.5 - Initialisation du joueur

---

## Phase 1 : Modèles de données

### 1.1 Modèle Galaxy

```python
class Galaxy(db.Model):
    id: int (PK)
    game_id: int (FK -> Game)
    shape: Enum('circle', 'spiral', 'cluster', 'random')
    star_count: int
    density: Enum('low', 'medium', 'high')
    width: float  # dimensions en unités de jeu
    height: float
    created_at: datetime
```

### 1.2 Modèle Star (Étoile/Système)

```python
class Star(db.Model):
    id: int (PK)
    galaxy_id: int (FK -> Galaxy)
    name: str  # nom napoléonien
    x: float  # position
    y: float
    is_nova: bool = False
    nova_turn: int | None  # tour où la nova se produira
```

### 1.3 Modèle Planet

```python
class Planet(db.Model):
    id: int (PK)
    star_id: int (FK -> Star)
    name: str
    temperature: float  # -273 à +500, idéal 22°C
    gravity: float  # 0.1 à 3.0, idéal 1.0g
    metal_reserves: int  # réserves initiales
    metal_remaining: int  # réserves actuelles
    state: Enum('unexplored', 'explored', 'colonized', 'developed', 'hostile', 'abandoned')
    owner_id: int | None (FK -> Player)
    population: int = 0
    max_population: int  # calculé selon temp/gravité
```

### 1.4 Modèle Game (extension)

```python
class Game(db.Model):
    # ... champs existants ...
    turn_duration_years: int = 10
    current_turn: int = 1
    current_year: int = 2200
    status: Enum('lobby', 'in_progress', 'finished')
    max_players: int
    luck_enabled: bool = True
    alliances_enabled: bool = True
    creator_id: int (FK -> User)
```

### 1.5 Modèle Player (joueur dans une partie)

```python
class Player(db.Model):
    id: int (PK)
    game_id: int (FK -> Game)
    user_id: int | None (FK -> User)  # None = IA
    is_ai: bool = False
    ai_difficulty: Enum('easy', 'medium', 'hard', 'expert') | None
    color: str  # couleur hex
    name: str  # pseudo ou nom IA
    money: int = 10000
    debt: int = 0
    is_eliminated: bool = False
    turn_submitted: bool = False
    home_planet_id: int | None (FK -> Planet)
```

### 1.6 Tâches Phase 1

- [ ] T1.1 - Créer le modèle Galaxy
- [ ] T1.2 - Créer le modèle Star avec noms napoléoniens
- [ ] T1.3 - Créer le modèle Planet avec états
- [ ] T1.4 - Étendre le modèle Game pour configuration
- [ ] T1.5 - Créer le modèle Player (humain/IA)
- [ ] T1.6 - Créer les migrations
- [ ] T1.7 - Fichier de données : noms de planètes napoléoniens

---

## Phase 2 : Génération de galaxie

### 2.1 Algorithmes de forme

| Forme | Algorithme |
|-------|------------|
| **Cercle** | Distribution uniforme dans un disque |
| **Spirale** | 2-4 bras spiraux avec perturbation |
| **Amas** | Clusters gaussiens multiples |
| **Aléatoire** | Poisson disk sampling pour espacement minimal |

### 2.2 Paramètres de génération

```python
GALAXY_PRESETS = {
    'small': {'stars': 20, 'width': 100, 'height': 100},
    'medium': {'stars': 50, 'width': 200, 'height': 200},
    'large': {'stars': 100, 'width': 300, 'height': 300},
    'huge': {'stars': 200, 'width': 500, 'height': 500},
}

DENSITY_FACTORS = {
    'low': 1.5,    # étoiles plus espacées
    'medium': 1.0,
    'high': 0.7,   # étoiles plus proches
}
```

### 2.3 Génération des planètes

- Chaque étoile a 1-4 planètes
- Distribution des caractéristiques :
  - Température : distribution normale centrée sur 0°C, σ=100
  - Gravité : distribution normale centrée sur 1.0g, σ=0.5
  - Métal : distribution exponentielle (beaucoup de pauvres, peu de riches)

### 2.4 Tâches Phase 2

- [ ] T2.1 - Service GalaxyGenerator avec interface commune
- [ ] T2.2 - Algorithme forme cercle
- [ ] T2.3 - Algorithme forme spirale
- [ ] T2.4 - Algorithme forme amas
- [ ] T2.5 - Algorithme forme aléatoire (Poisson disk)
- [ ] T2.6 - Générateur de planètes par étoile
- [ ] T2.7 - Calcul max_population selon temp/gravité
- [ ] T2.8 - Tests unitaires génération

---

## Phase 3 : API Configuration de partie

### 3.1 Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/games` | Créer une nouvelle partie |
| GET | `/api/games` | Lister les parties (lobby) |
| GET | `/api/games/:id` | Détails d'une partie |
| PATCH | `/api/games/:id` | Modifier config (créateur only) |
| DELETE | `/api/games/:id` | Supprimer partie (créateur only) |
| POST | `/api/games/:id/join` | Rejoindre une partie |
| POST | `/api/games/:id/leave` | Quitter une partie |
| POST | `/api/games/:id/start` | Lancer la partie |
| POST | `/api/games/:id/ai` | Ajouter un joueur IA |

### 3.2 Schémas de validation

```python
class CreateGameSchema(BaseModel):
    name: str
    galaxy_shape: Literal['circle', 'spiral', 'cluster', 'random']
    galaxy_size: Literal['small', 'medium', 'large', 'huge']
    density: Literal['low', 'medium', 'high']
    max_players: int = Field(ge=2, le=8)
    turn_duration_years: int = Field(ge=10, le=100)
    luck_enabled: bool = True
    alliances_enabled: bool = True

class AddAISchema(BaseModel):
    difficulty: Literal['easy', 'medium', 'hard', 'expert']
    name: str | None = None  # auto-généré si absent
```

### 3.3 Tâches Phase 3

- [ ] T3.1 - Schémas Pydantic pour configuration
- [ ] T3.2 - Endpoint POST /api/games (création)
- [ ] T3.3 - Endpoint GET /api/games (liste lobby)
- [ ] T3.4 - Endpoint GET /api/games/:id (détails)
- [ ] T3.5 - Endpoint PATCH /api/games/:id (modification)
- [ ] T3.6 - Endpoint DELETE /api/games/:id (suppression)
- [ ] T3.7 - Endpoint POST /api/games/:id/join
- [ ] T3.8 - Endpoint POST /api/games/:id/leave
- [ ] T3.9 - Endpoint POST /api/games/:id/ai
- [ ] T3.10 - Endpoint POST /api/games/:id/start
- [ ] T3.11 - Documentation Swagger pour tous les endpoints

---

## Phase 4 : Gestion des joueurs

### 4.1 Niveaux de difficulté IA

| Niveau | Caractéristiques |
|--------|------------------|
| **Facile** | Décisions aléatoires, pas d'optimisation |
| **Moyen** | Stratégie basique, expansion simple |
| **Difficile** | Optimisation économique, attaques ciblées |
| **Expert** | Stratégie avancée, coordination multi-planètes |

### 4.2 Noms IA thématiques

```python
AI_NAMES = [
    "Maréchal Ney",
    "Général Murat",
    "Duc de Wellington",
    "Amiral Nelson",
    "Maréchal Davout",
    "Prince Koutouzov",
    "Général Blücher",
    "Maréchal Lannes",
]
```

### 4.3 Couleurs des joueurs

```python
PLAYER_COLORS = [
    '#1E88E5',  # Bleu
    '#E53935',  # Rouge
    '#43A047',  # Vert
    '#FDD835',  # Jaune
    '#8E24AA',  # Violet
    '#FB8C00',  # Orange
    '#00ACC1',  # Cyan
    '#6D4C41',  # Marron
]
```

### 4.4 Tâches Phase 4

- [ ] T4.1 - Service PlayerManager (création, couleurs)
- [ ] T4.2 - Attribution automatique des couleurs
- [ ] T4.3 - Génération noms IA thématiques
- [ ] T4.4 - Validation nombre de joueurs (2-8)
- [ ] T4.5 - Gestion des slots (humain/IA/vide)

---

## Phase 5 : Frontend Lobby

### 5.1 Pages à créer

| Page | Route | Description |
|------|-------|-------------|
| GameList | `/games` | Liste des parties disponibles |
| CreateGame | `/games/new` | Formulaire création |
| GameLobby | `/games/:id/lobby` | Salle d'attente avant démarrage |

### 5.2 Composants

```
frontend/src/
├── pages/
│   ├── GameList.tsx        # Liste des parties
│   ├── CreateGame.tsx      # Création de partie
│   └── GameLobby.tsx       # Lobby d'attente
├── components/
│   ├── GalaxyPreview.tsx   # Aperçu de la galaxie (canvas)
│   ├── PlayerSlot.tsx      # Slot joueur dans le lobby
│   ├── GameCard.tsx        # Carte partie dans la liste
│   └── DifficultySelect.tsx # Sélecteur difficulté IA
```

### 5.3 Interface CreateGame

```
┌─────────────────────────────────────────────────┐
│  Nouvelle Partie                                │
├─────────────────────────────────────────────────┤
│  Nom: [________________________]                │
│                                                 │
│  Galaxie                                        │
│  ├─ Taille:  ○ Petite ● Moyenne ○ Grande       │
│  ├─ Forme:   [Spirale ▼]                       │
│  └─ Densité: ○ Faible ● Normale ○ Élevée       │
│                                                 │
│  ┌──────────────┐                              │
│  │  [Aperçu]    │  Joueurs: [2-8 ▼]            │
│  │   galaxie    │  Durée tour: [10 ans ▼]      │
│  │   (canvas)   │  ☑ Chance au combat          │
│  └──────────────┘  ☑ Alliances                 │
│                                                 │
│  [Créer la partie]                             │
└─────────────────────────────────────────────────┘
```

### 5.4 Interface GameLobby

```
┌─────────────────────────────────────────────────┐
│  Lobby: "Campagne d'Austerlitz"                │
├─────────────────────────────────────────────────┤
│  Joueurs (3/8)                                  │
│  ┌─────────────────────────────────────────┐   │
│  │ 🔵 Général Franz (Hôte)          [Prêt]│   │
│  │ 🔴 Maréchal Ney (IA Difficile)   [IA]  │   │
│  │ 🟢 En attente...            [+ Joueur] │   │
│  │ ⚪ Vide                      [+ IA]    │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Configuration                                  │
│  • Galaxie: Spirale, 50 étoiles, densité moyenne│
│  • Tours de 10 ans                             │
│  • Chance: Oui | Alliances: Oui                │
│                                                 │
│  [Quitter]                    [Lancer la partie]│
└─────────────────────────────────────────────────┘
```

### 5.5 Tâches Phase 5

- [ ] T5.1 - Page GameList avec liste des parties
- [ ] T5.2 - Composant GameCard pour afficher une partie
- [ ] T5.3 - Page CreateGame avec formulaire complet
- [ ] T5.4 - Composant GalaxyPreview (canvas 2D)
- [ ] T5.5 - Page GameLobby avec slots joueurs
- [ ] T5.6 - Composant PlayerSlot (humain/IA/vide)
- [ ] T5.7 - Composant DifficultySelect
- [ ] T5.8 - WebSocket pour updates temps réel du lobby
- [ ] T5.9 - Navigation et routing
- [ ] T5.10 - CSS responsive pour toutes les pages

---

## Phase 6 : Initialisation de partie

### 6.1 Algorithme d'attribution des planètes mères

1. Générer la galaxie complète
2. Identifier les planètes "habitables" (temp proche 22°C, gravité ~1g)
3. Sélectionner N planètes (N = nombre de joueurs) maximisant la distance entre elles
4. Terraformer complètement ces planètes (22°C exactement)
5. Attribuer à chaque joueur

### 6.2 Ressources initiales

```python
INITIAL_RESOURCES = {
    'money': 10000,
    'metal': 500,
    'population': 100000,  # sur planète mère
    'tech_levels': {
        'range': 1,
        'speed': 1,
        'weapons': 1,
        'shields': 1,
        'miniaturization': 1,
        'radical': 0,
    }
}
```

### 6.3 Vaisseaux de départ

```python
INITIAL_SHIPS = [
    {'type': 'scout', 'count': 2},      # 2 éclaireurs
    {'type': 'fighter', 'count': 3},    # 3 chasseurs
    {'type': 'colony', 'count': 1},     # 1 vaisseau colonial
]
```

### 6.4 Tâches Phase 6

- [ ] T6.1 - Service GameInitializer
- [ ] T6.2 - Algorithme sélection planètes mères (distance max)
- [ ] T6.3 - Terraformation initiale planètes mères
- [ ] T6.4 - Attribution ressources initiales
- [ ] T6.5 - Création technologies de base
- [ ] T6.6 - Création flotte de départ
- [ ] T6.7 - Transition status lobby → in_progress
- [ ] T6.8 - Notification WebSocket démarrage partie
- [ ] T6.9 - Redirection vers page de jeu

---

## WebSocket Events (EPIC 2)

| Événement | Direction | Payload |
|-----------|-----------|---------|
| `lobby_update` | Server → Client | Liste joueurs mise à jour |
| `player_joined` | Server → Client | Nouveau joueur |
| `player_left` | Server → Client | Joueur parti |
| `game_starting` | Server → Client | Compte à rebours |
| `game_started` | Server → Client | Redirection vers jeu |

---

## Critères d'acceptation EPIC 2

- [ ] Un joueur peut créer une partie avec tous les paramètres de galaxie
- [ ] Un joueur peut voir la liste des parties en attente
- [ ] Un joueur peut rejoindre/quitter une partie
- [ ] L'hôte peut ajouter des joueurs IA avec différents niveaux
- [ ] L'aperçu de galaxie montre la forme choisie
- [ ] La partie démarre avec planètes mères équidistantes
- [ ] Chaque joueur commence avec les ressources correctes
- [ ] Le lobby se met à jour en temps réel (WebSocket)
- [ ] L'interface est responsive (mobile friendly)

---

## Risques et mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Génération galaxie lente | Moyen | Pré-calculer en background, progress bar |
| Planètes mères mal réparties | Élevé | Algorithme de maximisation des distances |
| Désynchronisation lobby | Moyen | WebSocket + polling fallback |
| Complexité UI configuration | Faible | Presets par défaut, options avancées cachées |

---

## Estimation

| Phase | Complexité |
|-------|------------|
| Phase 1 - Modèles | Moyenne |
| Phase 2 - Génération | Élevée |
| Phase 3 - API | Moyenne |
| Phase 4 - Joueurs | Faible |
| Phase 5 - Frontend | Élevée |
| Phase 6 - Initialisation | Moyenne |

---

*Document généré pour EPIC 2 - Configuration de Partie*
*Projet Colonie-IA*
