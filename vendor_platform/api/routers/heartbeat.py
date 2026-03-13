"""
Heartbeat Endpoint
Enterprise instances POST metrics every 5 minutes.
Updates last_seen on the instance and appends a metrics row.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
import models

router = APIRouter()


class HeartbeatRequest(BaseModel):
    instance_id: str
    license_key: str
    system_status: str = "active"
    query_count: int = 0
    error_count: int = 0
    uptime: int = 0
    version: str = ""
    hostname: str = ""
    timestamp: int = 0


@router.post("/api/heartbeat")
def receive_heartbeat(req: HeartbeatRequest, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    # Update instance last_seen
    inst = db.query(models.Instance).filter(
        models.Instance.instance_id == req.instance_id
    ).first()
    if inst:
        inst.last_seen = now
        inst.status = "active"
        if req.hostname:
            inst.hostname = req.hostname
        if req.version:
            inst.version = req.version

    # Append metric row
    metric = models.Metric(
        instance_id=req.instance_id,
        timestamp=now,
        query_count=req.query_count,
        error_count=req.error_count,
        uptime=req.uptime,
    )
    db.add(metric)
    db.commit()

    return {"status": "ok", "received_at": now.isoformat()}
