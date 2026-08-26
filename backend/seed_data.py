import asyncio
import logging
from datetime import datetime, timezone, timedelta

from backend.app.database import async_session_maker, engine, Base
from backend.app.models import User, Camera, Watchlist, Vehicle, Detection, Alert
from backend.app.services.auth_service import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        logger.info("Seeding users...")
        users_data = [
            {"username": "admin", "password": "admin123", "role": "ADMIN", "email": "admin@example.com"},
            {"username": "operator", "password": "operator123", "role": "OPERATOR", "email": "operator@example.com"},
            {"username": "analyst", "password": "analyst123", "role": "ANALYST", "email": "analyst@example.com"},
            {"username": "viewer", "password": "viewer123", "role": "VIEWER", "email": "viewer@example.com"},
        ]
        for u in users_data:
            user = User(
                username=u["username"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
                is_active=True
            )
            db.add(user)
        
        logger.info("Seeding cameras...")
        cameras_data = [
            {"name": "C01", "lat": 21.2514, "lon": 81.6296, "road": "VIP Road", "zone": "Raipur North"},
            {"name": "C08", "lat": 21.2350, "lon": 81.6100, "road": "Ring Road", "zone": "Raipur West"},
            {"name": "C15", "lat": 21.2200, "lon": 81.5950, "road": "GE Road", "zone": "Raipur South"},
            {"name": "C22", "lat": 21.2100, "lon": 81.6350, "road": "Pandri", "zone": "Raipur Central"}
        ]
        
        camera_objs = []
        for c in cameras_data:
            cam = Camera(
                camera_name=c["name"],
                latitude=c["lat"],
                longitude=c["lon"],
                road_name=c["road"],
                zone=c["zone"],
                status="ONLINE",
                location=f"POINT({c['lon']} {c['lat']})"
            )
            db.add(cam)
            camera_objs.append(cam)
            
        await db.flush()
        
        logger.info("Seeding watchlist...")
        watchlist_entry = Watchlist(
            plate_number="CG04AB1234",
            reason="Stolen Vehicle",
            status="ACTIVE",
            priority="HIGH",
            created_at=datetime.now(timezone.utc)
        )
        db.add(watchlist_entry)
        
        logger.info("Seeding vehicles and detections...")
        vehicle = Vehicle(
            plate_number="CG04AB1234",
            vehicle_type="CAR",
            vehicle_color="BLACK",
            first_seen=datetime.now(timezone.utc) - timedelta(hours=2),
            last_seen=datetime.now(timezone.utc)
        )
        db.add(vehicle)
        await db.flush()
        
        # Add detections along the cameras to form a trajectory
        time_offsets = [120, 90, 60, 30] # minutes ago
        for i, cam in enumerate(camera_objs):
            det_time = datetime.now(timezone.utc) - timedelta(minutes=time_offsets[i])
            det = Detection(
                camera_id=cam.id,
                vehicle_id=vehicle.id,
                plate_number="CG04AB1234",
                ocr_confidence=0.98,
                timestamp=det_time,
                latitude=cam.latitude,
                longitude=cam.longitude,
                direction="NORTH",
                speed=45.5,
                vehicle_type="CAR",
                location=f"POINT({cam.longitude} {cam.latitude})"
            )
            db.add(det)
            
        logger.info("Seeding alerts...")
        alert = Alert(
            vehicle_id=vehicle.id,
            camera_id=camera_objs[0].id,
            alert_type="WATCHLIST_MATCH",
            severity="HIGH",
            message="Stolen vehicle detected on VIP Road",
            timestamp=datetime.now(timezone.utc),
            status="NEW"
        )
        db.add(alert)

        await db.commit()
        logger.info("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_data())
