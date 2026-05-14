# ═══════════════════════════════════════════════════════════════════
#  AI Text Summarizer  —  Production Dockerfile
#
#  Multi-stage build:
#    stage 1 (builder)  —  install all Python packages
#    stage 2 (runtime)  —  copy wheels only; no build toolchain in prod
#
#  NOTE: Final image will be large (~3-5 GB) because of PyTorch.
#        This is expected for ML workloads.
# ═══════════════════════════════════════════════════════════════════

# ── Build args (populated by CI) ────────────────────────────────────
ARG PYTHON_VERSION=3.10

# ══════════════════════════════════════════════════════════════════════
#  STAGE 1 — builder
# ══════════════════════════════════════════════════════════════════════
FROM python:${PYTHON_VERSION}-slim AS builder

WORKDIR /build

# Install C build tools needed by some Python packages (e.g., tokenizers)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only the dependency manifest first (maximises layer cache hits)
COPY requirements.txt .

# Install all packages into /build/wheels so the runtime stage
# can copy them without carrying the build toolchain
RUN python -m pip install --upgrade pip && \
    pip install \
        --prefix=/build/install \
        --no-cache-dir \
        --compile \
        -r requirements.txt

# ══════════════════════════════════════════════════════════════════════
#  STAGE 2 — runtime
# ══════════════════════════════════════════════════════════════════════
FROM python:${PYTHON_VERSION}-slim AS runtime

# ── Build-time metadata labels ────────────────────────────────────────
ARG BUILD_DATE
ARG GIT_COMMIT
ARG GIT_BRANCH
ARG PYTHON_VERSION=3.10

LABEL maintainer="navneet"
LABEL org.opencontainers.image.title="AI Text Summarizer"
LABEL org.opencontainers.image.description="FastAPI-based AI text summarization service"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"
LABEL org.opencontainers.image.source="https://github.com/navneetsxngh/TextSummarizer"

# ── Runtime system dependencies ───────────────────────────────────────
# libgomp1 : required by PyTorch for OpenMP multithreading
# curl     : required by the HEALTHCHECK command
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ── Create a non-root user (security best practice) ───────────────────
RUN groupadd --system appgroup && \
    useradd  --system \
             --gid  appgroup \
             --home /app \
             --shell /sbin/nologin \
             appuser

# ── Copy installed packages from builder stage ────────────────────────
COPY --from=builder /build/install /usr/local

# ── Set working directory ─────────────────────────────────────────────
WORKDIR /app

# ── Copy application source code ─────────────────────────────────────
# Copy in layers so unchanged code layers are cached
COPY --chown=appuser:appgroup src/       ./src/
COPY --chown=appuser:appgroup config/    ./config/
COPY --chown=appuser:appgroup templates/ ./templates/
COPY --chown=appuser:appgroup static/    ./static/
COPY --chown=appuser:appgroup app.py     ./app.py
COPY --chown=appuser:appgroup main.py    ./main.py
COPY --chown=appuser:appgroup params.yaml ./params.yaml

# ── Create directories for model artifacts (written at runtime) ───────
# The actual model weights are NOT baked in — they are downloaded /
# mounted via EFS or S3 at container start time.
RUN mkdir -p \
        artifacts/model_trainer/pegasus-samsum-model \
        artifacts/tokenizer \
        logs \
    && chown -R appuser:appgroup artifacts logs

# ── Runtime environment ───────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    # Suppress HuggingFace progress bars in production logs
    TRANSFORMERS_VERBOSITY=error \
    HF_HUB_DISABLE_PROGRESS_BARS=1 \
    # Reduce tokenizer thread noise
    TOKENIZERS_PARALLELISM=false \
    PORT=8080

# ── Switch to non-root user ───────────────────────────────────────────
USER appuser

EXPOSE 8080

# ── Health check ──────────────────────────────────────────────────────
# FastAPI returns 200 on GET /  after the frontend PR
HEALTHCHECK \
    --interval=30s \
    --timeout=10s \
    --start-period=60s \
    --retries=3 \
    CMD curl -fsSL http://localhost:8080/ -o /dev/null \
        || exit 1

# ── Start uvicorn ─────────────────────────────────────────────────────
# workers=2 is safe for ML workloads (each worker loads the model separately).
# Increase to 4 only if you have enough RAM for multiple model copies.
CMD ["uvicorn", "app:app", \
     "--host",       "0.0.0.0", \
     "--port",       "8080", \
     "--workers",    "2", \
     "--log-level",  "info", \
     "--access-log", \
     "--proxy-headers"]
