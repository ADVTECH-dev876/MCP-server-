from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship
from .base import Base
import enum

class Role(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class User(AsyncAttrs, Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(Role), default=Role.VIEWER)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    project_permissions = relationship("ProjectPermission", back_populates="user")
