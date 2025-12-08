"""
SQLAlchemy models for the application.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    """
    User model (optional cache of Firebase users).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="user")  # user, admin, professional
    opt_out_data_collection = Column(Integer, default=0) # 0=False (collect), 1=True (opt-out)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    scans = relationship("Scan", back_populates="user")

class Scan(Base):
    """
    Skin analysis scan record.
    """
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String, unique=True, index=True) # Timestamp-based ID from frontend
    image_path = Column(String) # Path to image in storage (local/S3)
    
    # Link to User via Firebase UID
    user_id = Column(String, ForeignKey("users.firebase_uid"), nullable=True)

    # Store JSON results
    skin_type_result = Column(JSON) # {type: "Oily", confidence: 90}
    skin_issues_result = Column(JSON) # [{name: "Acne", confidence: 80}]
    demographics_result = Column(JSON) # {age: "25", gender: "Female"}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="scans")
    chat_messages = relationship("ChatMessage", back_populates="scan")
    professional_label = relationship("ProfessionalLabel", back_populates="scan", uselist=False)

class ChatMessage(Base):
    """
    Chat message associated with a scan.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String, ForeignKey("scans.scan_id"), nullable=False)
    role = Column(String) # user, assistant
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    scan = relationship("Scan", back_populates="chat_messages")

class ProfessionalLabel(Base):
    """
    Expert label for a scan (for active learning).
    """
    __tablename__ = "professional_labels"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), unique=True, nullable=False)
    
    # Professional who labeled
    professional_id = Column(String)  # Professional/dermatologist ID
    
    # Corrected labels
    verified_skin_type = Column(String)
    verified_issues = Column(JSON)  # List of verified issues
    ai_was_correct = Column(Integer, default=0)  # Boolean as int: 0=False, 1=True
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    scan = relationship("Scan", back_populates="professional_label")

