"""
License Client Service
Periodically contacts the vendor license server, verifies the HMAC signature,
and caches the result locally in `system_license_status`.

Grace period: if the server is unreachable within LICENSE_FAIL_GRACE_PERIOD seconds 
(default 24 h), the last cached state is used and the system keeps running.
"""
import os
import asyncio
import hashlib
import hmac
import socket
import time
from datetime import datetime, timezone
from typing import Optional

import httpx

from data.database import SessionLocal

# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------
LICENSE_KEY: str = os.environ.get("LICENSE_KEY", "")
LICENSE_SERVER_URL: str = os.environ.get("LICENSE_SERVER_URL", "").rstrip("/")
LICENSE_PUBLIC_KEY: str = os.environ.get("LICENSE_PUBLIC_KEY", "")   # HMAC secret
LICENSE_CHECK_INTERVAL: int = int(os.environ.get("LICENSE_CHECK_INTERVAL", "300"))
LICENSE_FAIL_GRACE_PERIOD: int = int(os.environ.get("LICENSE_FAIL_GRACE_PERIOD", "86400"))

VERSION = "2.0.0"


# ---------------------------------------------------------------------------
# Signature verification
# ---------------------------------------------------------------------------

def _verify_signature(payload: dict, signature: str) -> bool:
    """Verify the vendor HMAC-SHA256 signature on the license response."""
    if not LICENSE_PUBLIC_KEY:
        # No key configured — skip verification (dev mode)
        return True
    
    # Handle the fact that 'expires_at' can be None in JSON, which needs to be "" for canonical string
    exp = payload.get('expires_at') or ""
    valid = payload.get('valid')
    active = payload.get('system_active')
    
    canonical = f"{valid}:{active}:{exp}"
    expected = hmac.new(
        LICENSE_PUBLIC_KEY.encode(),
        canonical.encode(),
        hashlib.sha256,
    ).hexdigest()
    
    result = hmac.compare_digest(expected, signature or "")
    if not result:
        print(f"🔑 [Signature] Verification FAILED.", flush=True)
        print(f"   - Canonical string used: '{canonical}'", flush=True)
        # Never log the full secret, but we can log that it exists
        print(f"   - Secret configured: {'YES' if LICENSE_PUBLIC_KEY else 'NO'}", flush=True)
        
    return result


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _get_cached_status():
    """Return the most recent SystemLicenseStatus row, or None."""
    from api.models import SystemLicenseStatus
    db = SessionLocal()
    try:
        return db.query(SystemLicenseStatus).order_by(
            SystemLicenseStatus.last_checked.desc()
        ).first()
    finally:
        db.close()


def _save_status(
    license_key: str,
    valid: bool,
    active: bool,
    expires_at: Optional[datetime],
    signature: str,
):
    from api.models import SystemLicenseStatus
    db = SessionLocal()
    try:
        row = db.query(SystemLicenseStatus).filter(
            SystemLicenseStatus.license_key == license_key
        ).first()
        if row:
            row.last_checked = datetime.now(timezone.utc)
            row.license_valid = valid
            row.system_active = active
            row.expires_at = expires_at
            row.server_signature = signature
        else:
            row = SystemLicenseStatus(
                license_key=license_key,
                last_checked=datetime.now(timezone.utc),
                license_valid=valid,
                system_active=active,
                expires_at=expires_at,
                server_signature=signature,
            )
            db.add(row)
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# License check
# ---------------------------------------------------------------------------

async def check_license_once() -> bool:
    """
    Contact vendor server, verify response, update local cache.
    Returns True if license is valid and active.
    """
    if not LICENSE_KEY or not LICENSE_SERVER_URL:
        print("⚠️  LICENSE_KEY or LICENSE_SERVER_URL not set — license check skipped.")
        return True   # Dev mode: allow everything

    from services.instance_service import get_instance_id
    instance_id = get_instance_id()

    payload = {
        "license_key": LICENSE_KEY,
        "instance_id": instance_id,
        "hostname": socket.gethostname(),
        "version": VERSION,
        "timestamp": int(time.time()),
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{LICENSE_SERVER_URL}/api/license/check",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        valid: bool = data.get("valid", False)
        active: bool = data.get("system_active", True)
        expires_str: Optional[str] = data.get("expires_at")
        signature: str = data.get("signature", "")

        # Verify vendor signature
        if not _verify_signature(data, signature):
            print("❌ License signature verification FAILED — treating as invalid.")
            valid = False

        expires_at: Optional[datetime] = None
        if expires_str:
            try:
                expires_at = datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
            except ValueError:
                pass

        _save_status(LICENSE_KEY, valid, active, expires_at, signature)
        status = "✅ valid" if valid and active else "🚫 invalid/disabled"
        print(f"🔑 License check completed — {status}")
        return valid and active

    except Exception as exc:
        print(f"⚠️  License server unreachable: {exc}")
        print(f"  └─ Attempted URL: {LICENSE_SERVER_URL}/api/license/check")
        # Use cached state + grace period
        cached = _get_cached_status()
        if cached:
            age = (datetime.now(timezone.utc) - cached.last_checked.replace(tzinfo=timezone.utc)).total_seconds()
            if age <= LICENSE_FAIL_GRACE_PERIOD:
                print(f"  └─ Grace period active ({int(age)}s / {LICENSE_FAIL_GRACE_PERIOD}s) — using cached state (Valid: {cached.license_valid}, Active: {cached.system_active}).")
                return cached.license_valid and cached.system_active
        print("  └─ No valid cache or grace period exceeded — marking license as invalid.")
        return False


# ---------------------------------------------------------------------------
# Background task loop
# ---------------------------------------------------------------------------

async def license_check_loop():
    """Runs forever, checking license periodically."""
    # Short initial sleep to allow server to fully start
    await asyncio.sleep(2)
    
    interval = int(os.environ.get("LICENSE_CHECK_INTERVAL", "300"))
    print(f"🔑 [Background] License service loop STARTING. (Check Interval: {interval}s)", flush=True)
    print(f"   - Server URL: {LICENSE_SERVER_URL}", flush=True)

    while True:
        try:
            print(f"\n🔑 [Background] Starting scheduled license check at {datetime.now().strftime('%H:%M:%S')}...", flush=True)
            status = await check_license_once()
            print(f"🔑 [Background] Check result: {'✅ Valid' if status else '🚫 Invalid/Disabled'}", flush=True)
        except Exception as exc:
            print(f"❌ [Background] Unexpected error in license loop: {exc}", flush=True)
            import traceback
            traceback.print_exc()
        
        interval = int(os.environ.get("LICENSE_CHECK_INTERVAL", "300"))
        await asyncio.sleep(interval)


def is_license_valid() -> bool:
    """
    Synchronous check for use in middleware.
    Reads the locally cached DB state — does NOT make a network call.
    """
    if not LICENSE_KEY:
        return True   # Dev mode

    cached = _get_cached_status()
    if not cached:
        return True   # No record yet (first boot before first check) — allow

    now = datetime.now(timezone.utc)

    # Expire check
    if cached.expires_at:
        exp = cached.expires_at.replace(tzinfo=timezone.utc) if cached.expires_at.tzinfo is None else cached.expires_at
        if now > exp:
            return False

    # Grace period check (server unreachable case)
    age = (now - cached.last_checked.replace(tzinfo=timezone.utc)).total_seconds()
    if not cached.license_valid and age > LICENSE_FAIL_GRACE_PERIOD:
        return False

    return cached.license_valid and cached.system_active
