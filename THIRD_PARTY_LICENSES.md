# Third-Party Licenses

This document lists all third-party dependencies used in the City-Wide ANPR system, their licenses, and repository URLs.

> **Before integrating any third-party repository or model, its license was inspected and documented here.**

---

## Python Backend Dependencies

| Component | Version | License | Repository |
|-----------|---------|---------|------------|
| FastAPI | ≥0.115.0 | MIT | https://github.com/fastapi/fastapi |
| Pydantic | ≥2.9.0 | MIT | https://github.com/pydantic/pydantic |
| pydantic-settings | ≥2.5.0 | MIT | https://github.com/pydantic/pydantic-settings |
| SQLAlchemy | ≥2.0.35 | MIT | https://github.com/sqlalchemy/sqlalchemy |
| asyncpg | ≥0.30.0 | Apache-2.0 | https://github.com/MagicStack/asyncpg |
| GeoAlchemy2 | ≥0.15.0 | MIT | https://github.com/geoalchemy/geoalchemy2 |
| Alembic | ≥1.14.0 | MIT | https://github.com/sqlalchemy/alembic |
| Uvicorn | ≥0.30.0 | BSD-3-Clause | https://github.com/encode/uvicorn |
| passlib | ≥1.7.4 | BSD-3-Clause | https://github.com/hlandau/passlib |
| python-jose | ≥3.3.0 | MIT | https://github.com/mpdavis/python-jose |
| python-multipart | ≥0.0.12 | Apache-2.0 | https://github.com/Kludex/python-multipart |
| redis (Python client) | ≥5.2.0 | MIT | https://github.com/redis/redis-py |
| websockets | ≥13.0 | BSD-3-Clause | https://github.com/python-websockets/websockets |
| httpx | ≥0.27.0 | BSD-3-Clause | https://github.com/encode/httpx |
| Pillow | ≥10.4.0 | HPND | https://github.com/python-pillow/Pillow |
| NumPy | ≥1.26.0 | BSD-3-Clause | https://github.com/numpy/numpy |
| Shapely | ≥2.0.0 | BSD-3-Clause | https://github.com/shapely/shapely |
| pyproj | ≥3.7.0 | MIT | https://github.com/pyproj4/pyproj |
| python-dotenv | ≥1.0.1 | BSD-3-Clause | https://github.com/theskumar/python-dotenv |
| loguru | ≥0.7.0 | MIT | https://github.com/Delgan/loguru |

## AI/ML Dependencies

| Component | Version | License | Repository | Notes |
|-----------|---------|---------|------------|-------|
| **Ultralytics (YOLOv8)** | ≥8.3.0 | **AGPL-3.0** | https://github.com/ultralytics/ultralytics | **Copyleft license.** Acceptable for local prototyping. If deploying as a network service, AGPL-3.0 requires releasing all source code under AGPL-3.0. Enterprise license available for commercial use. |
| OpenCV (headless) | ≥4.10.0 | Apache-2.0 | https://github.com/opencv/opencv-python | Image preprocessing pipeline |
| PaddlePaddle | ≥2.6.0 | Apache-2.0 | https://github.com/PaddlePaddle/Paddle | Deep learning framework for OCR |
| PaddleOCR | ≥2.8.0 | Apache-2.0 | https://github.com/PaddlePaddle/PaddleOCR | License plate text recognition |
| pytesseract | ≥0.3.13 | Apache-2.0 | https://github.com/madmaze/pytesseract | Python wrapper for Tesseract |
| Tesseract OCR | 5.x | Apache-2.0 | https://github.com/tesseract-ocr/tesseract | Fallback OCR engine |
| SciPy | ≥1.14.0 | BSD-3-Clause | https://github.com/scipy/scipy | Hungarian matching for tracking |
| Supervision | ≥0.25.0 | MIT | https://github.com/roboflow/supervision | CV utilities (optional) |

## Frontend Dependencies

