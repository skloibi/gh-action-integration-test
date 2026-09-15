from argparse import ArgumentParser

import pytest

from gh_action_integration_test.cli.args import create_parser


@pytest.fixture
def parser() -> ArgumentParser:
    return create_parser()


def test_parse_args_minimal_verify(parser: ArgumentParser) -> None:
    args = parser.parse_args(["verify", "OK", "scenario0"])
    assert args.task == "verify"
    assert args.outcome == "OK"
    assert args.scenario == "scenario0"
    assert args.scenario_dir == "action_tests"
    assert args.local_path == "/tmp/test-locals"  # noqa: S108
    assert args.remote_path == "/tmp/test-remotes"  # noqa: S108


def test_parse_args_minimal_prepare(parser: ArgumentParser) -> None:
    args = parser.parse_args(["prepare", "scenarioX"])
    assert args.task == "prepare"
    assert "outcome" not in args
    assert args.scenario == "scenarioX"
    assert args.scenario_dir == "action_tests"
    assert args.local_path == "/tmp/test-locals"  # noqa: S108
    assert args.remote_path == "/tmp/test-remotes"  # noqa: S108


def test_scenario_dir(parser: ArgumentParser) -> None:
    args = parser.parse_args(["--scenario-dir", "/path/to/scenarios", "verify", "fail", "simple_scenario"])
    assert args.scenario_dir == "/path/to/scenarios"
    assert args.task == "verify"
    assert args.outcome == "fail"
    assert args.scenario == "simple_scenario"


def test_paths(parser: ArgumentParser) -> None:
    args = parser.parse_args(
        [
            "--scenario-dir",
            "/path/to/scenarios",
            "--remote-path",
            "/path/to/remotes",
            "--local-path",
            "/path/to/locals",
            "prepare",
            "test",
        ]
    )
    assert args.remote_path == "/path/to/remotes"
    assert args.local_path == "/path/to/locals"
    assert args.task == "prepare"
    assert "outcome" not in args
    assert args.scenario == "test"
