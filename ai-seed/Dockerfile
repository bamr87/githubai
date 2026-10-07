# pinned: crewai publishes no release for Python 3.14, so pip backtracks to an
# ancient one whose numpy/regex sdists will not build (ai-seed#78). Hold at 3.13
# until crewai ships cp314 — see bamr87/bamr87 docs/DOCKER.md, image_overrides.
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash aiuser \
    && chown -R aiuser:aiuser /app
USER aiuser

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "src/main.py"]
