from __future__ import annotations

import os
import subprocess
import sys


class TestMigrations:
    def test_alembic_upgrade_from_empty(self, tmp_path) -> None:
        db_path = tmp_path / "test.db"
        env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{db_path}"}
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            env=env,
            cwd=os.getcwd(),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_alembic_check_is_clean(self, tmp_path) -> None:
        db_path = tmp_path / "test.db"
        env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{db_path}"}
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            env=env,
            cwd=os.getcwd(),
        )
        assert result.returncode == 0, f"upgrade failed: {result.stderr}"

        result = subprocess.run(
            [sys.executable, "-m", "alembic", "check"],
            capture_output=True,
            text=True,
            env=env,
            cwd=os.getcwd(),
        )
        assert result.returncode == 0, f"check failed: {result.stderr}"
