# AutonomyLoops Production container image
# Multi-stage build for minimal runtime footprint

FROM python:3.12-slim AS builder

WORKDIR /build
COPY pyproject.toml README.md ./
COPY autonomy_loops/ autonomy_loops/
COPY roles/ roles/
COPY modes/ modes/
COPY plugins/ plugins/
COPY pipelines/ pipelines/

RUN pip install --no-cache-dir --prefix=/install .

# --- Runtime image ---
FROM python:3.12-slim

# Security: run as non-root
RUN useradd --create-home --shell /bin/bash agent
WORKDIR /app

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy steering files
COPY roles/ roles/
COPY modes/ modes/
COPY plugins/ plugins/
COPY pipelines/ pipelines/
COPY autonomy-loops.example.yaml autonomy-loops.yaml

# Drop to non-root user
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=5s \
    CMD python -c "from autonomy_loops import __version__; print(__version__)"

ENTRYPOINT ["autonomy-loops"]
CMD ["--help"]
