# Stage 1: Build React Frontend
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve Frontend and Backend via Python FastAPI
FROM python:3.10-slim
WORKDIR /app

# Install system utilities needed by OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir fastapi uvicorn pydantic reportlab pillow numpy pandas matplotlib plotly

# Copy files
COPY --from=builder /app/dist ./dist
COPY backend ./backend

# Expose port
EXPOSE 8000

# Create data directory and ensure full write access for user 1000
RUN mkdir -p /app/backend/data && chmod -R 777 /app

# Retrain models during container startup if they are missing
WORKDIR /app/backend
CMD python -c "import os; import train_models; \
if not os.path.exists('plant_model.pth') or not os.path.exists('xray_model.pth'): \
    train_models.main()" && \
    uvicorn main:app --host 0.0.0.0 --port 8000
