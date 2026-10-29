"""Scenario definition within a submodule of the search path."""

from gh_action_integration_test.git.repository import TestRepository
from gh_action_integration_test.scenario import FileTreeScenario


class NestedScenario(FileTreeScenario):
    def __init__(self) -> None:
        super().__init__("nested_scenario", "success")

    def verify(self, repo: TestRepository) -> None:
        pass
