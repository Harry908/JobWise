"""Database models."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Float, JSON
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UserModel(Base):
    """User database model."""
    __tablename__ = "users"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MasterProfileModel(Base):
    """Master profile database model."""
    __tablename__ = "master_profiles"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)

    # Personal info stored as JSON
    personal_info = Column(JSON, nullable=False)

    # Professional summary
    professional_summary = Column(Text)

    # Skills stored as JSON (technical, soft, languages, certifications)
    skills = Column(JSON, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", backref="profiles")
    experiences = relationship("ExperienceModel", backref="profile", cascade="all, delete-orphan")
    education = relationship("EducationModel", backref="profile", cascade="all, delete-orphan")
    projects = relationship("ProjectModel", backref="profile", cascade="all, delete-orphan")


class ExperienceModel(Base):
    """Work experience database model."""
    __tablename__ = "experiences"

    id = Column(String, primary_key=True)  # UUID as string
    profile_id = Column(String, ForeignKey("master_profiles.id"), nullable=False, index=True)

    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    start_date = Column(String, nullable=False)  # ISO date string
    end_date = Column(String)  # ISO date string, null for current
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    achievements = Column(JSON)  # List of achievement strings


class EducationModel(Base):
    """Education database model."""
    __tablename__ = "education"

    id = Column(String, primary_key=True)  # UUID as string
    profile_id = Column(String, ForeignKey("master_profiles.id"), nullable=False, index=True)

    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    field_of_study = Column(String, nullable=False)
    start_date = Column(String, nullable=False)  # ISO date string
    end_date = Column(String, nullable=False)  # ISO date string
    gpa = Column(Float)
    honors = Column(JSON)  # List of honor strings


class ProjectModel(Base):
    """Project database model."""
    __tablename__ = "projects"

    id = Column(String, primary_key=True)  # UUID as string
    profile_id = Column(String, ForeignKey("master_profiles.id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    technologies = Column(JSON)  # List of technology strings
    url = Column(String)
    start_date = Column(String, nullable=False)  # ISO date string
    end_date = Column(String)  # ISO date string