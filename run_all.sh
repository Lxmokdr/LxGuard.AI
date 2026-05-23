#!/usr/bin/env bash

# Premium Startup Script for LxGuard.AI Hybrid NLP-Expert Agent System
# Manages Environment Variables, Docker Compose backends, and Local Node Frontends

set -e

# Disable Next.js telemetry to avoid ConnectTimeoutError on isolated/offline networks
export NEXT_TELEMETRY_DISABLED=1

# --- Theme & Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Print banner
echo -e "${CYAN}${BOLD}"
echo "=========================================================================="
echo "    __    ________                    __         ___    ____ "
echo "   / /   / ____/ /_  ______ _________/ /  _     /   |  /  _/ "
echo "  / /   / / __/ / / / / __ \`/ ___/ __  /  (_)   / /| |  / /   "
echo " / /___/ /_/ / / /_/ / /_/ / /  / /_/ /  _     / ___ |_/ /    "
echo "/_____/\____/_/\__,_/\__,_/_/   \__,_/  (_)   /_/  |_/___/    "
echo "                                                                          "
echo "         Multi-Tenant Neuro-Symbolic Governance & RAG Platform"
echo "=========================================================================="
echo -e "${NC}"

# Define files and paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADMIN_ENV="$PROJECT_ROOT/admin-frontend/.env.local"
CHATBOT_ENV="$PROJECT_ROOT/chatbot-frontend/.env"
VENDOR_ENV="$PROJECT_ROOT/vendor_platform/dashboard/.env.local"

# Keep track of child PIDs for cleanup
declare -a FRONTEND_PIDS

cleanup() {
    echo -e "\n${YELLOW}${BOLD}[*] Initiating graceful shutdown...${NC}"
    
    # Kill local node processes
    for pid in "${FRONTEND_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${NC}Stopping frontend process (PID: $pid)..."
            kill "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null
        fi
    done

    # Ask to stop docker compose
    echo -e "${YELLOW}[?] Do you want to shut down the running Docker containers? (y/n)${NC}"
    read -r -t 5 response || response="n"
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}[*] Shutting down Docker containers...${NC}"
        docker compose down 2>/dev/null || true
        docker compose -f vendor_platform/docker-compose.yml down 2>/dev/null || true
    else
        echo -e "${GREEN}[✓] Docker containers left running in background.${NC}"
    fi

    echo -e "${GREEN}${BOLD}[✓] Cleaned up! Goodbye.${NC}"
    exit 0
}

# Trap exit signals
trap cleanup SIGINT SIGTERM EXIT

# Helper to check if a port is in use and kill it
clear_port() {
    local port=$1
    local name=$2
    local pid
    pid=$(lsof -t -i:"$port" 2>/dev/null || true)
    if [ ! -z "$pid" ] && [ "$pid" != "" ]; then
        echo -e "${YELLOW}[!] Port $port ($name) is currently occupied by PID: $pid. Releasing...${NC}"
        kill -9 "$pid" 2>/dev/null || true
        sleep 0.5
    fi
}

# --- 1. Mode Selection ---
mode_choice=""
if [ "$1" = "--local" ] || [ "$1" = "-l" ] || [ "$1" = "1" ]; then
    mode_choice="1"
elif [ "$1" = "--deployed" ] || [ "$1" = "-d" ] || [ "$1" = "2" ]; then
    mode_choice="2"
fi

if [ -z "$mode_choice" ]; then
    echo -e "${BOLD}Select Backend Environment Mode:${NC}"
    echo -e "  ${CYAN}[1] Local Backend${NC} (FastAPI container on localhost:8001)"
    echo -e "  ${CYAN}[2] Deployed Backend${NC} (Hugging Face Space at lxmix-lxguard-ai.hf.space)"
    echo -ne "\nEnter choice [1 or 2]: "
    read -r mode_choice
fi

if [ "$mode_choice" = "2" ]; then
    BACKEND_URL="https://lxmix-lxguard-ai.hf.space"
    echo -e "\n${GREEN}${BOLD}[✓] Selected: Deployed Backend (${BACKEND_URL})${NC}"
else
    BACKEND_URL="http://localhost:8001"
    echo -e "\n${GREEN}${BOLD}[✓] Selected: Local Backend (${BACKEND_URL})${NC}"
fi

# --- 2. Configure Environment Files ---
echo -e "\n${BLUE}[*] Updating Frontend Environment Files...${NC}"

# Admin Frontend Env
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > "$ADMIN_ENV"
echo -e "  ${GRAY}→ Admin Frontend Env: NEXT_PUBLIC_API_URL=$BACKEND_URL${NC}"

# Chatbot Frontend Env
echo "VITE_API_URL=$BACKEND_URL" > "$CHATBOT_ENV"
echo -e "  ${GRAY}→ Chatbot Frontend Env: VITE_API_URL=$BACKEND_URL${NC}"

# Vendor Frontend Env (Always points to local vendor api on 8002)
echo "NEXT_PUBLIC_VENDOR_API_URL=http://localhost:8002" > "$VENDOR_ENV"
echo -e "  ${GRAY}→ Vendor Dashboard Env: NEXT_PUBLIC_VENDOR_API_URL=http://localhost:8002${NC}"

