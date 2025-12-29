# Security

Règles et bonnes pratiques de sécurité pour le projet.

# Standards de Sécurité

Ce document définit les règles de sécurité obligatoires pour le développement et le déploiement de l'application SaaS.

---

## Table des matières

1. [Principes fondamentaux](#principes-fondamentaux)
2. [Sécurité du code](#sécurité-du-code)
3. [Authentification et autorisation](#authentification-et-autorisation)
4. [Sécurité des API](#sécurité-des-api)
5. [Sécurité des données](#sécurité-des-données)
6. [Sécurité Frontend](#sécurité-frontend)
7. [Sécurité Backend](#sécurité-backend)
8. [Gestion des secrets](#gestion-des-secrets)
9. [Logging et monitoring](#logging-et-monitoring)
10. [Architecture Azure](#architecture-azure)
11. [Architecture On-Premises](#architecture-on-premises)
12. [Conformité et audit](#conformité-et-audit)

---

## Principes fondamentaux

### Defense in Depth

Appliquer plusieurs couches de sécurité indépendantes. La compromission d'une couche ne doit pas compromettre l'ensemble du système.

### Principle of Least Privilege

Chaque composant, utilisateur ou service ne doit avoir accès qu'aux ressources strictement nécessaires à son fonctionnement.

### Zero Trust

Ne jamais faire confiance implicitement à un utilisateur, appareil ou réseau. Vérifier systématiquement chaque requête.

### Secure by Default

Les configurations par défaut doivent être les plus restrictives possibles. L'ouverture de droits doit être explicite.

### Fail Secure

En cas d'erreur ou de défaillance, le système doit se mettre dans un état sécurisé (refus d'accès par défaut).

---

## Sécurité du code

### Règles obligatoires

```python
# ❌ JAMAIS d'informations sensibles dans le code
API_KEY = "sk-1234567890"  # Interdit
DATABASE_URL = "postgres://user:password@host/db"  # Interdit

# ✅ Utiliser des variables d'environnement
API_KEY = os.environ["API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
```

```typescript
// ❌ JAMAIS de secrets côté client
const API_SECRET = "secret-key";  // Interdit

// ✅ Seules les clés publiques côté client
const API_PUBLIC_KEY = import.meta.env.VITE_API_PUBLIC_KEY;
```

### Validation des entrées

Toute entrée utilisateur est potentiellement malveillante. Valider systématiquement :

```python
# Backend : validation avec Pydantic
from pydantic import BaseModel, EmailStr, Field, validator
import bleach

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    bio: str | None = Field(None, max_length=500)

    @validator("name")
    def sanitize_name(cls, v: str) -> str:
        # Supprimer les caractères dangereux
        return bleach.clean(v, tags=[], strip=True)

    @validator("bio")
    def sanitize_bio(cls, v: str | None) -> str | None:
        if v is None:
            return None
        # Autoriser seulement certaines balises HTML
        return bleach.clean(v, tags=["b", "i", "p"], strip=True)
```

```typescript
// Frontend : validation avec Zod
import { z } from "zod";
import DOMPurify from "dompurify";

const userSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100).transform((val) => DOMPurify.sanitize(val)),
  bio: z.string().max(500).optional().transform((val) => 
    val ? DOMPurify.sanitize(val) : undefined
  ),
});
```

### Protection contre les injections

```python
# ❌ JAMAIS de concaténation SQL
query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL Injection

# ✅ Requêtes paramétrées obligatoires
query = "SELECT * FROM users WHERE id = :user_id"
result = db.execute(text(query), {"user_id": user_id})

# ✅ Avec un ORM (SQLAlchemy)
user = db.query(User).filter(User.id == user_id).first()
```

```python
# ❌ JAMAIS d'exécution de commandes avec entrées utilisateur
os.system(f"convert {filename} output.pdf")  # Command Injection

# ✅ Utiliser des listes d'arguments
import subprocess
subprocess.run(["convert", filename, "output.pdf"], check=True)

# ✅ Valider strictement les noms de fichiers
import re
if not re.match(r'^[a-zA-Z0-9_-]+\.(png|jpg|pdf)$', filename):
    raise ValidationError("Invalid filename")
```

### Dépendances

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: '0 6 * * 1'  # Hebdomadaire

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Python
      - name: Run Safety check
        run: |
          pip install safety
          safety check -r requirements.txt

      # JavaScript
      - name: Run npm audit
        run: npm audit --audit-level=high

      # SAST
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten
```

---

## Authentification et autorisation

### Authentification

#### Mots de passe

```python
# Configuration minimale
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True

# Hashage avec Argon2 (recommandé) ou bcrypt
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,        # Nombre d'itérations
    memory_cost=65536,  # 64 MB
    parallelism=4,      # Threads
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hash: str) -> bool:
    try:
        ph.verify(hash, password)
        return True
    except Exception:
        return False
```

#### Tokens JWT

```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from pydantic import BaseModel

# Configuration
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # Minimum 256 bits
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Court pour limiter l'exposition
REFRESH_TOKEN_EXPIRE_DAYS = 7

class TokenPayload(BaseModel):
    sub: str  # User ID
    exp: datetime
    iat: datetime
    jti: str  # Token ID unique (pour révocation)
    type: str  # "access" ou "refresh"

def create_access_token(user_id: str) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return TokenPayload(**payload)
    except JWTError as e:
        raise AuthenticationError("Invalid token") from e
```

#### Multi-Factor Authentication (MFA)

```python
import pyotp

def generate_totp_secret() -> str:
    """Génère un secret TOTP pour l'utilisateur."""
    return pyotp.random_base32()

def get_totp_uri(secret: str, email: str, issuer: str = "MyApp") -> str:
    """Génère l'URI pour le QR code."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)

def verify_totp(secret: str, code: str) -> bool:
    """Vérifie un code TOTP avec une fenêtre de tolérance."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # ±30 secondes
```

### Autorisation

#### Role-Based Access Control (RBAC)

```python
from enum import Enum
from functools import wraps

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"

class Permission(str, Enum):
    # Users
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    # Projects
    PROJECT_READ = "project:read"
    PROJECT_WRITE = "project:write"
    PROJECT_DELETE = "project:delete"
    # Admin
    ADMIN_ACCESS = "admin:access"

# Matrice de permissions
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {p for p in Permission},  # Toutes les permissions
    Role.MANAGER: {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
        Permission.PROJECT_DELETE,
    },
    Role.MEMBER: {
        Permission.USER_READ,
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
    },
    Role.VIEWER: {
        Permission.USER_READ,
        Permission.PROJECT_READ,
    },
}

def require_permission(permission: Permission):
    """Décorateur pour vérifier les permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = get_current_user()
            user_permissions = ROLE_PERMISSIONS.get(current_user.role, set())
            
            if permission not in user_permissions:
                raise AuthorizationError(
                    f"Permission '{permission}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@require_permission(Permission.PROJECT_DELETE)
async def delete_project(project_id: int) -> None:
    ...
```

#### Attribute-Based Access Control (ABAC)

```python
from dataclasses import dataclass

@dataclass
class AccessContext:
    user: User
    resource: Any
    action: str
    environment: dict  # IP, heure, device, etc.

class AccessPolicy:
    """Politique d'accès basée sur les attributs."""

    def can_access(self, ctx: AccessContext) -> bool:
        raise NotImplementedError

class ProjectAccessPolicy(AccessPolicy):
    def can_access(self, ctx: AccessContext) -> bool:
        project = ctx.resource
        user = ctx.user

        # Admin peut tout faire
        if user.role == Role.ADMIN:
            return True

        # Propriétaire peut tout faire sur son projet
        if project.owner_id == user.id:
            return True

        # Membre de l'équipe peut lire/écrire
        if user.id in project.team_member_ids:
            return ctx.action in ["read", "write"]

        # Sinon, accès refusé
        return False
```

### Protection contre le brute force

```python
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class RateLimiter:
    def __init__(
        self,
        max_attempts: int = 5,
        window_seconds: int = 300,  # 5 minutes
        lockout_seconds: int = 900,  # 15 minutes
    ):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.lockout_seconds = lockout_seconds
        self.attempts: dict[str, list[datetime]] = defaultdict(list)
        self.lockouts: dict[str, datetime] = {}

    async def check(self, key: str) -> None:
        """Vérifie si la clé est autorisée, lève une exception sinon."""
        now = datetime.utcnow()

        # Vérifier le lockout
        if key in self.lockouts:
            lockout_until = self.lockouts[key]
            if now < lockout_until:
                remaining = (lockout_until - now).seconds
                raise RateLimitError(
                    f"Too many attempts. Try again in {remaining} seconds."
                )
            else:
                del self.lockouts[key]

        # Nettoyer les anciennes tentatives
        window_start = now - timedelta(seconds=self.window_seconds)
        self.attempts[key] = [
            t for t in self.attempts[key] if t > window_start
        ]

        # Vérifier le nombre de tentatives
        if len(self.attempts[key]) >= self.max_attempts:
            self.lockouts[key] = now + timedelta(seconds=self.lockout_seconds)
            raise RateLimitError("Too many attempts. Account temporarily locked.")

    async def record_attempt(self, key: str) -> None:
        """Enregistre une tentative."""
        self.attempts[key].append(datetime.utcnow())

# Usage dans l'authentification
login_limiter = RateLimiter(max_attempts=5, window_seconds=300)

async def login(email: str, password: str) -> Token:
    await login_limiter.check(email)
    
    user = await user_repository.get_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        await login_limiter.record_attempt(email)
        raise AuthenticationError("Invalid credentials")
    
    return create_tokens(user)
```

---

## Sécurité des API

### Headers de sécurité

```python
# FastAPI middleware
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Protection XSS
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS (HTTPS obligatoire)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        
        # CSP
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://api.example.com; "
            "frame-ancestors 'none';"
        )
        
        # Referrer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), "
            "gyroscope=(), magnetometer=(), microphone=(), "
            "payment=(), usb=()"
        )
        
        return response

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)
```

### CORS

```python
from fastapi.middleware.cors import CORSMiddleware

# ❌ JAMAIS en production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dangereux
    allow_credentials=True,
)

# ✅ Configuration stricte
ALLOWED_ORIGINS = [
    "https://app.example.com",
    "https://admin.example.com",
]

if os.environ.get("ENV") == "development":
    ALLOWED_ORIGINS.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=86400,  # Cache preflight 24h
)
```

### Rate Limiting API

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Limites globales
@app.get("/api/users")
@limiter.limit("100/minute")
async def list_users():
    ...

# Limites par endpoint sensible
@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login():
    ...

# Limites par utilisateur authentifié
def get_user_id(request: Request) -> str:
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        payload = verify_token(token)
        return f"user:{payload.sub}"
    return get_remote_address(request)

@app.post("/api/exports")
@limiter.limit("10/hour", key_func=get_user_id)
async def create_export():
    ...
```

### Validation des requêtes

```python
from pydantic import BaseModel, Field, validator
from typing import Literal
import re

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, le=1000)
    per_page: int = Field(20, ge=1, le=100)
    sort_by: str = Field("created_at")
    sort_order: Literal["asc", "desc"] = "desc"

    @validator("sort_by")
    def validate_sort_by(cls, v: str) -> str:
        allowed_fields = {"created_at", "updated_at", "name", "email"}
        if v not in allowed_fields:
            raise ValueError(f"sort_by must be one of {allowed_fields}")
        return v

class SearchParams(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)

    @validator("query")
    def sanitize_query(cls, v: str) -> str:
        # Supprimer les caractères spéciaux SQL/NoSQL
        return re.sub(r'[<>"\';\\]', '', v)
```

---

## Sécurité des données

### Chiffrement au repos

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class FieldEncryption:
    """Chiffrement de champs sensibles en base de données."""

    def __init__(self, key: bytes):
        self.fernet = Fernet(key)

    @classmethod
    def derive_key(cls, password: str, salt: bytes) -> bytes:
        """Dérive une clé à partir d'un mot de passe."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data: str) -> str:
        """Chiffre une chaîne."""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Déchiffre une chaîne."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

# Usage avec SQLAlchemy
from sqlalchemy import TypeDecorator, String

class EncryptedString(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, encryption: FieldEncryption, *args, **kwargs):
        self.encryption = encryption
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            return self.encryption.encrypt(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return self.encryption.decrypt(value)
        return value

# Modèle avec champs chiffrés
class UserSensitiveData(Base):
    __tablename__ = "user_sensitive_data"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ssn = Column(EncryptedString(field_encryption))  # Numéro de sécu chiffré
    bank_account = Column(EncryptedString(field_encryption))
```

### Chiffrement en transit

```yaml
# Configuration TLS (nginx)
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # Certificats
    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;

    # Protocoles et ciphers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    # Session
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
}
```

### Anonymisation et pseudonymisation

```python
import hashlib
from typing import Any

def anonymize_email(email: str) -> str:
    """Anonymise un email pour les logs."""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    return f"{local[0]}***@{domain}"

def anonymize_ip(ip: str) -> str:
    """Anonymise une IP (masque le dernier octet)."""
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
    return "0.0.0.0"

def pseudonymize(value: str, salt: str) -> str:
    """Pseudonymise une valeur de façon déterministe."""
    return hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:16]

# Usage dans les logs
logger.info(
    "User login",
    extra={
        "email": anonymize_email(user.email),  # j***@example.com
        "ip": anonymize_ip(request.client.host),  # 192.168.1.0
        "user_pseudo": pseudonymize(str(user.id), LOG_SALT),
    }
)
```

### Rétention et suppression

```python
from datetime import datetime, timedelta
from sqlalchemy import and_

class DataRetentionService:
    """Service de gestion de la rétention des données."""

    RETENTION_POLICIES = {
        "audit_logs": timedelta(days=365),      # 1 an
        "session_logs": timedelta(days=90),     # 3 mois
        "deleted_users": timedelta(days=30),    # 30 jours (RGPD)
        "temp_files": timedelta(days=7),        # 7 jours
    }

    async def cleanup_expired_data(self) -> dict[str, int]:
        """Supprime les données expirées."""
        results = {}
        now = datetime.utcnow()

        # Audit logs
        cutoff = now - self.RETENTION_POLICIES["audit_logs"]
        count = await self._delete_audit_logs_before(cutoff)
        results["audit_logs"] = count

        # Sessions
        cutoff = now - self.RETENTION_POLICIES["session_logs"]
        count = await self._delete_sessions_before(cutoff)
        results["session_logs"] = count

        # Soft-deleted users (suppression définitive)
        cutoff = now - self.RETENTION_POLICIES["deleted_users"]
        count = await self._hard_delete_users_before(cutoff)
        results["deleted_users"] = count

        return results

    async def handle_gdpr_deletion_request(self, user_id: int) -> None:
        """Traite une demande de suppression RGPD."""
        # Soft delete immédiat
        await self.user_repository.soft_delete(user_id)

        # Anonymisation des données qui doivent être conservées
        await self._anonymize_user_audit_logs(user_id)

        # Suppression des données non essentielles
        await self._delete_user_preferences(user_id)
        await self._delete_user_sessions(user_id)

        # Log de la demande (obligatoire RGPD)
        await self.audit_service.log(
            action="GDPR_DELETION_REQUEST",
            user_id=user_id,
            details={"status": "processed"},
        )
```

---

## Sécurité Frontend

### Protection XSS

```typescript
import DOMPurify from "dompurify";

// ✅ Sanitizer le HTML avant insertion
function renderUserContent(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ["b", "i", "em", "strong", "p", "br"],
    ALLOWED_ATTR: [],
  });
}

// ✅ Utiliser textContent plutôt que innerHTML
element.textContent = userInput;  // Safe
element.innerHTML = userInput;    // Dangereux

// ✅ En React, le JSX échappe automatiquement
function UserName({ name }: { name: string }) {
  return <span>{name}</span>;  // Safe, échappé automatiquement
}

// ❌ dangerouslySetInnerHTML à éviter
function UnsafeComponent({ html }: { html: string }) {
  return <div dangerouslySetInnerHTML={{ __html: html }} />;  // Dangereux
}

// ✅ Si dangerouslySetInnerHTML est nécessaire, sanitizer
function SafeHtmlComponent({ html }: { html: string }) {
  const sanitized = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

### Protection CSRF

```typescript
// Service API avec token CSRF
class ApiClient {
  private csrfToken: string | null = null;

  async getCsrfToken(): Promise<string> {
    if (!this.csrfToken) {
      const response = await fetch("/api/csrf-token");
      const data = await response.json();
      this.csrfToken = data.token;
    }
    return this.csrfToken;
  }

  async post<T>(url: string, data: unknown): Promise<T> {
    const csrfToken = await this.getCsrfToken();

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfToken,
      },
      credentials: "include",  // Important pour les cookies
      body: JSON.stringify(data),
    });

    if (response.status === 403) {
      // Token expiré, renouveler
      this.csrfToken = null;
      return this.post(url, data);
    }

    return response.json();
  }
}
```

```python
# Backend : validation CSRF
from fastapi import Request, HTTPException
from itsdangerous import URLSafeTimedSerializer

csrf_serializer = URLSafeTimedSerializer(os.environ["CSRF_SECRET"])

def generate_csrf_token(session_id: str) -> str:
    return csrf_serializer.dumps(session_id)

def verify_csrf_token(token: str, session_id: str, max_age: int = 3600) -> bool:
    try:
        data = csrf_serializer.loads(token, max_age=max_age)
        return data == session_id
    except Exception:
        return False

async def csrf_middleware(request: Request, call_next):
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        csrf_token = request.headers.get("X-CSRF-Token")
        session_id = request.cookies.get("session_id")

        if not csrf_token or not verify_csrf_token(csrf_token, session_id):
            raise HTTPException(status_code=403, detail="Invalid CSRF token")

    return await call_next(request)
```

### Stockage sécurisé côté client

```typescript
// ❌ Ne JAMAIS stocker de secrets dans localStorage
localStorage.setItem("api_key", secretKey);  // Accessible par XSS

// ✅ Utiliser des cookies HttpOnly pour les tokens sensibles
// (gérés côté serveur)

// ✅ Pour les données non sensibles, chiffrer si nécessaire
import CryptoJS from "crypto-js";

class SecureStorage {
  private encryptionKey: string;

  constructor(key: string) {
    this.encryptionKey = key;
  }

  setItem(key: string, value: unknown): void {
    const encrypted = CryptoJS.AES.encrypt(
      JSON.stringify(value),
      this.encryptionKey
    ).toString();
    localStorage.setItem(key, encrypted);
  }

  getItem<T>(key: string): T | null {
    const encrypted = localStorage.getItem(key);
    if (!encrypted) return null;

    try {
      const decrypted = CryptoJS.AES.decrypt(encrypted, this.encryptionKey);
      return JSON.parse(decrypted.toString(CryptoJS.enc.Utf8));
    } catch {
      return null;
    }
  }
}
```

### Content Security Policy

```typescript
// next.config.js (Next.js)
const securityHeaders = [
  {
    key: "Content-Security-Policy",
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'",  // Ajuster selon besoins
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self'",
      "connect-src 'self' https://api.example.com wss://ws.example.com",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join("; "),
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: "/:path*",
        headers: securityHeaders,
      },
    ];
  },
};
```

---

## Sécurité Backend

### Configuration sécurisée

```python
# config/settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class SecuritySettings(BaseSettings):
    # Secrets (jamais de valeur par défaut)
    secret_key: str
    jwt_secret: str
    database_encryption_key: str

    # Configuration
    debug: bool = False
    allowed_hosts: list[str] = ["api.example.com"]

    # Sessions
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"

    # Mots de passe
    password_min_length: int = 12
    password_hash_iterations: int = 480000

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache
def get_security_settings() -> SecuritySettings:
    return SecuritySettings()

# Validation au démarrage
settings = get_security_settings()
assert len(settings.secret_key) >= 32, "SECRET_KEY must be at least 32 characters"
assert not settings.debug or os.environ.get("ENV") != "production", "DEBUG must be False in production"
```

### Gestion des sessions

```python
from datetime import datetime, timedelta
import secrets

class SessionManager:
    def __init__(self, redis_client, settings: SecuritySettings):
        self.redis = redis_client
        self.settings = settings
        self.session_ttl = timedelta(hours=24)

    async def create_session(self, user_id: int, metadata: dict) -> str:
        """Crée une nouvelle session."""
        session_id = secrets.token_urlsafe(32)

        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "ip_address": metadata.get("ip_address"),
            "user_agent": metadata.get("user_agent"),
        }

        await self.redis.setex(
            f"session:{session_id}",
            self.session_ttl,
            json.dumps(session_data),
        )

        return session_id

    async def validate_session(self, session_id: str, request_ip: str) -> dict:
        """Valide une session existante."""
        session_data = await self.redis.get(f"session:{session_id}")

        if not session_data:
            raise SessionExpiredError()

        data = json.loads(session_data)

        # Validation de l'IP (optionnel, peut causer des problèmes avec NAT)
        if self.settings.validate_session_ip:
            if data.get("ip_address") != request_ip:
                await self.invalidate_session(session_id)
                raise SessionInvalidError("IP address mismatch")

        # Prolonger la session
        await self.redis.expire(f"session:{session_id}", self.session_ttl)

        return data

    async def invalidate_session(self, session_id: str) -> None:
        """Invalide une session."""
        await self.redis.delete(f"session:{session_id}")

    async def invalidate_all_user_sessions(self, user_id: int) -> int:
        """Invalide toutes les sessions d'un utilisateur."""
        pattern = "session:*"
        count = 0

        async for key in self.redis.scan_iter(pattern):
            session_data = await self.redis.get(key)
            if session_data:
                data = json.loads(session_data)
                if data.get("user_id") == user_id:
                    await self.redis.delete(key)
                    count += 1

        return count
```

### Protection des endpoints sensibles

```python
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter

router = APIRouter()

# Middleware de logging pour endpoints sensibles
async def audit_sensitive_action(request: Request, call_next):
    response = await call_next(request)

    if request.url.path.startswith("/api/admin"):
        await audit_service.log(
            action=f"{request.method} {request.url.path}",
            user_id=request.state.user_id,
            ip_address=request.client.host,
            status_code=response.status_code,
        )

    return response

# Endpoint avec protections multiples
@router.delete("/users/{user_id}")
@limiter.limit("10/hour")
@require_permission(Permission.USER_DELETE)
@require_mfa  # MFA obligatoire pour cette action
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    audit: AuditService = Depends(get_audit_service),
):
    # Vérification supplémentaire
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot delete your own account")

    # Action
    await user_service.delete(user_id)

    # Audit
    await audit.log(
        action="USER_DELETED",
        actor_id=current_user.id,
        target_id=user_id,
        details={"reason": "admin_action"},
    )

    return {"status": "deleted"}
```

---

## Gestion des secrets

### Vault / Azure Key Vault

```python
# Azure Key Vault
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class AzureSecretManager:
    def __init__(self, vault_url: str):
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_url, credential=credential)
        self._cache: dict[str, str] = {}

    def get_secret(self, name: str, use_cache: bool = True) -> str:
        if use_cache and name in self._cache:
            return self._cache[name]

        secret = self.client.get_secret(name)
        self._cache[name] = secret.value
        return secret.value

    def set_secret(self, name: str, value: str) -> None:
        self.client.set_secret(name, value)
        self._cache[name] = value

# HashiCorp Vault
import hvac

class HashicorpVaultManager:
    def __init__(self, url: str, token: str):
        self.client = hvac.Client(url=url, token=token)

    def get_secret(self, path: str, key: str) -> str:
        response = self.client.secrets.kv.v2.read_secret_version(path=path)
        return response["data"]["data"][key]

    def get_database_credentials(self, role: str) -> dict:
        """Récupère des credentials dynamiques pour la BDD."""
        response = self.client.secrets.database.generate_credentials(name=role)
        return {
            "username": response["data"]["username"],
            "password": response["data"]["password"],
            "ttl": response["lease_duration"],
        }
```

### Rotation des secrets

```python
import asyncio
from datetime import datetime, timedelta

class SecretRotationService:
    def __init__(self, vault: SecretManager, notification: NotificationService):
        self.vault = vault
        self.notification = notification

    async def rotate_database_password(self) -> None:
        """Rotation du mot de passe de la base de données."""
        # Générer un nouveau mot de passe
        new_password = secrets.token_urlsafe(32)

        # Mettre à jour dans la BDD
        await self._update_database_password(new_password)

        # Mettre à jour dans le vault
        self.vault.set_secret("database-password", new_password)

        # Logger
        await self.audit.log(action="SECRET_ROTATED", details={"secret": "database-password"})

    async def check_expiring_secrets(self) -> list[str]:
        """Vérifie les secrets proches de l'expiration."""
        expiring = []
        secrets_to_check = [
            ("api-key-external", timedelta(days=30)),
            ("ssl-certificate", timedelta(days=30)),
            ("jwt-secret", timedelta(days=90)),
        ]

        for secret_name, warning_threshold in secrets_to_check:
            expiry = await self._get_secret_expiry(secret_name)
            if expiry and expiry - datetime.utcnow() < warning_threshold:
                expiring.append(secret_name)
                await self.notification.send_alert(
                    f"Secret '{secret_name}' expires on {expiry}"
                )

        return expiring
```

### Variables d'environnement

```bash
# .env.example (template, JAMAIS de vraies valeurs)
# Application
ENV=development
DEBUG=false
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DATABASE_POOL_SIZE=10

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (générer avec: openssl rand -base64 32)
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
ENCRYPTION_KEY=your-encryption-key-here

# External Services
STRIPE_SECRET_KEY=sk_test_xxx
SENDGRID_API_KEY=SG.xxx

# Azure (si applicable)
AZURE_KEY_VAULT_URL=https://myvault.vault.azure.net/
```

```python
# Validation des variables d'environnement au démarrage
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str
    debug: bool = False

    # Ces champs n'ont pas de défaut = obligatoires
    database_url: str
    secret_key: str
    jwt_secret: str

    class Config:
        env_file = ".env"

    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

# Échoue au démarrage si les variables manquent
settings = Settings()
```

---

## Logging et monitoring

### Audit logging

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class AuditAction(str, Enum):
    # Auth
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    MFA_ENABLED = "MFA_ENABLED"
    MFA_DISABLED = "MFA_DISABLED"

    # Data
    DATA_EXPORT = "DATA_EXPORT"
    DATA_DELETE = "DATA_DELETE"
    GDPR_REQUEST = "GDPR_REQUEST"

    # Admin
    USER_CREATED = "USER_CREATED"
    USER_DELETED = "USER_DELETED"
    ROLE_CHANGED = "ROLE_CHANGED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"

    # Security
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INVALID_TOKEN = "INVALID_TOKEN"

class AuditLogEntry(BaseModel):
    timestamp: datetime
    action: AuditAction
    actor_id: int | None
    actor_email: str | None
    target_type: str | None
    target_id: str | None
    ip_address: str
    user_agent: str | None
    details: dict
    severity: str  # info, warning, critical

class AuditService:
    def __init__(self, repository: AuditRepository):
        self.repository = repository

    async def log(
        self,
        action: AuditAction,
        request: Request,
        actor: User | None = None,
        target: Any = None,
        details: dict | None = None,
        severity: str = "info",
    ) -> None:
        entry = AuditLogEntry(
            timestamp=datetime.utcnow(),
            action=action,
            actor_id=actor.id if actor else None,
            actor_email=anonymize_email(actor.email) if actor else None,
            target_type=type(target).__name__ if target else None,
            target_id=str(target.id) if target and hasattr(target, "id") else None,
            ip_address=anonymize_ip(request.client.host),
            user_agent=request.headers.get("user-agent"),
            details=details or {},
            severity=severity,
        )

        await self.repository.save(entry)

        # Alerte immédiate pour les événements critiques
        if severity == "critical":
            await self._send_security_alert(entry)
```

### Alertes de sécurité

```python
class SecurityAlertService:
    ALERT_THRESHOLDS = {
        "failed_logins": {"count": 10, "window_minutes": 5},
        "rate_limit_hits": {"count": 100, "window_minutes": 1},
        "invalid_tokens": {"count": 50, "window_minutes": 5},
    }

    async def check_and_alert(self, event_type: str, identifier: str) -> None:
        threshold = self.ALERT_THRESHOLDS.get(event_type)
        if not threshold:
            return

        count = await self._count_recent_events(
            event_type, identifier, threshold["window_minutes"]
        )

        if count >= threshold["count"]:
            await self._send_alert(
                severity="high",
                title=f"Security threshold exceeded: {event_type}",
                details={
                    "event_type": event_type,
                    "identifier": identifier,
                    "count": count,
                    "threshold": threshold["count"],
                    "window_minutes": threshold["window_minutes"],
                },
            )

    async def _send_alert(self, severity: str, title: str, details: dict) -> None:
        # Slack
        await self.slack.send_message(
            channel="#security-alerts",
            text=f"🚨 [{severity.upper()}] {title}",
            attachments=[{"fields": [{"title": k, "value": str(v)} for k, v in details.items()]}],
        )

        # PagerDuty pour les alertes critiques
        if severity == "critical":
            await self.pagerduty.create_incident(
                title=title,
                details=details,
                urgency="high",
            )
```

### Métriques de sécurité

```python
from prometheus_client import Counter, Histogram, Gauge

# Compteurs
auth_attempts = Counter(
    "auth_attempts_total",
    "Total authentication attempts",
    ["status", "method"],  # status: success/failure, method: password/mfa/oauth
)

rate_limit_hits = Counter(
    "rate_limit_hits_total",
    "Total rate limit hits",
    ["endpoint"],
)

security_events = Counter(
    "security_events_total",
    "Total security events",
    ["event_type", "severity"],
)

# Histogrammes
auth_latency = Histogram(
    "auth_latency_seconds",
    "Authentication latency",
    ["method"],
)

# Jauges
active_sessions = Gauge(
    "active_sessions",
    "Number of active sessions",
)

failed_login_rate = Gauge(
    "failed_login_rate",
    "Failed login rate (per minute)",
)
```

---

## Architecture Azure

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INTERNET                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Azure Front Door                                     │
│                    (WAF, DDoS Protection, CDN)                              │
│                         + Azure CDN (static assets)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Application Gateway (WAF v2)                              │
│                      (SSL Termination, Path routing)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│   AKS / App Service │ │   AKS / App Service │ │   Azure Functions   │
│      (Frontend)     │ │       (API)         │ │   (Background jobs) │
│                     │ │                     │ │                     │
│  - React SPA        │ │  - FastAPI/Node     │ │  - Scheduled tasks  │
│  - Static assets    │ │  - Business logic   │ │  - Event processing │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Virtual Network                                    │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Private Subnet                                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ Azure SQL   │  │ Azure Redis │  │ Azure Blob  │  │ Key Vault   │  │  │
│  │  │ (Private    │  │ (Private    │  │ (Private    │  │ (Private    │  │  │
│  │  │  Endpoint)  │  │  Endpoint)  │  │  Endpoint)  │  │  Endpoint)  │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Services Azure recommandés

| Composant | Service Azure | Configuration sécurité |
|-----------|---------------|------------------------|
| WAF/DDoS | Azure Front Door Premium | WAF policy, DDoS Standard |
| Load Balancer | Application Gateway v2 | WAF v2, SSL/TLS 1.2+ |
| Compute | AKS ou App Service | Private endpoints, managed identity |
| Database | Azure SQL / Cosmos DB | TDE, Private endpoint, AAD auth |
| Cache | Azure Redis | Private endpoint, TLS, auth |
| Storage | Azure Blob | Private endpoint, encryption, SAS |
| Secrets | Azure Key Vault | RBAC, soft delete, purge protection |
| Identity | Azure AD B2C / Entra ID | MFA, conditional access |
| Monitoring | Azure Monitor + Sentinel | Log Analytics, alerting |

### Configuration Terraform

```hcl
# main.tf

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location
  tags     = var.tags
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "${var.project_name}-${var.environment}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

# Subnets
resource "azurerm_subnet" "app_gateway" {
  name                 = "app-gateway-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "app" {
  name                 = "app-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]

  delegation {
    name = "app-service-delegation"
    service_delegation {
      name    = "Microsoft.Web/serverFarms"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}

resource "azurerm_subnet" "data" {
  name                 = "data-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.3.0/24"]

  private_endpoint_network_policies_enabled = true
}

# Network Security Groups
resource "azurerm_network_security_group" "app" {
  name                = "${var.project_name}-app-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowAppGateway"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "10.0.1.0/24"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                       = "${var.project_name}-${var.environment}-kv"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 90
  purge_protection_enabled   = true

  network_acls {
    default_action             = "Deny"
    bypass                     = "AzureServices"
    virtual_network_subnet_ids = [azurerm_subnet.app.id]
  }
}

# Azure SQL avec Private Endpoint
resource "azurerm_mssql_server" "main" {
  name                         = "${var.project_name}-${var.environment}-sql"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_login
  administrator_login_password = var.sql_admin_password

  azuread_administrator {
    login_username = var.aad_admin_username
    object_id      = var.aad_admin_object_id
  }

  public_network_access_enabled = false

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_private_endpoint" "sql" {
  name                = "${var.project_name}-sql-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.data.id

  private_service_connection {
    name                           = "sql-privateserviceconnection"
    private_connection_resource_id = azurerm_mssql_server.main.id
    subresource_names              = ["sqlServer"]
    is_manual_connection           = false
  }
}

# Application Gateway avec WAF
resource "azurerm_application_gateway" "main" {
  name                = "${var.project_name}-${var.environment}-appgw"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }

  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }

  ssl_policy {
    policy_type = "Predefined"
    policy_name = "AppGwSslPolicy20220101S"
  }

  # ... autres configurations (frontend, backend, listeners)
}
```

### Bonnes pratiques Azure

1. **Managed Identity** : Utiliser les identités managées pour l'authentification entre services Azure (pas de credentials à gérer)

2. **Private Endpoints** : Tous les services PaaS accessibles uniquement via Private Endpoints

3. **Network Security Groups** : Règles de filtrage sur chaque subnet

4. **Azure Policy** : Appliquer des policies de conformité (ex: forcer le chiffrement, interdire les IPs publiques)

5. **Microsoft Defender for Cloud** : Activer pour la détection des menaces

6. **Azure Sentinel** : SIEM pour la corrélation des événements de sécurité

---

