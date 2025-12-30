# Plan de Développement - EPIC 1 : Plateforme Technique

## Vue d'ensemble

L'EPIC 1 établit les fondations techniques du projet Colonie-IA : infrastructure, API et système d'authentification.

**Stack technique** (cf. ARCHITECTURE.md) :
- Frontend : React.js
- Backend : Python (Flask)
- Base de données : PostgreSQL (SQLite pour MVP)
- Hébergement : Azure App Service
- Authentification : Email/mot de passe + OAuth Google

---

## Phase 1 : Infrastructure de base

### 1.1 Structure du projet

```
colonie-ia/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── migrations/
│   ├── tests/
│   ├── requirements.txt
│   └── wsgi.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── docs/
├── plan/
└── docker-compose.yml
```

### 1.2 Tâches - US 1.6 (Environnements séparés)

| Tâche | Description | Fichiers |
|-------|-------------|----------|
| T1.2.1 | Créer la structure backend Flask | `backend/app/__init__.py`, `config.py` |
| T1.2.2 | Configuration par environnement (dev/staging/prod) | `backend/app/config.py`, `.env.example` |
| T1.2.3 | Initialiser le projet React avec Vite | `frontend/` |
| T1.2.4 | Docker Compose pour développement local | `docker-compose.yml` |
| T1.2.5 | Scripts de démarrage | `Makefile` ou `scripts/` |

### 1.3 Tâches - US 1.3 (Persistance des données)

| Tâche | Description | Fichiers |
|-------|-------------|----------|
| T1.3.1 | Configuration SQLAlchemy + Flask-Migrate | `backend/app/models/__init__.py` |
| T1.3.2 | Modèle User de base | `backend/app/models/user.py` |
| T1.3.3 | Modèle Game (partie) | `backend/app/models/game.py` |
| T1.3.4 | Script de migration initiale | `backend/migrations/` |
| T1.3.5 | Connexion PostgreSQL (prod) / SQLite (dev) | `backend/app/config.py` |

---

## Phase 2 : API RESTful (US 1.5)

### 2.1 Configuration API

| Tâche | Description | Fichiers |
|-------|-------------|----------|
| T2.1.1 | Blueprint Flask pour routes API | `backend/app/routes/__init__.py` |
| T2.1.2 | Middleware CORS sécurisé | `backend/app/__init__.py` |
| T2.1.3 | Validation des entrées (Pydantic/Marshmallow) | `backend/app/schemas/` |
| T2.1.4 | Gestion globale des erreurs | `backend/app/utils/errors.py` |
| T2.1.5 | Documentation OpenAPI/Swagger | `backend/app/routes/docs.py` |

