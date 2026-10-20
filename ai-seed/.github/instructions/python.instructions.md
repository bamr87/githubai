---
file: python.instructions.md
description: Python-specific AI instructions for development standards, patterns, and best practices in container environments
author: AI-Seed Team <team@ai-seed.org>
created: 2025-07-19
lastModified: 2025-07-19
version: 1.0.0
relatedIssues: []
relatedEvolutions: []
dependencies:
  - space.instructions.md: Foundation principles and path-based development
  - project.instructions.md: Project-specific context and requirements
containerRequirements:
  baseImage: 
    - python:3.11-slim
    - python:3.11-alpine
  exposedPorts:
    - 8000/tcp
    - 5000/tcp
  volumes:
    - /app/src:rw
    - /app/data:rw
  environment:
    PYTHONPATH: /app
    PYTHONUNBUFFERED: 1
  resources:
    cpu: 0.5-2.0
    memory: 512MiB-2GiB
  healthCheck: python -c "import sys; sys.exit(0)"
paths:
  python-development-path: Virtual env setup → coding → testing → containerization
  data-processing-path: Input validation → transformation → output with error handling
  api-service-path: Request handling → business logic → response formatting
changelog:
  - date: 2025-07-19
    change: Initial creation
    author: AI-Seed Team
usage: Reference for all Python development within container environments
notes: Emphasizes path-based development and container-first principles
---

# Python Language Instructions

These instructions provide comprehensive guidance for Python development within the AI-seed ecosystem, emphasizing container-first development, path-based architecture, and AI-assisted coding practices.

## Python Environment Setup

### Container-First Python Development

#### Base Container Configuration
```dockerfile
# Multi-stage build for Python applications
FROM python:3.11-slim AS base
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base AS development
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1

# Copy requirements first for better caching
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Production stage
FROM base AS production
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY src/ ./src/
USER 1000:1000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "src.main:app"]
```

#### Virtual Environment Path
Even within containers, maintain virtual environments for development:
```bash
# Container entry script
python -m venv /app/venv
source /app/venv/bin/activate
pip install -r requirements-dev.txt
```

### Dependency Management

#### Requirements Structure
- `requirements.txt`: Production dependencies only
- `requirements-dev.txt`: Development dependencies (includes requirements.txt)
- `requirements-test.txt`: Testing-specific dependencies

#### Path-Based Dependency Organization
```python
# Path: dependency-resolution-path
# requirements.txt - Production path
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# requirements-dev.txt - Development path
-r requirements.txt
pytest==7.4.3
black==23.11.0
mypy==1.7.1
pre-commit==3.5.0

# requirements-test.txt - Testing path
-r requirements.txt
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
```

## Code Structure and Organization

### Path-Based Module Organization

#### Directory Structure
```
src/
├── __init__.py
├── main.py                 # Application entry point
├── core/                   # Core business logic path
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── exceptions.py      # Custom exception hierarchy
│   └── logging.py         # Centralized logging
├── api/                    # API service path
│   ├── __init__.py
│   ├── routes/            # Endpoint definitions
│   ├── middleware/        # Request/response processing
│   └── schemas/           # Data validation models
├── domain/                 # Business domain path
│   ├── __init__.py
│   ├── models/            # Domain entities
│   ├── services/          # Business logic
│   └── repositories/      # Data access abstractions
├── infrastructure/        # External service path
│   ├── __init__.py
│   ├── database/          # Database connections
│   ├── external/          # Third-party integrations
│   └── storage/           # File and blob storage
└── utils/                  # Utility path
    ├── __init__.py
    ├── helpers.py         # General utility functions
    └── decorators.py      # Reusable decorators
```

### Naming Conventions Following Natural Paths

#### Variables and Functions
```python
# Path: data-flow-naming
input_data = load_raw_data()           # Entry point
validated_data = validate_input(input_data)  # Validation path
processed_data = transform_data(validated_data)  # Processing path
output_result = format_output(processed_data)    # Exit point

# Function naming reflects position in execution path
def validate_input_data(data: dict) -> dict:
    """Entry point for data validation path."""
    pass

def process_validated_data(data: dict) -> dict:
    """Core processing in the transformation path."""
    pass

def format_processed_output(data: dict) -> str:
    """Final formatting in the output path."""
    pass
```

