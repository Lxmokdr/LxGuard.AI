"""
Vendor Admin API
CRUD for customers, licenses, and instances.
All endpoints require vendor admin JWT.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_admin, hash_password, create_access_token, verify_password
from fastapi.security import OAuth2PasswordRequestForm
import models

router = APIRouter(prefix="/admin")


# ── Auth ────────────────────────────────────────────────────────────────────

@router.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.AdminUser).filter(models.AdminUser.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/register-first-admin")
def register_first_admin(email: str, password: str, db: Session = Depends(get_db)):
    """One-time setup: create first admin if none exist."""
    if db.query(models.AdminUser).count() > 0:
        raise HTTPException(status_code=403, detail="Admin already exists")
    user = models.AdminUser(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    return {"status": "created", "email": email}


# ── Customers ───────────────────────────────────────────────────────────────

class CustomerCreate(BaseModel):
    name: str
    contact_email: str
    organization_type: str = "enterprise"


@router.get("/customers")
def list_customers(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    customers = db.query(models.Customer).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "contact_email": c.contact_email,
            "organization_type": c.organization_type,
            "created_at": c.created_at.isoformat(),
            "license_count": len(c.licenses),
        }
        for c in customers
    ]


@router.post("/customers")
def create_customer(body: CustomerCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    customer = models.Customer(**body.dict())
    db.add(customer)
    db.commit()
    return {"id": customer.id, "name": customer.name}


@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: str, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    c = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(c)
    db.commit()
    return {"status": "deleted"}


# ── Licenses ────────────────────────────────────────────────────────────────

class LicenseCreate(BaseModel):
    customer_id: str
    expires_at: Optional[str] = None
    max_instances: int = 3


class LicenseUpdate(BaseModel):
    status: Optional[str] = None          # active | revoked
    expires_at: Optional[str] = None
    max_instances: Optional[int] = None


@router.get("/licenses")
def list_licenses(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    licenses = db.query(models.License).all()
    return [
        {
            "id": l.id,
            "license_key": l.license_key,
            "customer_id": l.customer_id,
            "customer_name": l.customer.name if l.customer else None,
            "status": l.status,
            "expires_at": l.expires_at.isoformat() if l.expires_at else None,
            "max_instances": l.max_instances,
            "instance_count": len(l.instances),
            "created_at": l.created_at.isoformat(),
        }
        for l in licenses
    ]


@router.post("/licenses")
def create_license(body: LicenseCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    expires_at = datetime.fromisoformat(body.expires_at) if body.expires_at else None
    lic = models.License(
        customer_id=body.customer_id,
        expires_at=expires_at,
        max_instances=body.max_instances,
    )
    db.add(lic)
    db.commit()
    return {"id": lic.id, "license_key": lic.license_key, "status": lic.status}


@router.put("/licenses/{license_id}")
def update_license(license_id: str, body: LicenseUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    lic = db.query(models.License).filter(models.License.id == license_id).first()
    if not lic:
        raise HTTPException(status_code=404, detail="License not found")
    if body.status:
        lic.status = body.status
    if body.expires_at:
        lic.expires_at = datetime.fromisoformat(body.expires_at)
    if body.max_instances is not None:
        lic.max_instances = body.max_instances
    db.commit()
    return {"status": "updated", "license_key": lic.license_key, "new_status": lic.status}


@router.delete("/licenses/{license_id}")
def delete_license(license_id: str, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    lic = db.query(models.License).filter(models.License.id == license_id).first()
    if not lic:
        raise HTTPException(status_code=404, detail="License not found")
    db.delete(lic)
    db.commit()
    return {"status": "deleted"}


# ── Instances ───────────────────────────────────────────────────────────────

@router.get("/instances")
def list_instances(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    instances = db.query(models.Instance).all()
    now = datetime.now(timezone.utc)
    return [
        {
            "id": i.id,
            "instance_id": i.instance_id,
            "license_key": i.license_key,
            "hostname": i.hostname,
            "version": i.version,
            "last_seen": i.last_seen.isoformat() if i.last_seen else None,
            "status": i.status,
            "online": (now - i.last_seen.replace(tzinfo=timezone.utc)).total_seconds() < 600 if i.last_seen else False,
        }
        for i in instances
    ]


@router.post("/instances/{instance_id}/disable")
def disable_instance(instance_id: str, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    """Disable a specific instance by revoking its license."""
    inst = db.query(models.Instance).filter(models.Instance.instance_id == instance_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    lic = db.query(models.License).filter(models.License.license_key == inst.license_key).first()
    if lic:
        lic.status = "revoked"
    inst.status = "disabled"
    db.commit()
    return {"status": "disabled", "instance_id": instance_id}


# ── Metrics ─────────────────────────────────────────────────────────────────

@router.get("/metrics")
def get_metrics(instance_id: Optional[str] = None, limit: int = 100, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    q = db.query(models.Metric)
    if instance_id:
        q = q.filter(models.Metric.instance_id == instance_id)
    rows = q.order_by(models.Metric.timestamp.desc()).limit(limit).all()
    return [
        {
            "instance_id": r.instance_id,
            "timestamp": r.timestamp.isoformat(),
            "query_count": r.query_count,
            "error_count": r.error_count,
            "uptime": r.uptime,
        }
        for r in rows
    ]


# ── Dashboard Stats ──────────────────────────────────────────────────────────

@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    now = datetime.now(timezone.utc)
    total_customers = db.query(models.Customer).count()
    active_licenses = db.query(models.License).filter(models.License.status == "active").count()
    total_instances = db.query(models.Instance).count()
    online_instances = sum(
        1 for i in db.query(models.Instance).all()
        if i.last_seen and (now - i.last_seen.replace(tzinfo=timezone.utc)).total_seconds() < 600
    )
    return {
        "total_customers": total_customers,
        "active_licenses": active_licenses,
        "total_instances": total_instances,
        "online_instances": online_instances,
    }
