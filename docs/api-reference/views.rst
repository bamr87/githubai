Views & API Endpoints
=====================

This page documents all REST API views and endpoints in the GitHubAI application.

.. module:: core.views

REST API Views
-------------

GitHubAI uses Django REST Framework to provide a RESTful API.

Issue ViewSet
~~~~~~~~~~~~

.. autoclass:: IssueViewSet
   :members:
   :undoc-members:
   :show-inheritance:

Chat View
~~~~~~~~

.. autoclass:: ChatView
   :members:
   :undoc-members:
   :show-inheritance:

Health Check
~~~~~~~~~~~

.. autoclass:: HealthCheckView
   :members:
   :undoc-members:
   :show-inheritance:

API Endpoints Summary
--------------------

Issue Endpoints
~~~~~~~~~~~~~~

* ``GET /api/issues/`` - List all issues
* ``POST /api/issues/`` - Create a new issue
* ``GET /api/issues/{id}/`` - Get issue details
* ``PUT /api/issues/{id}/`` - Update an issue
* ``DELETE /api/issues/{id}/`` - Delete an issue
* ``POST /api/issues/create_from_feedback/`` - Create issue from user feedback
* ``POST /api/issues/create_sub_issue/`` - Create sub-issue from template
* ``POST /api/issues/auto_create/`` - Auto-generate issue from repo analysis

Chat Endpoints
~~~~~~~~~~~~~

* ``POST /api/chat/`` - Send chat message and receive AI response

Health Check
~~~~~~~~~~~

* ``GET /api/health/`` - Check API and database health

For detailed API usage examples with request/response schemas, see:

* `Auto Issue Endpoints Guide <../api/AUTO_ISSUE_ENDPOINTS.html>`_
* `Chat Endpoint Guide <../api/CHAT_ENDPOINT.html>`_
