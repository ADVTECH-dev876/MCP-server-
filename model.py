from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship
from .base import Base
from .user import Role
import datetime

class Project(AsyncAttrs, Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    storage_path = Column(String)  # Relative path under upload_dir
    
    # Relationships
    permissions = relationship("ProjectPermission", back_populates="project")
    uploads = relationship("Upload", back_populates="project")

class ProjectPermission(AsyncAttrs, Base):
    __tablename__ = "project_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    role = Column(Enum(Role))
    
    # Relationships
    user = relationship("User", back_populates="project_permissions")
    project = relationship("Project", back_populates="permissions")