#### Class Organization
```python
# Path: object-lifecycle-management
class DataPipeline:
    """Orchestrates the complete data processing path."""
    
    def __init__(self):
        self.path_history: List[str] = []
        self.error_recovery_path: Optional[Callable] = None
    
    def execute_path(self, data: Any) -> Any:
        """Follow the complete processing path."""
        try:
            # Path segment 1: Validation
            validated = self._validate_data(data)
            self.path_history.append("validation")
            
            # Path segment 2: Processing
            processed = self._process_data(validated)
            self.path_history.append("processing")
            
            # Path segment 3: Output
            result = self._format_output(processed)
            self.path_history.append("output")
            
            return result
        except Exception as e:
            return self._handle_error_path(e)
    
    def _handle_error_path(self, error: Exception) -> Any:
        """Alternative path for error conditions."""
        if self.error_recovery_path:
            return self.error_recovery_path(error)
        raise
```

## Error Handling and Path Management

### Path-Aware Exception Hierarchy
```python
# Path: error-classification-hierarchy
class PathError(Exception):
    """Base exception for path-related errors."""
    
    def __init__(self, message: str, path_context: str = None):
        super().__init__(message)
        self.path_context = path_context
        self.timestamp = datetime.utcnow()

class ValidationPathError(PathError):
    """Errors in the data validation path."""
    pass

class ProcessingPathError(PathError):
    """Errors in the data processing path."""
    pass

class OutputPathError(PathError):
    """Errors in the output generation path."""
    pass

# Usage with path context
try:
    result = process_data(input_data)
except ValidationError as e:
    raise ValidationPathError(
        f"Validation failed: {e}",
        path_context="input-validation-path"
    )
```

### Fallback Path Implementation
```python
# Path: error-recovery-patterns
def execute_with_fallback_path(
    primary_func: Callable,
    fallback_func: Callable,
    *args,
    **kwargs
) -> Any:
    """Execute function with automatic fallback path."""
    try:
        return primary_func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Primary path failed: {e}, switching to fallback")
        return fallback_func(*args, **kwargs)

# Decorator for automatic path fallback
def with_fallback_path(fallback_func: Callable):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return execute_with_fallback_path(func, fallback_func, *args, **kwargs)
        return wrapper
    return decorator

@with_fallback_path(lambda x: {"error": "processing_failed", "input": x})
def process_user_data(data: dict) -> dict:
    """Process user data with automatic fallback."""
    # Primary processing path
    return complex_processing(data)
```

## Testing Patterns and Paths

### Path-Based Test Organization
```python
# Path: test-execution-hierarchy
import pytest
from unittest.mock import Mock, patch

class TestDataProcessingPaths:
    """Test suite for data processing paths."""
    
    def test_happy_path_execution(self):
        """Test successful execution through all path segments."""
        pipeline = DataPipeline()
        test_data = {"value": 42, "type": "number"}
        
        result = pipeline.execute_path(test_data)
        
        assert pipeline.path_history == ["validation", "processing", "output"]
        assert result["status"] == "success"
    
    def test_validation_error_path(self):
        """Test error path when validation fails."""
        pipeline = DataPipeline()
        invalid_data = {"invalid": "data"}
        
        with pytest.raises(ValidationPathError) as exc_info:
            pipeline.execute_path(invalid_data)
        
        assert exc_info.value.path_context == "input-validation-path"
    
    def test_fallback_path_activation(self):
        """Test automatic fallback path execution."""
        @with_fallback_path(lambda x: {"fallback": True})
        def failing_function(data):
            raise ProcessingError("Simulated failure")
        
        result = failing_function({"test": "data"})
        assert result["fallback"] is True

# Container-based test execution
@pytest.fixture
def container_environment():
    """Set up containerized test environment."""
    return {
        "database_url": "sqlite:///test.db",
        "redis_url": "redis://localhost:6379/1",
        "log_level": "DEBUG"
    }
```