| Component | Version | License | Repository |
|-----------|---------|---------|------------|
| React | ^18.3.1 | MIT | https://github.com/facebook/react |
| React DOM | ^18.3.1 | MIT | https://github.com/facebook/react |
| React Router DOM | ^6.28.0 | MIT | https://github.com/remix-run/react-router |
| Vite | ^6.0.0 | MIT | https://github.com/vitejs/vite |
| TypeScript | ^5.6.3 | Apache-2.0 | https://github.com/microsoft/TypeScript |
| Tailwind CSS | ^3.4.16 | MIT | https://github.com/tailwindlabs/tailwindcss |
| Axios | ^1.7.0 | MIT | https://github.com/axios/axios |
| Leaflet | ^1.9.4 | BSD-2-Clause | https://github.com/Leaflet/Leaflet |
| react-leaflet | ^4.2.1 | MIT | https://github.com/PaulLeCam/react-leaflet |
| leaflet.heat | ^0.2.0 | BSD-2-Clause | https://github.com/Leaflet/Leaflet.heat |
| Apache ECharts | ^5.5.1 | Apache-2.0 | https://github.com/apache/echarts |
| echarts-for-react | ^3.0.2 | MIT | https://github.com/hustcc/echarts-for-react |
| Lucide React | ^0.460.0 | ISC | https://github.com/lucide-icons/lucide |
| clsx | ^2.1.1 | MIT | https://github.com/lukeed/clsx |
| tailwind-merge | ^2.6.0 | MIT | https://github.com/dcastil/tailwind-merge |
| date-fns | ^4.1.0 | MIT | https://github.com/date-fns/date-fns |

## Infrastructure

| Component | Version | License | Source |
|-----------|---------|---------|--------|
| PostgreSQL | 16 | PostgreSQL License (permissive, MIT-like) | https://github.com/postgres/postgres |
| PostGIS | 3.4 | GPL-2.0-or-later | https://git.osgeo.org/gitea/postgis/postgis |
| Redis | 7 | BSD-3-Clause (7.x series) | https://github.com/redis/redis |
| Docker | Latest | Apache-2.0 | https://github.com/moby/moby |
| Nginx | Alpine | BSD-2-Clause | https://github.com/nginx/nginx |

## Map Data

| Component | License | Source | Notes |
|-----------|---------|--------|-------|
| OpenStreetMap Tiles | ODbL 1.0 (data) / CC-BY-SA 2.0 (tiles) | https://www.openstreetmap.org | Must display "© OpenStreetMap contributors" attribution. Public tile server has usage policy limits. |

## AI Model Weights

| Model | License | Source | Notes |
|-------|---------|--------|-------|
| YOLOv8n (COCO pretrained) | AGPL-3.0 | Ultralytics | Auto-downloaded. COCO dataset (CC-BY-4.0) used for pretraining. |
| PaddleOCR PP-OCRv4 | Apache-2.0 | PaddlePaddle | Auto-downloaded on first use. |

---

## License Compatibility Notes

1. **PostGIS (GPL-2.0)**: PostGIS runs as a PostgreSQL extension. Our application interacts with it through standard SQL over network sockets (via asyncpg/SQLAlchemy). This qualifies as independent work under copyright law — no copyleft contamination occurs.

2. **Ultralytics YOLO (AGPL-3.0)**: This is the most restrictive license in the stack. For a local prototype, AGPL-3.0 is fully compliant. If the system is deployed as a network-accessible service, AGPL-3.0 requires all source code to be released under AGPL-3.0. **Alternative**: RT-DETR (Apache-2.0) can replace YOLO for a fully permissive stack.

3. **Redis**: Redis 7.x uses BSD-3-Clause. Redis 7.4+ transitioned to RSALv2/SSPLv1. If using Redis 7.4+, consider using **Valkey** (BSD-3-Clause, drop-in compatible) from the Linux Foundation.

4. **OpenStreetMap**: Map tiles require visible attribution: `© OpenStreetMap contributors`. The public tile server has a [Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/) — acceptable for development and light production use.
