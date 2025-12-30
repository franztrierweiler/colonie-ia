# Discussions Techniques - Colonie-IA

Ce fichier consigne les discussions et décisions techniques prises au cours du développement.

---

## 2025-12-30 : Makefile pour les commandes de développement

**Contexte** : Lors de la mise en place de la Phase 1 (infrastructure), un Makefile a été créé pour centraliser les commandes de développement.

**Décision** : Utiliser un Makefile comme point d'entrée unifié.

**Justification** :
- Architecture multi-composants (backend Flask + frontend React + Docker + BDD)
- Simplifie les commandes courantes (`make dev`, `make test`, `make docker-up`)
- Documente implicitement les commandes standard du projet
- Indépendant du langage (fonctionne pour Python et Node)

**Alternatives considérées** :
- Scripts shell séparés (`scripts/dev.sh`, etc.)
- npm scripts uniquement (limité au frontend)
- Pas de scripts (commandes manuelles)

---

## 2025-12-30 : Docker pour l'environnement de développement

**Contexte** : Un `docker-compose.yml` a été créé avec Flask, React, PostgreSQL et Redis.

**Décision** : Docker est **optionnel** pour le MVP, mais les fichiers sont prêts pour la suite.

**Justification** :
- Le MVP peut fonctionner avec SQLite (configuré par défaut) sans Docker
- `python run.py` + `npm run dev` suffisent pour développer
- Docker devient utile quand :
  - On veut PostgreSQL en local sans installation système
  - On prépare le déploiement production
  - On travaille en équipe avec des environnements différents

**Relation avec Azure** :
- Azure App Service peut déployer du code directement (sans Docker)
- Docker apporte la reproductibilité dev/prod et facilite les déploiements conteneurisés
- Les Dockerfiles seront utiles pour Azure Container Apps ou AKS si besoin de scaler

**Alternatives considérées** :
- Pas de Docker du tout (risque d'inconsistance entre environnements)
- Docker obligatoire (trop complexe pour un MVP)

---

## 2025-12-30 : Accès Docker pour Claude Code

**Contexte** : Lors du debug de l'authentification JWT, Claude Code n'a pas pu accéder aux logs Docker (`docker logs`) car les commandes nécessitent `sudo`.

**Problème** : Claude Code ne peut pas exécuter de commandes avec `sudo`, ce qui limite sa capacité à :
- Voir les logs des containers (`docker logs`)
- Exécuter des commandes dans les containers (`docker compose exec`)
- Diagnostiquer les erreurs backend en temps réel

**TODO** : Trouver une solution pour donner accès à Docker sans sudo :
- Option 1 : Ajouter l'utilisateur au groupe `docker` (`sudo usermod -aG docker $USER`)
- Option 2 : Configurer un alias ou script wrapper
- Option 3 : Utiliser les logs exposés via un volume

**Impact** : Sans cet accès, le debug nécessite une collaboration manuelle (l'utilisateur copie les logs).

---

## Template pour nouvelles discussions

```markdown
## [Date] : [Sujet]

**Contexte** : [Pourquoi cette discussion ?]

**Décision** : [Ce qui a été décidé]

**Justification** : [Pourquoi ce choix ?]

**Alternatives considérées** : [Autres options évaluées]
```
