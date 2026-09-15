import re
from unittest.mock import MagicMock, patch

import pytest

from gh_action_integration_test.main import main


def test_no_args_system_exit() -> None:
    with pytest.raises(SystemExit):
        main([])


def test_scenario_not_found() -> None:
    with pytest.raises(ValueError, match=re.escape("Scenario 'scenario1' not found.")):
        main(["--scenario-dir", "scenarios", "prepare", "scenario1"])


@patch("gh_action_integration_test.main.ScenarioManager.prepare")
def test_prepare(mock_prepare: MagicMock) -> None:
    main(["--scenario-dir", "tests/scenarios/_test_scenarios_", "prepare", "simple_scenario"])

    mock_prepare.assert_called_once_with("simple_scenario")


@patch("gh_action_integration_test.main.ScenarioManager.verify")
def test_verify(mock_verify: MagicMock) -> None:
    main(["--scenario-dir", "tests/scenarios/_test_scenarios_/nested", "verify", "okay", "nested_scenario"])

    mock_verify.assert_called_once_with("nested_scenario", "okay")
