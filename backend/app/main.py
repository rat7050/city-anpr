import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.app.config import settings
from backend.app.database import engine, init_db
from backend.app.services.redis_service import RedisService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Redis service instance
redis_service = RedisService(settings.REDIS_URL, enabled=settings.REDIS_ENABLED)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    # Import all models so Base.metadata is populated
    from backend.app.models import User, Camera, Vehicle, Detection, Trajectory, Alert, Watchlist, AuditLog  # noqa
    await init_db()
    logger.info("Database initialized.")
    await redis_service.connect()
    # Store redis_service in app state for access from routes
    app.state.redis = redis_service

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await redis_service.disconnect()
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - import here to avoid circular imports
from backend.app.api import auth, cameras, vehicles, detections, analytics, alerts, watchlist, websocket  # noqa

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