### 2.2 Endpoints de base

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health` | GET | Health check |
| `/api/version` | GET | Version de l'API |

---

## Phase 3 : WebSocket temps réel (US 1.2)

### 3.1 Configuration WebSocket

| Tâche | Description | Fichiers |
|-------|-------------|----------|
| T3.1.1 | Intégrer Flask-SocketIO | `backend/app/__init__.py` |
| T3.1.2 | Namespace pour les parties | `backend/app/sockets/game.py` |
| T3.1.3 | Gestion des rooms (une par partie) | `backend/app/sockets/rooms.py` |
| T3.1.4 | Authentification WebSocket | `backend/app/sockets/auth.py` |

### 3.2 Événements WebSocket

| Événement | Direction | Description |
|-----------|-----------|-------------|
| `join_game` | Client → Serveur | Rejoindre une partie |
| `leave_game` | Client → Serveur | Quitter une partie |
| `game_update` | Serveur → Client | Mise à jour état de jeu |
| `turn_end` | Serveur → Client | Fin de tour |
| `chat_message` | Bidirectionnel | Message chat |

---

## Phase 4 : Authentification (US 1.7 à 1.14)

### 4.1 Modèle et schémas

| Tâche | Description | Fichiers |
|-------|-------------|----------|
| T4.1.1 | Modèle User complet | `backend/app/models/user.py` |
| T4.1.2 | Schémas validation (register, login) | `backend/app/schemas/auth.py` |

**Modèle User** :
```python
class User:
    id: int (PK)
    email: str (unique)
    password_hash: str (nullable si OAuth)
    pseudo: str
    avatar_url: str (nullable)
    oauth_provider: str (nullable)
    oauth_id: str (nullable)
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime (nullable, soft delete RGPD)
```

### 4.2 US 1.7 - Création de compte

| Tâche | Description |
|-------|-------------|
| T4.2.1 | Endpoint POST `/api/auth/register` |
| T4.2.2 | Validation email unique |
| T4.2.3 | Hashage mot de passe (Argon2) |
| T4.2.4 | Règles mot de passe (12 chars, majuscule, minuscule, chiffre, spécial) |
| T4.2.5 | Email de vérification (optionnel V1) |

### 4.3 US 1.8 - Connexion sécurisée

| Tâche | Description |
|-------|-------------|
| T4.3.1 | Endpoint POST `/api/auth/login` |
| T4.3.2 | Génération JWT (access + refresh tokens) |
| T4.3.3 | Rate limiting (5 tentatives / 5 min) |
| T4.3.4 | Logging des tentatives (audit) |

### 4.4 US 1.9 - OAuth Google

| Tâche | Description |
|-------|-------------|
| T4.4.1 | Configuration OAuth2 Google |
| T4.4.2 | Endpoint GET `/api/auth/google` |
| T4.4.3 | Callback `/api/auth/google/callback` |
| T4.4.4 | Création/liaison compte OAuth |

### 4.5 US 1.10 - Mot de passe oublié

| Tâche | Description |
|-------|-------------|
| T4.5.1 | Endpoint POST `/api/auth/forgot-password` |
| T4.5.2 | Génération token réinitialisation (expiration 1h) |
| T4.5.3 | Envoi email (SendGrid/SMTP) |
| T4.5.4 | Endpoint POST `/api/auth/reset-password` |

### 4.6 US 1.11 - Session persistante

| Tâche | Description |
|-------|-------------|
| T4.6.1 | Refresh token longue durée (7 jours) |
| T4.6.2 | Endpoint POST `/api/auth/refresh` |
| T4.6.3 | Cookie HttpOnly sécurisé |

### 4.7 US 1.12 - Déconnexion

| Tâche | Description |
|-------|-------------|
| T4.7.1 | Endpoint POST `/api/auth/logout` |
| T4.7.2 | Invalidation du refresh token |
| T4.7.3 | Blacklist JWT (Redis optionnel) |

### 4.8 US 1.13 - Profil utilisateur

| Tâche | Description |
|-------|-------------|
| T4.8.1 | Endpoint GET `/api/users/me` |
| T4.8.2 | Endpoint PATCH `/api/users/me` |
| T4.8.3 | Upload avatar (Azure Blob ou local) |
| T4.8.4 | Validation et sanitization pseudo |

### 4.9 US 1.14 - Suppression de compte (RGPD)

| Tâche | Description |
|-------|-------------|
| T4.9.1 | Endpoint DELETE `/api/users/me` |
| T4.9.2 | Soft delete avec anonymisation |
| T4.9.3 | Suppression définitive après 30 jours |
| T4.9.4 | Export des données utilisateur |

---

## Phase 5 : Frontend React (US 1.1)

### 5.1 Structure frontend

| Tâche | Description | Fichiers |
|-------|-------------|----------|
| T5.1.1 | Configuration Vite + TypeScript | `frontend/vite.config.ts` |
| T5.1.2 | Setup TailwindCSS ou CSS Modules | `frontend/src/styles/` |
| T5.1.3 | Client API (axios/fetch) | `frontend/src/services/api.ts` |
| T5.1.4 | Client WebSocket | `frontend/src/services/socket.ts` |
| T5.1.5 | Routing (React Router) | `frontend/src/App.tsx` |

### 5.2 Pages authentification

| Page | Route | Description |
|------|-------|-------------|
| Login | `/login` | Connexion email + OAuth |
| Register | `/register` | Création de compte |
| ForgotPassword | `/forgot-password` | Demande réinitialisation |
| ResetPassword | `/reset-password/:token` | Nouveau mot de passe |
| Profile | `/profile` | Édition profil |

### 5.3 Composants communs

| Composant | Description |
|-----------|-------------|
| `AuthProvider` | Context authentification |
| `ProtectedRoute` | Route nécessitant connexion |
| `Layout` | Layout principal responsive |
| `Input`, `Button`, `Form` | Composants UI réutilisables |

---

## Phase 6 : Scalabilité (US 1.4)

### 6.1 Préparation scalabilité

| Tâche | Description |
|-------|-------------|
| T6.1.1 | Sessions externalisées (Redis) |
| T6.1.2 | Configuration Gunicorn multi-workers |
| T6.1.3 | Health checks pour load balancer |
| T6.1.4 | Logs structurés (JSON) |

---

## Sécurité (cf. SECURITY.md)

### Checklist sécurité EPIC 1

- [ ] Hashage Argon2 pour mots de passe
- [ ] JWT avec expiration courte (15 min access, 7j refresh)
- [ ] Headers de sécurité (HSTS, CSP, X-Frame-Options)
- [ ] CORS restrictif (domaines autorisés uniquement)
- [ ] Rate limiting sur endpoints sensibles
- [ ] Validation et sanitization de toutes les entrées
- [ ] Audit logging des actions d'authentification
- [ ] Pas de secrets dans le code (variables d'environnement)
- [ ] HTTPS obligatoire en production

---

## Dépendances Python (backend)

```txt
# Framework
Flask>=3.0.0
Flask-SQLAlchemy>=3.1.0
Flask-Migrate>=4.0.0
Flask-SocketIO>=5.3.0
Flask-CORS>=4.0.0

