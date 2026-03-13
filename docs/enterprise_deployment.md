# Enterprise Deployment Guide

This guide covers how to install the AI Expert Agent platform at an enterprise customer site and activate it with a vendor-issued license.

---

## Prerequisites

- Docker & Docker Compose installed
- A license key issued by your vendor (see [Vendor Platform Guide](vendor_platform.md))
- Outbound HTTPS access to the vendor license server

---

## 1. Installation

Clone (or unzip) the project:

```bash
git clone <your-repo-url> expert-agent
cd expert-agent
```

Copy environment template:

```bash
cp Expert_Agent/.env.example Expert_Agent/.env
```

---

## 2. License Activation

Edit `Expert_Agent/.env` (or set the variables in your Docker host / secrets manager):

```env
LICENSE_KEY=<your-license-key-from-vendor>
LICENSE_SERVER_URL=https://licenses.yourvendor.com
LICENSE_PUBLIC_KEY=<hmac-secret-shared-by-vendor>

# Optional tuning
LICENSE_CHECK_INTERVAL=300       # seconds between checks (default 5 min)
LICENSE_FAIL_GRACE_PERIOD=86400  # seconds to operate without server contact (default 24h)
HEARTBEAT_INTERVAL=300           # seconds between metric reports
```

> **Note**: If `LICENSE_KEY` is not set, the system runs in **development mode** — all license checks are bypassed.

---

## 3. Start the Stack

```bash
docker compose up -d --build
```

The system will perform an immediate license verification on startup. Check the logs:

```bash
docker compose logs backend --tail=30
```

You should see:
```
🆔 New instance ID generated: <uuid>
🔑 License check completed — ✅ valid
💓 Heartbeat service started (interval: 300s)
✅ System Ready
```

---

## 4. Verify License Status

```bash
curl http://localhost:8001/license/status
```

Example response when valid:
```json
{
  "licensed": true,
  "active": true,
  "expires_at": "2027-01-01T00:00:00",
  "expired": false,
  "last_checked": "2026-03-09T22:00:00",
  "license_key_prefix": "abc12345..."
}
```

---

## 5. What Happens When a License is Revoked

When your vendor disables the license:

1. Enterprise instance contacts the server at next `LICENSE_CHECK_INTERVAL`
2. Server returns `system_active: false`
3. Local cache is updated
4. All API endpoints (except `/health`, `/license/status`) return:
   ```json
   HTTP 503
   {"error": "system_disabled", "message": "This system has been remotely disabled. Contact your vendor."}
   ```
5. **In-progress streaming responses are NOT interrupted** — only new requests are blocked

---

## 6. Grace Period

If the vendor server is temporarily unreachable, the system will continue operating using the **last cached license state** for up to `LICENSE_FAIL_GRACE_PERIOD` seconds (default: 86400 = 24 hours).

This prevents vendor-side outages from impacting enterprise operations.

---

## 7. Instance ID

A unique UUID (`/data/instance_id`) is generated on first boot and persisted to the `instance_data` Docker volume. This ID is sent with every license check and heartbeat. The vendor uses it to distinguish between multiple deployments under the same license.

---

## 8. Multi-Enterprise Isolation

Each enterprise installation is fully independent:
- Separate PostgreSQL database (`hybrid_db`)
- Separate Redis cache
- Separate Ollama LLM instance
- Separate document store

No enterprise data is ever sent to the vendor server — only:
- `instance_id`, `license_key`, `hostname`, `version`, `timestamp`
- Aggregated counters: `query_count`, `error_count`, `uptime`

---

## Ports

| Service | Port |
|---|---|
| Backend API | 8001 |
| Admin Console | 3000 |
| Chatbot UI | 5173 |
| PostgreSQL | 5434 |
| Redis | 6379 |
| Ollama | 11435 |
