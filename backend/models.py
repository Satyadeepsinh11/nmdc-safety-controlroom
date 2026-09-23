from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="operator")
    full_name = Column(String)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_code = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    node_id = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # CRITICAL, WARNING, INFO
    description = Column(Text, nullable=False)
    status = Column(String, default="OPEN")  # OPEN, ACKNOWLEDGED, RESOLVED
    notes = Column(Text, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    module = Column(String, nullable=False)
    payload = Column(Text, nullable=True)