"""Runtime checks using temporary SQLite databases; no Telegram requests."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def run_python(self, code, directory, database_url):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        if database_url is None:
            environment.pop("DATABASE_URL", None)
        else:
            environment["DATABASE_URL"] = database_url
        result = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(code)],
            cwd=directory,
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_database_url_defaults_and_environment(self):
        for value in (None, "", "sqlite+aiosqlite:///./configured.db"):
            with self.subTest(database_url=value), tempfile.TemporaryDirectory() as directory:
                expected = value or "sqlite+aiosqlite:///./database.db"
                self.run_python(
                    f"from app.database.session import DATABASE_URL; assert DATABASE_URL == {expected!r}",
                    directory,
                    value,
                )

    def test_health_and_schema_with_isolated_database(self):
        with tempfile.TemporaryDirectory() as directory:
            self.run_python(
                """
                import sqlite3
                from unittest.mock import patch
                from fastapi.testclient import TestClient
                from sqlalchemy.exc import SQLAlchemyError
                from app.main import app, engine

                with TestClient(app) as client:
                    response = client.get('/health')
                    assert response.status_code == 200, response.text
                    assert response.json() == {'status': 'ok'}
                    with sqlite3.connect('runtime.db') as database:
                        tables = database.execute(
                            "SELECT name FROM sqlite_master WHERE type = 'table'"
                        ).fetchall()
                        assert tables, 'Startup did not create the schema'

                    with patch.object(type(engine), 'connect', side_effect=SQLAlchemyError('test')):
                        response = client.get('/health')
                        assert response.status_code == 503, response.text
                        assert response.json() == {'detail': 'Database unavailable'}

                    assert client.get('/health').status_code == 200
                """,
                directory,
                "sqlite+aiosqlite:///./runtime.db",
            )


if __name__ == "__main__":
    unittest.main()
