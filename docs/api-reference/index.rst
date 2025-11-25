GitHubAI API Reference
======================

Welcome to GitHubAI's API documentation. This documentation is automatically generated from the source code docstrings.

GitHubAI is a production-ready Django application for AI-powered GitHub automation with support for multiple AI providers, automated issue generation, documentation generation, and version management.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   models
   services
   views
   serializers
   management

Quick Links
-----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Architecture Overview
--------------------

GitHubAI follows a **service layer pattern** where business logic is encapsulated in service classes:

* **Models** (``core.models``): Domain models for AI providers, prompts, issues, documentation, and versioning
* **Services** (``core.services``): Business logic services (AIService, GitHubService, IssueService, etc.)
* **Views** (``core.views``): REST API endpoints using Django REST Framework
* **Serializers** (``core.serializers``): Data serialization for API responses

Key Features
-----------

* **Multi-Provider AI Integration**: OpenAI, XAI (Grok), extensible provider factory pattern
* **Response Caching**: Automatic caching via AIResponse model to reduce API costs
* **Prompt Management**: Database-driven templates with Jinja2 rendering and versioning
* **Auto Issue Generation**: Analyze repositories and create GitHub issues automatically
* **Documentation Generation**: Parse Python files and generate documentation
* **Semantic Versioning**: Automated version bumping and changelog management

Getting Started
--------------

For user guides and tutorials, see the main documentation in the ``docs/`` directory:

* `Getting Started Guide <../GETTING_STARTED.html>`_
* `AI Provider Configuration <../guides/ai-provider-configuration.html>`_
* `Auto Issue Feature <../guides/auto-issue-feature.html>`_
* `Chat Interface Guide <../guides/chat-interface.html>`_
