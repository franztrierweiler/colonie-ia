# Spécifications Interface Utilisateur - Colonie-IA

Ce document définit les spécifications visuelles et d'interaction de l'interface du jeu.

## Référence : Spaceward Ho! Classique

Les captures d'écran de référence sont disponibles dans `/ux-ui/spaceward-classic-screens/`. Ces écrans servent de base pour le design de l'interface de Colonie-IA.

### Captures disponibles

| Fichier | Description | Éléments clés |
|---------|-------------|---------------|
| `16529325-...-game-start.png` | Début de partie (an 2000) | Layout complet, panneau planète, carte galaxie |
| `16491454-...-later-in-the-game.png` | Partie avancée (an 2610) | Empire développé, économie avancée |
| `16529028-...-create-a-new-ship.png` | Concepteur de vaisseaux | Dialog ship designer avec sliders tech |
| `16529454-...-attacking-planet-sith.png` | Combat spatial | Interface de bataille |
| `16529283-...-the-first-scouts-battle.png` | Premier combat | Résumé de bataille |
| `16528953-...-create-a-new-galaxy.png` | Création galaxie | Options de configuration |
| `16490638-...-main-menu.png` | Menu principal | Écran d'accueil |

---

## Layout Principal du Jeu

Basé sur les captures Spaceward Ho!, le layout principal comprend :

