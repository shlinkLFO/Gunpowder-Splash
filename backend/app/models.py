"""
SQLAlchemy ORM models for Beacon Studio
"""
from sqlalchemy import (
    Column, String, Integer, BigInteger, Boolean, DateTime, Text, 
    ForeignKey, Enum as SQLEnum, UniqueConstraint, CheckConstraint, TIMESTAMP
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import uuid
import enum
from .database import Base


class RoleEnum(str, enum.Enum):
    """User roles within a workspace"""
    ADMIN = "ADMIN"
    MOD = "MOD"
    USER = "USER"


class User(Base):
    """OAuth-authenticated user"""
    __tablename__ = "user"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    primary_email = Column(String, nullable=False, unique=True, index=True)
    display_name = Column(String)
    avatar_url = Column(String)
    provider = Column(String, nullable=False)  # Primary provider: 'google' or 'github'
    provider_user_id = Column(String, nullable=False)
    google_avatar_url = Column(String)  # Store Google avatar separately
    github_avatar_url = Column(String)  # Store GitHub avatar separately
    linked_providers = Column(String, default='[]')  # JSON array of linked providers ['google', 'github']
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    last_login_at = Column(TIMESTAMP(timezone=True))
    
    # Relationships
    owned_workspaces = relationship("Workspace", back_populates="owner", foreign_keys="Workspace.owner_user_id")
    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    ai_usage = relationship("AIUsage", back_populates="user")
    
    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uq_provider_user'),
    )


class Plan(Base):
    """Subscription plan (Free, Haste I/II/III)"""
    __tablename__ = "plan"
    
    id = Column(String, primary_key=True)  # 'free', 'haste_i', 'haste_ii', 'haste_iii'
    name = Column(String, nullable=False)
    price_cents = Column(Integer, nullable=False)
    storage_limit_bytes = Column(BigInteger, nullable=False)
    max_members = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    workspaces = relationship("Workspace", back_populates="plan")


class Workspace(Base):
    """Multi-tenant workspace container"""
    __tablename__ = "workspace"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(String, ForeignKey("plan.id"), nullable=False)
    storage_used_bytes = Column(BigInteger, nullable=False, default=0)
    cancelled_at = Column(TIMESTAMP(timezone=True))
    delete_after = Column(TIMESTAMP(timezone=True))
    is_read_only = Column(Boolean, nullable=False, default=False)
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="owned_workspaces", foreign_keys=[owner_user_id])
    plan = relationship("Plan", back_populates="workspaces")
    memberships = relationship("Membership", back_populates="workspace", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    ai_usage = relationship("AIUsage", back_populates="workspace")
    
    __table_args__ = (
        CheckConstraint('storage_used_bytes >= 0', name='storage_non_negative'),
    )


class Membership(Base):
    """User-workspace association with role"""
    __tablename__ = "membership"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id", ondelete="CASCADE"), primary_key=True)
    role = Column(SQLEnum(RoleEnum, name="role"), nullable=False)
    joined_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="memberships")
    workspace = relationship("Workspace", back_populates="memberships")


class Project(Base):
    """Code project within a workspace"""
    __tablename__ = "project"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    
    __table_args__ = (
        UniqueConstraint('workspace_id', 'name', name='uq_workspace_project_name'),
    )


class AIUsage(Base):
    """AI API usage tracking"""
    __tablename__ = "ai_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String, nullable=False)  # 'gemini', 'lm_studio', 'ollama'
    model_name = Column(String)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    cost_cents = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ai_usage")
    workspace = relationship("Workspace", back_populates="ai_usage")


class OAuthState(Base):
    """OAuth state tokens for secure OAuth flow"""
    __tablename__ = "oauth_state"
    
    state = Column(String, primary_key=True)
    provider = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now() + timedelta(minutes=10))


class AuditLog(Base):
    """Security and compliance audit trail"""
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"))
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id", ondelete="CASCADE"))
    action = Column(String, nullable=False)
    resource_type = Column(String)
    resource_id = Column(String)
    details = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

