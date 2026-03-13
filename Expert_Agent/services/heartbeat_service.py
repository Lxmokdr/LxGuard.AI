"""
Heartbeat Monitoring Service
Sends system metrics to the vendor monitoring API every 5 minutes.
Failures are silent — never blocks the enterprise system.
"""
import asyncio
import os
import socket
import time
from datetime import datetime, timezone

import httpx

LICENSE_KEY: str = os.environ.get("LICENSE_KEY", "")
LICENSE_SERVER_URL: str = os.environ.get("LICENSE_SERVER_URL", "").rstrip("/")
HEARTBEAT_INTERVAL: int = int(os.environ.get("HEARTBEAT_INTERVAL", "300"))  # 5 min

VERSION = "2.0.0"

# Simple in-memory counters (incremented by the pipeline)
_query_count: int = 0
_error_count: int = 0
_start_time: float = time.time()


def increment_query():
    global _query_count
    _query_count += 1


def increment_error():
    global _error_count
    _error_count += 1


async def send_heartbeat():
    """POST metrics to vendor heartbeat endpoint. Never raises."""
    if not LICENSE_KEY or not LICENSE_SERVER_URL:
        return   # Dev mode

    from services.instance_service import get_instance_id
    try:
        payload = {
            "instance_id": get_instance_id(),
            "license_key": LICENSE_KEY,
            "system_status": "active",
            "query_count": _query_count,
            "error_count": _error_count,
            "uptime": int(time.time() - _start_time),
            "version": VERSION,
            "hostname": socket.gethostname(),
            "timestamp": int(time.time()),
        }
        async with httpx.AsyncClient(timeout=8.0) as client:
            await client.post(f"{LICENSE_SERVER_URL}/api/heartbeat", json=payload)
    except Exception as exc:
        # Heartbeat failures must never stop the system
        print(f"⚠️  Heartbeat failed (non-critical): {exc}")


async def heartbeat_loop():
    """Runs forever, sending a heartbeat every HEARTBEAT_INTERVAL seconds."""
    print(f"💓 Heartbeat service started (interval: {HEARTBEAT_INTERVAL}s)")
    # Stagger first beat to avoid thundering herd on startup
    await asyncio.sleep(30)
    while True:
        await send_heartbeat()
        await asyncio.sleep(HEARTBEAT_INTERVAL)
