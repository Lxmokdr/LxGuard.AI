# LxGuard.AI — Client Deployment Guide

**Audience:** LxGuard.AI deployment engineer  
**Time to complete:** ~30–45 minutes  
**Version:** 3.0

This is the complete, end-to-end guide for deploying LxGuard.AI at a **Linux** client site — from issuing a fresh license key on the vendor platform to verifying the system is fully operational and handing off to the client.

> 🪟 **Windows clients:** See [`DEPLOYMENT_GUIDE_WINDOWS.md`](./DEPLOYMENT_GUIDE_WINDOWS.md) for the PowerShell / Docker Desktop version.

---

## Overview

### Deployed Architecture
```
Vendor Platform (Railway)                     Client / Cloud Deployment
──────────────────────────────────────        ──────────────────────────────────────────────
https://lxguard-vendor-api-production         Expert Agent Backend
  .up.railway.app                         →     :8001
  (license checks, telemetry, admin API)   ←  heartbeat  https://lxmix-lxguard-ai.hf.space
  vendor_dashboard :4000 (local only)           admin-frontend   :3000 (local/vps)
                                                chatbot-frontend :5173 (local/vps)
                                                postgres         :5434
                                                redis            :6379
```

### On-Premise / Local-Only Fallback
```
Your Machine (Vendor Side)              Client Server (Local Backend)
─────────────────────────────           ────────────────────────────────
vendor_api       :8002           →      expert-agent-backend  :8001
vendor_dashboard :4000           ←      heartbeat + license checks
vendor_db        :5435                  admin-frontend        :3000
                                        chatbot-frontend      :5173
                                        postgres              :5434
                                        redis                 :6379
```

---

## Part 0 — System Requirements (Client Server)

Before arriving at the client site, verify the client server meets these requirements:

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Operating System | Ubuntu 22.04 / Debian 12 / RHEL 9 | Ubuntu 22.04 LTS |
| Docker | 24+ | Latest stable |
| Docker Compose | 2.20+ | Latest stable |
| RAM | 8 GB | 16 GB |
| Disk | 40 GB free | 100 GB |
| CPU | 4 cores | 8 cores |
| Network | Outbound HTTPS to vendor platform URL | — |
| Ports | 3000, 5173, 8001, 5434, 6379 open internally | — |

### Install Docker on the Client Server (if not already installed)

```bash
# Install Docker Engine
curl -fsSL https://get.docker.com | sh

# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group change without logout
newgrp docker

# Verify
docker --version
docker compose version
```

---

## Part 1 — Vendor Side: Issue a License Key

> ⚠️ **The vendor API must be publicly accessible** so that client backends can reach it for license validation.
> If you haven't deployed it yet, see **Step 1.0** below.

### Step 1.0 — Deploy the Vendor API (first time only)

The simplest option is **Render.com** (free tier, Docker-native):