# Authentification
PyJWT>=2.8.0
argon2-cffi>=23.1.0
Authlib>=1.3.0  # OAuth

# Validation
pydantic>=2.5.0
email-validator>=2.1.0

# Sécurité
python-dotenv>=1.0.0
bleach>=6.1.0

# Base de données
psycopg2-binary>=2.9.9
SQLAlchemy>=2.0.0

# Production
gunicorn>=21.2.0
eventlet>=0.33.0  # pour SocketIO

# Tests
pytest>=7.4.0
pytest-cov>=4.1.0
```

---

## Dépendances npm (frontend)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "axios": "^1.6.0",
    "socket.io-client": "^4.7.0",
    "zod": "^3.22.0",
    "dompurify": "^3.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "vitest": "^1.1.0"
  }
}
```

---

## Ordre d'implémentation recommandé

1. **Sprint 1** : Infrastructure (Phase 1)
   - Structure projet backend/frontend
   - Configuration environnements
   - Docker Compose
   - Modèles de base

2. **Sprint 2** : API et Auth basique (Phases 2 + 4.1-4.3)
   - API RESTful
   - Register / Login
   - JWT tokens

3. **Sprint 3** : Auth complet (Phase 4.4-4.9)
   - OAuth Google
   - Forgot/Reset password
   - Profil utilisateur
   - RGPD (suppression compte)

4. **Sprint 4** : Frontend Auth (Phase 5)
   - Pages authentification
   - Intégration API
   - Responsive design

5. **Sprint 5** : WebSocket + Scalabilité (Phases 3 + 6)
   - WebSocket configuration
   - Sessions Redis
   - Tests de charge

---

## Critères d'acceptation EPIC 1

- [ ] Un utilisateur peut créer un compte avec email/mot de passe
- [ ] Un utilisateur peut se connecter via Google OAuth
- [ ] Les sessions persistent entre les visites (refresh token)
- [ ] Un utilisateur peut modifier son pseudo et avatar
- [ ] Un utilisateur peut supprimer son compte (RGPD)
- [ ] L'API est documentée via Swagger/OpenAPI
- [ ] WebSocket fonctionne pour les événements temps réel
- [ ] L'application est responsive (desktop + mobile)
- [ ] Les tests couvrent >80% du code critique
- [ ] Aucune vulnérabilité OWASP Top 10 détectée

---

## Risques et mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Complexité OAuth | Moyen | Utiliser Authlib (bibliothèque mature) |
| Sécurité JWT | Élevé | Suivre SECURITY.md strictement |
| Performance WebSocket | Moyen | Prévoir Redis dès le début |
| Compatibilité mobile | Faible | Tests réguliers sur appareils réels |

---

*Document généré pour EPIC 1 - Plateforme Technique*
*Projet Colonie-IA*
