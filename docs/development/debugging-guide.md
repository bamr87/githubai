# VS Code Remote Debugging Guide

This guide explains how to use VS Code's debugging capabilities with the GitHubAI Docker development environment.

## Overview

GitHubAI supports remote debugging using `debugpy`, allowing you to:

- Set breakpoints in VS Code and debug Django code running in Docker containers
- Debug Celery workers and beat scheduler
- Step through code, inspect variables, and use all VS Code debugging features

## Prerequisites

- VS Code with Python extension installed
- Docker and Docker Compose
- GitHubAI repository cloned locally

## Quick Start

1. **Start the Debug Stack**:
   - Open VS Code Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
   - Run task: `Docker: Start Debug Stack`
   - Or run manually:

     ```bash
     docker-compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.debug.yml up
     ```

2. **Attach VS Code Debugger**:
   - Open the Debug panel (`Cmd+Shift+D` / `Ctrl+Shift+D`)
   - Select "Docker: Attach to Django (web)" from the dropdown
   - Click the green play button or press `F5`

3. **Set Breakpoints and Debug**:
   - Set breakpoints in your code by clicking in the gutter
   - Trigger the code path (via API call, management command, etc.)
   - VS Code will pause at your breakpoints

## Debug Configurations

The following debug configurations are available in `.vscode/launch.json`:

### Docker: Attach to Django (web)

Connects to the Django web server on port 5678.

- Use for debugging views, serializers, models, and services
- Path mapping: `${workspaceFolder}` → `/app`

### Docker: Attach to Celery Worker

Connects to the Celery worker on port 5679.

- Use for debugging async tasks and background jobs
- Path mapping: `${workspaceFolder}` → `/app`

### Docker: Attach to Celery Beat

Connects to the Celery beat scheduler on port 5680.

- Use for debugging scheduled tasks
- Path mapping: `${workspaceFolder}` → `/app`

### Docker: Attach Django + Celery (Compound)

Attaches to both Django and Celery worker simultaneously.

- Useful when debugging request → task workflows

### Python: Debug Tests

Runs pytest with debugging enabled locally.

- Uses `githubai.settings_test` configuration
- Disables coverage and parallel execution for debugging

## VS Code Tasks

The following tasks are available via Command Palette (`Tasks: Run Task`):

| Task | Description |
|------|-------------|
| Docker: Start Debug Stack | Start db, redis, then web with debugpy |
| Docker: Start Full Debug Stack | Start all services with debugpy |
| Docker: Start Dev Stack | Standard development stack (no debugpy) |
| Docker: Stop All | Stop all containers |
| Docker: Run Migrations | Execute Django migrations |
| Docker: Run Tests | Run pytest in container |
| Docker: Run Tests (Current File) | Run tests for current file |
| Docker: Django Shell | Open Django shell |
| Docker: Rebuild Web Container | Rebuild the web container |
| Docker: View Logs (web) | Tail web container logs |
| Docker: View Logs (celery_worker) | Tail celery worker logs |

## Debug Ports

| Service | Port | Description |
|---------|------|-------------|
| Django (web) | 5678 | debugpy for Django web server |
| Celery Worker | 5679 | debugpy for Celery worker |
| Celery Beat | 5680 | debugpy for Celery beat scheduler |

## Configuration Files

### Docker Compose Debug Override

`infra/docker/docker-compose.debug.yml` - Overrides for debug mode:

- Starts services with `debugpy --wait-for-client`
- Exposes debugpy ports
- Sets `DJANGO_DEBUG=True` and `DEBUGPY_ENABLE=1`
- Uses `--noreload` for Django (required for debugging)
- Uses `--pool=solo --concurrency=1` for Celery (single-threaded debugging)

### VS Code Launch Configuration

`.vscode/launch.json` - Debug configurations:

- Remote attach configurations for each service
- Path mappings for source code
- Compound configuration for multi-service debugging

### VS Code Task Definitions

`.vscode/tasks.json` - Task definitions for common Docker operations.

## Debugging Workflow Examples

### Debug a View

1. Set a breakpoint in `apps/core/views.py`
2. Start debug stack and attach to Django
3. Make an API request (via browser, curl, or frontend)
4. VS Code pauses at breakpoint

### Debug a Celery Task

1. Set a breakpoint in `apps/core/tasks.py`
2. Start debug stack and attach to Celery Worker
3. Trigger the task (via API or management command)
4. VS Code pauses at breakpoint

### Debug a Service

1. Set a breakpoint in `apps/core/services/`
2. Attach to the appropriate container (Django or Celery)
3. Trigger code that calls the service
4. Step through the service logic

## Troubleshooting

### Debugger Won't Connect

- Ensure the container is running and waiting for client:

  ```bash
  docker logs web 2>&1 | grep debugpy
  ```

- Check port is exposed: `docker ps | grep 5678`
- Verify no other process is using the port

### Breakpoints Not Hit

- Ensure path mappings are correct in `launch.json`
- Verify you're attached to the correct container
- Check the code path is actually executed

### Performance Issues

- Debug mode is slower due to `--noreload` and debugpy overhead
- Use standard dev stack for non-debugging work
- Celery uses single concurrency in debug mode

### Import Errors

- The debug configuration includes `PYTHONPATH=${workspaceFolder}/apps`
- Verify imports work in the container first

## Tips

1. **Hot Reload Disabled**: The debug stack disables Django's auto-reload. Restart the container after code changes.

2. **Wait for Client**: The container waits for VS Code to attach before starting. Be patient on first connection.

3. **Conditional Breakpoints**: Use VS Code's conditional breakpoint feature to break only on specific conditions.

4. **Logpoints**: Use logpoints instead of print statements - they don't require restarting the container.

5. **Watch Expressions**: Add variables to the Watch panel for continuous monitoring.

## Related Documentation

- [Testing Guide](./testing-guide.md) - Running and debugging tests
- [Contributing Guide](./contributing.md) - Development workflow
- [Docker Configuration](../../infra/docker/) - Docker compose files
