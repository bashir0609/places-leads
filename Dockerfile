# ── Stage 1: Build React frontend ────────────────────────────
FROM node:18-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ ./
RUN REACT_APP_API_URL="" npm run build

# ── Stage 2: Python backend + serve React static files ─────────
FROM python:3.11-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=frontend-build /frontend/build /app/frontend/build

ENV PYTHONUNBUFFERED=1
ENV FRONTEND_BUILD=/app/frontend/build
EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
