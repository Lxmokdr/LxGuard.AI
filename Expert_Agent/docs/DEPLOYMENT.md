# Enterprise Deployment Guide

This guide details how to deploy the **Hybrid NLP-Expert Agent** in a production environment.

## 1. System Requirements

*   **OS**: Linux (Ubuntu 22.04 LTS recommended)
*   **CPU**: 4+ Cores (AVX2 support required for Ollama)
*   **RAM**: 16GB minimum (8GB for LLM, 4GB for Services, 4GB for OS)
*   **Disk**: 50GB SSD
*   **Network**: Internal network access (Air-gapped supported)

## 2. Prerequisites

### Install System Dependencies
```bash
sudo apt update && sudo apt install -y python3.10 python3-pip python3-venv nodejs npm git curl
```

### Install Ollama (Local LLM)
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma3:4b
```

## 3. Application Installation

Clone the repository to `/opt/expert-agent`:
```bash
sudo git clone https://github.com/your-org/hybrid-nlp-expert-agent.git /opt/expert-agent
sudo chown -R expert-user:expert-group /opt/expert-agent
cd /opt/expert-agent
```

### Backend Setup
```bash
cd Expert_Agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Frontend Setup
```bash
# Chatbot
cd ../chatbot-frontend
npm install
npm run build

# Admin Console
cd ../admin-frontend
npm install
npm run build
```

## 4. Service Configuration (Systemd)

We recommend using `systemd` to manage the services.

### Expert Agent Backend (`/etc/systemd/system/expert-backend.service`)
```ini
[Unit]
Description=Expert Agent Backend API
After=network.target

[Service]
User=expert-user
WorkingDirectory=/opt/expert-agent/Expert_Agent
ExecStart=/opt/expert-agent/Expert_Agent/venv/bin/uvicorn api_hybrid:app --host 0.0.0.0 --port 8001 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

### Admin Console (`/etc/systemd/system/expert-admin.service`)
```ini
[Unit]
Description=Expert Agent Admin Console
After=network.target

[Service]
User=expert-user
WorkingDirectory=/opt/expert-agent/admin-frontend
ExecStart=/usr/bin/npm start -- -p 3003
Restart=always
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

### Chatbot UI (`/etc/systemd/system/expert-chatbot.service`)
Since the chatbot is a static SPA (Single Page App), you should serve the `dist` folder using Nginx.

## 5. Nginx Reverse Proxy (Recommended)

Configure Nginx to handle SSL and routing:

```nginx
server {
    listen 443 ssl;
    server_name agent.internal.corp;

    # SSL Config
    ssl_certificate /etc/ssl/certs/agent.crt;
    ssl_certificate_key /etc/ssl/private/agent.key;

    # Chatbot UI
    location / {
        root /opt/expert-agent/chatbot-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Admin Console
    location /admin/ {
        proxy_pass http://localhost:3003;
        proxy_set_header Host $host;
    }

    # API Backend
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
    }
}
```

## 6. Security Hardening

1.  **Firewall**: Allow ports 80/443 only. Block 8001/3003/8080 externally.
2.  **Service User**: Run all services as a non-root user (`expert-user`).
3.  **Audit Logs**: Mount `/opt/expert-agent/Expert_Agent/logs` to a dedicated secure volume.
4.  **RBAC**: Configure initial admin users in `auth.py` or your external IDP.

## 7. Monitoring & Maintenance

*   **Check Status**: `systemctl status expert-backend`
*   **View Logs**: `journalctl -u expert-backend -f`
*   **Audit Trail**: Logs are stored in `Expert_Agent/logs/audit/`.
    *   Rotate logs daily using `logrotate`.
*   **Updates**:
    *   `git pull`
    *   Restart services: `sudo systemctl restart expert-*`
