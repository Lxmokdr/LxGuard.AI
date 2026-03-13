# Vendor Platform Guide

This guide explains how to run the vendor license management infrastructure and use the control dashboard.

---

## Overview

The vendor platform is completely separate from enterprise deployments. It consists of:

| Component | Port | Description |
|---|---|---|
| `vendor_api` | 8002 | FastAPI license server + admin API |
| `vendor_dashboard` | 4000 | Next.js control panel |
| `vendor_db` | 5435 | Dedicated PostgreSQL (never accessed by enterprises) |

---

## 1. Start the Vendor Stack

```bash
cd vendor_platform

# Set secrets (use real values in production)
export VENDOR_HMAC_SECRET="your-very-secret-hmac-key"
export VENDOR_JWT_SECRET="your-very-secret-jwt-key"

docker compose up -d --build
```

---

## 2. Create the First Admin User

```bash
curl -X POST "http://localhost:8002/admin/auth/register-first-admin?email=admin@vendor.com&password=changeme"
```

> This endpoint is locked after the first admin is created.

---

## 3. Sign In to the Dashboard

Open **http://localhost:4000** and sign in with your admin credentials.

---

## 4. Creating a License

1. Navigate to **Customers** → **Add Customer** (fill in company name + contact email)
2. Navigate to **Licenses** → select customer → set expiry date → **Create**
3. Copy the generated `license_key` — this is sent to the enterprise customer

---

## 5. Disabling a License (Remote Kill)

**Via Dashboard:**
- Go to **Licenses** → click the 🚫 (Ban) icon next to the license → confirms revocation

**Via API:**
```bash
curl -X PUT http://localhost:8002/admin/licenses/<license-id> \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "revoked"}'
```

Within one `LICENSE_CHECK_INTERVAL` (default 5 min), the enterprise instance will contact the license server, receive `system_active: false`, and start blocking requests with HTTP 503.

---

## 6. Disabling a Specific Instance

If a customer has multiple deployments and you need to disable only one:

**Via Dashboard:**
- Go to **Instances** → click **Disable** on the specific instance

**Via API:**
```bash
curl -X POST http://localhost:8002/admin/instances/<instance-id>/disable \
  -H "Authorization: Bearer <token>"
```

This revokes the associated license key, affecting the specific instance.

---

## 7. Extending a License

```bash
curl -X PUT http://localhost:8002/admin/licenses/<license-id> \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"expires_at": "2028-01-01T00:00:00"}'
```

---

## 8. Monitoring

The **Metrics** page shows:
- Query volume per instance (sparkline)
- Error count
- Average uptime

Data is updated every time an enterprise instance sends a heartbeat (every 5 minutes by default).

An instance is shown as **online** if its last heartbeat was within 10 minutes.

---

## 9. Security Notes

- The `VENDOR_HMAC_SECRET` is used to sign license responses. Enterprise instances verify this signature before trusting the response. **Never expose this secret.**
- The vendor database (`vendor_db`) runs on port 5435 and should be firewall-restricted to the vendor API container only.
- All API endpoints under `/admin/*` require a valid JWT token.
- Enterprise instances communicate only with `POST /api/license/check` and `POST /api/heartbeat` (no auth required, rate-limited by your reverse proxy).

---

## 10. Production Checklist

- [ ] Set `VENDOR_HMAC_SECRET` to a cryptographically random value (≥ 32 bytes)
- [ ] Set `VENDOR_JWT_SECRET` to a cryptographically random value
- [ ] Put `vendor_api` behind HTTPS (nginx + certbot or Cloudflare)
- [ ] Restrict `vendor_db` port 5435 to internal traffic only
- [ ] Set up PostgreSQL backups for `vendor_db`
- [ ] Configure rate limiting on `/api/license/check` and `/api/heartbeat` endpoints
