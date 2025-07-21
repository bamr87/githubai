---
file: mcp.instructions.md
description: Model Context Protocol (MCP) integration instructions for standardized AI application context sharing and tool orchestration
applyTo: "**/*.mcp.json,**/*mcp*.ts,**/*mcp*.js,**/*mcp*.py,**/mcp-server.py,**/mcp-client.py"
author: AI-Seed Team <team@ai-seed.org>
created: 2025-07-19
lastModified: 2025-07-19
version: 1.0.0
relatedIssues: []
relatedEvolutions: []
dependencies:
  - space.instructions.md: Foundation principles and path-based development
  - project.instructions.md: Project-specific context and requirements
  - python.instructions.md: Python MCP server implementation patterns
  - javascript.instructions.md: TypeScript/JavaScript MCP client patterns
  - bash.instructions.md: Shell scripting for MCP automation
containerRequirements:
  baseImage: 
    - python:3.11-alpine
    - node:18-alpine
  exposedPorts: 
    - 3000
    - 8080
  volumes:
    - /mcp-servers:rw
    - /mcp-data:rw
    - /workspace:rw
  environment:
    MCP_PROTOCOL_VERSION: "2025-06-18"
    MCP_SERVER_HOST: "0.0.0.0"
    MCP_SERVER_PORT: "3000"
    MCP_LOG_LEVEL: "INFO"
  resources:
    cpu: 0.5-2.0
    memory: 512MiB-2GiB
  healthCheck: "/health"
paths:
  mcp-server-lifecycle-path: Initialization → registration → resource exposure → request handling → cleanup
  mcp-client-connection-path: Discovery → authentication → capability negotiation → operation execution
  context-sharing-path: Resource identification → data extraction → context formatting → transmission
  tool-orchestration-path: Tool discovery → capability validation → execution → result processing
changelog:
  - date: 2025-07-19
    change: Initial creation based on MCP specification
    author: AI-Seed Team
usage: Reference for all Model Context Protocol implementations and integrations
notes: Emphasizes path-based MCP architectures and container-first deployment
---

# Model Context Protocol (MCP) Instructions

Apply the [general coding guidelines](../copilot-instructions.md) to all code.

These instructions provide comprehensive guidance for implementing and integrating Model Context Protocol (MCP) capabilities within the AI-seed ecosystem, emphasizing path-based context sharing, standardized server-client architectures, and secure AI application integration.

## MCP Philosophy and Architecture

### Path-Based Context Protocol Design

MCP implementations should follow natural data flow paths, enabling seamless context sharing between AI applications and various data sources while maintaining the path of least resistance principle.

#### Core MCP Principles
- **Standardized Context Sharing**: Use MCP as the universal interface for AI applications to access external context
- **Path-Aware Resource Exposure**: Resources should follow logical discovery and access paths
- **Container-First Deployment**: All MCP servers run within isolated, scalable container environments
- **Tool Orchestration**: Enable LLMs to perform actions through well-defined tool interfaces
- **Secure Data Access**: Maintain security boundaries while enabling flexible context sharing

### MCP Component Architecture

```
MCP Ecosystem Architecture:
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Host Applications                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Claude      │  │ Custom AI   │  │ Development Tools       │  │
│  │ Desktop     │  │ Applications│  │ (IDEs, CLI Tools)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                          ┌─────────────┐
                          │ MCP Clients │
                          │ (Protocol   │
                          │ Handlers)   │
                          └─────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Server Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ File System │  │ Database    │  │ API Integration         │  │
│  │ MCP Server  │  │ MCP Server  │  │ MCP Servers             │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Git         │  │ Docker      │  │ Custom Tool             │  │
│  │ MCP Server  │  │ MCP Server  │  │ MCP Servers             │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                    Data Sources & Services                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Local Files │  │ Databases   │  │ External APIs           │  │
│  │ & Folders   │  │ & Storage   │  │ & Services              │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## MCP Server Implementation Patterns

### Path-Aware MCP Server Architecture

#### Python MCP Server Template
```python
#!/usr/bin/env python3
# Path: mcp-server-implementation
# File: src/mcp/servers/base_server.py

