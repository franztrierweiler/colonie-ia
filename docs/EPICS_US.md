# EPICs et User Stories - Colonie-IA

Ce document organise les fonctionnalités de FEATURES.md en EPICs et User Stories pour faciliter la planification du développement.

---

## EPIC 1 : Plateforme Technique

> **À définir** : Cet EPIC sera complété après la rédaction de ARCHITECTURE.md. Il contiendra les User Stories relatives à l'infrastructure technique, au choix des technologies, au système de build, etc.

### US 1.1 - [À définir]
### US 1.2 - [À définir]
### US 1.3 - [À définir]

---

## EPIC 2 : Configuration de Partie

### US 2.1 - Configuration de la galaxie
**En tant que** joueur,
**Je veux** configurer les paramètres de la galaxie (nombre d'étoiles, forme, densité),
**Afin de** personnaliser la durée et la complexité de ma partie.

### US 2.2 - Choix des adversaires
**En tant que** joueur,
**Je veux** choisir le nombre d'adversaires (1-7) et leur type (IA ou humain),
**Afin de** adapter le challenge à mes préférences.

### US 2.3 - Niveau de difficulté IA
**En tant que** joueur,
**Je veux** sélectionner le niveau de difficulté de l'IA,
**Afin de** jouer contre des adversaires adaptés à mon niveau.

### US 2.4 - Durée des tours
**En tant que** joueur,
**Je veux** définir la durée des tours (minimum 10 ans in-game),
**Afin de** contrôler le rythme de la partie.

### US 2.5 - Initialisation du joueur
**En tant que** joueur,
**Je veux** démarrer avec une planète mère terraformée, des ressources initiales et des technologies de base,
**Afin de** commencer la partie avec une base fonctionnelle.

---

## EPIC 3 : Système de Ressources

### US 3.1 - Gestion de l'argent
**En tant que** joueur,
**Je veux** percevoir des revenus basés sur la taxation de mes colonies,
**Afin de** financer mes activités (recherche, terraformation, construction).

### US 3.2 - Gestion du métal
**En tant que** joueur,
**Je veux** extraire du métal de mes planètes,
**Afin de** construire des vaisseaux.

### US 3.3 - Épuisement des ressources
**En tant que** joueur,
**Je veux** voir les réserves de métal diminuer avec l'extraction,
**Afin de** gérer stratégiquement cette ressource non-renouvelable.

### US 3.4 - Système de dette
**En tant que** joueur,
**Je veux** pouvoir emprunter jusqu'à 5x mon revenu total avec 15% d'intérêt par tour,
**Afin de** financer des programmes d'urgence.

### US 3.5 - Disponibilité globale de l'argent
**En tant que** joueur,
**Je veux** que mon argent soit disponible instantanément dans tout l'empire,
**Afin de** ne pas gérer de logistique financière.

---

## EPIC 4 : Système Planétaire

### US 4.1 - Caractéristiques planétaires
**En tant que** joueur,
**Je veux** voir les caractéristiques de chaque planète (température, gravité, métal),
**Afin de** évaluer son potentiel de colonisation.

### US 4.2 - Terraformation
**En tant que** joueur,
**Je veux** investir dans la terraformation pour rapprocher la température de 22°C,
**Afin d'** augmenter la capacité de population maximale.

### US 4.3 - États des planètes
**En tant que** joueur,
**Je veux** que les planètes passent par différents états (inexplorée, explorée, colonisée, développée, hostile, abandonnée),
**Afin de** suivre leur progression.

### US 4.4 - Économie planétaire
**En tant que** joueur,
**Je veux** que mes colonies à population élevée génèrent des revenus et celles à population faible coûtent de l'argent,
**Afin de** gérer un empire économiquement viable.

### US 4.5 - Budget planétaire
**En tant que** joueur,
**Je veux** répartir les dépenses entre terraformation et minage via un slider,
**Afin d'** optimiser le développement de chaque planète.

### US 4.6 - Rendements décroissants
**En tant que** joueur,
**Je veux** que l'efficacité des dépenses diminue de façon logarithmique,
**Afin de** privilégier des investissements réguliers et modérés.

### US 4.7 - Abandon de planète
**En tant que** joueur,
**Je veux** pouvoir strip-miner puis abandonner une planète non rentable,
**Afin de** récupérer ses ressources avant de la quitter.

---

## EPIC 5 : Système Technologique

### US 5.1 - Recherche Portée
**En tant que** joueur,
**Je veux** investir dans la technologie Portée,
**Afin d'** augmenter la distance de vol de mes vaisseaux avant ravitaillement.

### US 5.2 - Recherche Vitesse
**En tant que** joueur,
**Je veux** investir dans la technologie Vitesse,
**Afin d'** améliorer la rapidité de déplacement et la priorité au combat.

### US 5.3 - Recherche Armes
**En tant que** joueur,
**Je veux** investir dans la technologie Armes,
**Afin d'** augmenter la puissance offensive de mes vaisseaux.

### US 5.4 - Recherche Boucliers
**En tant que** joueur,
**Je veux** investir dans la technologie Boucliers,
**Afin d'** améliorer la résistance aux dégâts de mes vaisseaux.

### US 5.5 - Recherche Miniaturisation
**En tant que** joueur,
**Je veux** investir dans la Miniaturisation,
**Afin de** réduire le coût en métal des vaisseaux (contre un coût en argent accru).

### US 5.6 - Recherche Radicale
**En tant que** joueur,
**Je veux** investir dans la recherche Radicale pour obtenir des percées imprévisibles,
**Afin d'** obtenir des bonus, nouvelles technologies ou informations stratégiques.

### US 5.7 - Mécanisme de percée radicale
**En tant que** joueur,
**Je veux** éliminer une des 4 percées potentielles affichées pour que l'une des 3 restantes se débloque aléatoirement,
**Afin de** participer au choix tout en conservant une part d'incertitude.

### US 5.8 - Comparaison technologique
**En tant que** joueur,
**Je veux** voir ma position technologique relative aux adversaires,
**Afin d'** évaluer mes forces et faiblesses.

---

## EPIC 6 : Système de Vaisseaux

### US 6.1 - Types de vaisseaux de base
**En tant que** joueur,
**Je veux** construire des Chasseurs, Éclaireurs, Vaisseaux Coloniaux, Satellites, Ravitailleurs et Cuirassés,
**Afin de** constituer une flotte diversifiée.

### US 6.2 - Vaisseaux spéciaux
**En tant que** joueur,
**Je veux** débloquer les Leurres et Biologiques via la recherche Radicale,
**Afin d'** accéder à des options tactiques avancées.

### US 6.3 - Conception de vaisseaux
**En tant que** joueur,
**Je veux** définir les 5 valeurs technologiques (Portée/Vitesse/Armes/Boucliers/Mini) de mes designs,
**Afin de** créer des vaisseaux adaptés à mes besoins.

### US 6.4 - Prototype vs Production
**En tant que** joueur,
**Je veux** payer le coût de prototype pour un nouveau design puis produire des copies moins chères,
**Afin d'** optimiser mes dépenses de construction.

### US 6.5 - Déplacement des flottes
**En tant que** joueur,
**Je veux** déplacer mes flottes par glisser-déposer d'une étoile à une autre,
**Afin de** contrôler intuitivement mes unités.

### US 6.6 - Trajectoire fixe en hyperespace
**En tant que** joueur,
**Je veux** que mes flottes ne puissent pas changer de cap en hyperespace,
**Afin d'** ajouter une dimension stratégique à la planification des mouvements.

### US 6.7 - Ravitaillement automatique
**En tant que** joueur,
**Je veux** que mes flottes se ravitaillent automatiquement sur mes planètes et celles de mes alliés,
**Afin de** simplifier la logistique.

### US 6.8 - Organisation des flottes
**En tant que** joueur,
**Je veux** regrouper, diviser et créer des flottes mixtes,
**Afin de** gérer tactiquement mes forces.

### US 6.9 - Démantèlement de vaisseaux
**En tant que** joueur,
**Je veux** démanteler des vaisseaux sur une colonie pour récupérer 75% du métal,
**Afin de** recycler les unités obsolètes.

### US 6.10 - Configuration comportement combat
**En tant que** joueur,
**Je veux** configurer le comportement au combat de chaque type de vaisseau (offensif, défensif, suivre),
**Afin d'** optimiser mes tactiques.

---

## EPIC 7 : Système de Combat

### US 7.1 - Combat automatique
**En tant que** joueur,
**Je veux** que les combats se résolvent automatiquement sans contrôle tactique,
**Afin de** me concentrer sur la stratégie globale.

### US 7.2 - Combat orbital uniquement
**En tant que** joueur,
**Je veux** que les combats ne se produisent qu'au-dessus des planètes,
**Afin de** planifier mes attaques et défenses autour des points stratégiques.

### US 7.3 - Séquence de combat
**En tant que** joueur,
**Je veux** que les batailles suivent la séquence : combat orbital → bombardement → colonisation,
**Afin de** comprendre le déroulement des affrontements.

### US 7.4 - Priorité Vitesse
**En tant que** joueur,
**Je veux** que la technologie Vitesse détermine qui tire en premier,
**Afin de** valoriser cet investissement technologique.

### US 7.5 - Défense au sol
**En tant que** joueur,
**Je veux** que ma population défende avec la meilleure technologie disponible,
**Afin de** protéger mes colonies même sans flotte.

### US 7.6 - Ciblage IA des Vaisseaux Coloniaux
**En tant que** joueur,
**Je veux** que l'IA cible prioritairement mes Vaisseaux Coloniaux,
**Afin de** les protéger stratégiquement.

### US 7.7 - Récupération de débris
**En tant que** joueur,
**Je veux** récupérer une partie du métal des vaisseaux détruits au-dessus de mes planètes,
**Afin d'** obtenir des ressources en fin de partie.

### US 7.8 - Dégâts collatéraux des débris
**En tant que** joueur,
**Je veux** que les débris qui tombent puissent tuer des habitants,
**Afin d'** ajouter une conséquence aux batailles orbitales.

---

## EPIC 8 : Système d'Alliances

### US 8.1 - Types de relations
**En tant que** joueur,
**Je veux** définir mes relations avec les autres joueurs (Ennemi, Allié, Allié de confiance),
**Afin de** gérer mes interactions diplomatiques.

### US 8.2 - Ravitaillement allié
**En tant que** joueur,
**Je veux** ravitailler mes flottes sur les planètes de mes alliés,
**Afin d'** étendre ma portée opérationnelle.

### US 8.3 - Combat conjoint
**En tant que** joueur,
**Je veux** combattre aux côtés de mes alliés contre un ennemi commun,
**Afin de** coordonner nos forces.

### US 8.4 - Tirs amis accidentels
**En tant que** joueur,
**Je veux** que des alliés puissent accidentellement se tirer dessus lors de batailles multi-factions,
**Afin d'** ajouter du réalisme et de la complexité.

### US 8.5 - Communication entre alliés
**En tant que** joueur,
**Je veux** communiquer avec mes alliés via chat/messages,
**Afin de** coordonner nos stratégies.

---

## EPIC 9 : Événements Spéciaux

### US 9.1 - Novas stellaires aléatoires
**En tant que** joueur,
**Je veux** que certaines étoiles explosent aléatoirement en cours de partie,
**Afin d'** ajouter de l'imprévisibilité et de nouvelles opportunités de métal.

### US 9.2 - Effets des novas
**En tant que** joueur,
**Je veux** que les novas détruisent les colonies présentes et projettent du métal sur les planètes voisines,
**Afin de** créer des bouleversements stratégiques.

### US 9.3 - Bouton Armageddon
**En tant que** joueur,
**Je veux** pouvoir déclencher Armageddon (nova d'1/4 des étoiles),
**Afin d'** avoir une option de dernier recours.

### US 9.4 - Confirmation Armageddon
**En tant que** joueur,
**Je veux** voir un dialogue de confirmation humoristique avant de déclencher Armageddon,
**Afin de** prévenir les activations accidentelles.

---

## EPIC 10 : Interface Utilisateur

### US 10.1 - Carte stellaire 2D
**En tant que** joueur,
**Je veux** voir une carte 2D de la galaxie avec mes planètes et flottes,
**Afin de** visualiser l'état du jeu.

### US 10.2 - Niveaux de zoom
**En tant que** joueur,
**Je veux** disposer de 3 niveaux de zoom sur la carte,
**Afin de** voir la situation globale ou les détails locaux.

### US 10.3 - Représentation visuelle des planètes
**En tant que** joueur,
**Je veux** distinguer visuellement les planètes (possédées avec bicorne, explorées, inexplorées avec "?"),
**Afin de** comprendre rapidement la situation.

### US 10.4 - Lignes de trajectoire
**En tant que** joueur,
**Je veux** voir les lignes de trajectoire des flottes avec segments par tour,
**Afin de** anticiper les arrivées.

### US 10.5 - Panneau d'information planète
**En tant que** joueur,
**Je veux** voir les détails d'une planète sélectionnée (caractéristiques, budget, flottes),
**Afin de** gérer mes colonies efficacement.

### US 10.6 - Graphique budget pseudo-logarithmique
**En tant que** joueur,
**Je veux** voir la répartition du budget sous forme de graphique à barres pseudo-logarithmique,
**Afin de** visualiser les rendements décroissants.

### US 10.7 - Graphique historique
**En tant que** joueur,
**Je veux** voir l'évolution des joueurs dans le temps,
**Afin de** suivre la progression de la partie.

### US 10.8 - Rapport de tour
**En tant que** joueur,
**Je veux** voir un rapport récapitulant les événements du tour (constructions, batailles, économie),
**Afin de** suivre ce qui s'est passé.

### US 10.9 - Barre latérale de gestion des flottes
**En tant que** joueur,
**Je veux** gérer mes flottes via une barre latérale dédiée,
**Afin d'** organiser mes forces efficacement.

### US 10.10 - Sauvegarde disposition fenêtres
**En tant que** joueur,
**Je veux** que la disposition des fenêtres soit sauvegardée automatiquement,
**Afin de** retrouver mon interface personnalisée.

---

## EPIC 11 : Mode Multijoueur

### US 11.1 - Partie jusqu'à 8 joueurs
**En tant que** joueur,
**Je veux** jouer des parties avec jusqu'à 8 joueurs simultanés,
**Afin de** profiter d'affrontements multiples.

### US 11.2 - Horloge de tour
**En tant que** joueur,
**Je veux** que la partie soit rythmée par une horloge de tour,
**Afin de** maintenir un rythme de jeu fluide.

### US 11.3 - Chat intégré
**En tant que** joueur,
**Je veux** communiquer via un chat intégré,
**Afin d'** interagir avec les autres joueurs.

### US 11.4 - Rejoindre partie en cours
**En tant que** joueur,
**Je veux** pouvoir rejoindre une partie en cours,
**Afin de** remplacer un joueur absent.

### US 11.5 - Administrateur de partie
**En tant que** administrateur,
**Je veux** forcer le passage au tour suivant,
**Afin de** gérer les joueurs absents ou lents.

### US 11.6 - Options de partie
**En tant que** hôte,
**Je veux** activer/désactiver la chance au combat et les alliances,
**Afin de** personnaliser les règles.

---

## EPIC 12 : Intelligence Artificielle

### US 12.1 - IA compétente
**En tant que** joueur,
**Je veux** affronter une IA reconnue comme compétente,
**Afin d'** avoir des parties solo intéressantes.

### US 12.2 - Niveaux de difficulté
**En tant que** joueur,
**Je veux** choisir parmi plusieurs niveaux de difficulté,
**Afin d'** adapter le challenge.

### US 12.3 - IA utilisant ravitailleurs et biologiques
**En tant que** joueur,
**Je veux** que l'IA sache utiliser les ravitailleurs et vaisseaux biologiques,
**Afin de** me forcer à adapter ma stratégie.

### US 12.4 - Attaques coordonnées multi-planètes
**En tant que** joueur,
**Je veux** que l'IA lance des attaques coordonnées sur plusieurs planètes,
**Afin de** me confronter à des tactiques avancées.

### US 12.5 - Gestion optimisée du métal
**En tant que** joueur,
**Je veux** que l'IA gère efficacement le métal en fin de partie,
**Afin de** rester un adversaire jusqu'au bout.

### US 12.6 - Mode Auto-Play
**En tant que** joueur,
**Je veux** laisser l'IA jouer à ma place temporairement,
**Afin d'** observer les stratégies efficaces.

---

## EPIC 13 : Éléments Cosmétiques

### US 13.1 - Thème Empire Napoléonien
**En tant que** joueur,
**Je veux** que le jeu ait un thème visuel Empire Napoléonien,
**Afin de** profiter d'une ambiance humoristique unique.

### US 13.2 - Bicornes sur les planètes
**En tant que** joueur,
**Je veux** voir des bicornes napoléoniens sur mes planètes,
**Afin de** les identifier visuellement comme miennes.

### US 13.3 - Sons et voix d'époque
**En tant que** joueur,
**Je veux** entendre des voix et sons humoristiques d'époque,
**Afin d'** être immergé dans le thème.

### US 13.4 - Noms de technologies thématiques
**En tant que** joueur,
**Je veux** que les technologies aient des noms inspirés des campagnes napoléoniennes,
**Afin de** renforcer l'immersion.

### US 13.5 - Graphiques de vaisseaux évolutifs
**En tant que** joueur,
**Je veux** que l'apparence des vaisseaux change selon leur niveau technologique,
**Afin de** visualiser leur puissance.

### US 13.6 - Easter Eggs calendaires
**En tant que** joueur,
**Je veux** découvrir des Easter Eggs les 2 décembre et 15 août,
**Afin de** profiter de surprises thématiques.

### US 13.7 - Messages spéciaux de planètes
**En tant que** joueur,
**Je veux** voir des messages spéciaux pour certaines planètes (Elbe, Waterloo),
**Afin de** profiter de clins d'œil historiques.

### US 13.8 - Noms de planètes historiques
**En tant que** joueur,
**Je veux** que les planètes portent des noms de batailles napoléoniennes,
**Afin de** renforcer le thème.

---

## Résumé des EPICs

| EPIC | Titre | Nb US |
|------|-------|-------|
| 1 | Plateforme Technique | À définir |
| 2 | Configuration de Partie | 5 |
| 3 | Système de Ressources | 5 |
| 4 | Système Planétaire | 7 |
| 5 | Système Technologique | 8 |
| 6 | Système de Vaisseaux | 10 |
| 7 | Système de Combat | 8 |
| 8 | Système d'Alliances | 5 |
| 9 | Événements Spéciaux | 4 |
| 10 | Interface Utilisateur | 10 |
| 11 | Mode Multijoueur | 6 |
| 12 | Intelligence Artificielle | 6 |
| 13 | Éléments Cosmétiques | 8 |
| **Total** | | **82+** |
