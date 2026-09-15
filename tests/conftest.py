import shutil

import pytest


def pytest_configure() -> None:
    if shutil.which("git") is None:
        pytest.exit(
            "\n\nERROR: 'git' is required but not found on PATH.\nInstall Git, then re-run tests.\n",
            returncode=1,
        )
