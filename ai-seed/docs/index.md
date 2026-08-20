# AI-Seed

AI-Seed is the autonomous AI orchestration framework: a plantable kernel that lets any GitHub repository initialize itself from a written concept and grow through incremental Claude Code OAuth passes, with GitHub as the entire SDLC platform. Start with **[Architecture](ARCHITECTURE.md)** (the system design) and **[Pattern provenance](PATTERNS.md)** (which fleet repo proved each mechanism); the planting quick start lives in the [repository README](https://github.com/bamr87/ai-seed#quick-start-plant--germinate--grow).

## The resident example (generations G1–G2)

The sections below describe the repo's earlier era — the CrewAI-based agent application that this repository grew before the kernel existed. It remains runnable as a worked example; the framework itself is the kernel + planter + doctrine above.

## What the example app is

The example is a boilerplate application capable of issue-driven evolution through AI agent collaboration. When you submit a GitHub issue describing desired functionality, specialized AI agents automatically:

- 📋 **Plan** the implementation approach
- 💻 **Code** the solution following best practices
- 🧪 **Test** with comprehensive coverage
- 📚 **Document** all changes
- 🚀 **Deploy** the updates
- 🔄 **Learn** from the outcomes

## Key Features

- **Autonomous Development**: AI agents handle 80% of development tasks
- **Human Oversight**: All changes go through PR review process
- **Multi-Agent Collaboration**: Specialized agents work together using CrewAI
- **Issue-Driven Evolution**: Simple GitHub issues trigger complete implementations
- **Continuous Learning**: System improves its own capabilities over time
- **Production Ready**: Full CI/CD, testing, documentation, and deployment

## Architecture Overview

```mermaid
graph TB
    A[GitHub Issue] --> B[Evolution Workflow]
    B --> C[Planner Agent]
    C --> D[Coder Agent]
    D --> E[Tester Agent]
    E --> F[Documenter Agent]
    F --> G[Deployer Agent]
    G --> H[Pull Request]
    H --> I[Human Review]
    I --> J[Merge & Deploy]
    J --> K[Evolver Agent]
    K --> L[System Improvement]
```

## Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/ai-seed-repo
   cd ai-seed-repo
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Application**
   ```bash
   python src/main.py
   ```

5. **Trigger Evolution**
   - Create a GitHub issue using the evolution template
   - Watch agents automatically implement your request
   - Review and merge the generated pull request

## Agent Roles

### 🎯 Planner Agent
- Analyzes evolution requests
- Creates comprehensive implementation plans
- Identifies dependencies and risks

### 💻 Coder Agent
- Generates high-quality, maintainable code
- Follows project patterns and conventions
- Implements comprehensive error handling

### 🧪 Tester Agent
- Creates exhaustive test suites
- Ensures high code coverage (95%+)
- Tests edge cases and error conditions

### 📚 Documenter Agent
- Updates all relevant documentation
- Generates API documentation from code
- Maintains user guides and examples

### 🚀 Deployer Agent
- Manages deployment configurations
- Updates infrastructure as needed
- Ensures smooth rollout processes

### 🔄 Evolver Agent
- Analyzes outcomes and performance
- Improves agent prompts and capabilities
- Evolves the system architecture

## Evolution Examples

Here are some example evolution requests:

- **"Add user authentication with JWT"** → Complete auth system with login, registration, and middleware
- **"Implement rate limiting"** → Rate limiting middleware with Redis backend and configuration
- **"Add database integration"** → SQLAlchemy models, migrations, and CRUD operations
- **"Create admin dashboard"** → Full admin interface with user management

## Technology Stack

- **Language**: Python 3.12+
- **Web Framework**: FastAPI
- **AI Framework**: CrewAI
- **LLMs**: OpenAI GPT-4o or Anthropic Claude
- **Testing**: Pytest with comprehensive coverage
- **Documentation**: MkDocs with Material theme
- **CI/CD**: GitHub Actions
- **Containerization**: Docker
- **Memory**: Pinecone or FAISS for agent memory

## Contributing

While this repository evolves autonomously, human contributions are welcome:

1. Submit evolution requests via GitHub issues
2. Review agent-generated pull requests
3. Provide feedback on implementations
4. Contribute to agent prompts and configurations

## Monitoring and Observability

- **Real-time Logs**: Comprehensive logging of all agent activities
- **Metrics Dashboard**: Track evolution success rates and performance
- **Health Checks**: Application and agent health monitoring
- **Evolution History**: Complete audit trail of all changes

## Security and Safety

- **Human Approval**: All changes require PR review
- **Security Scanning**: Automated vulnerability checks
- **Rollback Capability**: Easy reversion of problematic changes
- **Sandboxed Execution**: Agents operate in controlled environments

## Getting Help

- 📚 [Full Documentation](https://your-username.github.io/ai-seed-repo)
- 🐛 [Report Issues](https://github.com/your-username/ai-seed-repo/issues)
- 💬 [Discussions](https://github.com/your-username/ai-seed-repo/discussions)
- 📧 [Contact](mailto:your-email@domain.com)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Ready to experience autonomous software evolution? Create your first evolution request and watch the AI agents bring your ideas to life!**
