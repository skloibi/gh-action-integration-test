"""Simple scenario."""

from pathlib import Path

from gh_action_integration_test.git.repository import TestRepository
from gh_action_integration_test.scenario import FileTreeScenario


class SimpleScenario(FileTreeScenario):
    def __init__(self) -> None:
        super().__init__("simple_scenario", "OK")
        self.prepared = False
        self.verified = False

    def prepare(self, remote_path: Path, local_path: Path) -> None:  # noqa: ARG002
        self.prepared = True

    def verify(self, repo: TestRepository) -> None:  # noqa: ARG002
        self.verified = True
