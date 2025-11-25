Serializers Reference
=====================

This page documents all DRF serializers used for API data serialization.

.. module:: core.serializers

REST Framework Serializers
--------------------------

Issue Serializers
~~~~~~~~~~~~~~~~

.. autoclass:: IssueSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: IssueTemplateSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: IssueFileReferenceSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: CreateSubIssueSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: CreateFeedbackIssueSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: CreateAutoIssueSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: CreateREADMEUpdateSerializer
   :members:
   :undoc-members:
   :show-inheritance:

Chat Serializers
~~~~~~~~~~~~~~~

.. module:: core.chat_serializers

.. autoclass:: ChatMessageSerializer
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: ChatResponseSerializer
   :members:
   :undoc-members:
   :show-inheritance:

Serializer Usage
---------------

Serializers are used by Django REST Framework views to validate incoming data and format outgoing responses::

    from core.serializers import IssueSerializer
    from core.models import Issue

    # Serialize a model instance
    issue = Issue.objects.get(id=1)
    serializer = IssueSerializer(issue)
    data = serializer.data  # Returns dict suitable for JSON response

    # Validate and deserialize incoming data
    serializer = IssueSerializer(data=request.data)
    if serializer.is_valid():
        issue = serializer.save()
    else:
        errors = serializer.errors
