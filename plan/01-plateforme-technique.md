# Plan de Développement - EPIC 1 : Plateforme Technique

## Statut Global

| Phase | Description | Statut |
|-------|-------------|--------|
| 1 | Infrastructure de base | ✅ Terminé |
| 2 | API RESTful | ✅ Terminé |
| 3 | WebSocket temps réel | ✅ Terminé |
| 4 | Authentification | ✅ Terminé |
| 5 | Frontend React | ✅ Terminé |
| 6 | Scalabilité | ⏳ À faire |

---

## Vue d'ensemble

L'EPIC 1 établit les fondations techniques du projet Colonie-IA : infrastructure, API et système d'authentification.

**Stack technique** (cf. ARCHITECTURE.md) :
- Frontend : React.js
- Backend : Python (Flask)
- Base de données : PostgreSQL (SQLite pour MVP)
- Hébergement : Azure App Service
- Authentification : Email/mot de passe + OAuth Google

---

## Phase 1 : Infrastructure de base ✅

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

- [x] T1.2.1 - Créer la structure backend Flask
- [x] T1.2.2 - Configuration par environnement (dev/staging/prod)
- [x] T1.2.3 - Initialiser le projet React avec Vite
- [x] T1.2.4 - Docker Compose pour développement local
- [x] T1.2.5 - Scripts de démarrage (Makefile)

### 1.3 Tâches - US 1.3 (Persistance des données)

- [x] T1.3.1 - Configuration SQLAlchemy + Flask-Migrate
- [x] T1.3.2 - Modèle User de base
- [x] T1.3.3 - Modèle Game (partie)
- [x] T1.3.4 - Script de migration initiale
- [x] T1.3.5 - Connexion PostgreSQL (prod) / SQLite (dev)

---

## Phase 2 : API RESTful (US 1.5) ✅

### 2.1 Configuration API

- [x] T2.1.1 - Blueprint Flask pour routes API
- [x] T2.1.2 - Middleware CORS sécurisé
- [x] T2.1.3 - Validation des entrées (Pydantic)
- [x] T2.1.4 - Gestion globale des erreurs
- [x] T2.1.5 - Documentation OpenAPI/Swagger (Flasgger)

### 2.2 Endpoints de base

- [x] GET `/api/health` - Health check
- [x] GET `/api/version` - Version de l'API

---

## Phase 3 : WebSocket temps réel (US 1.2) ✅

### 3.1 Configuration WebSocket

- [x] T3.1.1 - Intégrer Flask-SocketIO
- [x] T3.1.2 - Namespace pour les parties
- [x] T3.1.3 - Gestion des rooms (une par partie)
- [x] T3.1.4 - Authentification WebSocket

### 3.2 Événements WebSocket

| Événement | Direction | Description |
|-----------|-----------|-------------|
| `join_game` | Client → Serveur | Rejoindre une partie |
| `leave_game` | Client → Serveur | Quitter une partie |
| `game_update` | Serveur → Client | Mise à jour état de jeu |
| `turn_end` | Serveur → Client | Fin de tour |
| `chat_message` | Bidirectionnel | Message chat |

---

## Phase 4 : Authentification (US 1.7 à 1.14) 🔶

### 4.1 Modèle et schémas

- [x] T4.1.1 - Modèle User complet
- [x] T4.1.2 - Schémas validation (register, login)

### 4.2 US 1.7 - Création de compte ✅

- [x] T4.2.1 - Endpoint POST `/api/auth/register`
- [x] T4.2.2 - Validation email unique
- [x] T4.2.3 - Hashage mot de passe (Argon2)
- [x] T4.2.4 - Règles mot de passe (8 chars, majuscule, minuscule, chiffre)
- [ ] T4.2.5 - Email de vérification (optionnel V1)

### 4.3 US 1.8 - Connexion sécurisée ✅

- [x] T4.3.1 - Endpoint POST `/api/auth/login`
- [x] T4.3.2 - Génération JWT (access + refresh tokens)
- [x] T4.3.3 - Rate limiting (5 tentatives / 5 min)
- [ ] T4.3.4 - Logging des tentatives (audit)

### 4.4 US 1.9 - OAuth Google ✅

- [x] T4.4.1 - Configuration OAuth2 Google (Authlib)
- [x] T4.4.2 - Endpoint GET `/api/auth/google`
- [x] T4.4.3 - Callback `/api/auth/google/callback`
- [x] T4.4.4 - Création/liaison compte OAuth
- [x] T4.4.5 - Frontend: bouton Google + callback page

