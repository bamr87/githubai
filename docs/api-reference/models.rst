Models Reference
================

This page documents all Django models in the GitHubAI application.

.. module:: core.models

Database Models
--------------

The GitHubAI application uses 12 main models organized into functional groups:

AI Provider Models
~~~~~~~~~~~~~~~~~

.. autoclass:: AIProvider
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: AIModel
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: APILog
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: AIResponse
   :members:
   :undoc-members:
   :show-inheritance:

Prompt Management Models
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: PromptTemplate
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: PromptSchema
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: PromptDataset
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: PromptDatasetEntry
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: PromptExecution
   :members:
   :undoc-members:
   :show-inheritance:

Issue Models
~~~~~~~~~~~

.. autoclass:: Issue
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: IssueTemplate
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: IssueFileReference
   :members:
   :undoc-members:
   :show-inheritance:

Documentation Models
~~~~~~~~~~~~~~~~~~~

.. autoclass:: DocumentationFile
   :members:
   :undoc-members:
   :show-inheritance:

Versioning Models
~~~~~~~~~~~~~~~~

.. autoclass:: Version
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: ChangelogEntry
   :members:
   :undoc-members:
   :show-inheritance:

Base Models
~~~~~~~~~~

.. autoclass:: TimeStampedModel
   :members:
   :undoc-members:
   :show-inheritance:
