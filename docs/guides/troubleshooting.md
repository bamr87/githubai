# Troubleshooting Guide

Common issues and solutions for GitHubAI.

## Docker & Services

### Services Won't Start

**Symptom**: `docker-compose up` fails

**Solutions**:

```bash
# Check Docker is running
docker ps

# Check for port conflicts
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # PostgreSQL

# Stop conflicting services
docker-compose down

# Remove volumes and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Database Connection Errors

**Symptom**: `django.db.utils.OperationalError: could not connect to server`

**Solutions**:

```bash
# Wait for database to be ready
docker-compose up -d db
sleep 10
docker-compose up web

# Reset database
docker-compose down -v
docker-compose up -d db
docker-compose exec web python manage.py migrate
```

### Frontend Not Loading

**Symptom**: `ERR_CONNECTION_REFUSED` at localhost:5173

**Solutions**:

```bash
# Check frontend service status
docker-compose ps frontend

# Check logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

## Authentication Errors

### GitHub API 401 Unauthorized

**Symptom**: `GitHubException: 401 Unauthorized`

**Solutions**:

1. **Verify token is set**:

   ```bash
   docker-compose exec web python -c "from django.conf import settings; print(settings.GITHUB_TOKEN[:10])"
   ```

2. **Check token permissions**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Verify token has `repo` scope
   - Regenerate if expired

3. **Update .env**:

   ```bash
   GITHUB_TOKEN=ghp_your_new_token_here
   ```

4. **Restart services**:

   ```bash
   docker-compose restart web
   ```

### AI Provider Authentication Failed

**Symptom**: `AIServiceException: API key invalid`

**Solutions**:

1. **Check AI configuration**:

   ```bash
   docker-compose exec web python manage.py configure_ai --check-keys
   ```

2. **Update .env**:

   ```bash
   AI_PROVIDER=xai  # or openai
   XAI_API_KEY=your_valid_key
   ```

3. **Test provider**:

   ```bash
   docker-compose exec web python manage.py test_ai_providers --test-provider xai
   ```

## API Errors

### CORS Errors in Browser

**Symptom**: `Access to fetch at ... has been blocked by CORS policy`

**Solutions**:

1. **Check CORS settings** in `apps/githubai/settings.py`:

   ```python
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:5173",
       "http://localhost:3000"
   ]
   ```

2. **Restart backend**:

   ```bash
   docker-compose restart web
   ```

3. **Verify frontend URL** in `frontend/.env`:

   ```bash
   VITE_API_URL=http://localhost:8000
   ```

### 500 Internal Server Error

**Symptom**: API returns 500 error

**Solutions**:

1. **Check logs**:

   ```bash
   docker-compose logs web --tail=50
   ```

2. **Enable debug mode** (development only):

   ```bash
   # In .env
   DJANGO_DEBUG=True
   ```

3. **Common causes**:
   - Missing environment variables
   - Database connection issues
   - AI provider API limits exceeded
   - Invalid API keys

### 400 Bad Request

**Symptom**: API returns 400 error

**Solutions**:

1. **Check request format**: Ensure JSON is valid
2. **Verify required fields**: Check API documentation
3. **Review validation errors** in response body
4. **Test with curl**:

   ```bash
   curl -X POST http://localhost:8000/api/chat/ \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}' -v
   ```

## Feature-Specific Issues

### Auto Issue: No Files Found

**Symptom**: "No files found for analysis"

**Solutions**:

1. **Check repository name format**: Must be `owner/repo`
2. **Verify file paths**: Use relative paths from repo root
3. **Try without --files flag**: Use default file selection

   ```bash
   docker-compose exec web python manage.py auto_issue \
     --chore-type code_quality \
     --dry-run
   ```

### Auto Issue: Analysis Takes Too Long

**Symptom**: Request times out after 30+ seconds

**Solutions**:

1. **Limit file scope**:

   ```bash
   --files "apps/**/*.py"  # More specific
   ```

2. **Use dry-run first**: Preview without creating issue
3. **Check AI provider status**: Verify provider is responsive

### Chat: AI Not Responding

**Symptom**: Message sent but no response

**Solutions**:

1. **Check backend logs**:

   ```bash
   docker-compose logs web | grep -i error
   ```

