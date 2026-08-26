# Architecture

## System Overview
```mermaid
graph TD
    A[Cameras] -->|Video/Events| B(AI Worker Node)
    B -->|Detections| C{Backend API}
    C -->|Store| D[(PostgreSQL + PostGIS)]
    C -->|Cache| E[(Redis)]
    C -->|WebSocket| F[Frontend Dashboard]
```

## Data Flow
Cameras stream to AI Workers -> AI extracts Plates -> Backend processes -> DB stores -> Frontend displays.

## AI Pipeline
Frame -> Object Detection (YOLO) -> Tracker (ByteTrack) -> OCR (PaddleOCR).

## Real-time Event Flow
Backend utilizes Redis Pub/Sub to push events to active WebSocket connections.
