FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc libgeos-dev libproj-dev \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# AI dependencies (heavier)
RUN pip install --no-cache-dir \
    ultralytics>=8.3.0 \
    paddlepaddle>=2.6.0 \
    paddleocr>=2.8.0 \
    pytesseract>=0.3.13 \
    scipy>=1.14.0 \
    supervision>=0.25.0

COPY backend/ ./backend/
COPY ai/ ./ai/
COPY camera_simulator/ ./camera_simulator/

CMD ["python", "-m", "camera_simulator.simulator", "--mode", "continuous"]
