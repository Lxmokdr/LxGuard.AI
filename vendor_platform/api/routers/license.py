"""
License Check Endpoint
Enterprise installations POST here every LICENSE_CHECK_INTERVAL seconds.
Response is HMAC-signed so enterprise instances can verify authenticity.
"""
import hashlib
import hmac
import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends

from database import get_db
import models

router = APIRouter()

HMAC_SECRET = os.environ.get("VENDOR_HMAC_SECRET", "change-me-vendor-hmac-secret")


class LicenseCheckRequest(BaseModel):
    license_key: str
    instance_id: str
    hostname: str
    version: str
    timestamp: int


def _sign_response(valid: bool, active: bool, expires_at: str) -> str:
    canonical = f"{valid}:{active}:{expires_at}"
    return hmac.new(HMAC_SECRET.encode(), canonical.encode(), hashlib.sha256).hexdigest()


@router.post("/api/license/check")
def check_license(req: LicenseCheckRequest, db: Session = Depends(get_db)):
    """Validate enterprise license and return signed response."""
    license = db.query(models.License).filter(
        models.License.license_key == req.license_key
    ).first()

    if not license:
        return {
            "valid": False,
            "system_active": False,
            "expires_at": None,
            "signature": _sign_response(False, False, ""),
        }

    now = datetime.now(timezone.utc)
    valid = license.status == "active"
    active = license.status != "revoked"
    expired = False
    expires_str = ""

    if license.expires_at:
        exp = license.expires_at.replace(tzinfo=timezone.utc) if license.expires_at.tzinfo is None else license.expires_at
        if now > exp:
            valid = False
            expired = True
        expires_str = license.expires_at.isoformat()

    # Upsert instance record
    inst = db.query(models.Instance).filter(
        models.Instance.instance_id == req.instance_id
    ).first()
    if inst:
        inst.last_seen = now
        inst.hostname = req.hostname
        inst.version = req.version
        inst.status = "active" if valid else "disabled"
    else:
        # Check max_instances
        current_count = db.query(models.Instance).filter(
            models.Instance.license_key == req.license_key
        ).count()
        if current_count >= license.max_instances:
            valid = False
            active = False
        else:
            inst = models.Instance(
                instance_id=req.instance_id,
                license_key=req.license_key,
                hostname=req.hostname,
                version=req.version,
                last_seen=now,
                status="active" if valid else "disabled",
            )
            db.add(inst)

    db.commit()

    return {
        "valid": valid,
        "system_active": active and not expired,
        "expires_at": expires_str or None,
        "signature": _sign_response(valid, active and not expired, expires_str),
    }
