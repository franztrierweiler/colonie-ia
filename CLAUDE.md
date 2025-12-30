# CLAUDE.md

Ce fichier fournit des instructions à Claude Code (claude.ai/code) pour travailler avec le code de ce dépôt.

## Présentation du Projet

**Colonie-IA** est une recréation d'un jeu de stratégie 4X galactique des années 1990 (eXplore, eXpand, eXploit, eXterminate) avec un thème humoristique Empire Napoléonien. Le projet est actuellement en **phase de spécification** - aucun code d'implémentation n'existe encore.

## État Actuel

- `docs/FEATURES.md` - Spécification fonctionnelle complète (440 lignes)
- `docs/EPICS_US.md` - EPICs et User Stories (96 US réparties en 13 EPICs)
- `docs/ARCHITECTURE.md` - Choix d'architecture technique
- `docs/SECURITY.md` - Spécifications de sécurité
- `docs/ART_PROMPT.md` - Prompts pour génération d'assets graphiques (logo)
- `README.md` - Description brève du projet
- Aucun système de build, tests ou code source n'existe actuellement

## Résumé de la Spécification (depuis FEATURES.md)

### Systèmes Principaux à Implémenter

1. **Ressources** : Argent (renouvelable, taxation) et Métal (non-renouvelable, minage)
2. **Planètes** : Température (terraformable vers 22°C idéal), gravité (fixe), réserves de métal
3. **Arbre Technologique** : 6 domaines - Portée, Vitesse, Armes, Boucliers, Miniaturisation, Radical
4. **Vaisseaux** : 8 types - Chasseur, Éclaireur, Vaisseau Colonial, Satellite, Ravitailleur, Cuirassé, Leurre, Biologique
5. **Combat** : Résolution automatique au-dessus des planètes uniquement ; Vitesse détermine la priorité
6. **Économie** : Rendements décroissants logarithmiques sur toutes les dépenses
7. **Alliances** : Ennemi/Allié/Allié de confiance avec ravitaillement partagé et combat conjoint

### Mécaniques Clés

- Système de dette : emprunt jusqu'à 5x le revenu à 15% d'intérêt/tour
- Déplacement des flottes par glisser-déposer ; pas de changement de cap en hyperespace
- Recyclage des vaisseaux récupère 75% du métal
- Novas stellaires aléatoires redistribuent le métal
- Bouton Armageddon : déclenche la nova d'1/4 des étoiles

### Exigences Interface

- Carte stellaire 2D avec 3 niveaux de zoom
- Panneau d'info planète avec sliders de budget
- Barre latérale de gestion des flottes
- Graphiques historiques et comparaison technologique
- Thème visuel napoléonien (bicornes sur les planètes contrôlées)

### Multijoueur

- 1-8 joueurs, timer de tour, chat, contrôles admin
- Solo contre IA avec plusieurs niveaux de difficulté
- Mode auto-play pour observer les stratégies de l'IA

## Règles

- Toujours lire les fichiers markdown dans `/docs` au démarrage de Claude Code
- Les spécifications fonctionnelles sont dans FEATURES.md
- Ne pas ajouter "Co-Authored-By: Claude" dans les messages de commit
- Lors d'une demande de planification, documenter chaque planification d'EPIC dans un fichier spécifique stocké dans plan/xx avec xx = nom de l'EPIC qui comprend son numéro.