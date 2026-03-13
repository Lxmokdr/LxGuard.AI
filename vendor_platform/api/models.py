"""
Vendor Platform ORM Models
Completely separate from enterprise PostgreSQL.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from database import Base


def _uuid():
    return str(uuid.uuid4())


class Customer(Base):
    __tablename__ = "customers"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    organization_type = Column(String, default="enterprise")
    created_at = Column(DateTime, default=datetime.utcnow)
    licenses = relationship("License", back_populates="customer")


class License(Base):
    __tablename__ = "licenses"
    id = Column(String, primary_key=True, default=_uuid)
    license_key = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("customers.id"))
    status = Column(String, default="active")   # active | revoked | expired
    expires_at = Column(DateTime, nullable=True)
    max_instances = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship("Customer", back_populates="licenses")
    instances = relationship("Instance", back_populates="license")


class Instance(Base):
    __tablename__ = "instances"
    id = Column(String, primary_key=True, default=_uuid)
    instance_id = Column(String, unique=True, nullable=False)
    license_key = Column(String, ForeignKey("licenses.license_key"))
    hostname = Column(String)
    version = Column(String)
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")   # active | offline | disabled
    license = relationship("License", back_populates="instances")
    metrics = relationship("Metric", back_populates="instance")


class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    instance_id = Column(String, ForeignKey("instances.instance_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    query_count = Column(BigInteger, default=0)
    error_count = Column(BigInteger, default=0)
    uptime = Column(BigInteger, default=0)   # seconds
    instance = relationship("Instance", back_populates="metrics")


class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(String, primary_key=True, default=_uuid)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="admin")   # admin | viewer
    created_at = Column(DateTime, default=datetime.utcnow)
