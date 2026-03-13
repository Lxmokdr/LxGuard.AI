"""
Vendor Platform — Main FastAPI Application
Serves: license check, heartbeat, and admin management endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models  # noqa: registers all models

from routers import license, heartbeat, admin

app = FastAPI(
    title="Vendor License & Control Platform",
    description="Centralized license management and monitoring for enterprise installations.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict to dashboard domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables on startup
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("✅ Vendor database tables initialized")

# Public endpoints (no auth)
app.include_router(license.router)
app.include_router(heartbeat.router)

# Admin endpoints (JWT protected)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"service": "Vendor License Platform", "status": "online"}


@app.get("/health")
def health():
    return {"status": "healthy"}
