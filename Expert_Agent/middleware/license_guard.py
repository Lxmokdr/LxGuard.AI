"""
License Guard Middleware
Sits at the FastAPI middleware layer and blocks requests when the license
is invalid, expired, or the system has been remotely disabled.

STREAMING SAFETY: Validation occurs before the request starts.
In-progress streams are never interrupted.
"""
from datetime import datetime, timezone
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Endpoints always allowed regardless of license state
WHITELISTED_PATHS = {
    "/health",
    "/license/status",
    "/admin/system",
    "/",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class LicenseGuardMiddleware(BaseHTTPMiddleware):
    """
    Checks license state before every request.
    Uses the locally cached DB state — no network call per request.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Always allow whitelisted paths
        if path in WHITELISTED_PATHS or path.startswith("/admin/system"):
            return await call_next(request)

        # Check license (reads local DB cache — fast)
        result = self._check_license()

        if result == "expired":
            return JSONResponse(
                status_code=503,
                content={"error": "license_expired", "message": "Enterprise license has expired. Contact your vendor."},
            )
        if result == "disabled":
            return JSONResponse(
                status_code=503,
                content={"error": "system_disabled", "message": "This system has been remotely disabled. Contact your vendor."},
            )
        if result == "invalid":
            return JSONResponse(
                status_code=503,
                content={"error": "system_disabled", "message": "License is invalid or could not be verified."},
            )

        # License OK — continue normally
        return await call_next(request)

    @staticmethod
    def _check_license() -> Optional[str]:
        """
        Returns None (OK) or one of: 'expired', 'disabled', 'invalid'
        Reads the locally cached `system_license_status` row.
        """
        import os
        license_key = os.environ.get("LICENSE_KEY", "")
        grace_period = int(os.environ.get("LICENSE_FAIL_GRACE_PERIOD", "86400"))

        if not license_key:
            return None   # Dev mode — no license configured, allow all

        try:
            from data.database import SessionLocal
            from api.models import SystemLicenseStatus

            db = SessionLocal()
            try:
                cached = db.query(SystemLicenseStatus).filter(
                    SystemLicenseStatus.license_key == license_key
                ).order_by(SystemLicenseStatus.last_checked.desc()).first()
            finally:
                db.close()

            if not cached:
                # No record yet (very first boot before first license check) — allow
                return None

            now = datetime.now(timezone.utc)

            # 1. Expiry check
            if cached.expires_at:
                exp = (
                    cached.expires_at.replace(tzinfo=timezone.utc)
                    if cached.expires_at.tzinfo is None
                    else cached.expires_at
                )
                if now > exp:
                    return "expired"

            # 2. Remote disable check
            if not cached.system_active:
                return "disabled"

            # 3. Validity + grace period check
            if not cached.license_valid:
                last = cached.last_checked.replace(tzinfo=timezone.utc)
                age = (now - last).total_seconds()
                if age > grace_period:
                    return "invalid"
                # Within grace period — allow with cached state

            return None   # All checks passed

        except Exception as exc:
            # DB unavailable — fail open to prevent self-induced outage
            print(f"⚠️  LicenseGuard DB read failed (fail-open): {exc}")
            return None