### Async Path Testing
```python
# Path: asynchronous-execution-testing
import asyncio
import pytest

class TestAsyncPaths:
    """Test asynchronous execution paths."""
    
    @pytest.mark.asyncio
    async def test_async_pipeline_path(self):
        """Test async data processing pipeline."""
        async def async_process_data(data):
            await asyncio.sleep(0.1)  # Simulate async operation
            return {"processed": data}
        
        pipeline = AsyncDataPipeline()
        result = await pipeline.execute_async_path({"test": "data"})
        
        assert result["processed"]["test"] == "data"
        assert "async_processing" in pipeline.path_history
    
    @pytest.mark.asyncio
    async def test_concurrent_path_execution(self):
        """Test multiple paths executing concurrently."""
        tasks = [
            async_process_data(f"data_{i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        assert len(results) == 5
        assert all(not isinstance(r, Exception) for r in results)
```

## API Development Patterns

### FastAPI Path-Based Development
```python
# Path: api-request-response-cycle
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="AI-Seed API", version="1.0.0")

class DataRequest(BaseModel):
    """Request model for data processing path."""
    data: dict
    processing_options: Optional[dict] = None

class DataResponse(BaseModel):
    """Response model for successful path completion."""
    result: dict
    path_taken: list[str]
    processing_time: float

@app.middleware("http")
async def path_tracking_middleware(request, call_next):
    """Middleware to track request paths."""
    start_time = time.time()
    request.state.path_history = []
    
    response = await call_next(request)
    
    processing_time = time.time() - start_time
    response.headers["X-Path-History"] = ",".join(request.state.path_history)
    response.headers["X-Processing-Time"] = str(processing_time)
    
    return response

@app.post("/process", response_model=DataResponse)
async def process_data_endpoint(
    request: DataRequest,
    processor: DataProcessor = Depends(get_data_processor)
):
    """Main data processing endpoint following defined paths."""
    try:
        # Path: request-validation → processing → response-formatting
        result = await processor.execute_async_path(request.data)
        
        return DataResponse(
            result=result,
            path_taken=processor.path_history,
            processing_time=processor.last_execution_time
        )
    except PathError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": str(e),
                "path_context": e.path_context,
                "timestamp": e.timestamp.isoformat()
            }
        )

# Dependency injection for path components
async def get_data_processor() -> DataProcessor:
    """Factory for data processor with configured paths."""
    processor = DataProcessor()
    processor.add_validation_path(validate_business_rules)
    processor.add_processing_path(apply_transformations)
    processor.add_output_path(format_api_response)
    return processor
```

## Data Validation and Schema Management

### Pydantic Models with Path Context
```python
# Path: data-model-validation-hierarchy
from pydantic import BaseModel, validator, Field
from typing import Union, Optional
from datetime import datetime

class BaseDataModel(BaseModel):
    """Base model with path tracking capabilities."""
    
    class Config:
        # Path: configuration-inheritance
        validate_assignment = True
        use_enum_values = True
        allow_population_by_field_name = True
    
    def validate_path(self, path_name: str) -> bool:
        """Validate model according to specific path requirements."""
        # Override in subclasses for path-specific validation
        return True

class InputDataModel(BaseDataModel):
    """Model for data entering the processing path."""
    
    data_id: str = Field(..., description="Unique identifier for data")
    content: dict = Field(..., description="Raw data content")
    processing_hints: Optional[dict] = Field(None, description="Path optimization hints")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('content')
    def validate_content_structure(cls, v):
        """Ensure content follows expected path requirements."""
        if not isinstance(v, dict):
            raise ValueError("Content must be a dictionary for processing path")
        
        required_keys = ['type', 'payload']
        if not all(key in v for key in required_keys):
            raise ValueError(f"Content missing required keys: {required_keys}")
        
        return v
    
    def validate_path(self, path_name: str) -> bool:
        """Validate for specific processing paths."""
        if path_name == "ml_processing":
            return 'features' in self.content.get('payload', {})
        elif path_name == "data_transformation":
            return 'schema' in self.processing_hints or {}
        return super().validate_path(path_name)

class OutputDataModel(BaseDataModel):
    """Model for data exiting the processing path."""
    
    result: Union[dict, list, str, int, float]
    path_executed: list[str] = Field(default_factory=list)
    execution_metadata: dict = Field(default_factory=dict)
    success: bool = True
    error_details: Optional[str] = None
```