# --- Permission Check for Frontends ---
echo -e "\n${BLUE}[*] Checking file permissions...${NC}"
root_files=$(find "$PROJECT_ROOT/admin-frontend" "$PROJECT_ROOT/chatbot-frontend" "$PROJECT_ROOT/vendor_platform/dashboard" -user root 2>/dev/null | wc -l || echo 0)

if [ "$root_files" -gt 0 ]; then
    echo -e "${RED}${BOLD}[!] Permission Issue Detected:${NC}"
    echo -e "  Some files in the frontend directories are owned by 'root' (likely created by Docker)."
    echo -e "  To prevent Next.js and Vite from failing, please run the following command to restore ownership:"
    echo -e "  ${CYAN}${BOLD}sudo chown -R \$USER:\$USER \"$PROJECT_ROOT\"${NC}"
    echo -e "  Then run the script again."
    exit 1
fi
echo -e "${GREEN}[✓] Permissions are correct.${NC}"

# --- 3. Start Backend Services (Docker Compose) ---
echo -e "\n${BLUE}[*] Checking Backend Services (Docker Compose)...${NC}"

if [ "$mode_choice" = "2" ]; then
    # Deployed Backend mode: We only need local vendor_platform database & API
    echo -e "${YELLOW}[i] Starting Vendor Licensing API and DB locally...${NC}"
    docker compose -f "$PROJECT_ROOT/vendor_platform/docker-compose.yml" up -d vendor_db vendor_api
    
    # Stop local Docker frontends to release ports
    echo -e "${YELLOW}[i] Ensuring Docker-based frontends are stopped...${NC}"
    docker compose stop admin-frontend chatbot-frontend 2>/dev/null || true
    docker compose -f "$PROJECT_ROOT/vendor_platform/docker-compose.yml" stop vendor_dashboard 2>/dev/null || true
else
    # Local Backend mode: We need all core backend containers + vendor API & DB
    echo -e "${YELLOW}[i] Starting Local Core Backend Services (Postgres, Keycloak, Redis, FastAPI)...${NC}"
    docker compose up -d postgres keycloak redis ollama backend
    
    echo -e "${YELLOW}[i] Starting Vendor Licensing API and DB...${NC}"
    docker compose -f "$PROJECT_ROOT/vendor_platform/docker-compose.yml" up -d vendor_db vendor_api
    
    # Stop local Docker frontends to release ports
    echo -e "${YELLOW}[i] Ensuring Docker-based frontends are stopped...${NC}"
    docker compose stop admin-frontend chatbot-frontend 2>/dev/null || true
    docker compose -f "$PROJECT_ROOT/vendor_platform/docker-compose.yml" stop vendor_dashboard 2>/dev/null || true
fi

# Check Docker Container health
echo -e "\n${BLUE}[*] Checking container statuses...${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# --- 4. Prepare Ports ---
echo -e "\n${BLUE}[*] Preparing ports for local Dev Servers...${NC}"
clear_port 3000 "Admin UI"
clear_port 8080 "Chatbot UI"
clear_port 4000 "Vendor UI"

# --- 5. Start Frontends ---
echo -e "\n${BLUE}[*] Launching Node.js Frontends...${NC}"

# Start Chatbot Frontend
echo -e "${MAGENTA}[+] Starting Chatbot Frontend (Vite) on port 8080...${NC}"
cd "$PROJECT_ROOT/chatbot-frontend"
npm run dev -- --port 8080 --host &
FRONTEND_PIDS+=($!)

# Start Admin Frontend
echo -e "${MAGENTA}[+] Starting Admin Frontend (Next.js) on port 3000...${NC}"
cd "$PROJECT_ROOT/admin-frontend"
npm run dev &
FRONTEND_PIDS+=($!)

# Start Vendor Platform Dashboard
echo -e "${MAGENTA}[+] Starting Vendor Dashboard (Next.js) on port 4000...${NC}"
cd "$PROJECT_ROOT/vendor_platform/dashboard"
npm run dev &
FRONTEND_PIDS+=($!)

cd "$PROJECT_ROOT"

# Wait a moment to let Next.js and Vite start up
sleep 3

echo -e "\n${GREEN}${BOLD}=========================================================================="
echo -e "   🎉 All systems configured and running!"
echo -e "=========================================================================="
echo -e "   🛡️  Chatbot UI:          ${CYAN}http://localhost:8080${NC} (or http://localhost:5173 inside docker)"
echo -e "   ⚙️  Admin Console:       ${CYAN}http://localhost:3000${NC}"
echo -e "   💳  Vendor Dashboard:    ${CYAN}http://localhost:4000${NC}"
echo -e "--------------------------------------------------------------------------"
echo -e "   🔗  Backend API Target:  ${BOLD}${BACKEND_URL}${NC}"
echo -e "   🔑  Vendor API:          ${BOLD}http://localhost:8002${NC}"
echo -e "=========================================================================="
echo -e "   Press [Ctrl+C] to stop dev servers and clean up."
echo -e "==========================================================================${NC}\n"

# Keep the script running to keep trap alive
while true; do
    sleep 1
done
