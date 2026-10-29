from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from gh_action_integration_test.git.repository import TestRepository
from gh_action_integration_test.scenario import FileTreeScenario, Scenario, ScenarioManager, check_commit, is_scenario
from tests.scenario_utils import DummyScenario


@pytest.fixture
def local_path(fs: FakeFilesystem) -> Path:  # noqa: ARG001
    return Path("/base/local")


@pytest.fixture
def remote_path(fs: FakeFilesystem) -> Path:  # noqa: ARG001
    return Path("/base/remote")


class TestIsScenario:
    def test_is_scenario_true(self) -> None:
        class TestScenario(DummyScenario):
            pass

        assert is_scenario(DummyScenario)
        assert is_scenario(TestScenario)

    def test_is_scenario_false(self) -> None:
        class NotAScenario:
            pass

        assert not is_scenario(Scenario)
        assert not is_scenario(FileTreeScenario)
        assert not is_scenario(NotAScenario)
        assert not is_scenario(ScenarioManager)


class TestCheckCommit:
    msg = "User Name:user.name@mail.com:chore: important commit"

    def test_invalid_name(self) -> None:
        with pytest.raises(AssertionError, match="Invalid commit author name"):
            check_commit(self.msg, "Test User", "user.name@mail.com")

    def test_invalid_email(self) -> None:
        with pytest.raises(AssertionError, match="Invalid commit author email"):
            check_commit(self.msg, "User Name", "test.user@mail.com")

    def test_no_message(self) -> None:
        check_commit(self.msg, "User Name", "user.name@mail.com")
        # success

    def test_valid_message(self) -> None:
        check_commit(
            self.msg,
            "User Name",
            "user.name@mail.com",
            "chore: important commit",
        )
        # success

    def test_invalid_message(self) -> None:
        with pytest.raises(AssertionError, match="Mismatching commit message"):
            check_commit(
                self.msg,
                "User Name",
                "user.name@mail.com",
                "fix: important commit",
            )

    def test_malformed_commit_line(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            check_commit(
                "User Name user.name@mail.com important commit",
                "User Name",
                "user.name@mail.com",
                "fix: important commit",
            )


class PathChoiceScenario(FileTreeScenario):
    def _prepare_repository(self, repo: TestRepository) -> None:
        pass

    def verify(self, repo: TestRepository) -> None:
        pass


class TestScenario:
    def test_assigns_given_base_path(self, fs: FakeFilesystem) -> None:  # noqa: ARG002
        scenario = PathChoiceScenario("dummy", "success", Path("test"))
        assert scenario.path == Path("test") / "dummy"

    def test_prepare_fails_if_repo_dirs_dont_exist(self, fs: FakeFilesystem) -> None:
        fs.create_dir("/base/remote")
        fs.create_dir("/base/local")
        with pytest.raises(OSError):  # noqa: PT011
            DummyScenario().prepare(Path("/base/remote/dir"), Path("/base/local/dir"))

    @patch("shutil.copytree")
    def test_prepare_success(
        self,
        copytree: MagicMock,
        remote_path: Path,
        local_path: Path,
        fs: FakeFilesystem,
    ) -> None:
        fs.create_dir(remote_path)
        fs.create_dir(local_path)

        with patch("gh_action_integration_test.scenario.scenario.TestRepository") as mock_class:
            mock_repo = mock_class()
            mock_repo.tag = "mocked_dummy"
            mock_repo.remote_path = remote_path / "mocked_dummy"
            mock_repo.local_path = local_path / "mocked_dummy"
            mock_repo.default_branch = "prime"
            mock_class.return_value = mock_repo

            DummyScenario("mocked_dummy").prepare(remote_path, local_path)

            mock_repo.initialize_repo.assert_called_once_with()
            copytree.assert_called_once_with(
                Path("action_tests", "_files", "mocked_dummy"), local_path / "mocked_dummy", dirs_exist_ok=True
            )

            mock_repo.commit_all.assert_called_once_with("Initial commit")
            mock_repo.push.assert_called_once_with()

    def test_check_outcome_success(self) -> None:
        DummyScenario().check_outcome("success")
        # should not throw

    def test_check_outcome_failure(self) -> None:
        with pytest.raises(AssertionError, match="Invalid action outcome: failure"):
            DummyScenario().check_outcome("failure")

    def test_test_successful_outcome(self, remote_path: Path, local_path: Path, fs: FakeFilesystem) -> None:
        fs.create_dir(remote_path)
        fs.create_dir(local_path)

        with patch("gh_action_integration_test.scenario.scenario.TestRepository") as mock_class:
            mock_repo = mock_class()
            mock_repo.tag = "dummy"
            mock_repo.remote_path = remote_path / "dummy"
            mock_repo.local_path = local_path / "dummy"
            mock_repo.default_branch = "prime"
            mock_class.return_value = mock_repo

            s = DummyScenario()
            s.test(remote_path, local_path, "success")

            assert s.verified

    def test_test_unsuccessful_outcome(self, remote_path: Path, local_path: Path, fs: FakeFilesystem) -> None:
        fs.create_dir(remote_path)
        fs.create_dir(local_path)

        with patch("gh_action_integration_test.scenario.scenario.TestRepository") as mock_class:
            mock_repo = mock_class()
            mock_repo.tag = "dummy"
            mock_repo.remote_path = remote_path / "dummy"
            mock_repo.local_path = local_path / "dummy"
            mock_repo.default_branch = "prime"
            mock_class.return_value = mock_repo

            s = DummyScenario()

            with pytest.raises(AssertionError, match="Invalid action outcome: failed"):
                s.test(remote_path, local_path, "failed")

            assert not s.verified