2. **Verify AI provider configuration**:

   ```bash
   docker-compose exec web env | grep AI_
   ```

3. **Test AI service directly**:

   ```bash
   docker-compose exec web python manage.py shell
   >>> from core.services import AIService
   >>> service = AIService()
   >>> response = service.call_ai_chat("system", "test")
   >>> print(response)
   ```

### Chat: Slow Response Times

**Symptom**: Responses take >10 seconds

**Solutions**:

1. **Check network connectivity**: Verify internet connection
2. **Review AI provider status**: Check status page
3. **Enable caching**: Verify caching is working
4. **Reduce token limits**: Lower `MAX_TOKENS` in .env

## Performance Issues

### High Memory Usage

**Solutions**:

```bash
# Check container stats
docker stats

# Restart services
docker-compose restart

# Clear old logs
docker-compose logs --tail=0 > /dev/null
```

### Slow Database Queries

**Solutions**:

```bash
# Check database size
docker-compose exec db psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('githubai'));"

# Clear old API logs
docker-compose exec web python manage.py shell
>>> from core.models import APILog
>>> APILog.objects.filter(created_at__lt='2025-01-01').delete()
```

## Development Issues

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'core.services.auto_issue_service'`

**Solutions**:

```bash
# Restart Django to reload code
docker-compose restart web

# Verify file exists
docker-compose exec web ls -la apps/core/services/

# Check Python path
docker-compose exec web python -c "import sys; print(sys.path)"
```

### Migrations Not Applying

**Symptom**: Database out of sync

**Solutions**:

```bash
# Show migration status
docker-compose exec web python manage.py showmigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# If stuck, reset (development only)
docker-compose down -v
docker-compose up -d db
docker-compose exec web python manage.py migrate
```

### Tests Failing

**Symptom**: pytest tests fail

**Solutions**:

```bash
# Run specific failing test
docker-compose exec web pytest tests/test_file.py::test_name -vv

# Clear pytest cache
docker-compose exec web pytest --cache-clear

# Check test database
docker-compose exec web pytest --create-db
```

## Logs and Debugging

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs frontend

# Follow logs (live)
docker-compose logs -f web

# Last N lines
docker-compose logs --tail=50 web

# Grep for errors
docker-compose logs web | grep -i error
```

### Enable Debug Logging

```python
# In apps/githubai/settings.py
LOGGING = {
    'loggers': {
        'githubai': {
            'level': 'DEBUG',  # Change from INFO
        }
    }
}
```

### Django Shell Debugging

```bash
docker-compose exec web python manage.py shell

# Test service
>>> from core.services import AutoIssueService
>>> service = AutoIssueService()
>>> service.list_chore_types()

# Check database
>>> from core.models import Issue
>>> Issue.objects.all().count()
```

## Common Error Messages

### "This field is required"

**Cause**: Missing required field in API request

**Solution**: Check API documentation for required fields

### "Invalid choice"

**Cause**: Invalid value for choice field (e.g., chore_type)

**Solution**: Use `--list-chores` to see valid options

### "Repository not found"

**Cause**: Invalid repository name or insufficient permissions

**Solution**: Verify repo name format and GitHub token permissions

### "Rate limit exceeded"

**Cause**: Too many GitHub API requests

**Solution**: Wait for rate limit reset or upgrade GitHub plan

## Getting More Help

### Check Documentation

- [User Guides](../guides/)
- [API Reference](../api/)
- [Development Docs](.)

### Review Logs

```bash
# Application logs
docker-compose logs web

# Database logs
docker-compose logs db

# All logs
docker-compose logs
```

### Report Issues

If you can't resolve the issue:

1. **Gather information**:
   - Error message
   - Docker logs
   - Steps to reproduce
   - Environment details

2. **Search existing issues**: <https://github.com/bamr87/githubai/issues>

3. **Create new issue**: <https://github.com/bamr87/githubai/issues/new>

## Prevention Tips

1. **Keep services updated**: Regularly pull latest changes
2. **Monitor logs**: Check for warnings
3. **Backup data**: Export important data regularly
4. **Use dry-run**: Test before creating actual issues
5. **Set alerts**: Monitor AI API usage and costs
6. **Document custom changes**: Track any local modifications
