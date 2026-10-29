"""One py file with multiple scenario definitions."""

from gh_action_integration_test.git.repository import TestRepository
from gh_action_integration_test.scenario import FileTreeScenario, Scenario


class Scenario0(Scenario):
    def __init__(self) -> None:
        super().__init__("scenario0", "success")

    def _prepare_repository(self, repo: TestRepository) -> None:
        pass

    def verify(self, repo: TestRepository) -> None:
        pass


class Scenario1(FileTreeScenario):
    def __init__(self) -> None:
        super().__init__("scenario1", "success")

    def verify(self, repo: TestRepository) -> None:
        pass