## Logging and Monitoring Paths

### Path-Aware Logging System
```python
# Path: observability-and-monitoring
import logging
import json
from datetime import datetime
from contextlib import contextmanager
from typing import Any, Dict

class PathLogger:
    """Logger that tracks execution paths and performance."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.current_path: Optional[str] = None
        self.path_stack: List[str] = []
        self.path_metrics: Dict[str, Any] = {}
    
    @contextmanager
    def path_context(self, path_name: str):
        """Context manager for path execution tracking."""
        start_time = datetime.utcnow()
        self.enter_path(path_name)
        
        try:
            yield self
        except Exception as e:
            self.log_path_error(path_name, e)
            raise
        finally:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.exit_path(path_name, execution_time)
    
    def enter_path(self, path_name: str):
        """Enter a new execution path."""
        self.path_stack.append(path_name)
        self.current_path = path_name
        
        self.logger.info(
            "Entering path",
            extra={
                "path_name": path_name,
                "path_stack": self.path_stack.copy(),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def exit_path(self, path_name: str, execution_time: float):
        """Exit the current execution path."""
        if self.path_stack and self.path_stack[-1] == path_name:
            self.path_stack.pop()
        
        self.current_path = self.path_stack[-1] if self.path_stack else None
        
        # Track path performance
        if path_name not in self.path_metrics:
            self.path_metrics[path_name] = {
                "executions": 0,
                "total_time": 0.0,
                "avg_time": 0.0
            }
        
        metrics = self.path_metrics[path_name]
        metrics["executions"] += 1
        metrics["total_time"] += execution_time
        metrics["avg_time"] = metrics["total_time"] / metrics["executions"]
        
        self.logger.info(
            "Exiting path",
            extra={
                "path_name": path_name,
                "execution_time": execution_time,
                "path_metrics": metrics,
                "remaining_stack": self.path_stack.copy()
            }
        )
    
    def log_path_error(self, path_name: str, error: Exception):
        """Log errors with path context."""
        self.logger.error(
            "Path execution error",
            extra={
                "path_name": path_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "path_stack": self.path_stack.copy()
            },
            exc_info=True
        )

# Usage example
logger = PathLogger(__name__)

async def process_data_with_logging(data: dict) -> dict:
    """Data processing with comprehensive path logging."""
    
    with logger.path_context("data_validation"):
        validated_data = validate_input_data(data)
    
    with logger.path_context("data_processing"):
        processed_data = await process_validated_data(validated_data)
    
    with logger.path_context("output_formatting"):
        result = format_output_data(processed_data)
    
    return result
```

## Container Integration Patterns

### Docker-Compose Development Setup
```yaml
# Path: multi-container-development-environment
version: '3.8'

services:
  # Main application service
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    volumes:
      - ./src:/app/src:rw
      - ./tests:/app/tests:rw
      - python_cache:/app/.cache
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=DEBUG
      - DATABASE_URL=postgresql://user:pass@db:5432/aiSeed
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    networks:
      - ai-seed-network
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  # Database service for development
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=aiSeed
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - ai-seed-network

  # Redis for caching and session management
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - ai-seed-network

  # Testing service
  test:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    volumes:
      - ./src:/app/src:ro
      - ./tests:/app/tests:ro
      - test_reports:/app/reports:rw
    environment:
      - PYTHONPATH=/app
      - DATABASE_URL=postgresql://user:pass@test_db:5432/test
    depends_on:
      - test_db
    networks:
      - ai-seed-network
    command: pytest tests/ --cov=src --cov-report=html:/app/reports/

  test_db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=test
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    networks:
      - ai-seed-network

volumes:
  postgres_data:
  python_cache:
  test_reports:

networks:
  ai-seed-network:
    driver: bridge
```

