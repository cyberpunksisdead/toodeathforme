"""Database models for admin panel."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
  """Base class for all SQLAlchemy models."""
  pass

class User(Base):
  """User model with authentication fields."""
  __tablename__ = 'users'
  
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
  hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
  is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
  is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
  updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)
  
  def __repr__(self) -> str:
    return f'<User(id={self.id}, email="{self.email}", is_admin={self.is_admin})>'

class Post(Base):
  """Blog post model for dynamic content management."""
  __tablename__ = 'posts'
  
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
  title: Mapped[str] = mapped_column(String(500), nullable=False)
  content: Mapped[str] = mapped_column(Text, nullable=False)
  description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
  
  # Metadata (stored as JSON)
  tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
  image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
  
  # Publishing control
  published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
  publish_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
  
  # Timestamps
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
  updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)
  
  def __repr__(self) -> str:
    return f'<Post(id={self.id}, slug="{self.slug}", published={self.published})>'
