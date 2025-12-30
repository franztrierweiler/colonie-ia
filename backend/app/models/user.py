"""
User model
"""
from datetime import datetime
from app import db


class User(db.Model):
    """User account model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    pseudo = db.Column(db.String(30), nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)

    # OAuth fields
    oauth_provider = db.Column(db.String(50), nullable=True)  # google, github, etc.
    oauth_id = db.Column(db.String(255), nullable=True)

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete for GDPR

    # Password reset
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    # Relationships
    games = db.relationship(
        "GamePlayer", back_populates="user", lazy="dynamic"
    )

    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        """Serialize user to dictionary (safe for API response)."""
        return {
            "id": self.id,
            "email": self.email,
            "pseudo": self.pseudo,
            "avatar_url": self.avatar_url,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def is_deleted(self):
        """Check if user is soft-deleted."""
        return self.deleted_at is not None
