# Architecture

Structure et stack technique du projet colonie-ia

## 1. Architecture Technique

La solution est décomposée en trois modules:
- Un frontend
- Un backend
- Une base de données

### 1.1 Stack technologique et hébergement de la V0

Cette première stack et ce premier mode d'hébergement permettent de réaliser une première version de production.

| Composant | Technologie |
|-----------|-------------|
| Frontend | React.js |
| Backend | Python (Flask) |
| Base de données | PostgreSQL (recommandé) ou SQLite (pour simplifier le MVP) |
| Hébergement | Azure App Service |
| Authentification | Email/mot de passe ou OAuth Google |

### 1.2 Stack technologique des versions ultérieures (au delà de V0)

Cette stack technologique sera à définir selon les contraintes d'hébergement.

## 2. Structure de données

Les données sont documentées dans le fichier DATA.md
