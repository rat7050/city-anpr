# City-Wide AI Engine for Multi-Camera ANPR Trajectory Tracking and Urban Traffic Analytics

A modular, scalable, privacy-conscious platform for processing multiple CCTV/ANPR camera streams. Detects vehicles, recognizes license plates via OCR, tracks vehicles across multiple cameras, reconstructs trajectories, and provides city-wide traffic analytics — all using **free and open-source software only**.

> **⚠ DEMO / DEVELOPMENT RESULT**: All accuracy metrics, benchmarks, and analytics thresholds are prototype values. No claims of >90% accuracy are made without evaluation on a representative test dataset.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Installation](#4-installation)
5. [Dataset Setup](#5-dataset-setup)
6. [Model Setup](#6-model-setup)
7. [Running the Camera Simulator](#7-running-the-camera-simulator)
8. [Starting Backend](#8-starting-backend)
9. [Starting Frontend](#9-starting-frontend)
10. [Running AI Inference](#10-running-ai-inference)
11. [Database Setup](#11-database-setup)
12. [API Documentation](#12-api-documentation)
13. [Testing](#13-testing)
14. [Evaluation](#14-evaluation)
15. [Limitations](#15-limitations)
16. [Privacy Considerations](#16-privacy-considerations)
17. [Open-Source Licenses](#17-open-source-licenses)

---

## 1. Project Overview

This system demonstrates:

- **Vehicle Detection** — YOLOv8 for car, motorcycle, bus, truck detection
- **License Plate Detection** — Dedicated plate detection within vehicle crops
- **OCR** — PaddleOCR (primary) / Tesseract (fallback) for plate text extraction
- **Indian Plate Validation** — Regex-based validation with configurable state codes
- **Single-Camera Tracking** — ByteTrack for persistent vehicle tracking across frames
- **Multi-Camera Association** — Weighted scoring engine to link vehicles across cameras
- **Trajectory Reconstruction** — Chronological route building with GIS visualization
- **Traffic Analytics** — Vehicle counts, density, speed, congestion scoring
- **Heatmap Visualization** — Real-time density/congestion heatmaps on OpenStreetMap
- **Origin-Destination Analysis** — Zone-to-zone traffic flow matrices
- **Watchlist Alerts** — Configurable plate watchlist with real-time alert notifications
- **Route Anomaly Detection** — Statistical detection of unusual travel patterns
- **Real-Time Dashboard** — WebSocket-powered command-center UI

The entire system runs locally without any paid API or cloud service.

---

## 2. Architecture

```
Camera Sources (Video Files / RTSP / Simulator)
    │
    ▼
┌─────────────────────────────────────────┐
│           AI Pipeline Worker            │
│  Frame Extraction → Vehicle Detection   │
│  → Plate Detection → Preprocessing     │
│  → OCR → Validation → Tracking         │
│  → Multi-Camera Association            │
└────────────────┬────────────────────────┘
                 │ Detection Events
                 ▼
┌────────────────────────────────────────┐
│         FastAPI Backend                │
│  Auth │ Cameras │ Vehicles │ Analytics │
│  Alerts │ Watchlist │ Trajectories     │
└──────┬──────────────┬──────────────────┘
       │              │
       ▼              ▼
┌──────────┐   ┌───────────┐
│PostgreSQL│   │   Redis   │
│+ PostGIS │   │  Pub/Sub  │
└──────────┘   └─────┬─────┘
                     │ WebSocket
                     ▼
┌────────────────────────────────────────┐
│        React Dashboard (Vite)          │
│  Map │ Charts │ Alerts │ Search       │
│  Heatmap │ OD Matrix │ Trajectory     │
└────────────────────────────────────────┘
```

### Project Structure

```
city-anpr/
├── frontend/          # React + TypeScript + Vite + Tailwind
├── backend/           # FastAPI + SQLAlchemy + Pydantic
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── models/    # SQLAlchemy ORM models
│   │   ├── schemas/   # Pydantic request/response schemas
│   │   ├── services/  # Business logic
│   │   └── middleware/ # Auth middleware
│   └── alembic/       # Database migrations
├── ai/                # Computer vision pipeline
│   ├── detection/     # YOLO vehicle & plate detection
│   ├── ocr/           # PaddleOCR + preprocessing
│   ├── tracking/      # ByteTrack single-camera tracking
│   ├── reid/          # Multi-camera vehicle association
│   └── analytics/     # Traffic analysis, OD, anomaly
├── camera_simulator/  # Synthetic detection generator
├── docker/            # Dockerfiles + nginx config
├── tests/             # Automated tests
├── scripts/           # Evaluation and utility scripts
├── docs/              # Architecture, API, deployment docs
├── docker-compose.yml
├── README.md
├── LICENSE            # MIT
└── THIRD_PARTY_LICENSES.md
```

---

## 3. Technology Stack

| Component | Technology | License | Purpose |
|-----------|-----------|---------|---------|
| Frontend | React 18 + TypeScript | MIT | Dashboard UI |
| Build Tool | Vite 6 | MIT | Fast dev server and bundling |
| CSS | Tailwind CSS 3 | MIT | Utility-first styling |
| Mapping | Leaflet + OpenStreetMap | BSD-2 / ODbL | GIS visualization (no API key) |
| Charts | Apache ECharts 5 | Apache-2.0 | Traffic analytics charts |
| Icons | Lucide React | ISC | UI icons |
| Backend | FastAPI | MIT | Async REST API + WebSocket |
| Validation | Pydantic v2 | MIT | Request/response schemas |
| ORM | SQLAlchemy 2.0 | MIT | Async database access |
| Database | PostgreSQL 16 + PostGIS | PostgreSQL / GPL-2.0 | Spatial data storage |
| Cache/PubSub | Redis 7 | BSD-3-Clause | Real-time event broadcasting |
| Migrations | Alembic | MIT | Database schema migrations |
| Auth | python-jose + passlib | MIT | JWT tokens + bcrypt hashing |
| Detection | Ultralytics YOLOv8 | **AGPL-3.0** | Vehicle detection |
| OCR (Primary) | PaddleOCR | Apache-2.0 | License plate OCR |
| OCR (Fallback) | Tesseract | Apache-2.0 | Fallback OCR engine |
| Image Processing | OpenCV | Apache-2.0 | Plate preprocessing |
| Tracking | ByteTrack | MIT | Multi-object tracking |
| Containerization | Docker + Compose | Apache-2.0 | Deployment |

> **⚠ Note**: Ultralytics YOLO uses AGPL-3.0 (copyleft). This is acceptable for local prototyping. See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for details.

---

## 4. Installation

### Prerequisites

- Docker and Docker Compose (recommended)
- OR: Python 3.11+, Node.js 20+, PostgreSQL 16+ with PostGIS, Redis 7+

### Quick Start (Docker)

```bash
# Clone the repository
git clone <repository-url>
cd city-anpr

# Start all services
docker compose up --build

# Services will be available at:
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
# PostgreSQL: localhost:5432
# Redis:      localhost:6379
```

### Manual Setup (Windows)

```powershell
# 1. Install Python dependencies
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Install frontend dependencies
cd ..\frontend
npm install

# 3. Start PostgreSQL + PostGIS (using Docker)
docker run -d --name city-anpr-db -p 5432:5432 `
  -e POSTGRES_DB=city_anpr -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres `
  postgis/postgis:16-3.4

# 4. Start Redis
docker run -d --name city-anpr-redis -p 6379:6379 redis:7-alpine

# 5. Create .env file
copy backend\.env.example backend\.env

# 6. Start backend
cd backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Start frontend (new terminal)
cd frontend
npm run dev

# 8. Seed demo data
cd backend
python -m backend.seed_data
```

### Manual Setup (Linux)

```bash
# 1. Install Python dependencies
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Install frontend dependencies
cd ../frontend
npm install

# 3. Start PostgreSQL + PostGIS
docker run -d --name city-anpr-db -p 5432:5432 \
  -e POSTGRES_DB=city_anpr -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
  postgis/postgis:16-3.4

# 4. Start Redis
docker run -d --name city-anpr-redis -p 6379:6379 redis:7-alpine

# 5. Create .env
cp backend/.env.example backend/.env

# 6. Start backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Start frontend (new terminal)
cd frontend && npm run dev

# 8. Seed demo data
python -m backend.seed_data
```

---

## 5. Dataset Setup

The system supports user-provided or synthetic video data. No proprietary datasets are included.

**Recommended open datasets for training/evaluation:**

| Dataset | Source | License |
|---------|--------|---------|
| Indian License Plates | Roboflow Universe | CC-BY-4.0 |
| OpenImages Vehicle | Google | Apache-2.0 |
| COCO (vehicles) | Microsoft | CC-BY-4.0 |

For demonstration, use the built-in camera simulator (no video files needed).

---

## 6. Model Setup

### Vehicle Detection (automatic)
YOLOv8n weights are downloaded automatically on first run:
```bash
# Weights stored at: ~/.ultralytics/models/yolov8n.pt
```

### Plate Detection
For a custom plate detection model, place weights at:
```bash
models/plate_detector.pt
```
If no custom model is available, the system falls back to OpenCV contour-based plate detection.

### OCR
PaddleOCR models download automatically on first run.

---

## 7. Running the Camera Simulator

The simulator generates realistic detection events without requiring physical cameras.

```bash
# Demo mode: generates a complete demo scenario with 4 cameras
python -m camera_simulator.simulator --mode demo --api-url http://localhost:8000

# Continuous mode: generates ongoing detections
python -m camera_simulator.simulator --mode continuous --rate 10

# With authentication
python -m camera_simulator.simulator --mode demo --token YOUR_JWT_TOKEN
```

### Demo Scenario
- Vehicle `CG04AB1234` traverses cameras: C01 → C08 → C15 → C22
- 12+ additional vehicles with varied patterns
- Realistic timing between camera observations
- Watchlist match triggers alert

---

## 8. Starting Backend

```bash
cd backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Or via Docker:
```bash
docker compose up backend
```

### Default Credentials (seeded)

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | ADMIN |
| operator | operator123 | OPERATOR |
| analyst | analyst123 | ANALYST |
| viewer | viewer123 | VIEWER |

---

## 9. Starting Frontend

```bash
cd frontend
npm run dev
# Opens at http://localhost:5173 (dev) or http://localhost:3000 (Docker)
```

---

## 10. Running AI Inference

### With Docker
```bash
docker compose up ai-worker
```

### Manual (requires GPU for real-time performance)
```bash
pip install ultralytics paddleocr paddlepaddle
python -m ai.pipeline --camera-id c01 --video path/to/video.mp4
```

---

## 11. Database Setup

### Using Alembic Migrations
```bash
cd backend
alembic upgrade head
```

### Direct Table Creation
Tables are auto-created on backend startup via `init_db()` for development.

### Seed Demo Data
```bash
python -m backend.seed_data
```

---

## 12. API Documentation

Interactive API documentation (Swagger UI) is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login, get JWT token |
| GET | `/api/cameras` | List all cameras |
| GET | `/api/vehicles?plate=CG04AB1234` | Search vehicles |
| GET | `/api/vehicles/{plate}/trajectory` | Get trajectory |
| GET | `/api/detections/recent` | Recent detections |
| GET | `/api/analytics/stats` | Traffic statistics |
| GET | `/api/analytics/heatmap` | Heatmap data |
| GET | `/api/analytics/od-matrix` | OD matrix |
| GET | `/api/alerts` | List alerts |
| POST | `/api/watchlist` | Add to watchlist |
| WS | `/ws/live?token=TOKEN` | Real-time events |

See [docs/api.md](docs/api.md) for full documentation.

---

## 13. Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Specific test suites
python -m pytest tests/test_plate_validator.py -v
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_multi_camera_matching.py -v
python -m pytest tests/test_analytics.py -v
```

---

## 14. Evaluation

```bash
python scripts/evaluate.py --report
```

Measures:
- **Detection**: Precision, Recall, mAP (DEMO/DEVELOPMENT RESULT)
- **OCR**: Character accuracy, full-plate accuracy, edit distance
- **Tracking**: ID consistency, ID switches
- **System**: FPS, latency, CPU/GPU/memory usage

> All results are labeled as **DEMO / DEVELOPMENT RESULT** unless evaluated on a representative test dataset.

---

## 15. Limitations

- **OCR accuracy** depends heavily on image quality, lighting, and camera angle. No claims of >90% accuracy without evaluation.
- **Speed estimation** is approximate (straight-line distance between cameras / travel time).
- **Congestion thresholds** are configurable prototypes, not scientifically validated.
- **Route anomaly detection** uses simple sequence comparison — not a trained ML model.
- **Real-time performance** on CPU is limited to ~2-5 FPS per camera. GPU recommended for multi-camera.
- **Indian plate support** covers standard formats. Specialty plates (diplomatic, military, vintage) may not validate.
- **Night/rain/fog** conditions significantly reduce detection and OCR accuracy.
- **No facial recognition** is implemented or planned.

---

## 16. Privacy Considerations

- **Access Control**: JWT authentication with 4 roles (ADMIN, OPERATOR, ANALYST, VIEWER)
- **Audit Logging**: All data access is logged
- **Data Retention**: Configurable retention periods (not enforced in prototype)
- **Aggregated Analytics**: Traffic analytics use aggregate data, not individual plate tracking
- **Plate Privacy**: Plate numbers are not exposed in public dashboards
- **No Facial Recognition**: The system does NOT identify individuals
- **No Individual Tracking**: Vehicles are tracked for authorized operational purposes only
- **Route Anomaly**: Anomalies are **decision-support signals**, not evidence of criminal behavior

---

## 17. Open-Source Licenses

All dependencies use free and open-source licenses. See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for the complete list.

**Notable license**: Ultralytics YOLO uses AGPL-3.0 (copyleft). If deploying as a network service, the AGPL-3.0 requires releasing source code. For permissive alternatives, consider RT-DETR (Apache-2.0).

---

## License

This project's source code is licensed under the [MIT License](LICENSE).

Third-party dependencies are subject to their own licenses as documented in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