### 4.5 US 1.10 - Mot de passe oublié ✅

- [x] T4.5.1 - Endpoint POST `/api/auth/forgot-password`
- [x] T4.5.2 - Génération token réinitialisation (expiration 1h)
- [ ] T4.5.3 - Envoi email (SendGrid/SMTP) - log en dev
- [x] T4.5.4 - Endpoint POST `/api/auth/reset-password`
- [x] T4.5.5 - Frontend: pages ForgotPassword et ResetPassword

### 4.6 US 1.11 - Session persistante ✅

- [x] T4.6.1 - Refresh token longue durée (7 jours)
- [x] T4.6.2 - Endpoint POST `/api/auth/refresh`
- [ ] T4.6.3 - Cookie HttpOnly sécurisé

### 4.7 US 1.12 - Déconnexion ✅

- [x] T4.7.1 - Endpoint POST `/api/auth/logout`
- [ ] T4.7.2 - Invalidation du refresh token
- [ ] T4.7.3 - Blacklist JWT (Redis optionnel)

### 4.8 US 1.13 - Profil utilisateur 🔶

- [x] T4.8.1 - Endpoint GET `/api/users/me`
- [x] T4.8.2 - Endpoint PATCH `/api/users/me`
- [ ] T4.8.3 - Upload avatar (Azure Blob ou local)
- [x] T4.8.4 - Validation et sanitization pseudo

### 4.9 US 1.14 - Suppression de compte (RGPD) ✅

- [x] T4.9.1 - Endpoint DELETE `/api/users/me`
- [x] T4.9.2 - Soft delete avec anonymisation
- [ ] T4.9.3 - Suppression définitive après 30 jours
- [ ] T4.9.4 - Export des données utilisateur

---

## Phase 5 : Frontend React (US 1.1) ✅

### 5.1 Structure frontend

- [x] T5.1.1 - Configuration Vite + TypeScript
- [x] T5.1.2 - CSS custom (style noir minimaliste)
- [x] T5.1.3 - Client API (axios)
- [x] T5.1.4 - Client WebSocket
- [x] T5.1.5 - Routing (React Router)

### 5.2 Pages authentification

- [x] AuthModal - Modale connexion/inscription (+ bouton Google OAuth)
- [x] ForgotPassword - Demande réinitialisation
- [x] ResetPassword - Nouveau mot de passe
- [x] OAuthCallback - Callback OAuth
- [x] Profile - Édition profil

### 5.3 Composants communs

- [x] `AuthProvider` - Context authentification
- [x] `ProtectedRoute` - Route nécessitant connexion
- [x] `Layout` - Layout principal responsive
- [x] `AuthModal` - Modale d'authentification

---

## Phase 6 : Scalabilité (US 1.4) ⏳

### 6.1 Préparation scalabilité

- [ ] T6.1.1 - Sessions externalisées (Redis)
- [ ] T6.1.2 - Configuration Gunicorn multi-workers
- [x] T6.1.3 - Health checks pour load balancer
- [ ] T6.1.4 - Logs structurés (JSON)

---

## Sécurité (cf. SECURITY.md)

### Checklist sécurité EPIC 1

- [x] Hashage Argon2 pour mots de passe
- [x] JWT avec expiration courte (15 min access, 7j refresh)
- [x] Headers de sécurité (HSTS, CSP, X-Frame-Options)
- [x] CORS restrictif (domaines autorisés uniquement)
- [x] Rate limiting sur endpoints sensibles
- [x] Validation et sanitization de toutes les entrées
- [ ] Audit logging des actions d'authentification
- [x] Pas de secrets dans le code (variables d'environnement)
- [ ] HTTPS obligatoire en production

---

## Critères d'acceptation EPIC 1

- [x] Un utilisateur peut créer un compte avec email/mot de passe
- [x] Un utilisateur peut se connecter via Google OAuth
- [x] Un utilisateur peut réinitialiser son mot de passe
- [x] Les sessions persistent entre les visites (refresh token)
- [x] Un utilisateur peut modifier son pseudo et avatar
- [x] Un utilisateur peut supprimer son compte (RGPD)
- [x] L'API est documentée via Swagger/OpenAPI
- [x] WebSocket fonctionne pour les événements temps réel
- [x] L'application est responsive (desktop + mobile)
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
