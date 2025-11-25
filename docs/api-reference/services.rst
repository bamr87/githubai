Services Reference
==================

This page documents all service layer classes in the GitHubAI application.

Service Layer Pattern
--------------------

GitHubAI follows a strict **service layer pattern** where all business logic is encapsulated in service classes. Views and models should remain thin, delegating complex operations to services.

.. module:: core.services

Core Services
------------

AI Service
~~~~~~~~~

.. automodule:: core.services.ai_service
   :members:
   :undoc-members:
   :show-inheritance:

GitHub Service
~~~~~~~~~~~~~

.. automodule:: core.services.github_service
   :members:
   :undoc-members:
   :show-inheritance:

Issue Service
~~~~~~~~~~~~

.. automodule:: core.services.issue_service
   :members:
   :undoc-members:
   :show-inheritance:

Auto Issue Service
~~~~~~~~~~~~~~~~~

.. automodule:: core.services.auto_issue_service
   :members:
   :undoc-members:
   :show-inheritance:

Documentation Service
~~~~~~~~~~~~~~~~~~~~

.. automodule:: core.services.doc_service
   :members:
   :undoc-members:
   :show-inheritance:

Versioning Service
~~~~~~~~~~~~~~~~~

.. automodule:: core.services.versioning_service
   :members:
   :undoc-members:
   :show-inheritance:

AI Provider Factory
~~~~~~~~~~~~~~~~~~

.. automodule:: core.services.ai_providers
   :members:
   :undoc-members:
   :show-inheritance:

Service Usage Pattern
--------------------

Always import and instantiate services in your views::

    from core.services import AIService, IssueService

    def my_view(request):
        ai_service = AIService()
        response = ai_service.call_ai_chat(
            system_prompt="You are a helpful assistant",
            user_prompt="Generate a summary"
        )

        issue_service = IssueService()
        issue = issue_service.create_sub_issue_from_template(
            repo="owner/repo",
            parent_issue_number=123,
            file_refs=["README.md"]
        )

Never call AI APIs or external services directly from views - always use the service layer.
