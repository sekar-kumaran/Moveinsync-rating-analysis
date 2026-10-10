# ============================================================
# MoveInSync FDE Case Study — Dockerfile
# ============================================================
# Multi-stage image:
#   Stage 1 (builder): install Python deps
#   Stage 2 (runtime): lean image with app + data
#
# Usage:
#   docker build -t moveinsync-fde .
#   docker run -p 8501:8501 moveinsync-fde
# ============================================================

# --- Stage 1: builder ---
FROM python:3.11-slim AS builder

WORKDIR /build

# System deps for matplotlib, reportlab, lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir python-docx nbconvert nbformat ipykernel

# --- Stage 2: runtime ---
FROM python:3.11-slim AS runtime

LABEL maintainer="FDE Candidate" \
      description="MoveInSync Play Store Review Analytics" \
      version="1.0"

WORKDIR /app

# Install only runtime libs (not build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project files
COPY . /app

# Create directories that may not exist
RUN mkdir -p data/raw data/processed data/sample \
             reports/figures deliverables models notebooks

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default: run the dashboard
# Override with: docker run moveinsync-fde python src/collect_reviews.py
CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
