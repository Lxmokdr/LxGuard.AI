"""
Enhanced API with Full Hybrid Architecture + French Language Support
Exposes all 8 layers through REST API with complete explainability
"""

import asyncio
import uvicorn
import os
import traceback
import sys
from datetime import timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from middleware.license_guard import LicenseGuardMiddleware

# Import our hybrid system components
from core.hybrid_pipeline import HybridPipeline
# Import Dual-Mode Components
from core.router import IntentRouter
from engines.ontology_engine import OntologyEngine
from engines.llm_engine import LLMEngine

# Import Modular Routers
from api.routers import chat, admin, utils, database, auth

app = FastAPI(title="Hybrid NLP-Expert Agent API", version="2.0.0")

# Enable CORS with more origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# License guard — runs AFTER CORS so preflight OPTIONS always passes
app.add_middleware(LicenseGuardMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"🔥 UNCAUGHT EXCEPTION: {exc}", flush=True)
    traceback.print_exc()
    origin = request.headers.get("origin")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        },
        headers=headers
    )

@app.on_event("startup")
async def startup_event():
    print("⚡ [Startup] Initializing Multi-Tenant Hybrid Architecture...", flush=True)
    
    try:
        # 0. Initialize Database Tables
        from data.database import engine, Base
        import api.models # Ensure all models are registered with Base.metadata
        print("📦 [Startup] Initializing Database Tables...", flush=True)
        from sqlalchemy import text
        # Enable pgvector extension first (required for VECTOR column type)
        with engine.connect() as conn:
            # Check if extension exists and create if not
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        print("✅ [Startup] Database Tables Initialized!", flush=True)
        
        # 1. Initialize Pipeline Manager
        from core.pipeline_manager import pipeline_manager
        from data.database import SessionLocal
        from api.models import Domain
        
        db = SessionLocal()
        try:
            first_domain = db.query(Domain).first()
            default_domain_id = first_domain.id if first_domain else "529af299-a716-44a0-b2ea-a262a501982f"
        finally:
            db.close()
            
        print(f"🏢 [Startup] Loading default pipeline: {default_domain_id}", flush=True)
        app.state.pipeline = pipeline_manager.get_pipeline(domain_id=default_domain_id)
        print(f"🏢 [Startup] Pipeline Manager ready (Default: {default_domain_id})", flush=True)
        
        # 2. Initialize Dual-Mode Components (Generic)
        print("🔧 [Startup] Initializing Dual-Mode Components...", flush=True)
        app.state.dual_router = IntentRouter()
        app.state.dual_llm = LLMEngine()
        
        # 3. Admin Config
        app.state.admin_config = {"source_directory": "docs"}
        
        # 4. Start Knowledge Sync Watcher (Automatic Indexing)
        print("🔭 [Startup] Starting Knowledge Sync Watcher...", flush=True)
        from services.knowledge_sync import start_knowledge_sync
        app.state.watcher = start_knowledge_sync(app.state)
        print("✅ [Startup] Knowledge Sync Watcher started.", flush=True)

        # 5. License verification background loop (NON-BLOCKING)
        print("🔑 [Startup] Scheduling license verification loop...", flush=True)
        from services.license_service import license_check_loop
        app.state.license_task = asyncio.create_task(license_check_loop())
        print("🔑 [Startup] License loop scheduled.", flush=True)

        # 6. Heartbeat monitoring background loop
        print("💓 [Startup] Scheduling heartbeat monitoring loop...", flush=True)
        from services.heartbeat_service import heartbeat_loop
        app.state.heartbeat_task = asyncio.create_task(heartbeat_loop())
        print("💓 [Startup] Heartbeat loop scheduled.", flush=True)

        print("✅ [Startup] System Ready & Multi-Tenant State Initialized!", flush=True)
        
    except Exception as exc:
        print(f"❌ [Startup] CRITICAL FAILURE DURING STARTUP: {exc}", flush=True)
        import traceback
        traceback.print_exc()

# Include Routers
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(utils.router)
app.include_router(database.router)
app.include_router(auth.router)

# Serve documents statically
docs_path = os.path.join(os.path.dirname(__file__), "..", "docs")
if not os.path.exists(docs_path):
    # Fallback for docker environment where docs might be in /app/docs
    docs_path = "/app/docs"

print(f"📁 [Startup] Serving static documents from: {os.path.abspath(docs_path)}")
app.mount("/docs", StaticFiles(directory=docs_path), name="docs")

# Root health check
@app.get("/")
async def root():
    return {"status": "online", "system": "Hybrid NLP-Expert Agent"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/license/status")
async def license_status():
    """Returns current license state — always accessible, no auth required."""
    license_key = os.environ.get("LICENSE_KEY", "")
    if not license_key:
        return {"licensed": True, "mode": "development", "message": "No license key configured (dev mode)."}

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
            return {"licensed": True, "mode": "pending", "message": "License check pending (first boot)."}

        from datetime import datetime
        now = datetime.now(timezone.utc)
        expired = False
        if cached.expires_at:
            exp = cached.expires_at.replace(tzinfo=timezone.utc) if cached.expires_at.tzinfo is None else cached.expires_at
            expired = now > exp

        return {
            "licensed": cached.license_valid,
            "active": cached.system_active,
            "expires_at": cached.expires_at.isoformat() if cached.expires_at else None,
            "expired": expired,
            "last_checked": cached.last_checked.isoformat(),
            "license_key_prefix": license_key[:8] + "...",
        }
    except Exception as exc:
        return {"licensed": True, "mode": "error", "message": str(exc)}

if __name__ == "__main__":
    uvicorn.run("api_hybrid:app", host="0.0.0.0", port=8000, reload=True)