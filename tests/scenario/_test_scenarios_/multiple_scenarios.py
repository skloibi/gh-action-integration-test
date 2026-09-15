"""One py file with multiple scenario definitions."""

from gh_action_integration_test.git.repository import TestRepository
from gh_action_integration_test.scenario import Scenario


class Scenario0(Scenario):
    def __init__(self) -> None:
        super().__init__("scenario0", "success")

    def verify(self, repo: TestRepository) -> None:
        pass


class Scenario1(Scenario):
    def __init__(self) -> None:
        super().__init__("scenario1", "success")

    def verify(self, repo: TestRepository) -> None:
        pass
