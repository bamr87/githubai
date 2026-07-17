"""Pytest settings shim for bare runners (CI, local dev without docker).

Wraps the repo's designed test settings (``githubai.settings_test`` —
mock AI provider, eager Celery, ``.env.test`` auto-load) but defaults the
database to sqlite when the environment provides no DATABASE_URL: bare
runners have no Postgres at the compose host ``db``. ``.env.test`` is
loaded with setdefault semantics, so a real environment variable (e.g.
injected by docker-compose.test.yml) still wins.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///test_db.sqlite3")

from .settings_test import *  # noqa: F401,F403,E402
