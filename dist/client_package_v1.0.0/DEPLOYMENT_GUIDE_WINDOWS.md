# LxGuard.AI — Client Deployment Guide (Windows)

**Audience:** LxGuard.AI deployment engineer  
**Platform:** Windows 10 Pro / Windows 11 Pro / Windows Server 2019+  
**Time to complete:** ~45–60 minutes  
**Version:** 3.0

This is the complete, end-to-end guide for deploying LxGuard.AI at a **Windows** client site — from issuing a fresh license key on the vendor platform to verifying the system is fully operational.

> 📌 **Linux/macOS users:** See [`DEPLOYMENT_GUIDE.md`](./DEPLOYMENT_GUIDE.md)

---

## Overview

### Deployed Architecture
```
Vendor Platform (Railway)                      Client / Cloud Deployment
───────────────────────────────────────        ──────────────────────────────────────────────
https://lxguard-vendor-api-production          Expert Agent Backend
  .up.railway.app                          →     :8001
  (license checks, telemetry, admin API)   ←  heartbeat  https://lxmix-lxguard-ai.hf.space
  vendor_dashboard :4000 (local only)           admin-frontend   :3000 (local/vps)
                                                chatbot-frontend :5173 (local/vps)
                                                postgres         :5434
                                                redis            :6379
```

### On-Premise / Local-Only Fallback
```
Your Machine (Vendor Side)              Client Windows Server (Local Backend)
─────────────────────────────           ─────────────────────────────────────
vendor_api       :8002           →      expert-agent-backend  :8001
vendor_dashboard :4000           ←      heartbeat + license checks
vendor_db        :5435                  admin-frontend        :3000
                                        chatbot-frontend      :5173
                                        postgres              :5434
                                        redis                 :6379
```

All commands below are written for **PowerShell** (run as Administrator) unless stated otherwise.

---

## Part 0 — System Requirements (Client Windows Machine)

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Operating System | Windows 10 Pro (21H2+) | Windows 11 Pro / Server 2022 |
| Architecture | 64-bit (x86_64) | 64-bit |
| RAM | 8 GB | 16 GB |
| Disk | 40 GB free | 100 GB SSD |
| CPU | 4 cores | 8 cores |
| Virtualisation | Enabled in BIOS/UEFI | — |
| Docker Desktop | 4.20+ | Latest stable |
| WSL 2 | Enabled | — |
| Network | Outbound HTTPS to vendor platform URL | — |
| Ports | 3000, 5173, 8001, 5434, 6379 open internally | — |

> ⚠️ **Home editions of Windows (Home) are NOT supported.** Docker Desktop requires Windows Pro, Enterprise, or Education.

---

## Part 0.1 — Install Prerequisites on the Client Machine

### Step A — Enable WSL 2

Open **PowerShell as Administrator** and run:

```powershell
# Enable WSL and Virtual Machine Platform features
wsl --install

# If WSL is already installed, just set version to 2
wsl --set-default-version 2
```

Restart the computer when prompted.

After restart, open PowerShell again and verify:
```powershell
wsl --status
# Should show: Default Version: 2
```

### Step B — Install Docker Desktop

1. Download Docker Desktop for Windows from: **https://www.docker.com/products/docker-desktop/**
2. Run the installer — accept all defaults, ensure **"Use WSL 2 instead of Hyper-V"** is checked
3. After installation, launch **Docker Desktop** from the Start Menu
4. Wait for Docker to start (the whale icon in the system tray must be green/still)

Verify in PowerShell:
```powershell
docker --version
# Expected: Docker version 24.x.x or higher

docker compose version
# Expected: Docker Compose version v2.x.x or higher
```

### Step C — Install Python 3 (for running healthcheck scripts)

1. Download Python 3.11+ from: **https://www.python.org/downloads/**
2. Run the installer — ✅ **Check "Add Python to PATH"** on the first screen
3. Click **"Install Now"**

Verify in a new PowerShell window:
```powershell
python --version
# Expected: Python 3.11.x or higher

pip --version
```

Install the `requests` library used by healthcheck scripts:
```powershell
pip install requests
```

### Step D — Install curl (built-in on Windows 10+)

```powershell
curl --version
# Should already be available. If not, install via winget:
winget install curl.curl
```

---

## Part 1 — Vendor Side: Issue a License Key