## Performance Optimization Paths

### Caching Strategies
```python
# Path: performance-optimization-through-caching
import functools
import asyncio
from typing import Any, Callable, Optional
import hashlib
import json

class PathCache:
    """Cache implementation aware of execution paths."""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._path_stats: Dict[str, Dict[str, int]] = {}
    
    def cache_key(self, func: Callable, args: tuple, kwargs: dict, path_context: str = None) -> str:
        """Generate cache key incorporating path context."""
        func_name = f"{func.__module__}.{func.__name__}"
        args_str = json.dumps(args, sort_keys=True, default=str)
        kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
        
        base_key = f"{func_name}:{args_str}:{kwargs_str}"
        if path_context:
            base_key = f"{path_context}:{base_key}"
        
        return hashlib.md5(base_key.encode()).hexdigest()
    
    def get(self, key: str, path_context: str = None) -> Optional[Any]:
        """Retrieve cached value with path statistics."""
        if path_context:
            self._update_path_stats(path_context, "cache_get")
        
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, path_context: str = None):
        """Store value in cache with path tracking."""
        self._cache[key] = value
        
        if path_context:
            self._update_path_stats(path_context, "cache_set")
    
    def _update_path_stats(self, path_context: str, operation: str):
        """Update cache statistics for path analysis."""
        if path_context not in self._path_stats:
            self._path_stats[path_context] = {"cache_get": 0, "cache_set": 0, "cache_hit": 0}
        
        self._path_stats[path_context][operation] += 1

# Global cache instance
path_cache = PathCache()

def cached_path(path_context: str = None, ttl: int = 3600):
    """Decorator for caching function results with path awareness."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = path_cache.cache_key(func, args, kwargs, path_context)
            
            # Try to get from cache
            cached_result = path_cache.get(cache_key, path_context)
            if cached_result is not None:
                path_cache._update_path_stats(path_context, "cache_hit")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            path_cache.set(cache_key, result, path_context)
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = path_cache.cache_key(func, args, kwargs, path_context)
            
            cached_result = path_cache.get(cache_key, path_context)
            if cached_result is not None:
                path_cache._update_path_stats(path_context, "cache_hit")
                return cached_result
            
            result = func(*args, **kwargs)
            path_cache.set(cache_key, result, path_context)
            
            return result
        
        # Return appropriate wrapper based on function type
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

# Usage examples
@cached_path(path_context="data_processing", ttl=1800)
async def expensive_data_transformation(data: dict) -> dict:
    """Expensive transformation with caching."""
    await asyncio.sleep(2)  # Simulate expensive operation
    return {"transformed": data, "timestamp": datetime.utcnow().isoformat()}

@cached_path(path_context="ml_inference")
def predict_user_behavior(user_features: dict) -> dict:
    """ML inference with result caching."""
    # Simulate ML model inference
    return {"prediction": "high_engagement", "confidence": 0.85}
```

## Integration with Other Instructions

This Python instruction file works in conjunction with:
- **space.instructions.md**: Foundational path-based principles
- **project.instructions.md**: AI-seed specific requirements
- **test.instructions.md**: Comprehensive testing strategies
- **ci-cd.instructions.md**: Automated deployment and integration
- **ai-agent.instructions.md**: AI-assisted development patterns

## Future Evolution

### Advanced Python Patterns
- **Type System Evolution**: Enhanced typing with path-aware type checking
- **Async Path Optimization**: Advanced asynchronous execution patterns
- **AI-Generated Code**: Python code generation with path optimization
- **Performance Profiling**: Automated path performance analysis

### Container Integration Enhancements
- **Multi-Architecture Builds**: ARM64 and AMD64 optimized containers
- **Distroless Images**: Minimal attack surface for production
- **Health Check Evolution**: Sophisticated health monitoring paths
- **Resource Optimization**: Dynamic resource allocation based on path usage
