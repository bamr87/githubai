# AI-Seed Multi-Stage Container Build
# Following path-based development and container-first principles

# Base stage with common dependencies
FROM node:18-alpine AS base
WORKDIR /app

# Install system dependencies for multiple language support
RUN apk add --no-cache \
    bash \
    curl \
    git \
    python3 \
    py3-pip \
    && rm -rf /var/cache/apk/*

# Development stage
FROM base AS development
ENV NODE_ENV=development
ENV AI_SEED_ENV=development
ENV PATH=/app/node_modules/.bin:$PATH
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Install development tools
RUN npm install -g nodemon eslint prettier && \
    pip3 install --upgrade pip --break-system-packages

# Copy package files for better caching
COPY src/package*.json ./src/
COPY src/frontend/package*.json ./src/frontend/
COPY src/api/package*.json ./src/api/

# Install dependencies
RUN cd src && npm ci --include=dev
RUN cd src/frontend && npm ci --include=dev  
RUN cd src/api && npm ci --include=dev

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Make scripts executable
RUN chmod +x scripts/**/*.sh

# Expose development ports
EXPOSE 3000 8000 5000

# Development command
CMD ["npm", "run", "dev", "--prefix", "src"]

# Production stage
FROM base AS production
ENV NODE_ENV=production
ENV AI_SEED_ENV=production

# Copy package files
COPY src/package*.json ./src/
COPY src/api/requirements.txt ./src/api/

# Install production dependencies only
RUN cd src && npm ci --only=production
RUN cd src/api && pip3 install -r requirements.txt --break-system-packages

# Copy built application
COPY src/ ./src/

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Change ownership
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose production port
EXPOSE 3000

# Production command
CMD ["npm", "start", "--prefix", "src"]

# AI Evolution Engine stage
FROM python:3.11-slim AS ai-engine
WORKDIR /app

# Install system dependencies and update certificates
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Install Python AI/ML dependencies
COPY src/ai/requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy AI engine source
COPY src/ai/ ./

# Expose AI engine port
EXPOSE 5000

# AI engine command
CMD ["python", "main.py"]