> ⚠️ **The vendor API must be publicly accessible** so that client backends can reach it for license validation.
> If you haven't deployed it yet, see **Step 1.0** below.

### Step 1.0 — Deploy the Vendor API (first time only)

The simplest option is **Render.com** (free tier, Docker-native):

1. Go to [https://render.com](https://render.com) → **New Web Service**
2. Connect your repo and point the root to `vendor_platform/api/`
3. Set the port to **8002**
4. Add environment variables in the Render dashboard:
   ```
   VENDOR_DATABASE_URL=postgresql://...   # Render Postgres add-on URL
   VENDOR_HMAC_SECRET=your-hmac-secret
   VENDOR_JWT_SECRET=your-jwt-secret
   ```
5. After deploy your vendor API URL will be: `https://your-service-name.onrender.com`

> Alternatively use **Railway** ([https://railway.app](https://railway.app)) or any VPS.

Save your deployed URL as a variable for all commands below:
```powershell
$VENDOR_API_URL = "https://lxguard-vendor-api-production.up.railway.app"
```

### Step 1.1 — Verify the Vendor Platform is Running

```powershell
Invoke-RestMethod -Uri "$VENDOR_API_URL/health"
# Expected: @{status=healthy}
```

### Step 1.2 — Create a Vendor Admin Account (first time only)

```powershell
# Using Invoke-RestMethod (native PowerShell):
Invoke-RestMethod -Method Post -Uri "$VENDOR_API_URL/admin/auth/register-first-admin?email=admin@lxguard.ai&password=CHANGE_THIS"
# Expected: @{status=created, email=admin@lxguard.ai}

# Alternatively, if you have curl.exe installed:
# curl.exe -s -X POST "$VENDOR_API_URL/admin/auth/register-first-admin?email=admin@lxguard.ai&password=CHANGE_THIS"
```

> ⚠️ If it returns `"Admin already exists"` — skip this step.

### Step 1.3 — Log In and Obtain a Vendor Admin Token

```powershell
# Get the token and save it to a variable
$response = Invoke-RestMethod -Method Post -Uri "$VENDOR_API_URL/admin/auth/login" `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "username=admin@lxguard.ai&password=CHANGE_THIS"

$VENDOR_TOKEN = $response.access_token
Write-Host "Token obtained: $($VENDOR_TOKEN.Substring(0, 40))..."
```

### Step 1.4 — Create a Customer Record

```powershell
$customerBody = @{
    name = "Client Organisation Name"
    contact_email = "it@clientorg.com"
    organization_type = "enterprise"
} | ConvertTo-Json

$customer = Invoke-RestMethod -Method Post -Uri "$VENDOR_API_URL/admin/customers" `
  -Headers @{ Authorization = "Bearer $VENDOR_TOKEN" } `
  -ContentType "application/json" `
  -Body $customerBody

$CUSTOMER_ID = $customer.id
Write-Host "Customer ID: $CUSTOMER_ID"
```

### Step 1.5 — Issue a License Key

```powershell
$licenseBody = @{
    customer_id = $CUSTOMER_ID
    max_instances = 3
    expires_at = "2027-12-31T23:59:59"
} | ConvertTo-Json

$license = Invoke-RestMethod -Method Post -Uri "$VENDOR_API_URL/admin/licenses" `
  -Headers @{ Authorization = "Bearer $VENDOR_TOKEN" } `
  -ContentType "application/json" `
  -Body $licenseBody

$LICENSE_KEY = $license.license_key

Write-Host ""
Write-Host "========================================"
Write-Host "  LICENSE KEY FOR CLIENT:"
Write-Host "  $LICENSE_KEY"
Write-Host "========================================"
```

> 📋 **Copy this `LICENSE_KEY`** — you will need it during the client-site setup.

### Step 1.6 — Verify the License Was Created

```powershell
$licenses = Invoke-RestMethod -Uri "$VENDOR_API_URL/admin/licenses" `
  -Headers @{ Authorization = "Bearer $VENDOR_TOKEN" }

foreach ($l in $licenses) {
    Write-Host "  $($l.customer_name): $($l.license_key) | $($l.status) | expires: $($l.expires_at)"
}
```

---

## Part 2 — Client Site: Install LxGuard.AI

> ⚠️ **Do this on the client's Windows machine.** All PowerShell commands must be run **as Administrator**.

### Step 2.1 — Transfer the Package

> ⚠️ **Send only the client delivery bundle — never the full source directory.**
> Run `./scripts/build_and_push.sh --export --tag v1.0.0` on your Linux/WSL machine first.
> This creates `dist/client_package_v1.0.0/` containing only:
> - `docker-compose.yml` (uses pre-built images, no source)
> - `.env.example`
> - `DEPLOYMENT_GUIDE.md`, `DEPLOYMENT_GUIDE_WINDOWS.md`, `PILOT_GUIDE.md`
> - `images/` — exported Docker image tarballs

**Option A — USB drive / file share (no internet required)**

On **your machine** (after running `build_and_push.sh --export`), zip only the client package:
```powershell
# On YOUR machine in WSL or Git Bash:
# ./scripts/build_and_push.sh --export --tag v1.0.0
# Then zip the output:
$source = "C:\path\to\projet\dist\client_package_v1.0.0"
$dest   = "C:\Users\YourUser\Desktop\lxguard_client_v1.0.0.zip"

Compress-Archive -Path "$source\*" -DestinationPath $dest -CompressionLevel Optimal

# Copy to USB or network share
Copy-Item $dest "E:\lxguard_client_v1.0.0.zip"
```

On the **client machine**, extract and import the images:
```powershell
# Open PowerShell as Administrator
New-Item -ItemType Directory -Path C:\lxguard -Force
Expand-Archive -Path "E:\lxguard_client_v1.0.0.zip" -DestinationPath "C:\lxguard"
cd C:\lxguard

# Load the pre-built Docker images
Get-ChildItem .\images\*.tar | ForEach-Object { docker load -i $_.FullName }
```

**Option B — Registry pull (client machine has internet access)**

Run `./scripts/build_and_push.sh --tag v1.0.0` (without `--export`) to push images to your registry.
Then deliver only the small text bundle (no image tarballs needed):
```powershell
# Share just the config files — images are pulled automatically on first 'docker compose up'
$source = "C:\path\to\projet\dist\client_package_v1.0.0"
# Copy everything EXCEPT the images/ folder
$dest = "E:\lxguard_client_v1.0.0"
New-Item -ItemType Directory -Path $dest -Force
Get-ChildItem $source -Exclude images | Copy-Item -Destination $dest -Recurse
```

### Step 2.2 — Configure the Environment File

```powershell
# Copy the template
Copy-Item .env.example .env

# Open in Notepad to edit
notepad .env
```

Fill in the following values:

```env
# ── LLM Provider ──────────────────────────────────────────────────────
# Get from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=AIza...your-gemini-key-here
GEMINI_MODEL=gemini-2.0-flash

# ── Vendor License ─────────────────────────────────────────────────────
# The key you generated in Step 1.5
LICENSE_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# URL where the vendor license server is reachable FROM this client machine
# URL of your DEPLOYED vendor license server (must be publicly accessible)
LICENSE_SERVER_URL=https://lxguard-vendor-api-production.up.railway.app

# HMAC secret — must exactly match VENDOR_HMAC_SECRET in vendor_platform/.env
LICENSE_PUBLIC_KEY=your-shared-hmac-secret

LICENSE_CHECK_INTERVAL=300
LICENSE_FAIL_GRACE_PERIOD=86400
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

> ⚠️ **Save the file.** Never commit `.env` to version control.

### Step 2.3 — Start All Services

Make sure **Docker Desktop is running** (check the taskbar — the whale icon should be green and not animating).

```powershell
docker compose up -d
```

The first run pulls images and builds containers — this takes **5–10 minutes** on Windows. Watch progress:

```powershell
docker compose logs -f --tail=30
```

Wait until you see in the logs:
```
✅ [Startup] System Ready & Multi-Tenant State Initialized!
🔑 License check completed — ✅ valid
💓 Heartbeat service started
```

Check all containers are running:
```powershell
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

```powershell
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

```powershell
python scripts\healthcheck.py
```

Expected output — all items must show `✅ PASS`:
```
==============================
  LxGuard.AI — System Health Check
==============================
▶ Backend API
  ✅ PASS  Backend reachable       — HTTP 200
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

1. Open a browser and go to **http://localhost:3000**
2. Log in with `admin` / `admin123`
3. Navigate to **System Readiness** in the sidebar
4. Verify all cards are green:

| Card | Expected Status |
|------|----------------|
| Database (PostgreSQL) | ✅ ok |
| Redis Cache | ✅ ok |
| LLM Provider | ✅ ok — latency shown |
| Vendor Connectivity | ✅ ok |
| Vendor License | ✅ Valid: True, Active: True |
| Telemetry Sync | ✅ Last heartbeat timestamp shown |

### Step 3.3 — Verify License Registration on Vendor Platform

Back on **your machine**:

```powershell
# Set your vendor API URL if not already set
$VENDOR_API_URL = "https://lxguard-vendor-api-production.up.railway.app"

# Get a fresh token
$response = Invoke-RestMethod -Method Post -Uri "$VENDOR_API_URL/admin/auth/login" `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "username=admin@lxguard.ai&password=CHANGE_THIS"
$VENDOR_TOKEN = $response.access_token

# Check registered instances
$instances = Invoke-RestMethod -Uri "$VENDOR_API_URL/admin/instances" `
  -Headers @{ Authorization = "Bearer $VENDOR_TOKEN" }

foreach ($i in $instances) {
    Write-Host "  Instance: $($i.instance_id.Substring(0,16))...  host: $($i.hostname)  online: $($i.online)"
}
```

You should see the client machine's hostname listed with `online: True`.

### Step 3.4 — Test the Chatbot

1. Open a browser and go to **http://localhost:5173**
2. Log in as `employee` / `employee123`
3. Send a test compliance query
4. Verify the response shows source documents and the Neuro-Console layers

---

## Part 4 — Demo User Accounts

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `admin` | `admin123` | Admin | Full system — rules, documents, users, audit logs |
| `developer` | `developer123` | Developer | Technical queries, integration testing |
| `employee` | `employee123` | Employee | Standard compliance queries via chatbot |
| `guest` | `guest123` | Guest | Read-only, restricted access |

> 🔐 **Change all default passwords before leaving the client site.**  
> Admin Console → Settings → Users → Select User → Set New Password

---

## Part 5 — Pre-Demo Reset

Before every client demonstration:

```powershell
docker exec expert-agent-backend python scripts/demo_reset.py
```

Expected:
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
```powershell
$VENDOR_API_URL = "https://lxguard-vendor-api-production.up.railway.app"
```

### Check Client Telemetry

```powershell
$metrics = Invoke-RestMethod -Uri "$VENDOR_API_URL/admin/metrics?limit=10" `
  -Headers @{ Authorization = "Bearer $VENDOR_TOKEN" }

foreach ($m in $metrics) {
    Write-Host "  $($m.timestamp.Substring(0,16))  queries: $($m.query_count)  errors: $($m.error_count)  uptime: $([math]::Floor($m.uptime/3600))h"
}
```

### Revoke a License

```powershell
# List licenses to get the ID
$licenses = Invoke-RestMethod -Uri "$VENDOR_API_URL/admin/licenses" `
  -Headers @{ Authorization = "Bearer $VENDOR_TOKEN" }
$licenses | Select-Object id, license_key, status | Format-Table

# Revoke by ID
Invoke-RestMethod -Method Put -Uri "$VENDOR_API_URL/admin/licenses/LICENSE_ID_HERE" `
  -Headers @{ Authorization = "Bearer $VENDOR_TOKEN" } `
  -ContentType "application/json" `
  -Body '{"status": "revoked"}'
```

### Extend License Expiry

```powershell
Invoke-RestMethod -Method Put -Uri "$VENDOR_API_URL/admin/licenses/LICENSE_ID_HERE" `
  -Headers @{ Authorization = "Bearer $VENDOR_TOKEN" } `
  -ContentType "application/json" `
  -Body '{"expires_at": "2028-12-31T23:59:59"}'
```

---

## Part 7 — Troubleshooting (Windows-Specific)

### Docker Desktop won't start

- Ensure **Virtualisation is enabled** in BIOS (check Task Manager → Performance → CPU → "Virtualisation: Enabled")
- Ensure **WSL 2** is installed and set as default: `wsl --set-default-version 2`
- Restart Docker Desktop from the taskbar icon → **Restart**

### "Access Denied" when running docker commands

Open PowerShell **as Administrator** (right-click → "Run as administrator").

### Port already in use

```powershell
# Find what's using port 3000 (or 5173, 8001 etc.)
netstat -ano | findstr :3000

# Kill the process by PID
taskkill /PID <PID_NUMBER> /F

# Then restart services
docker compose up -d
```

### Docker containers exit immediately

```powershell
docker compose logs backend --tail=50
```

Most common: `POSTGRES_HOST` not reachable — check `.env` and that Postgres container is healthy:
```powershell
docker compose ps
docker logs expert-agent-db --tail=20
```

### Readiness dashboard shows LLM error

`GOOGLE_API_KEY` is missing or invalid. Open `.env` in Notepad and verify it is set correctly. Then restart the backend:
```powershell
docker compose restart backend
```

Test the API key directly:
```powershell
docker exec expert-agent-backend python3 -c "
import os, google.generativeai as genai
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
r = genai.GenerativeModel('gemini-2.0-flash').generate_content('hello')
print('OK:', r.text[:50])
"
```

### License check fails

```powershell
docker logs expert-agent-backend --tail=50 | Select-String "license|License|ERROR"
```

Common causes:
- `LICENSE_SERVER_URL` is not reachable — check Windows Firewall and client's outbound HTTPS rules
- `LICENSE_PUBLIC_KEY` doesn't match `VENDOR_HMAC_SECRET` — must be identical on both sides
- License key was mistyped — always copy-paste

### Windows Firewall blocking ports

```powershell
# Allow inbound on ports 3000, 5173, 8001 (if other users on the network need access)
New-NetFirewallRule -DisplayName "LxGuard Admin"   -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
New-NetFirewallRule -DisplayName "LxGuard Chatbot" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow
New-NetFirewallRule -DisplayName "LxGuard API"     -Direction Inbound -Protocol TCP -LocalPort 8001 -Action Allow
```

### Full system restart

```powershell
docker compose down
docker compose up -d
Start-Sleep -Seconds 20
python scripts\healthcheck.py
```

### File permission issues (WSL path problems)

If you see permission errors on mounted volumes, ensure the project folder is stored on a **Windows drive** (e.g., `C:\lxguard\projet`) and not inside the WSL filesystem (`\\wsl$\...`).

---

## Acceptance Sign-Off Checklist

```
[ ] Docker Desktop running (whale icon green)
[ ] docker compose ps         → all containers healthy / running
[ ] python scripts\healthcheck.py  → PASS (all checks green)
[ ] http://localhost:3000/readiness → all dashboard cards green
[ ] Vendor platform shows instance as online
[ ] Vendor license_valid = True, system_active = True
[ ] Last heartbeat < 10 minutes ago
[ ] Gemini API live test PASS with latency shown
[ ] Admin login works (admin / new password)
[ ] Employee chatbot query returns a valid grounded answer
[ ] Neuro-Console shows all 8 layers in response
[ ] docker exec expert-agent-backend python scripts/demo_reset.py → Retrieval: PASS
[ ] All default passwords changed
[ ] Client IT contact has Admin Console URL and credentials
[ ] Windows Firewall rules configured for LAN access (if needed)
```

---

## Service & Port Reference

| Service | Container | Port | Browser URL |
|---------|-----------|------|-------------|
| Backend API | expert-agent-backend | 8001 | http://localhost:8001/docs |
| Admin Console | expert-agent-admin | 3000 | http://localhost:3000 |
| Chatbot UI | expert-agent-chatbot | 5173 | http://localhost:5173 |
| PostgreSQL | expert-agent-db | 5434 | — (internal) |
| Redis | expert-agent-cache | 6379 | — (internal) |
| Keycloak | expert-agent-auth | 8080 | http://localhost:8080 |
| Ollama | expert-agent-ollama | 11435 | — (internal) |
| Vendor API | lxguard-vendor-api | 8002 | https://lxguard-vendor-api-production.up.railway.app |

## Useful Docker Commands (Windows)

```powershell
# View all running containers
docker compose ps

# View backend logs live
docker compose logs -f backend

# Restart a specific service
docker compose restart backend

# Stop everything (keep data)
docker compose down

# Stop and delete all data (destructive)
docker compose down -v

# Open a shell inside the backend container
docker exec -it expert-agent-backend bash

# Check resource usage
docker stats
```
