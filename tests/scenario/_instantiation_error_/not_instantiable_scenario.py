"""Not instantiable scenario."""

from gh_action_integration_test.git.repository import TestRepository
from gh_action_integration_test.scenario import Scenario


class NotInstantiableScenario(Scenario):
    def __init__(self) -> None:
        super().__init__("not_instantiable_scenario", "success")
        msg = "This scenario cannot be instantiated."
        raise ValueError(msg)

    def verify(self, repo: TestRepository) -> None:
        pass