```
┌─────────────────────────────────────────────────────────────┐
│ [Menu Bar] File | Options | Ships | Galaxy | Window | Help  │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌────────────────────────────┐  [End Turn] │
│ │   PANNEAU   │  │                            │             │
│ │   PLANÈTE   │  │      CARTE DE LA GALAXIE   │             │
│ │             │  │                            │             │
│ ├─────────────┤  │    (planètes, flottes,     │             │
│ │   INFOS     │  │     trajectoires)          │             │
│ │   FLOTTE    │  │                            │             │
│ ├─────────────┤  └────────────────────────────┘             │
│ │  RESSOURCES │                                             │
│ │  GLOBALES   │                                             │
│ └─────────────┘                                             │
├─────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────┐ ┌───────────────────────────┐ │
│ │      TECH SPENDING        │ │        REPORTS            │ │
│ │  (barres par technologie) │ │  (événements du jeu)      │ │
│ └───────────────────────────┘ └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Panneau d'Information Planète

### Structure (référence: game-start.png)

Le panneau planète affiche les informations suivantes :

```
┌─────────────────────────────┐
│ [Nom de la planète]         │
├─────────────────────────────┤
│ Income:  $XX,XXX            │
│ Pop:     XXX,XXX            │
│ Temp:    XX.X°C             │
│ Gravity: X.XXG              │
│ Metal:   XX,XXX             │
├─────────────────────────────┤
│ Budget: [Terra][Mine][Ship] │
│         ████░░░░████░░████  │
├─────────────────────────────┤
│ Ships Queued: [liste]       │
└─────────────────────────────┘
```

### Champs affichés

| Champ | Description | Format |
|-------|-------------|--------|
| **Income** | Revenu de la planète par tour | $XX,XXX |
| **Pop** | Population actuelle | XXX,XXX |
| **Temp** | Température actuelle | XX.X°C |
| **Gravity** | Gravité | X.XXG |
| **Metal** | Métal restant sur la planète | XX,XXX |

### Allocation budgétaire

Graphique à barres horizontales montrant la répartition entre :
- **Terra** (bleu) : Budget terraformation
- **Mine** (orange) : Budget extraction minière
- **Ship** (vert) : Budget construction de vaisseaux

Les 3 budgets totalisent toujours 100%.

---

## Informations Flotte

### Structure (référence: game-start.png)

```
┌─────────────────────────────┐
│ Stationed at: [Planète]     │
│ Fuel: X/X  Speed: X         │
│ Scrap: XXX                  │
├─────────────────────────────┤
│ ▸ one Needle (1/1) Scout    │
│ ▸ one Spreader (2/2) Colony │
└─────────────────────────────┘
```

### Champs affichés

| Champ | Description |
|-------|-------------|
| **Stationed at** | Planète où la flotte est stationnée |
| **Fuel** | Carburant actuel / maximum |
| **Speed** | Vitesse de la flotte |
| **Scrap** | Valeur en métal si recyclée |
| **Liste vaisseaux** | Quantité et type de chaque vaisseau |

---

## Ressources Globales

### Structure (référence: later-in-the-game.png)

```
┌─────────────────────────────┐
│ Reserve Metal: 47,959 (↑1,484) │
│ Total Money: $827,898 (↑$52K)  │
│ Total Income: $131,553 (↑$3K)  │
└─────────────────────────────┘
```

Les variations par rapport au tour précédent sont affichées entre parenthèses.

---

## Tech Spending (Dépenses Technologiques)

### Structure (référence: game-start.png)

```
┌─────────────────────────────────────┐
│ Current Levels:                     │
│ Range    6   ████████░░░░░░         │
│ Speed    2   ████░░░░░░░░░░         │
│ Weapons  2   ████░░░░░░░░░░         │
│ Shields  2   ████░░░░░░░░░░         │
│ Mini     0   ░░░░░░░░░░░░░░         │
└─────────────────────────────────────┘
```

### Niveaux technologiques

| Technologie | Description | Impact |
|-------------|-------------|--------|
| **Range** | Portée | Distance max de déplacement |
| **Speed** | Vitesse | Tours pour atteindre destination |
| **Weapons** | Armes | Puissance d'attaque |
| **Shields** | Boucliers | Résistance aux dégâts |
| **Mini** | Miniaturisation | Réduction des coûts |

Les barres représentent le budget alloué à chaque recherche (0-100%).

---

## Panneau Reports

### Structure (référence: later-in-the-game.png)

```
┌─────────────────────────────────────┐
│ Reports                             │
├─────────────────────────────────────┤
│ 📅 The game has been updated to     │
│    year 2610.                       │
│ ♻️ Styx has run out of metal.       │
│ 🏠 Murzim has just become a         │
│    profitable colony.               │
└─────────────────────────────────────┘
```

### Types d'événements

| Icône | Type | Description |
|-------|------|-------------|
| 📅 | Tour | Changement de tour/année |
| ♻️ | Ressource | Métal épuisé, récupération |
| 🏠 | Colonie | Événement de colonisation |
| ⚔️ | Combat | Résultat de bataille |

---

## Concepteur de Vaisseaux

### Structure (référence: create-a-new-ship.png)

```
┌─────────────────────────────────────────────────┐
│         Name of New Ship Type:                  │
│         [___Games___________]                   │
├─────────────────────────────────────────────────┤
│                              ┌────────────────┐ │
│ Range:   6/6  [-][+]         │   [Prévisua-   │ │
│ Speed:   2/2  [-][+]         │    lisation    │ │
│ Weapons: 3/3  [-][+]         │    du          │ │
│ Shields: 3/3  [-][+]         │    vaisseau]   │ │
│ Mini:    0/0  [-][+]         │                │ │
│                              └────────────────┘ │
│ Class: [Fighter     ▼]                         │
├─────────────────────────────────────────────────┤
│ Dev. Cost:  $4,551                              │
│ Prod. Cost: $2,275                              │
│ Metal Cost: 758                                 │
├─────────────────────────────────────────────────┤
│ [Name It For Me]    [Cancel]    [OK]           │
└─────────────────────────────────────────────────┘
```

### Champs

| Champ | Description |
|-------|-------------|
| **Name** | Nom personnalisé du design |
| **Range/Speed/etc** | Niveau tech X/Max avec boutons +/- |
| **Class** | Type de vaisseau (Fighter, Scout, Colony, etc.) |
| **Dev. Cost** | Coût de développement du prototype |
| **Prod. Cost** | Coût de production en série |
| **Metal Cost** | Coût en métal |
| **Prévisualisation** | Image du vaisseau selon la classe |

---

## Carte de la Galaxie

### Planètes - Aspects Visuels

Les planètes sont représentées par des disques sur la carte. Leur apparence varie selon leur état et leurs caractéristiques.

Le nom d'une planète est toujours écrit sous la planète.

#### États des planètes

| État | Aspect visuel | Description |
|------|---------------|-------------|
| **Inexplorée** | Disque gris foncé avec un point d'interrogation noir | Planète dont on ne connaît pas les caractéristiques |
| **Explorée** | Planète avec un bicorne bleu-blanc-rouge | Planète visitée mais non colonisée |
| **Colonisée (moi)** | Planète avec un bicorne bleu-blanc-rouge | Ma colonie |
| **Colonisée (ennemi)** | Disque avec un bicorne de la couleur de l'opposant | Colonie ennemie |
| **Planète mère (moi)** | Disque bleu avec halo bleu ciel intense et bicorne bleu-blanc-rouge | Ma capitale |
| **Planète mère (ennemi)** | Disque bleu avec bicorne de la couleur de l'opposant | Capitale ennemie |

#### Types de planètes (selon caractéristiques)

| Type | Condition | Aspect visuel |
|------|-----------|---------------|
| **Astéroïde/Minerai** | Riche en métal, inhabitable | Grise avec cratères prononcés type lune |
| **Terraformable** | En cours de terraformation | De gris clair à bleu selon % |
| **Habitable** | Bien terraformée (>85%) | Bleu intense, terres et océans |
| **Hostile** | Température/gravité extrême | Gris foncé + points rouges (lave) ou halo orange (gazeuse) |

#### Indicateurs visuels

| Indicateur | Représentation |
|------------|----------------|
| **Possession** | Bicorne sur la planète |
| **Bicorne joueur** | Bleu-blanc-rouge |
| **Bicorne ennemi** | Couleur unie de l'adversaire |
| **Halo planète mère** | Animation légère pulsante |
| **Niveau terraformation** | Dégradé gris → bleu |
| **Défenses en orbite** | Cercle rouge discontinu |

---

## Flottes sur la Carte

### Représentation visuelle

| État | Aspect |
|------|--------|
| **Stationnée** | Icône vaisseau près de la planète |
| **En transit** | Ligne pointillée + position actuelle |
| **Combat** | Animation spéciale |

### Trajectoires (référence: later-in-the-game.png)

- Ligne pointillée de la planète de départ vers la destination
- Marqueurs de tour le long de la trajectoire
- Indicateur de position actuelle de la flotte
- Tour d'arrivée affiché près de la destination

---

## Résumé de Bataille

### Structure (référence: attacking-planet-sith.png)

```
┌─────────────────────────────────────────────────┐
│     Summary of battle at [Planète] in [Année]: │
├─────────────────────────────────────────────────┤
│   [Joueur 1]              [Joueur 2]           │
│   ┌────────┐              ┌────────┐           │
│   │Planète │              │Planète │           │
│   │Pop: X  │              │Pop: X  │           │
│   └────────┘              └────────┘           │
│                                                 │
│   🚀 5 Storm (2/2) Fighters  ←→  🚀 2 Explorer │
│   🚀 3 Storm (2/2) Fighters      (1/1) Scouts  │
│                                                 │
│   [Animations de tirs laser]                    │
│                                                 │
│              Round X                            │
├─────────────────────────────────────────────────┤
│                  [Skip]                         │
└─────────────────────────────────────────────────┘
```

---

## Création de Galaxie

### Options (référence: create-a-new-galaxy.png)

| Option | Choix disponibles |
|--------|-------------------|
| **Galaxy Density** | Dense, Sparse |
| **Galaxy Style** | Circle, Random, Ring, Spiral, Grid |
| **Galaxy Size** | Small, Medium, Large, Extra Large, Humongous |
| **Computer Intelligence** | Dumb, Average, Smart |
| **Number of Players** | 1-8 (slider) |

Chaque option est représentée par une icône visuelle distinctive.

---

## Palette de Couleurs

### Couleurs principales

| Élément | Couleur | Code |
|---------|---------|------|
| **Fond espace** | Bleu très foncé | #0a0a1a |
| **Planète habitable** | Bleu | #4a9eff |
| **Planète hostile** | Gris-rouge | #666 + lave |
| **Budget Terra** | Bleu | #4a9eff |
| **Budget Mine** | Orange | #ffa500 |
| **Budget Ship** | Vert | #50c878 |
| **Joueur principal** | Bleu-blanc-rouge | Tricolore |
| **Texte principal** | Blanc cassé | #e8e8f0 |
| **Texte secondaire** | Gris | #888 |

### Couleurs des joueurs

Chaque joueur a une couleur distinctive pour ses planètes et flottes (hors joueur principal qui utilise le tricolore).

---

## Typographie

| Usage | Police |
|-------|--------|
| **Titres** | Press Start 2P (pixel art) |
| **Corps de texte** | Arial |
| **Valeurs numériques** | Arial |
| **Interface** | Arial |

---

## Interactions

### Carte galaxie

| Action | Résultat |
|--------|----------|
| **Clic planète** | Affiche panneau planète |
| **Clic flotte** | Affiche panneau flotte |
| **Drag flotte** | Déplace vers destination |
| **Molette** | Zoom in/out |
| **Drag fond** | Pan de la carte |
| **Touches G/R/S** | Niveaux de zoom prédéfinis |

### Panneau planète

| Action | Résultat |
|--------|----------|
| **Slider budget** | Ajuste allocation (total=100%) |
| **Clic "Appliquer"** | Sauvegarde les budgets |
| **Clic "+ Ajouter à la file"** | Ajoute production |
