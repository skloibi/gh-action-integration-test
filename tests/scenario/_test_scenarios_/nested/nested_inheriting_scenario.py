"""Submodule with multiple scenario definitions inheriting from others."""

from gh_action_integration_test.git.repository import TestRepository
from gh_action_integration_test.scenario import Scenario
from tests.scenario._test_scenarios_.simple_scenario import SimpleScenario


class BaseScenario(Scenario):
    def __init__(self, name: str) -> None:
        super().__init__(name, "success")


class SubScenario0(BaseScenario):
    def __init__(self) -> None:
        super().__init__("sub_scenario0")

    def verify(self, repo: TestRepository) -> None:
        pass


class SubScenario1(SimpleScenario):
    def __init__(self) -> None:
        super().__init__()
        self.name = "sub_scenario1"

    def verify(self, repo: TestRepository) -> None:
        pass
