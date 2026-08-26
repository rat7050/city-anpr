import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.app.config import settings
from backend.app.database import engine, Base, init_db
from backend.app.api import auth, cameras, vehicles, detections, analytics, alerts, watchlist, websocket

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    # Import all models so Base.metadata is populated
    from backend.app.models import User, Camera, Vehicle, Detection, Trajectory, Alert, Watchlist, AuditLog  # noqa
    await init_db()
    logger.info("Database initialized.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    description="City-Wide ANPR System Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set this to frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(cameras.router)
app.include_router(vehicles.router)
app.include_router(detections.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(watchlist.router)
app.include_router(websocket.router)

@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
