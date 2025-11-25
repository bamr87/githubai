Management Commands
===================

This page documents Django management commands available in GitHubAI.

.. module:: core.management.commands

Available Commands
-----------------

All management commands are run using::

    python manage.py <command> [options]

Or in Docker::

    docker-compose -f infra/docker/docker-compose.yml exec web python manage.py <command> [options]

Auto Issue Command
~~~~~~~~~~~~~~~~~

.. automodule:: core.management.commands.auto_issue
   :members:
   :undoc-members:
   :show-inheritance:

**Usage**::

    python manage.py auto_issue --chore-type code_quality --repo owner/repo
    python manage.py auto_issue --chore-type todo_scan --dry-run

**Options:**

* ``--chore-type`` - Type of analysis (code_quality, todo_scan, security_audit, etc.)
* ``--repo`` - Repository in format owner/repo
* ``--dry-run`` - Preview issue without creating it
* ``--parent-issue`` - Parent issue number for sub-issues

Generate Docs Command
~~~~~~~~~~~~~~~~~~~~

.. automodule:: core.management.commands.generate_docs
   :members:
   :undoc-members:
   :show-inheritance:

**Usage**::

    python manage.py generate_docs --file apps/core/models.py
    python manage.py generate_docs --directory apps/core/services/

**Options:**

* ``--file`` - Path to Python file to document
* ``--directory`` - Directory to scan for Python files
* ``--output`` - Output format (markdown, html)

Bump Version Command
~~~~~~~~~~~~~~~~~~~

.. automodule:: core.management.commands.bump_version
   :members:
   :undoc-members:
   :show-inheritance:

**Usage**::

    python manage.py bump_version --type minor
    python manage.py bump_version --type patch --message "Bug fix release"

**Options:**

* ``--type`` - Version bump type (major, minor, patch)
* ``--message`` - Changelog message
* ``--dry-run`` - Preview version bump

Create Issue Command
~~~~~~~~~~~~~~~~~~~

.. automodule:: core.management.commands.create_issue
   :members:
   :undoc-members:
   :show-inheritance:

**Usage**::

    python manage.py create_issue --repo owner/repo --parent 123
    python manage.py create_issue --template "Bug Report" --title "Fix login issue"

**Options:**

* ``--repo`` - Repository in format owner/repo
* ``--parent`` - Parent issue number
* ``--template`` - Issue template name
* ``--title`` - Issue title
* ``--body`` - Issue body text
