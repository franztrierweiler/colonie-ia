"""
Schémas Pydantic pour l'authentification.
"""
import re
from pydantic import BaseModel, EmailStr, field_validator


class RegisterSchema(BaseModel):
    """Schéma pour l'inscription."""

    email: EmailStr
    password: str
    pseudo: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not re.search(r"[a-z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une minuscule")
        if not re.search(r"\d", v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        return v

    @field_validator("pseudo")
    @classmethod
    def validate_pseudo(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Le pseudo doit contenir au moins 3 caractères")
        if len(v) > 30:
            raise ValueError("Le pseudo ne doit pas dépasser 30 caractères")
        if not re.match(r"^[a-zA-Z0-9_\- ]+$", v):
            raise ValueError("Le pseudo ne peut contenir que des lettres, chiffres, espaces, tirets et underscores")
        return v


class LoginSchema(BaseModel):
    """Schéma pour la connexion."""

    email: EmailStr
    password: str


class RefreshSchema(BaseModel):
    """Schéma pour le rafraîchissement du token."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Réponse avec tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Réponse utilisateur (sans données sensibles)."""

    id: int
    email: str
    pseudo: str
    avatar_url: str | None = None
    is_verified: bool = False

    class Config:
        from_attributes = True