1. Go to [https://render.com](https://render.com) and create a new **Web Service**
2. Connect your repo (or use **Deploy from Dockerfile**), point to `vendor_platform/api/`
3. Set the port to **8002**
4. Add these environment variables in the Render dashboard:
   ```
   VENDOR_DATABASE_URL=postgresql://...   # Render Postgres add-on URL
   VENDOR_HMAC_SECRET=your-hmac-secret
   VENDOR_JWT_SECRET=your-jwt-secret
   ```
5. After deploy, your vendor API URL will be: `https://your-service-name.onrender.com`

> Alternatively use **Railway** ([https://railway.app](https://railway.app)) or any VPS — just expose port 8002 over HTTPS.

Save your deployed URL:
```bash
export VENDOR_API_URL="https://lxguard-vendor-api-production.up.railway.app"
```

### Step 1.1 — Verify the Vendor Platform is Running

```bash
curl $VENDOR_API_URL/health
# Expected: {"status":"healthy"}
```

### Step 1.2 — Create a Vendor Admin Account (first time only)

```bash
curl -s -X POST \
  "$VENDOR_API_URL/admin/auth/register-first-admin?email=admin@lxguard.ai&password=CHANGE_THIS"
# Expected: {"status":"created","email":"admin@lxguard.ai"}
```

> ⚠️ If it returns `"Admin already exists"` — skip this step, an account already exists.

### Step 1.3 — Log In and Obtain a Vendor Admin Token

```bash
VENDOR_TOKEN=$(curl -s -X POST $VENDOR_API_URL/admin/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@lxguard.ai&password=CHANGE_THIS" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token obtained: ${VENDOR_TOKEN:0:40}..."
```

### Step 1.4 — Create a Customer Record

Replace the placeholder values with the client's real details:

```bash
CUSTOMER=$(curl -s -X POST $VENDOR_API_URL/admin/customers \
  -H "Authorization: Bearer $VENDOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Client Organisation Name",
    "contact_email": "it@clientorg.com",
    "organization_type": "enterprise"
  }')

echo "$CUSTOMER"
CUSTOMER_ID=$(echo "$CUSTOMER" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Customer ID: $CUSTOMER_ID"
```

### Step 1.5 — Issue a License Key

```bash
LICENSE=$(curl -s -X POST $VENDOR_API_URL/admin/licenses \
  -H "Authorization: Bearer $VENDOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"customer_id\": \"$CUSTOMER_ID\",
    \"max_instances\": 3,
    \"expires_at\": \"2027-12-31T23:59:59\"
  }")

echo "$LICENSE"
LICENSE_KEY=$(echo "$LICENSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['license_key'])")

echo ""
echo "========================================"
echo "  LICENSE KEY FOR CLIENT:"
echo "  $LICENSE_KEY"
echo "========================================"
```

> 📋 **Copy this `LICENSE_KEY`** — you will need it during the client-site setup.

### Step 1.6 — Verify the License Was Created

```bash
curl -s -H "Authorization: Bearer $VENDOR_TOKEN" \
  $VENDOR_API_URL/admin/licenses | \
  python3 -c "
import sys, json
for l in json.load(sys.stdin):
    print(f\"  {l['customer_name']}: {l['license_key']} | {l['status']} | expires: {l['expires_at'] or 'Never'}\")
"
```

---

## Part 2 — Client Site: Install LxGuard.AI

> ⚠️ **Do this on the client's server.**

> ⚠️ **Send only the client delivery bundle — never the full source directory.**
> Run `./scripts/build_and_push.sh --export --tag v1.0.0` on your development machine first.
> This creates `dist/client_package_v1.0.0/` containing no source files.

**Option A — Archive and copy (no internet required on client)**

On **your machine**, archive the generated client package:
```bash
# Compress the exported package contents (from the 'dist/client_package_v1.0.0' directory)
tar -czf lxguard_client_v1.0.0.tar.gz -C dist/client_package_v1.0.0 .

# Copy to client machine
scp lxguard_client_v1.0.0.tar.gz admin@CLIENT_SERVER_IP:~/
```

On the **client server**, extract and load:
```bash
mkdir -p ~/lxguard && cd ~/lxguard
tar -xzf ~/lxguard_client_v1.0.0.tar.gz

# Load the pre-built Docker images
for f in images/*.tar; do docker load -i "$f"; done
```

**Option B — Registry pull (client server has internet access)**

Run `./scripts/build_and_push.sh --tag v1.0.0` (without `--export`) to push images to your registry.
Then deliver only the configuration and guide files (no image tarballs needed):
```bash
# On your machine, compress everything EXCEPT the images folder
tar -czf lxguard_client_v1.0.0.tar.gz --exclude='images' -C dist/client_package_v1.0.0 .

# Copy to client machine
scp lxguard_client_v1.0.0.tar.gz admin@CLIENT_SERVER_IP:~/
```

On the client server:
```bash
mkdir -p ~/lxguard && cd ~/lxguard
tar -xzf ~/lxguard_client_v1.0.0.tar.gz
# Images will be automatically pulled from registry on first 'docker compose up'
```

### Step 2.2 — Configure the Environment File

```bash
cp .env.example .env
nano .env
```

Fill in the following values — **all are required for a licensed deployment**:

```env
# ── LLM Provider ──────────────────────────────────────────────────────
# Get from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=AIza...your-gemini-key-here
GEMINI_MODEL=gemini-2.0-flash

# ── Vendor License ─────────────────────────────────────────────────────
# The key you generated in Step 1.5
LICENSE_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# URL of your DEPLOYED vendor license server (must be publicly accessible)
LICENSE_SERVER_URL=https://lxguard-vendor-api-production.up.railway.app

# HMAC secret — must exactly match VENDOR_HMAC_SECRET in vendor_platform/.env
LICENSE_PUBLIC_KEY=your-shared-hmac-secret

# License check frequency in seconds (default: 300 = 5 minutes)
LICENSE_CHECK_INTERVAL=300

# Grace period if vendor server is unreachable (default: 86400 = 24 hours)
LICENSE_FAIL_GRACE_PERIOD=86400

# Telemetry heartbeat interval in seconds (default: 300)
HEARTBEAT_INTERVAL=300

# ── Database ───────────────────────────────────────────────────────────
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=hybrid
POSTGRES_PASSWORD=hybridpass
POSTGRES_DB=hybrid_db

# ── Cache ──────────────────────────────────────────────────────────────
REDIS_HOST=redis
REDIS_PORT=6379
```

> ⚠️ **Never commit `.env` to version control.**

### Step 2.3 — Start All Services

```bash
docker compose up -d
```

The first run will pull all images and build containers — this takes **3–8 minutes** depending on internet speed. Monitor progress:

```bash
docker compose logs -f --tail=30
```

Wait until you see these messages in the backend logs:
```
✅ [Startup] System Ready & Multi-Tenant State Initialized!
🔑 License check completed — ✅ valid
💓 Heartbeat service started
```

Check that all containers are running:
```bash
docker compose ps
```

Expected output:
```
NAME                     STATUS          PORTS
expert-agent-backend     healthy         0.0.0.0:8001->8001/tcp
expert-agent-admin       running         0.0.0.0:3000->3000/tcp
expert-agent-chatbot     running         0.0.0.0:5173->8080/tcp
expert-agent-db          healthy         0.0.0.0:5434->5432/tcp
expert-agent-cache       healthy         0.0.0.0:6379->6379/tcp
expert-agent-ollama      running         0.0.0.0:11435->11434/tcp
expert-agent-auth        running         0.0.0.0:8080->8080/tcp
```

### Step 2.4 — Seed Demo Users and Data

Run once after the first start:

```bash
docker exec expert-agent-backend python scripts/seed_demo_data.py
```

Expected output:
```
🌱 Seeding Demo Tenant and Domain...
  Created default tenant.
  Created default domain.
  Added user: admin
  Added user: developer
  Added user: employee
  Added user: guest
✅ Seeding completed successfully!
```

---

## Part 3 — Verify the Installation

### Step 3.1 — Run the Automated Health Check

```bash
python3 scripts/healthcheck.py
```

Expected output:
```
==============================
  LxGuard.AI — System Health Check
==============================

▶ Backend API
  ✅ PASS  Backend reachable       — HTTP 200
  ✅ PASS  API docs endpoint       — HTTP 200

▶ Admin Frontend
  ✅ PASS  Admin UI reachable      — HTTP 200

▶ Chatbot Frontend
  ✅ PASS  Chatbot UI reachable    — HTTP 200

▶ Redis
  ✅ PASS  Redis reachable         — Memory: 1.10M

▶ LLM Provider
  ✅ PASS  Gemini API live test    — Latency: 1240ms | Model: gemini-2.0-flash

▶ License & Configuration
  ✅ PASS  LICENSE_KEY configured  — Set
  ✅ PASS  Vendor license server   — HTTP 200

==============================
  Result: PASS  (8/8 checks passed)
==============================
```

### Step 3.2 — Check the System Readiness Dashboard

1. Open **http://CLIENT_SERVER_IP:3000** in your browser
2. Log in with `admin` / `admin123`
3. Navigate to **System Readiness** in the sidebar
4. Verify all cards show green status:

| Card | Expected Status |
|------|----------------|
| Database (PostgreSQL) | ✅ ok |
| Redis Cache | ✅ ok |
| LLM Provider | ✅ ok — latency shown |
| Vendor Connectivity | ✅ ok |
| Vendor License | ✅ Valid: True, Active: True |
| Telemetry Sync | ✅ Last heartbeat timestamp shown |

### Step 3.3 — Verify License Registration on Vendor Platform

Back on **your machine**, confirm the client server registered itself:

```bash
# Set your vendor API URL if not already set
export VENDOR_API_URL="https://lxguard-vendor-api-production.up.railway.app"

# Get a fresh vendor token
VENDOR_TOKEN=$(curl -s -X POST $VENDOR_API_URL/admin/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@lxguard.ai&password=CHANGE_THIS" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Check registered instances
curl -s -H "Authorization: Bearer $VENDOR_TOKEN" \
  $VENDOR_API_URL/admin/instances | \
  python3 -c "
import sys, json
for i in json.load(sys.stdin):
    print(f\"  Instance: {i['instance_id'][:16]}...  host: {i['hostname']}  online: {i['online']}\")
"
```

You should see the client server's hostname listed as `online: True`.

### Step 3.4 — Test the Chatbot

1. Open **http://CLIENT_SERVER_IP:5173**
2. Log in as `employee` / `employee123`
3. Send a test query related to a compliance document in `docs/`
4. Verify the response is grounded (shows source documents) and the Neuro-Console layers are displayed

---

## Part 4 — Demo User Accounts

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `admin` | `admin123` | Admin | Full system — rules, documents, users, audit logs, readiness |
| `developer` | `developer123` | Developer | Technical queries, integration testing |
| `employee` | `employee123` | Employee | Standard compliance queries via chatbot |
| `guest` | `guest123` | Guest | Read-only, restricted chatbot access |

> 🔐 **Change all default passwords before leaving the client site.**

To change a password:  
**Admin Console → Settings → Users → Select User → Set New Password**

---

## Part 5 — Pre-Demo Reset

Before every client demonstration, reset the system to a verified clean state:

```bash
docker exec expert-agent-backend python scripts/demo_reset.py
```

Expected output:
```
  Documents  : 37
  Chunks     : 709
  Embeddings : 709
  Retrieval  : PASS
```

---

## Part 6 — License Management Reference

All commands run **on your machine** against the vendor platform.
Make sure you have set the URL variable:
```bash
export VENDOR_API_URL="https://lxguard-vendor-api-production.up.railway.app"
```

### Check Client Telemetry

```bash
curl -s -H "Authorization: Bearer $VENDOR_TOKEN" \
  "$VENDOR_API_URL/admin/metrics?limit=10" | \
  python3 -c "
import sys, json
for m in json.load(sys.stdin):
    print(f\"  {m['timestamp'][:16]}  queries: {m['query_count']}  errors: {m['error_count']}  uptime: {m['uptime']//3600}h\")
"
```

### Revoke a License

```bash
# Get the license ID first
curl -s -H "Authorization: Bearer $VENDOR_TOKEN" \
  $VENDOR_API_URL/admin/licenses | \
  python3 -c "import sys,json; [print(l['id'], l['license_key'], l['status']) for l in json.load(sys.stdin)]"

# Revoke by ID
curl -s -X PUT "$VENDOR_API_URL/admin/licenses/LICENSE_ID_HERE" \
  -H "Authorization: Bearer $VENDOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "revoked"}'
```

The client system will detect this within `LICENSE_CHECK_INTERVAL` seconds (default 5 min) and block all non-health routes with **HTTP 402**.

### Extend License Expiry

```bash
curl -s -X PUT "$VENDOR_API_URL/admin/licenses/LICENSE_ID_HERE" \
  -H "Authorization: Bearer $VENDOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"expires_at": "2028-12-31T23:59:59"}'
```

---

## Part 7 — Troubleshooting

### License check fails after install

```bash
docker logs expert-agent-backend --tail=50 | grep -E "license|License|ERROR"
```

**Common causes:**
- `LICENSE_SERVER_URL` is not reachable from the client server — check firewall rules and that the vendor API is publicly accessible
- `LICENSE_PUBLIC_KEY` doesn't match `VENDOR_HMAC_SECRET` — must be identical on both sides
- The license key was typed incorrectly — always copy-paste from the vendor platform

### Backend won't start

```bash
docker compose logs backend --tail=50
```

Most common: `POSTGRES_HOST` not reachable. Confirm containers are on the same network:
```bash
docker network ls
docker compose ps
```

### Readiness dashboard shows LLM error

`GOOGLE_API_KEY` is missing or invalid. Test it directly:
```bash
docker exec expert-agent-backend python3 -c "
import os, google.generativeai as genai
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
r = genai.GenerativeModel('gemini-2.0-flash').generate_content('hello')
print('OK:', r.text[:50])
"
```

### Container crashes on startup

```bash
docker compose down
docker compose up -d
sleep 20
docker compose ps
python3 scripts/healthcheck.py
```

### Check all container logs at once

```bash
docker compose logs --tail=30
```

### Port already in use

```bash
sudo lsof -i :3000   # or 5173, 8001, etc.
sudo kill -9 PID
docker compose up -d
```

---

## Acceptance Sign-Off Checklist

Complete every item before handing off to the client:

```
[ ] docker compose ps          → all containers healthy / running
[ ] python3 scripts/healthcheck.py  → PASS (all checks green)
[ ] http://CLIENT_IP:3000/readiness → all dashboard cards green
[ ] Vendor platform shows instance as online
[ ] Vendor license_valid = True, system_active = True
[ ] Last heartbeat < 10 minutes ago
[ ] Gemini API live test PASS with latency shown
[ ] Admin login works (admin / new password)
[ ] Employee chatbot query returns a valid grounded answer
[ ] Neuro-Console shows all 8 layers in response
[ ] python scripts/demo_reset.py → Retrieval: PASS
[ ] All default passwords changed
[ ] Client IT contact has the Admin Console URL and admin credentials
```

---

## Service Reference

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| Backend | expert-agent-backend | 8001 | FastAPI — Core AI pipeline |
| Admin UI | expert-agent-admin | 3000 | Next.js — Admin console |
| Chatbot UI | expert-agent-chatbot | 5173 | React/Vite — Employee chatbot |
| PostgreSQL | expert-agent-db | 5434 | Database + pgvector |
| Redis | expert-agent-cache | 6379 | Cache & session store |
| Keycloak | expert-agent-auth | 8080 | Optional SSO (dev: not required) |
| Ollama | expert-agent-ollama | 11435 | Local LLM (fallback if no Gemini key) |
| Vendor API | lxguard-vendor-api | 8002 | License & telemetry server |
| Vendor DB | lxguard-vendor-db | 5435 | Vendor platform database |

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Gemini API key for LLM generation | **Yes** |
| `LICENSE_KEY` | Enterprise license key from vendor platform | **Yes (production)** |
| `LICENSE_SERVER_URL` | Vendor license server URL | **Yes (production)** |
| `LICENSE_PUBLIC_KEY` | HMAC secret (must match vendor side) | **Yes (production)** |
| `GEMINI_MODEL` | Gemini model name (default: `gemini-2.0-flash`) | No |
| `LICENSE_CHECK_INTERVAL` | Seconds between license checks (default: 300) | No |
| `LICENSE_FAIL_GRACE_PERIOD` | Grace period if server unreachable (default: 86400) | No |
| `HEARTBEAT_INTERVAL` | Telemetry interval in seconds (default: 300) | No |
| `POSTGRES_HOST` | Postgres hostname (default: `postgres`) | No |
| `REDIS_HOST` | Redis hostname (default: `redis`) | No |