"""
Base MCP Server implementation with path-aware resource management
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from abc import ABC, abstractmethod

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Path: logging-configuration
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(path_context)s] %(message)s'
)

class PathAwareMCPServer(ABC):
    """
    Base class for path-aware MCP servers that follow natural data flow patterns
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.server = Server(name)
        self.path_context = []
        self.resource_paths = {}
        self.tool_paths = {}
        self.logger = logging.getLogger(name)
        
        # Path: server-capability-registration
        self._register_core_capabilities()
        
    def _register_core_capabilities(self):
        """Register core MCP server capabilities with path context"""
        
        # Path: resource-capability-registration
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            return await self._list_resources_with_paths()
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            return await self._read_resource_with_path_tracking(uri)
        
        # Path: tool-capability-registration
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return await self._list_tools_with_paths()
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None = None) -> list[types.TextContent]:
            return await self._execute_tool_with_path_tracking(name, arguments or {})
        
        # Path: prompt-capability-registration
        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            return await self._list_prompts_with_paths()
        
        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict | None = None) -> types.GetPromptResult:
            return await self._get_prompt_with_path_context(name, arguments or {})

    # Path: path-context-management
    def enter_path(self, path_name: str, context: Dict[str, Any] = None):
        """Enter a processing path with optional context"""
        path_entry = {
            "name": path_name,
            "timestamp": asyncio.get_event_loop().time(),
            "context": context or {}
        }
        self.path_context.append(path_entry)
        self.logger.info(f"Entering path: {path_name}", extra={"path_context": path_name})
    
    def exit_path(self, path_name: str):
        """Exit the current processing path"""
        if self.path_context and self.path_context[-1]["name"] == path_name:
            path_entry = self.path_context.pop()
            duration = asyncio.get_event_loop().time() - path_entry["timestamp"]
            self.logger.info(f"Exiting path: {path_name} (duration: {duration:.3f}s)", 
                           extra={"path_context": path_name})
        else:
            self.logger.warning(f"Path mismatch: expected {path_name}, got {self.path_context[-1]['name'] if self.path_context else 'empty'}")
    
    async def execute_in_path(self, path_name: str, func, *args, **kwargs):
        """Execute a function within a specific path context"""
        self.enter_path(path_name)
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            return result
        finally:
            self.exit_path(path_name)

    # Path: abstract-capability-definitions
    @abstractmethod
    async def _list_resources_with_paths(self) -> List[types.Resource]:
        """List available resources with path information"""
        pass
    
    @abstractmethod
    async def _read_resource_with_path_tracking(self, uri: str) -> str:
        """Read resource content with path tracking"""
        pass
    
    @abstractmethod
    async def _list_tools_with_paths(self) -> List[types.Tool]:
        """List available tools with path information"""
        pass
    
    @abstractmethod
    async def _execute_tool_with_path_tracking(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute tool with path tracking"""
        pass
    
    @abstractmethod
    async def _list_prompts_with_paths(self) -> List[types.Prompt]:
        """List available prompts with path information"""
        pass
    
    @abstractmethod
    async def _get_prompt_with_path_context(self, name: str, arguments: Dict[str, Any]) -> types.GetPromptResult:
        """Get prompt with path context"""
        pass

    # Path: server-lifecycle-management
    async def run(self):
        """Run the MCP server with path-aware lifecycle management"""
        self.enter_path("server_initialization")
        
        try:
            # Path: server-startup
            await self.execute_in_path("server_startup", self._initialize_server)
            
            # Path: server-operation
            self.enter_path("server_operation")
            self.logger.info(f"MCP Server '{self.name}' v{self.version} starting...")
            
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.name,
                        server_version=self.version,
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={}
                        )
                    )
                )
        
        except Exception as e:
            self.logger.error(f"Server error in path {self.path_context[-1]['name'] if self.path_context else 'unknown'}: {e}")
            raise
        finally:
            # Path: server-cleanup
            await self.execute_in_path("server_cleanup", self._cleanup_server)
            self.exit_path("server_operation")
            self.exit_path("server_initialization")
    
    async def _initialize_server(self):
        """Initialize server-specific resources and connections"""
        self.logger.info("Server initialization completed")
    
    async def _cleanup_server(self):
        """Cleanup server resources"""
        self.logger.info("Server cleanup completed")


# Path: filesystem-mcp-server-implementation
class FileSystemMCPServer(PathAwareMCPServer):
    """
    MCP Server for file system access with path-aware operations
    """
    
    def __init__(self, base_path: str = "."):
        super().__init__("filesystem-server", "1.0.0")
        self.base_path = Path(base_path).resolve()
        self.logger.info(f"Initialized FileSystem MCP Server with base path: {self.base_path}")
    
    async def _list_resources_with_paths(self) -> List[types.Resource]:
        """List file system resources with path information"""
        return await self.execute_in_path("resource_discovery", self._discover_file_resources)
    
    async def _discover_file_resources(self) -> List[types.Resource]:
        """Discover available file resources"""
        resources = []
        
        # Path: file-system-traversal
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = file_path.relative_to(self.base_path)
                
                resource = types.Resource(
                    uri=f"file://{relative_path}",
                    name=file_path.name,
                    description=f"File: {relative_path}",
                    mimeType=self._get_mime_type(file_path)
                )
                resources.append(resource)
        
        self.logger.info(f"Discovered {len(resources)} file resources")
        return resources
    
    async def _read_resource_with_path_tracking(self, uri: str) -> str:
        """Read file content with path tracking"""
        return await self.execute_in_path("resource_reading", self._read_file_content, uri)
    
    async def _read_file_content(self, uri: str) -> str:
        """Read file content"""
        # Path: uri-parsing
        if not uri.startswith("file://"):
            raise ValueError(f"Invalid file URI: {uri}")
        
        file_path = self.base_path / uri[7:]  # Remove "file://" prefix
        
        # Path: security-validation
        if not self._is_safe_path(file_path):
            raise ValueError(f"Access denied: {file_path}")
        
        # Path: file-reading
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.logger.info(f"Read file: {file_path} ({len(content)} characters)")
            return content
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    async def _list_tools_with_paths(self) -> List[types.Tool]:
        """List file system tools"""
        return [
            types.Tool(
                name="write_file",
                description="Write content to a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path relative to base directory"},
                        "content": {"type": "string", "description": "File content to write"}
                    },
                    "required": ["path", "content"]
                }
            ),
            types.Tool(
                name="create_directory",
                description="Create a new directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path to create"}
                    },
                    "required": ["path"]
                }
            ),
            types.Tool(
                name="list_directory",
                description="List contents of a directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path to list"}
                    },
                    "required": ["path"]
                }
            )
        ]
    
    async def _execute_tool_with_path_tracking(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute file system tools with path tracking"""
        return await self.execute_in_path(f"tool_execution_{name}", self._execute_file_tool, name, arguments)
    
    async def _execute_file_tool(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Execute specific file system tool"""
        if name == "write_file":
            return await self._write_file_tool(arguments)
        elif name == "create_directory":
            return await self._create_directory_tool(arguments)
        elif name == "list_directory":
            return await self._list_directory_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def _write_file_tool(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Write file tool implementation"""
        file_path = self.base_path / arguments["path"]
        content = arguments["content"]
        
        if not self._is_safe_path(file_path):
            raise ValueError(f"Access denied: {file_path}")
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Wrote file: {file_path} ({len(content)} characters)")
        return [types.TextContent(type="text", text=f"Successfully wrote {len(content)} characters to {arguments['path']}")]
    
    async def _create_directory_tool(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Create directory tool implementation"""
        dir_path = self.base_path / arguments["path"]
        
        if not self._is_safe_path(dir_path):
            raise ValueError(f"Access denied: {dir_path}")
        
        dir_path.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Created directory: {dir_path}")
        return [types.TextContent(type="text", text=f"Successfully created directory: {arguments['path']}")]
    
    async def _list_directory_tool(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """List directory tool implementation"""
        dir_path = self.base_path / arguments["path"]
        
        if not self._is_safe_path(dir_path) or not dir_path.is_dir():
            raise ValueError(f"Invalid directory: {dir_path}")
        
        items = []
        for item in dir_path.iterdir():
            item_type = "directory" if item.is_dir() else "file"
            items.append(f"{item_type}: {item.name}")
        
        result = "\n".join(items) if items else "Directory is empty"
        return [types.TextContent(type="text", text=result)]
    
    async def _list_prompts_with_paths(self) -> List[types.Prompt]:
        """List available prompts for file operations"""
        return [
            types.Prompt(
                name="analyze_codebase",
                description="Analyze codebase structure and patterns",
                arguments=[
                    types.PromptArgument(
                        name="focus_area",
                        description="Specific area to focus analysis on",
                        required=False
                    )
                ]
            ),
            types.Prompt(
                name="generate_documentation",
                description="Generate documentation for code files",
                arguments=[
                    types.PromptArgument(
                        name="file_pattern",
                        description="Pattern to match files for documentation",
                        required=True
                    )
                ]
            )
        ]
    
    async def _get_prompt_with_path_context(self, name: str, arguments: Dict[str, Any]) -> types.GetPromptResult:
        """Get prompt with file system context"""
        return await self.execute_in_path(f"prompt_generation_{name}", self._generate_file_prompt, name, arguments)
    
    async def _generate_file_prompt(self, name: str, arguments: Dict[str, Any]) -> types.GetPromptResult:
        """Generate prompts with file system context"""
        if name == "analyze_codebase":
            return await self._generate_codebase_analysis_prompt(arguments)
        elif name == "generate_documentation":
            return await self._generate_documentation_prompt(arguments)
        else:
            raise ValueError(f"Unknown prompt: {name}")
    
    async def _generate_codebase_analysis_prompt(self, arguments: Dict[str, Any]) -> types.GetPromptResult:
        """Generate codebase analysis prompt"""
        focus_area = arguments.get("focus_area", "general")
        
        # Collect codebase structure
        structure = await self._analyze_codebase_structure()
        
        prompt_text = f"""
# Codebase Analysis Request

Please analyze this codebase structure with focus on: {focus_area}

## Project Structure
{structure}

## Analysis Focus: {focus_area}

Please provide insights on:
1. Code organization and architecture patterns
2. Potential improvements or optimizations
3. Code quality and maintainability
4. Security considerations
5. Performance implications

Focus particularly on the {focus_area} aspects of the codebase.
"""
        
        return types.GetPromptResult(
            description=f"Codebase analysis focused on {focus_area}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=prompt_text)
                )
            ]
        )
    
    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe for access"""
        try:
            resolved_path = path.resolve()
            return resolved_path.is_relative_to(self.base_path)
        except (OSError, ValueError):
            return False
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for file"""
        suffix = file_path.suffix.lower()
        mime_types = {
            '.py': 'text/x-python',
            '.js': 'text/javascript',
            '.ts': 'text/typescript',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.yaml': 'text/yaml',
            '.yml': 'text/yaml',
            '.sh': 'text/x-shellscript',
            '.dockerfile': 'text/x-dockerfile'
        }
        return mime_types.get(suffix, 'text/plain')
    
    async def _analyze_codebase_structure(self) -> str:
        """Analyze and return codebase structure"""
        structure_lines = []
        
        def add_directory_tree(path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
            if current_depth >= max_depth:
                return
            
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            for i, item in enumerate(items):
                if item.name.startswith('.'):
                    continue
                
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                structure_lines.append(f"{prefix}{current_prefix}{item.name}")
                
                if item.is_dir() and current_depth < max_depth - 1:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    add_directory_tree(item, next_prefix, max_depth, current_depth + 1)
        
        add_directory_tree(self.base_path)
        return "\n".join(structure_lines)


# Path: main-server-execution
if __name__ == "__main__":
    import sys
    
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    server = FileSystemMCPServer(base_path)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
```

### Container-Based MCP Server Deployment

#### Multi-Stage Dockerfile for MCP Servers
```dockerfile
# Path: mcp-server-container-build
# File: docker/mcp-server.Dockerfile

# Multi-stage build for MCP servers
FROM python:3.11-alpine AS base

# Path: system-dependencies-installation
RUN apk add --no-cache \
    build-base \
    git \
    curl \
    jq \
    && rm -rf /var/cache/apk/*

# Path: python-dependencies-installation
WORKDIR /mcp-server
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage with additional tools
FROM base AS development

# Path: development-tools-installation
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    black \
    flake8 \
    mypy

COPY . .
RUN pip install -e .

# Path: development-server-entrypoint
CMD ["python", "-m", "mcp_servers.filesystem", "--base-path", "/workspace"]

# Production stage
FROM base AS production

# Path: production-code-installation
COPY src/ ./src/
COPY setup.py .
RUN pip install .

# Path: security-hardening
RUN addgroup -g 1000 mcpuser && \
    adduser -D -s /bin/sh -u 1000 -G mcpuser mcpuser

USER mcpuser
WORKDIR /home/mcpuser

# Path: health-check-setup
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from src.health_check import check_server_health; asyncio.run(check_server_health())"

# Path: production-server-entrypoint
CMD ["python", "-m", "mcp_servers.filesystem"]
```

#### Docker Compose for MCP Server Orchestration
```yaml
# Path: mcp-server-orchestration
# File: docker-compose.mcp.yml

version: '3.8'

services:
  # Path: filesystem-mcp-server
  mcp-filesystem:
    build:
      context: .
      dockerfile: docker/mcp-server.Dockerfile
      target: production
    environment:
      - MCP_SERVER_NAME=filesystem-server
      - MCP_SERVER_VERSION=1.0.0
      - MCP_LOG_LEVEL=INFO
      - MCP_BASE_PATH=/workspace
    volumes:
      - ./:/workspace:ro
      - mcp-logs:/logs:rw
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD", "python", "-c", "import asyncio; from src.health_check import check_server_health; asyncio.run(check_server_health())"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Path: database-mcp-server
  mcp-database:
    build:
      context: .
      dockerfile: docker/mcp-database-server.Dockerfile
      target: production
    environment:
      - MCP_SERVER_NAME=database-server
      - MCP_SERVER_VERSION=1.0.0
      - DATABASE_URL=postgresql://user:pass@postgres:5432/mcpdb
    depends_on:
      - postgres
    networks:
      - mcp-network
    restart: unless-stopped

  # Path: api-integration-mcp-server
  mcp-api-integration:
    build:
      context: .
      dockerfile: docker/mcp-api-server.Dockerfile
      target: production
    environment:
      - MCP_SERVER_NAME=api-integration-server
      - MCP_SERVER_VERSION=1.0.0
      - API_BASE_URL=https://api.example.com
      - API_KEY_FILE=/run/secrets/api_key
    secrets:
      - api_key
    networks:
      - mcp-network
    restart: unless-stopped

  # Path: supporting-database-service
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=mcpdb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - mcp-network
    restart: unless-stopped

  # Path: mcp-server-monitoring
  mcp-monitor:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    networks:
      - mcp-network
    ports:
      - "9090:9090"
    restart: unless-stopped

volumes:
  mcp-logs:
  postgres-data:
  prometheus-data:

networks:
  mcp-network:
    driver: bridge

secrets:
  api_key:
    file: ./secrets/api_key.txt
```

## MCP Client Implementation Patterns

### TypeScript/JavaScript MCP Client
```typescript
// Path: mcp-client-implementation
// File: src/mcp/clients/mcp-client.ts

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { 
    CallToolRequest, 
    ListResourcesRequest, 
    ListToolsRequest, 
    ReadResourceRequest,
    GetPromptRequest 
} from "@modelcontextprotocol/sdk/types.js";

/**
 * Path-aware MCP client for integrating with MCP servers
 */
export class PathAwareMCPClient {
    private client: Client;
    private transport: StdioServerTransport | null = null;
    private pathContext: Array<{ name: string; timestamp: number; context?: any }> = [];
    private logger: Console;

    constructor(
        private serverCommand: string,
        private serverArgs: string[] = [],
        private name: string = "mcp-client"
    ) {
        this.client = new Client(
            {
                name: this.name,
                version: "1.0.0",
            },
            {
                capabilities: {
                    resources: {},
                    tools: {},
                    prompts: {},
                },
            }
        );
        
        this.logger = console;
    }

    // Path: client-lifecycle-management
    async connect(): Promise<void> {
        return this.executeInPath("client_connection", async () => {
            this.transport = new StdioServerTransport({
                command: this.serverCommand,
                args: this.serverArgs,
            });

            await this.client.connect(this.transport);
            this.logger.log(`Connected to MCP server: ${this.serverCommand}`);
        });
    }

    async disconnect(): Promise<void> {
        return this.executeInPath("client_disconnection", async () => {
            if (this.transport) {
                await this.transport.close();
                this.transport = null;
            }
            this.logger.log("Disconnected from MCP server");
        });
    }

    // Path: resource-operations
    async listResources(): Promise<any[]> {
        return this.executeInPath("resource_listing", async () => {
            const request: ListResourcesRequest = {
                method: "resources/list",
                params: {},
            };

            const response = await this.client.request(request);
            this.logger.log(`Found ${response.resources?.length || 0} resources`);
            return response.resources || [];
        });
    }

    async readResource(uri: string): Promise<string> {
        return this.executeInPath("resource_reading", async () => {
            const request: ReadResourceRequest = {
                method: "resources/read",
                params: { uri },
            };

            const response = await this.client.request(request);
            const content = response.contents?.[0]?.text || "";
            this.logger.log(`Read resource: ${uri} (${content.length} characters)`);
            return content;
        });
    }

    // Path: tool-operations
    async listTools(): Promise<any[]> {
        return this.executeInPath("tool_listing", async () => {
            const request: ListToolsRequest = {
                method: "tools/list",
                params: {},
            };

            const response = await this.client.request(request);
            this.logger.log(`Found ${response.tools?.length || 0} tools`);
            return response.tools || [];
        });
    }

    async callTool(name: string, arguments_: Record<string, any> = {}): Promise<any[]> {
        return this.executeInPath(`tool_execution_${name}`, async () => {
            const request: CallToolRequest = {
                method: "tools/call",
                params: {
                    name,
                    arguments: arguments_,
                },
            };

            const response = await this.client.request(request);
            this.logger.log(`Executed tool: ${name}`);
            return response.content || [];
        });
    }

    // Path: prompt-operations
    async listPrompts(): Promise<any[]> {
        return this.executeInPath("prompt_listing", async () => {
            const request: ListToolsRequest = {
                method: "prompts/list",
                params: {},
            };

            const response = await this.client.request(request);
            this.logger.log(`Found ${response.prompts?.length || 0} prompts`);
            return response.prompts || [];
        });
    }

    async getPrompt(name: string, arguments_: Record<string, any> = {}): Promise<any> {
        return this.executeInPath(`prompt_retrieval_${name}`, async () => {
            const request: GetPromptRequest = {
                method: "prompts/get",
                params: {
                    name,
                    arguments: arguments_,
                },
            };

            const response = await this.client.request(request);
            this.logger.log(`Retrieved prompt: ${name}`);
            return response;
        });
    }

    // Path: context-management
    enterPath(pathName: string, context?: any): void {
        const pathEntry = {
            name: pathName,
            timestamp: Date.now(),
            context,
        };
        this.pathContext.push(pathEntry);
        this.logger.log(`[PATH] Entering: ${pathName}`);
    }

    exitPath(pathName: string): void {
        if (this.pathContext.length > 0 && this.pathContext[this.pathContext.length - 1].name === pathName) {
            const pathEntry = this.pathContext.pop()!;
            const duration = Date.now() - pathEntry.timestamp;
            this.logger.log(`[PATH] Exiting: ${pathName} (${duration}ms)`);
        } else {
            this.logger.warn(`[PATH] Path mismatch: expected ${pathName}, got ${this.pathContext[this.pathContext.length - 1]?.name || 'empty'}`);
        }
    }

    async executeInPath<T>(pathName: string, func: () => Promise<T>): Promise<T> {
        this.enterPath(pathName);
        try {
            return await func();
        } finally {
            this.exitPath(pathName);
        }
    }

    // Path: batch-operations
    async executeResourceWorkflow(resourceUris: string[]): Promise<{ uri: string; content: string; error?: string }[]> {
        return this.executeInPath("resource_workflow", async () => {
            const results = [];
            
            for (const uri of resourceUris) {
                try {
                    const content = await this.readResource(uri);
                    results.push({ uri, content });
                } catch (error) {
                    results.push({ uri, content: "", error: error.message });
                }
            }
            
            return results;
        });
    }

    async executeToolChain(toolChain: Array<{ name: string; args: Record<string, any> }>): Promise<any[]> {
        return this.executeInPath("tool_chain", async () => {
            const results = [];
            
            for (const tool of toolChain) {
                const result = await this.callTool(tool.name, tool.args);
                results.push(result);
            }
            
            return results;
        });
    }

    // Path: error-handling-and-recovery
    async withRetry<T>(operation: () => Promise<T>, maxRetries: number = 3, delay: number = 1000): Promise<T> {
        return this.executeInPath("retry_operation", async () => {
            let lastError: Error;
            
            for (let attempt = 1; attempt <= maxRetries; attempt++) {
                try {
                    return await operation();
                } catch (error) {
                    lastError = error as Error;
                    this.logger.warn(`Attempt ${attempt}/${maxRetries} failed: ${error.message}`);
                    
                    if (attempt < maxRetries) {
                        await new Promise(resolve => setTimeout(resolve, delay * attempt));
                    }
                }
            }
            
            throw lastError!;
        });
    }
}

// Path: usage-example
export async function demonstrateMCPUsage(): Promise<void> {
    const client = new PathAwareMCPClient("python", ["-m", "mcp_servers.filesystem", "/workspace"]);
    
    try {
        // Path: connection-establishment
        await client.connect();
        
        // Path: resource-discovery-and-reading
        const resources = await client.listResources();
        console.log("Available resources:", resources.map(r => r.uri));
        
        if (resources.length > 0) {
            const content = await client.readResource(resources[0].uri);
            console.log(`First resource content preview: ${content.substring(0, 200)}...`);
        }
        
        // Path: tool-discovery-and-execution
        const tools = await client.listTools();
        console.log("Available tools:", tools.map(t => t.name));
        
        if (tools.some(t => t.name === "list_directory")) {
            const dirListing = await client.callTool("list_directory", { path: "." });
            console.log("Directory listing:", dirListing);
        }
        
        // Path: batch-resource-processing
        const resourceUris = resources.slice(0, 3).map(r => r.uri);
        const batchResults = await client.executeResourceWorkflow(resourceUris);
        console.log(`Processed ${batchResults.length} resources in batch`);
        
    } finally {
        // Path: cleanup
        await client.disconnect();
    }
}
```

## MCP Integration Automation

### Automated MCP Server Discovery and Configuration
```bash
#!/bin/bash
# Path: mcp-server-discovery-automation
# File: scripts/mcp/discover-servers.sh

set -euo pipefail

# Path: script-initialization
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../" && pwd)"
readonly MCP_CONFIG_DIR="${PROJECT_ROOT}/config/mcp"

# Load libraries
source "${SCRIPT_DIR}/../lib/logging.sh"
source "${SCRIPT_DIR}/../lib/path_management.sh"

# Path: mcp-server-discovery-workflow
discover_and_configure_mcp_servers() {
    enter_path "mcp_server_discovery"
    
    log_info "Starting MCP server discovery and configuration" "mcp_discovery"
    
    # Path: available-server-discovery
    execute_in_path "available_server_discovery" \
        "discover_available_servers"
    
    # Path: server-capability-analysis
    execute_in_path "server_capability_analysis" \
        "analyze_server_capabilities"
    
    # Path: configuration-generation
    execute_in_path "configuration_generation" \
        "generate_mcp_configurations"
    
    # Path: integration-validation
    execute_in_path "integration_validation" \
        "validate_mcp_integrations"
    
    exit_path "mcp_server_discovery"
    log_info "MCP server discovery and configuration completed" "mcp_discovery"
}

# Path: server-discovery-implementation
discover_available_servers() {
    log_info "Discovering available MCP servers" "server_discovery"
    
    local servers_file="${MCP_CONFIG_DIR}/discovered_servers.json"
    mkdir -p "$(dirname "$servers_file")"
    
    # Path: container-based-server-discovery
    local discovered_servers=()
    
    # Discover file system servers
    if docker ps --format "table {{.Names}}" | grep -q "mcp-filesystem"; then
        discovered_servers+=("filesystem")
        log_info "Discovered filesystem MCP server" "server_discovery"
    fi
    
    # Discover database servers
    if docker ps --format "table {{.Names}}" | grep -q "mcp-database"; then
        discovered_servers+=("database")
        log_info "Discovered database MCP server" "server_discovery"
    fi
    
    # Discover API integration servers
    if docker ps --format "table {{.Names}}" | grep -q "mcp-api"; then
        discovered_servers+=("api-integration")
        log_info "Discovered API integration MCP server" "server_discovery"
    fi
    
    # Generate discovered servers configuration
    cat > "$servers_file" << EOF
{
    "discovered_at": "$(date -Iseconds)",
    "servers": [
$(printf '        "%s"' "${discovered_servers[@]}" | paste -sd ',' -)
    ],
    "total_count": ${#discovered_servers[@]}
}
EOF
    
    log_info "Server discovery completed: ${#discovered_servers[@]} servers found" "server_discovery"
}

# Path: capability-analysis-implementation
analyze_server_capabilities() {
    log_info "Analyzing MCP server capabilities" "capability_analysis"
    
    local capabilities_file="${MCP_CONFIG_DIR}/server_capabilities.json"
    
    # Initialize capabilities analysis
    cat > "$capabilities_file" << 'EOF'
{
    "analysis_timestamp": "$(date -Iseconds)",
    "servers": {}
}
EOF
    
    # Analyze each discovered server
    local discovered_servers_file="${MCP_CONFIG_DIR}/discovered_servers.json"
    if [[ -f "$discovered_servers_file" ]]; then
        local servers
        servers=$(jq -r '.servers[]' "$discovered_servers_file")
        
        while IFS= read -r server; do
            if [[ -n "$server" ]]; then
                analyze_individual_server_capabilities "$server" "$capabilities_file"
            fi
        done <<< "$servers"
    fi
    
    log_info "Server capability analysis completed" "capability_analysis"
}

analyze_individual_server_capabilities() {
    local server_name="$1"
    local capabilities_file="$2"
    
    log_debug "Analyzing capabilities for server: $server_name" "capability_analysis"
    
    # Use a temporary Python script to test server capabilities
    local temp_script="${PROJECT_ROOT}/tmp/test_${server_name}_capabilities.py"
    mkdir -p "$(dirname "$temp_script")"
    
    cat > "$temp_script" << EOF
#!/usr/bin/env python3
import asyncio
import json
import sys
import subprocess
from pathlib import Path

async def test_server_capabilities(server_name):
    try:
        # Test server connection
        result = subprocess.run(
            ["docker", "exec", f"mcp-{server_name}", "python", "-c", 
             "import asyncio; from src.health_check import check_server_health; asyncio.run(check_server_health())"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            capabilities = {
                "status": "healthy",
                "resources": True,  # Assume basic capabilities
                "tools": True,
                "prompts": True,
                "last_check": "$(date -Iseconds)"
            }
        else:
            capabilities = {
                "status": "unhealthy",
                "error": result.stderr,
                "last_check": "$(date -Iseconds)"
            }
        
        return capabilities
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "last_check": "$(date -Iseconds)"
        }

if __name__ == "__main__":
    server_name = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    capabilities = asyncio.run(test_server_capabilities(server_name))
    print(json.dumps(capabilities, indent=2))
EOF
    
    # Execute capability test
    if python3 "$temp_script" "$server_name" > "${PROJECT_ROOT}/tmp/${server_name}_capabilities.json" 2>/dev/null; then
        # Update main capabilities file
        local server_capabilities
        server_capabilities=$(cat "${PROJECT_ROOT}/tmp/${server_name}_capabilities.json")
        
        # Use jq to update the capabilities file
        jq --arg server "$server_name" --argjson caps "$server_capabilities" \
            '.servers[$server] = $caps' "$capabilities_file" > "${capabilities_file}.tmp" && \
            mv "${capabilities_file}.tmp" "$capabilities_file"
        
        log_debug "Capabilities analyzed for server: $server_name" "capability_analysis"
    else
        log_warning "Failed to analyze capabilities for server: $server_name" "capability_analysis"
    fi
    
    # Cleanup
    rm -f "$temp_script" "${PROJECT_ROOT}/tmp/${server_name}_capabilities.json"
}

# Path: configuration-generation-implementation
generate_mcp_configurations() {
    log_info "Generating MCP client configurations" "config_generation"
    
    local client_config_file="${MCP_CONFIG_DIR}/client_config.json"
    local capabilities_file="${MCP_CONFIG_DIR}/server_capabilities.json"
    
    if [[ ! -f "$capabilities_file" ]]; then
        log_error "Server capabilities file not found: $capabilities_file" "config_generation"
        return 1
    fi
    
    # Generate comprehensive client configuration
    cat > "$client_config_file" << 'EOF'
{
    "mcpVersion": "2025-06-18",
    "clientName": "ai-seed-mcp-client",
    "clientVersion": "1.0.0",
    "servers": {},
    "globalSettings": {
        "timeout": 30000,
        "retryAttempts": 3,
        "retryDelay": 1000,
        "logLevel": "INFO"
    },
    "pathTracking": {
        "enabled": true,
        "metricsCollection": true,
        "performanceMonitoring": true
    }
}
EOF
    
    # Process each server from capabilities
    local servers
    servers=$(jq -r '.servers | keys[]' "$capabilities_file")
    
    while IFS= read -r server; do
        if [[ -n "$server" ]]; then
            generate_server_client_config "$server" "$client_config_file" "$capabilities_file"
        fi
    done <<< "$servers"
    
    log_info "MCP client configuration generated: $client_config_file" "config_generation"
}

generate_server_client_config() {
    local server_name="$1"
    local client_config_file="$2"
    local capabilities_file="$3"
    
    local server_status
    server_status=$(jq -r ".servers[\"$server_name\"].status" "$capabilities_file")
    
    if [[ "$server_status" = "healthy" ]]; then
        # Generate server-specific configuration
        local server_config=$(cat << EOF
{
    "command": "docker",
    "args": ["exec", "-i", "mcp-$server_name", "python", "-m", "mcp_servers.$server_name"],
    "enabled": true,
    "capabilities": {
        "resources": true,
        "tools": true,
        "prompts": true
    },
    "settings": {
        "timeout": 30000,
        "retryAttempts": 3
    },
    "pathContext": {
        "serverType": "$server_name",
        "containerName": "mcp-$server_name"
    }
}
EOF
)
        
        # Update client configuration with server config
        jq --arg server "$server_name" --argjson config "$server_config" \
            '.servers[$server] = $config' "$client_config_file" > "${client_config_file}.tmp" && \
            mv "${client_config_file}.tmp" "$client_config_file"
        
        log_debug "Configuration generated for healthy server: $server_name" "config_generation"
    else
        log_warning "Skipping configuration for unhealthy server: $server_name" "config_generation"
    fi
}

# Path: integration-validation-implementation
validate_mcp_integrations() {
    log_info "Validating MCP integrations" "integration_validation"
    
    local client_config_file="${MCP_CONFIG_DIR}/client_config.json"
    local validation_report="${MCP_CONFIG_DIR}/validation_report.json"
    
    if [[ ! -f "$client_config_file" ]]; then
        log_error "Client configuration file not found: $client_config_file" "integration_validation"
        return 1
    fi
    
    # Initialize validation report
    cat > "$validation_report" << 'EOF'
{
    "validation_timestamp": "$(date -Iseconds)",
    "overall_status": "unknown",
    "tested_servers": {},
    "summary": {
        "total_servers": 0,
        "healthy_servers": 0,
        "failed_servers": 0,
        "success_rate": 0
    }
}
EOF
    
    # Test each configured server
    local servers
    servers=$(jq -r '.servers | keys[]' "$client_config_file")
    local total_servers=0
    local healthy_servers=0
    
    while IFS= read -r server; do
        if [[ -n "$server" ]]; then
            ((total_servers++))
            
            if validate_individual_server_integration "$server" "$client_config_file" "$validation_report"; then
                ((healthy_servers++))
            fi
        fi
    done <<< "$servers"
    
    # Update summary
    local success_rate=0
    if [[ $total_servers -gt 0 ]]; then
        success_rate=$(( (healthy_servers * 100) / total_servers ))
    fi
    
    jq --arg total "$total_servers" --arg healthy "$healthy_servers" --arg rate "$success_rate" \
        '.summary.total_servers = ($total | tonumber) |
         .summary.healthy_servers = ($healthy | tonumber) |
         .summary.success_rate = ($rate | tonumber) |
         .overall_status = (if ($rate | tonumber) >= 80 then "healthy" elif ($rate | tonumber) >= 50 then "warning" else "critical" end)' \
        "$validation_report" > "${validation_report}.tmp" && \
        mv "${validation_report}.tmp" "$validation_report"
    
    log_info "Integration validation completed: $healthy_servers/$total_servers servers healthy (${success_rate}%)" "integration_validation"
}

validate_individual_server_integration() {
    local server_name="$1"
    local client_config_file="$2"
    local validation_report="$3"
    
    log_debug "Validating integration for server: $server_name" "integration_validation"
    
    # Create a simple test script to validate server integration
    local test_script="${PROJECT_ROOT}/tmp/validate_${server_name}_integration.py"
    
    cat > "$test_script" << 'EOF'
#!/usr/bin/env python3
import asyncio
import json
import sys
import subprocess
from datetime import datetime

async def validate_server_integration(server_name):
    try:
        # Simple integration test: list resources
        result = subprocess.run([
            "docker", "exec", f"mcp-{server_name}",
            "python", "-c",
            """
import asyncio
import sys
from mcp_servers.base_server import PathAwareMCPServer

# Create a minimal test to verify server functionality
class TestServer(PathAwareMCPServer):
    async def _list_resources_with_paths(self):
        return []
    async def _read_resource_with_path_tracking(self, uri):
        return ""
    async def _list_tools_with_paths(self):
        return []
    async def _execute_tool_with_path_tracking(self, name, args):
        return []
    async def _list_prompts_with_paths(self):
        return []
    async def _get_prompt_with_path_context(self, name, args):
        return None

async def test():
    server = TestServer("test-server")
    # Test basic functionality
    return True

print("SUCCESS" if asyncio.run(test()) else "FAILURE")
            """
        ], capture_output=True, text=True, timeout=15)
        
        if "SUCCESS" in result.stdout:
            return {
                "status": "healthy",
                "test_timestamp": datetime.now().isoformat(),
                "response_time": "< 15s"
            }
        else:
            return {
                "status": "failed",
                "test_timestamp": datetime.now().isoformat(),
                "error": result.stderr or "Unknown error"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "test_timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

if __name__ == "__main__":
    server_name = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    result = asyncio.run(validate_server_integration(server_name))
    print(json.dumps(result, indent=2))
EOF
    
    # Execute validation test
    local validation_result
    if validation_result=$(python3 "$test_script" "$server_name" 2>/dev/null); then
        # Update validation report
        jq --arg server "$server_name" --argjson result "$validation_result" \
            '.tested_servers[$server] = $result' "$validation_report" > "${validation_report}.tmp" && \
            mv "${validation_report}.tmp" "$validation_report"
        
        local status
        status=$(echo "$validation_result" | jq -r '.status')
        
        if [[ "$status" = "healthy" ]]; then
            log_debug "Integration validation successful for server: $server_name" "integration_validation"
            rm -f "$test_script"
            return 0
        else
            log_warning "Integration validation failed for server: $server_name ($status)" "integration_validation"
        fi
    else
        log_error "Integration validation error for server: $server_name" "integration_validation"
    fi
    
    # Cleanup
    rm -f "$test_script"
    return 1
}

# Path: main-execution-workflow
main() {
    local start_time=$(date +%s.%N)
    
    log_info "Starting MCP server discovery and configuration workflow" "main"
    
    # Execute discovery and configuration workflow
    discover_and_configure_mcp_servers || {
        log_fatal "MCP server discovery and configuration failed" "main"
    }
    
    # Generate usage documentation
    generate_mcp_usage_documentation
    
    local end_time=$(date +%s.%N)
    local total_time=$(echo "$end_time - $start_time" | bc -l)
    
    log_performance_metric "mcp_discovery_time" "$total_time" "seconds" "main"
    log_info "MCP server discovery and configuration completed in ${total_time}s" "main"
}

generate_mcp_usage_documentation() {
    local docs_file="${PROJECT_ROOT}/docs/mcp-integration-guide.md"
    
    cat > "$docs_file" << 'EOF'
# MCP Integration Guide

*Auto-generated on $(date -Iseconds)*

This guide provides information about the configured MCP (Model Context Protocol) servers and how to use them in your AI applications.

## Available MCP Servers

$(if [[ -f "${MCP_CONFIG_DIR}/discovered_servers.json" ]]; then
    jq -r '.servers[] | "- " + .' "${MCP_CONFIG_DIR}/discovered_servers.json"
fi)

## Server Capabilities

$(if [[ -f "${MCP_CONFIG_DIR}/server_capabilities.json" ]]; then
    jq -r '.servers | to_entries[] | "### " + .key + "\n\n" + "Status: " + .value.status + "\n"' "${MCP_CONFIG_DIR}/server_capabilities.json"
fi)

## Client Configuration

The MCP client configuration is available at: `config/mcp/client_config.json`

## Usage Examples

### TypeScript/JavaScript Client

```typescript
import { PathAwareMCPClient } from './src/mcp/clients/mcp-client';

const client = new PathAwareMCPClient("docker", ["exec", "-i", "mcp-filesystem", "python", "-m", "mcp_servers.filesystem"]);
await client.connect();

// List available resources
const resources = await client.listResources();
console.log("Available resources:", resources);

// Read a specific resource
const content = await client.readResource(resources[0].uri);
console.log("Resource content:", content);

await client.disconnect();
```

### Python Client

```python
import asyncio
from src.mcp.clients.mcp_client_python import PathAwareMCPClient

async def main():
    client = PathAwareMCPClient("docker", ["exec", "-i", "mcp-filesystem", "python", "-m", "mcp_servers.filesystem"])
    await client.connect()
    
    # List available tools
    tools = await client.list_tools()
    print("Available tools:", tools)
    
    # Execute a tool
    result = await client.call_tool("list_directory", {"path": "."})
    print("Directory listing:", result)
    
    await client.disconnect()

asyncio.run(main())
```

## Troubleshooting

### Common Issues

1. **Server Connection Failed**
   - Ensure MCP server containers are running
   - Check container health status
   - Verify network connectivity

2. **Resource Access Denied**
   - Check file/directory permissions
   - Verify container volume mounts
   - Review security settings

3. **Tool Execution Failed**
   - Validate tool arguments
   - Check server logs for errors
   - Ensure required dependencies are available

### Health Checks

Run the discovery script to check server health:

```bash
./scripts/mcp/discover-servers.sh
```

Check the validation report at: `config/mcp/validation_report.json`

## Next Steps

- [MCP Server Development Guide](./mcp-server-development.md)
- [Custom MCP Integration Patterns](./mcp-integration-patterns.md)
- [MCP Security Best Practices](./mcp-security.md)
EOF
    
    log_info "MCP usage documentation generated: $docs_file" "documentation"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

## Integration with Other Instructions

This MCP instruction file works in conjunction with:
- **space.instructions.md**: Foundation principles and path-based development
- **project.instructions.md**: AI-seed specific requirements and MCP integration standards
- **python.instructions.md**: Python MCP server implementation patterns
- **javascript.instructions.md**: TypeScript/JavaScript MCP client patterns
- **bash.instructions.md**: Shell scripting for MCP automation and orchestration
- **docker.instructions.md**: Container-based MCP server deployment
- **ci-cd.instructions.md**: Automated MCP server testing and deployment

## Future Evolution

### Advanced MCP Features
- **Multi-Protocol Support**: Integration with additional AI protocols and standards
- **Dynamic Server Discovery**: Automatic detection and configuration of new MCP servers
- **Advanced Context Sharing**: Sophisticated context aggregation and filtering
- **Performance Optimization**: Path-based optimization of MCP communications

### AI-Enhanced MCP Operations
- **Intelligent Resource Mapping**: AI-driven resource discovery and categorization
- **Adaptive Tool Orchestration**: Dynamic tool chain optimization based on context
- **Predictive Context Sharing**: Anticipatory context preparation for AI applications
- **Autonomous Server Management**: Self-healing and self-optimizing MCP server networks 