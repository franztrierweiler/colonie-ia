# Spécification Fonctionnelle - Colonie

## 1. Présentation Générale

### 1.1 Vue d'ensemble
**Colonie** est un jeu de stratégie 4X (eXplore, eXpand, eXploit, eXterminate) au tour par tour sur le thème de la conquête galactique. Le jeu se distingue par sa simplicité élégante et son accessibilité, tout en conservant une profondeur stratégique significative.

### 1.2 Objectif du jeu
Le joueur contrôle l'ensemble de l'économie et de l'armée d'une civilisation spatiale. L'objectif est de conquérir la galaxie en éliminant toutes les colonies adverses.

### 1.3 Caractéristiques clés
- Jeu au tour par tour
- Durée de partie : 10 minutes à 1 heure selon les paramètres
- Multijoueur (jusqu'à 8 joueurs) ou solo contre IA
- Interface épurée avec thème visuel humoristique (style Empire Napoléonien)

---

## 2. Configuration de Partie

### 2.1 Paramètres de galaxie

| Paramètre | Description | Options |
|-----------|-------------|---------|
| Nombre d'étoiles | Taille de la galaxie | Variable (affecte la durée) |
| Forme de la galaxie | Disposition spatiale | Cercle, Spirale, Amas, Aléatoire |
| Densité stellaire | Espacement des étoiles | Faible à élevée |
| Nombre d'adversaires | Joueurs IA ou humains | 1 à 7 |
| Niveau de difficulté IA | Intelligence des adversaires | Multiple niveaux |
| Durée des tours | Années par tour | Minimum 10 ans |

### 2.2 Configuration initiale du joueur
- **Planète mère** : Une planète entièrement terraformée (22°C, ~1g)
- **Ressources initiales** : Stock de métal et revenus de départ
- **Technologies** : Niveaux technologiques de base dans toutes les catégories

---

## 3. Système de Ressources

### 3.1 Les deux ressources fondamentales

#### 3.1.1 Argent (Money)
- **Nature** : Ressource renouvelable
- **Source** : Taxation basée sur la population des colonies
- **Utilisation** : Recherche technologique, terraformation, minage, construction de vaisseaux
- **Particularité** : Disponible instantanément partout dans l'empire

#### 3.1.2 Métal (Metal)
- **Nature** : Ressource non-renouvelable
- **Source** : Extraction minière des planètes
- **Utilisation** : Construction de vaisseaux exclusivement
- **Particularité** : Une fois épuisé, définitivement perdu (sauf récupération de débris)

### 3.2 Système de dette
- Le joueur peut emprunter jusqu'à **5x le revenu total**
- **Taux d'intérêt** : 15% du montant emprunté déduit chaque tour
- Utile pour financer des programmes d'urgence

---

## 4. Système Planétaire

### 4.1 Caractéristiques des planètes

| Attribut | Modifiable | Description |
|----------|------------|-------------|
| **Température** | Oui (terraformation) | Idéal : 22°C pour le joueur |
| **Gravité** | Non | Idéal : 1.0g - détermine la capacité maximale |
| **Métal** | Consommable | Réserves minières disponibles |

### 4.2 États d'une planète

```
[Inexplorée] → [Explorée] → [Colonisée] → [Développée]
                    ↓              ↓
              [Hostile]     [Abandonnée]
```

### 4.3 Économie planétaire

#### Revenu (Income)
- **Population élevée** → Génère des revenus (positif)
- **Population faible** → Coûte de l'argent (négatif)
- Colonies récentes nécessitent des investissements initiaux

#### Actions sur une planète
1. **Terraformation** : Modifier la température vers 22°C
   - Augmente la capacité de population maximale
   - Suit la loi des rendements décroissants
   
2. **Minage** : Extraire le métal disponible
   - Alimente le stock global de métal
   - S'arrête quand les réserves sont épuisées
   
3. **Construction de vaisseaux** : Produire des unités spatiales

### 4.4 Gestion du budget planétaire
- Slider pour répartir les dépenses entre terraformation et minage
- Les planètes non rentables peuvent être strip-minées puis abandonnées
- Interface par graphique à barres pseudo-logarithmique

---

## 5. Système Technologique

### 5.1 Les six domaines de recherche

| Technologie | Abréviation | Effet |
|-------------|-------------|-------|
| **Portée (Range)** | R | Distance de vol avant ravitaillement |
| **Vitesse (Speed)** | S | Rapidité de déplacement + priorité au combat |
| **Armes (Weapons)** | W | Puissance offensive |
| **Boucliers (Shields)** | Sh | Résistance aux dégâts |
| **Miniaturisation (Mini)** | M | Réduction du métal requis (coût $ augmenté) |
| **Radical** | Rad | Avancées imprévisibles |

### 5.2 Recherche Radical
Investir dans la recherche radicale peut débloquer :
- Bonus temporaire dans une technologie
- Amélioration de la terraformation
- Information sur des planètes distantes
- Vol de technologie adverse
- Nouveau type de vaisseau (Leurre, Biologique)

Mécanisme : 4 percées potentielles apparaissent, le joueur en élimine une, l'une des trois restantes se débloque aléatoirement.

### 5.3 Loi des rendements décroissants
**Principe fondamental** : L'efficacité des dépenses diminue avec l'intensité.

```
Exemple : 
- 10% du budget sur le minage → X unités de métal
- 20% du budget sur le minage → 1.4X unités (pas 2X)
```

**Recommandation** : Dépenser régulièrement et modérément plutôt qu'intensivement sur de courtes périodes.

---

## 6. Système de Vaisseaux

### 6.1 Types de vaisseaux

| Type | Caractéristiques | Usage |
|------|------------------|-------|
| **Chasseur** | Équilibré en armes/vitesse | Combat standard |
| **Éclaireur** | Portée +3, armes faibles | Exploration longue distance |
| **Vaisseau Colonial** | Très coûteux, transporte 10 000 colons | Colonisation |
| **Satellite** | Portée 0, peu cher, fragile | Défense statique |
| **Ravitailleur** | Ravitaille les flottes | Opérations longue distance |
| **Cuirassé** | Très puissant, très cher | Combat lourd |
| **Leurre** | Ultra simple/pas cher | Leurre, éclaireur économique |
| **Biologique** | Spécial (recherche radicale) | Variable |

### 6.2 Conception de vaisseaux

#### Paramètres ajustables
Chaque vaisseau est défini par 5 valeurs technologiques :
```
[Portée] / [Vitesse] / [Armes] / [Boucliers] / [Miniaturisation]
Exemple : 5/4/3/3/2
```

#### Système de coûts
- **Prototype** : Conception initiale payante
- **Production** : Construire des copies d'un design existant (moins cher)
- **Miniaturisation** : Plus d'argent, moins de métal

### 6.3 Gestion des flottes

#### Déplacement
- Cliquer-glisser d'une étoile à une autre sur la carte
- Les flottes ne peuvent pas changer de cap en hyperespace
- Ravitaillement automatique sur les planètes alliées

#### Organisation
- Regroupement/division de flottes
- Flottes mixtes (différents types de vaisseaux)
- Configuration de comportement au combat par type de vaisseau

#### Démantèlement (Disband)
- Récupération de 75% du métal sur une colonie
- Permet de recycler les vaisseaux obsolètes

---

## 7. Système de Combat

### 7.1 Principes généraux
- Combat automatique (pas de contrôle tactique du joueur)
- Se produit uniquement au-dessus des planètes
- Aucune rencontre possible en hyperespace

### 7.2 Déroulement d'une bataille

```
1. Arrivée des flottes sur une planète
2. Combat orbital (vaisseaux vs vaisseaux/satellites)
3. Bombardement de la colonie (si vaisseaux survivants)
4. Colonisation possible (si Vaisseau Colonial présent)
```

### 7.3 Facteurs de combat

| Facteur | Effet |
|---------|-------|
| Technologie Vitesse | Détermine qui tire en premier |
| Technologie Armes | Puissance des attaques |
| Technologie Boucliers | Absorption des dégâts |
| Population au sol | Combat avec la meilleure technologie du défenseur |

### 7.4 Options tactiques par vaisseau
- **Offensif** : Bonus d'armes, malus de boucliers
- **Défensif** : Inverse
- **Suivre** : Le vaisseau (ex: Vaisseau Colonial) attend la fin du combat

### 7.5 Priorité de ciblage IA
L'IA cible en priorité les **Vaisseaux Coloniaux** adverses.

### 7.6 Récupération de débris
Les vaisseaux détruits au-dessus d'une planète contrôlée :
- Une partie du métal tombe sur la planète
- Peut tuer des habitants
- Source de métal en fin de partie

---

## 8. Système d'Alliances

### 8.1 Types de relations
- **Ennemi** : État par défaut
- **Allié** : Coopération militaire et économique
- **Allié de confiance** : Alliance renforcée

### 8.2 Fonctionnalités alliés
- Ravitaillement sur les planètes alliées
- Combats conjoints contre un ennemi commun
- Communication via chat/messages texte

### 8.3 Particularité
Des alliés peuvent accidentellement se tirer dessus lors d'une bataille à plusieurs factions.

---

## 9. Événements Spéciaux

### 9.1 Novas stellaires
- Certaines étoiles explosent aléatoirement en cours de partie
- Destruction de la colonie présente
- Projection massive de métal sur les planètes voisines
- Peut tuer des habitants sur les planètes touchées

### 9.2 Armageddon
- Dispositif activable par n'importe quel joueur
- Provoque la nova d'un quart des étoiles de la galaxie
- Affecte y compris ses propres colonies
- Option de dernier recours ("Hail Mary")

```
Dialogue de confirmation :
"Êtes-vous certain de vouloir déclencher la politique de la terre brûlée ?
Même Moscou n'y a pas survécu..."
```

---

## 10. Interface Utilisateur

### 10.1 Fenêtre principale

```
┌─────────────────────────────────────────────────────┐
│  [Titre: Joueur in Galaxie in Année]                │
├───────────────────┬─────────────────────────────────┤
│                   │                                 │
│  Infos Planète    │        CARTE STELLAIRE          │
│  Budget           │                                 │
│  Liste Flottes    │   ⭐ ⭐    ⭐                   │
│                   │      ⭐  👑⭐                   │
│                   │   ⭐    ⭐   ⭐                 │
│                   │                                 │
└───────────────────┴─────────────────────────────────┘
```

### 10.2 Carte stellaire
- Vue 2D de la galaxie
- Trois niveaux de zoom
- Glisser-déposer pour déplacer les flottes
- Lignes de trajectoire avec segments par tour

### 10.3 Représentation visuelle

| Élément | Représentation |
|---------|----------------|
| Planète possédée | Planète avec bicorne napoléonien |
| Planète explorée | Apparence selon caractéristiques |
| Planète inexplorée | Point d'interrogation |
| Satellites en orbite | Anneaux autour de la planète |
| Flotte en transit | Ligne pointillée vers destination |

### 10.4 Graphiques et rapports
- **Graphique historique** : Évolution des joueurs dans le temps
- **Rapport de tour** : Vaisseaux construits, batailles, événements économiques
- **Comparaison technologique** : Position relative aux adversaires

---

## 11. Conditions de Victoire

### 11.1 Victoire standard
**Éliminer toutes les colonies adverses.**

Le joueur peut continuer à jouer après la victoire, mais sans opposition.

### 11.2 Indicateurs de progression
- Nombre de planètes contrôlées
- Revenu total
- Puissance militaire
- Avance technologique

---

## 12. Mode Multijoueur

### 12.1 Fonctionnalités
- Jusqu'à 8 joueurs simultanés
- Horloge de tour pour rythmer la partie
- Chat et messages texte intégrés
- Possibilité de rejoindre une partie en cours
- Joueur "Administrateur" peut forcer le passage au tour suivant

### 12.2 Options
- Chance au combat (optionnel)
- Alliances activées/désactivées

---

## 13. Intelligence Artificielle

### 13.1 Caractéristiques
- IA reconnue comme particulièrement compétente
- Plusieurs niveaux de difficulté
- Capable d'utiliser ravitailleurs et vaisseaux biologiques
- Attaques multi-planètes coordonnées
- Gestion optimisée du métal en fin de partie

### 13.2 Mode Auto-Play
Le joueur peut laisser l'IA jouer à sa place temporairement pour observer les stratégies.

---

## 14. Éléments Cosmétiques

### 14.1 Thème Empire Napoléonien
- Planètes portant des bicornes
- Voix et sons humoristiques d'époque
- Noms de technologies inspirés des campagnes napoléoniennes (ex: "Retraite de Russie" pour les boucliers)

### 14.2 Graphiques de vaisseaux
Varient selon les technologies :
- Vaisseaux 10/10 : Apparence de navire de ligne
- Vaisseaux 13/13 : Apparence de vaisseau amiral
- Variantes avec aigles impériaux, canons d'époque, etc.

### 14.3 Easter Eggs
- **2 décembre** : Bicorne doré sur les planètes (anniversaire du sacre)
- **15 août** : Cocarde tricolore (anniversaire de Napoléon)
- **Planète "Elbe"** : Message spécial si abandonnée ("L'Empereur reviendra...")
- **Planète "Waterloo"** : Message de défaite dramatique
- **Ravitailleur "Grande Armée"** : Événement de retraite désastreuse

### 14.4 Noms de planètes référentiels
Austerlitz, Marengo, Iéna, Wagram, Arcole, Rivoli, Pyramides, Borodino, etc.

---

## 15. Spécifications Techniques

### 15.1 Performances
- Partie de 10 minutes à 1 heure selon la taille
- Interface réactive optimisée pour le gameplay rapide
- Sauvegarde automatique de la disposition des fenêtres

---

## 16. Formules et Mécaniques Détaillées

### 16.1 Rendements décroissants
```
Efficacité = log(dépense) plutôt que linéaire
```

### 16.2 Coût des vaisseaux
```
Coût($) = f(Tech_Armes, Tech_Boucliers, Tech_Vitesse, Tech_Portée, Type)
Coût(Métal) = g(Tech) / Tech_Mini
```
La miniaturisation réduit le métal mais augmente le coût en argent.

### 16.3 Revenus planétaires
```
Revenu = Population × Facteur_Habitabilité - Coût_Maintenance
Habitabilité = f(|Température - 22|, |Gravité - 1.0|)
```

---

## 17. Stratégies Recommandées (pour référence IA)

### 17.1 Début de partie
1. Explorer les étoiles proches avec des éclaireurs
2. Coloniser les planètes proches de 22°C et 1.0g
3. Investir régulièrement dans la technologie Vitesse

### 17.2 Milieu de partie
- Équilibrer expansion et défense
- Ne pas négliger les satellites défensifs
- Surveiller les stocks de métal

### 17.3 Fin de partie
- Le métal devient critique
- Recycler les vaisseaux obsolètes
- Les novas peuvent redistribuer le métal

---

## Annexe A : Glossaire

| Terme | Définition |
|-------|------------|
| **4X** | eXplore, eXpand, eXploit, eXterminate |
| **Terraformation** | Modification de la température planétaire |
| **Extraction intensive** | Extraction maximale puis abandon |
| **Flotte** | Groupe de vaisseaux se déplaçant ensemble |
| **Tour** | Un cycle de jeu (minimum 10 ans in-game) |
| **Recherche Radicale** | Recherche aux résultats imprévisibles |

---

