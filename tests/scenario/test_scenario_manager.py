import re
from collections.abc import Iterable
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from gh_action_integration_test.scenario import ScenarioManager
from tests.scenario_utils import DummyScenario, SimplePrepareScenario

REMOTE_PATH = Path("/tmp/test-remotes")  # noqa: S108
LOCAL_PATH = Path("/tmp/test-locals")  # noqa: S108

SCENARIOS_DIR = Path(__file__).parent / "_test_scenarios_"
assert SCENARIOS_DIR.is_dir()

GIT_DIR = Path(__file__).parent.parent / "git"
assert GIT_DIR.is_dir()


class TestScenarioManager:
    def test_without_scenario(self) -> None:
        mgr = ScenarioManager(REMOTE_PATH, LOCAL_PATH)

        assert len(list(mgr.scenarios())) == 0

    def test_instantiate_with_scenario(self) -> None:
        s = DummyScenario()
        mgr = ScenarioManager(REMOTE_PATH, LOCAL_PATH, s)

        assert len(list(mgr.scenarios())) == 1

        scenario = next(iter(mgr.scenarios()))

        assert scenario == s

    def test_with_multiple_scenarios(self) -> None:
        s0 = DummyScenario("test0")
        s1 = DummyScenario("test1")
        mgr = ScenarioManager(REMOTE_PATH, LOCAL_PATH, s0, s1)

        assert len(list(mgr.scenarios())) == 2

        actual0, actual1 = list(mgr.scenarios())

        assert actual0 == s0
        assert actual1 == s1

    def test_with_duplicate_scenarios(self) -> None:
        s0 = DummyScenario()
        s1 = DummyScenario()
        with pytest.raises(ValueError, match=re.escape("Scenario 'dummy' already registered.")):
            ScenarioManager(REMOTE_PATH, LOCAL_PATH, s0, s1)

    def test_get_scenarios_empty(self) -> None:
        with pytest.raises(ValueError, match=re.escape("Scenario 'dummy' not found.")):
            ScenarioManager(REMOTE_PATH, LOCAL_PATH).get_scenario("dummy")

    def test_get_scenarios_no_match(self) -> None:
        with pytest.raises(ValueError, match=re.escape("Scenario 'dummy0' not found.")):
            ScenarioManager(REMOTE_PATH, LOCAL_PATH, DummyScenario()).get_scenario("dummy0")

    def test_get_scenarios_match(self) -> None:
        s0 = DummyScenario("test0")
        s1 = DummyScenario("test1")
        assert ScenarioManager(REMOTE_PATH, LOCAL_PATH, s0, s1).get_scenario("test1") == s1

    def test_prepare(self) -> None:
        s0 = SimplePrepareScenario("test0")
        s1 = SimplePrepareScenario("test1")
        mgr = ScenarioManager(REMOTE_PATH, LOCAL_PATH, s0, s1)

        mgr.prepare("test0")

        assert s0.prepared
        assert not s1.prepared

    def test_verify(self) -> None:
        s0 = SimplePrepareScenario("test0")
        s1 = SimplePrepareScenario("test1")
        mgr = ScenarioManager(REMOTE_PATH, LOCAL_PATH, s0, s1)

        mgr.verify("test1", "success")

        assert not s0.prepared
        assert not s1.prepared

        assert not s0.verified
        assert s1.verified

    def test_collect_scenarios_invalid_target(self, fs: FakeFilesystem) -> None:
        fs.create_file("/no/directory")
        no_directory = Path("/no/directory")
        mgr = ScenarioManager.collect_scenarios(no_directory, Path("/base/remote"), Path("/base/local"))
        assert len(list(mgr.scenarios())) == 0

    def test_collect_scenarios_no_scenarios(self) -> None:
        mgr = ScenarioManager.collect_scenarios(GIT_DIR, Path("/base/remote"), Path("/base/local"))
        assert len(list(mgr.scenarios())) == 0

    @patch("gh_action_integration_test.scenario.scenario_manager.spec_from_file_location")
    def test_collect_scenarios_spec_error(self, mock_spec: MagicMock) -> None:
        mock_spec.side_effect = ValueError("Cannot create spec for /path/to/module.py")
        mgr = ScenarioManager.collect_scenarios(SCENARIOS_DIR, Path("/base/remote"), Path("/base/local"))
        assert len(list(mgr.scenarios())) == 0

    @patch("gh_action_integration_test.scenario.scenario_manager.spec_from_file_location")
    def test_collect_scenarios_spec_is_none(self, mock_spec: MagicMock) -> None:
        mock_spec.return_value = None
        mgr = ScenarioManager.collect_scenarios(SCENARIOS_DIR, Path("/base/remote"), Path("/base/local"))
        assert len(list(mgr.scenarios())) == 0

    def test_collect_scenarios(self) -> None:
        mgr = ScenarioManager.collect_scenarios(SCENARIOS_DIR, Path("/base/remote"), Path("/base/local"))

        assert_scenarios(
            mgr,
            [
                ("NestedScenario", "nested_scenario"),
                ("Scenario0", "scenario0"),
                ("Scenario1", "scenario1"),
                ("SimpleScenario", "simple_scenario"),
                ("SubScenario0", "sub_scenario0"),
                ("SubScenario1", "sub_scenario1"),
            ],
        )

    def test_collect_scenarios_submodule_only(self) -> None:
        test_scenarios = SCENARIOS_DIR / "nested"
        assert test_scenarios.is_dir()
        mgr = ScenarioManager.collect_scenarios(test_scenarios, Path("/base/remote"), Path("/base/local"))

        assert_scenarios(
            mgr,
            [
                ("NestedScenario", "nested_scenario"),
                ("SubScenario0", "sub_scenario0"),
                ("SubScenario1", "sub_scenario1"),
            ],
        )

    def test_collect_scenarios_import_failure(self) -> None:
        test_scenarios = Path(__file__).parent / "_import_error_"
        assert test_scenarios.is_dir()
        mgr = ScenarioManager.collect_scenarios(test_scenarios, Path("/base/remote"), Path("/base/local"))
        assert len(list(mgr.scenarios())) == 0

    def test_collect_scenarios_instantiation_failure(self) -> None:
        test_scenarios = Path(__file__).parent / "_instantiation_error_"
        assert test_scenarios.is_dir()
        mgr = ScenarioManager.collect_scenarios(test_scenarios, Path("/base/remote"), Path("/base/local"))
        assert len(list(mgr.scenarios())) == 0


def assert_scenarios(scenario_manager: ScenarioManager, expected_scenarios: Iterable[tuple[str, str]]) -> None:
    """Check if the given scenarios match the expected names."""

    def _sort_tuples(tuples: Iterable[tuple[str, str]]) -> Iterable[tuple[str, str]]:
        return sorted(tuples, key=lambda s: s[1])

    actual_scenarios = _sort_tuples((type(s).__name__, s.name) for s in scenario_manager.scenarios())
    expected_scenarios = _sort_tuples(expected_scenarios)

    assert actual_scenarios == expected_scenarios
