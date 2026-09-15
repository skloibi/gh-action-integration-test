import re
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from pytest_mock import MockerFixture

from gh_action_integration_test.git.commands import (
    check_git_installation,
    get_changed_files,
    get_oneline_log,
    git,
    set_git_config,
)


@pytest.fixture
def mock_subprocess_run(mocker: MockerFixture) -> MagicMock:
    subprocess_run = mocker.patch("subprocess.run")
    subprocess_run.return_value = subprocess.CompletedProcess(
        args=["git", "config"], returncode=0, stdout="", stderr=""
    )
    return subprocess_run


def test_git_command_execution(mock_subprocess_run: MagicMock) -> None:
    tempdir = Path(__file__).parent / "temp"

    git("status", cwd=tempdir, check=False)

    mock_subprocess_run.assert_called_once_with(
        ["/usr/bin/env", "git", "status"],
        capture_output=True,
        text=True,
        check=False,
        cwd=tempdir,
    )


@patch("gh_action_integration_test.git.commands.git")
def test_get_oneline_log(mock_git: MagicMock) -> None:
    mock_git.return_value.stdout = "  Test User:testuser@web.com:fix: fix application "

    cwd = Path("testdir")

    log = get_oneline_log(cwd)
    assert log == "Test User:testuser@web.com:fix: fix application"

    mock_git.assert_called_once_with("log", "--oneline", r"--format=%cn:%ce:%s", check=True, cwd=cwd)


@patch("gh_action_integration_test.git.commands.git")
def test_get_changed_files(mock_git: MagicMock) -> None:
    mock_git.return_value.stdout = "\nfile1\nfile2\nfile3\n   "

    cwd = Path("testdir")

    changed_files = get_changed_files(cwd)
    assert changed_files == ["file1", "file2", "file3"]

    mock_git.assert_called_once_with("log", "--name-only", "--pretty=", "HEAD~1..HEAD", check=True, cwd=cwd)


def test_applies_configuration(mock_subprocess_run: MagicMock) -> None:
    tempdir = Path(__file__).parent / "temp"
    set_git_config(tempdir, "Test User", "test@example.com")

    cwd = Path(__file__).parent / "temp"

    mock_subprocess_run.assert_has_calls(
        [
            call(
                ["/usr/bin/env", "git", "config", "user.name", "Test User"],
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd,
            ),
            call(
                ["/usr/bin/env", "git", "config", "user.email", "test@example.com"],
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd,
            ),
        ],
    )


def test_check_git_installation_success() -> None:
    check_git_installation()
    # shouldn't raise exception


@patch("gh_action_integration_test.git.commands.git")
def test_check_git_installation_failure(mock_git: MagicMock) -> None:
    mock_git.side_effect = subprocess.CalledProcessError(returncode=1, cmd="git --version")

    with pytest.raises(OSError, match=re.escape("Git is not installed or not found in PATH.")):
        check_git_installation()
