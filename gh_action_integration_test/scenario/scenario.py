"""Module that provides templates for defining integration test scenarios."""

import inspect
import logging
import shutil
from abc import ABC, abstractmethod
from pathlib import Path

from gh_action_integration_test.asserts import assert_eq
from gh_action_integration_test.git import TestRepository

log = logging.getLogger(__name__)


def is_scenario(clazz: type) -> bool:
    """Check if a class is a subclass of `Scenario` and not abstract.

    Args:
        clazz (Any) : the target inspection object to check

    """
    return inspect.isclass(clazz) and issubclass(clazz, Scenario) and not inspect.isabstract(clazz)


def check_commit(
    commit: str,
    expected_name: str,
    expected_email: str,
    expected_msg: str | None = None,
) -> None:
    """Check the given commit line for conformance to the expected arguments.

    Args:
        commit (str) : The commit oneline summary of name, email and message
        expected_name (str) : The expected committer name
        expected_email (str) : The expected committer email
        expected_msg (Optional[str]) : The expected commit message or `None` if
                                       it should not be checked

    """
    name, email, *msg = commit.split(":")
    assert_eq(expected_name, name, "Invalid commit author name")
    assert_eq(expected_email, email, "Invalid commit author email")
    if expected_msg:
        assert_eq(expected_msg, ":".join(msg), "Mismatching commit message")


class Scenario(ABC):
    """An abstract integration test scenario."""

    def __init__(self, name: str, expected_outcome: str) -> None:
        """Initialize a new test scenario.

        Args:
            name (str) : The name of the scenario
            expected_outcome (str) : The expected outcome of the scenario

        """
        self.name = name
        self.path = Path("action_tests") / "_files" / name
        self.expected_outcome = expected_outcome

    def prepare(self, remote_path: Path, local_path: Path) -> None:
        """Prepare the scenario in the given paths.

        Args:
            remote_path (Path) : the remote repository base path
            local_path (Path) : the local repository base path

        """
        log.info("-- Setting up scenario: %s", self.name)
        repo = TestRepository(self.name, remote_path, local_path)
        repo.initialize_repo()
        log.info("---- Remote path: %s", repo.remote_path)
        log.info("---- Local path: %s", repo.local_path)
        self.repository = repo

        self._prepare_repository(repo)

    @abstractmethod
    def _prepare_repository(self, repo: TestRepository) -> None:
        """Prepare the scenario by creating any required files in the repo.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory

        """

    def check_outcome(self, outcome: str) -> None:
        """Check the previous action outcome based on the expected one.

        See the documentation for step outcomes:
        https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#steps-context).

        Args:
            outcome (str) : The outcome of the previously executed action.

        """
        assert_eq(self.expected_outcome, outcome, f"Invalid action outcome: {outcome}")

    @abstractmethod
    def verify(self, repo: TestRepository) -> None:
        """Verify this test scenario by checking the commits and files.

        Args:
            repo (TestRepository) : The test repository that defines the
                                    working directory

        """

    def test(self, remote_path: Path, local_path: Path, outcome: str) -> None:
        """Tests the scenario in the given repository paths.

        Args:
            remote_path (Path) : The remote repository base path
            local_path (Path) : The local repository base path
            outcome (str) : The expected outcome

        """
        log.info("Verifying integration test outputs for '%s'", self.name)
        repo = TestRepository(self.name, remote_path, local_path)
        self.check_outcome(outcome)
        self.verify(repo)


class FileTreeScenario(Scenario):
    """An abstract integration test scenario backed by a given file tree."""

    def __init__(self, name: str, expected_outcome: str, base_path: Path | None = None) -> None:
        """Initialize a new test scenario.

        Args:
            name (str) : The name of the scenario
            expected_outcome (str) : The expected outcome of the scenario
            base_path (Optional[Path]) : The base path for the file tree

        """
        super().__init__(name, expected_outcome)

        if base_path is None:
            base_path = Path("action_tests") / "_files"

        self.path = base_path / name

    def _prepare_repository(self, repo: TestRepository) -> None:
        shutil.copytree(self.path, repo.local_path, dirs_exist_ok=True)

        repo.commit_all("Initial commit")
        repo.push()
