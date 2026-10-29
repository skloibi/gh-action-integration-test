from pathlib import Path

from gh_action_integration_test.git.repository import TestRepository
from gh_action_integration_test.scenario import FileTreeScenario


class DummyScenario(FileTreeScenario):
    def __init__(self, tag: str = "dummy") -> None:
        super().__init__(tag, "success")
        self.verified = False

    def verify(self, repo: TestRepository) -> None:  # noqa: ARG002
        self.verified = True


class SimplePrepareScenario(DummyScenario):
    def __init__(self, tag: str = "simple-prepare") -> None:
        super().__init__(tag)
        self.prepared = False

    def prepare(self, remote_path: Path, local_path: Path) -> None:  # noqa: ARG002
        self.prepared = True
