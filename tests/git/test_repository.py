from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture

import gh_action_integration_test.git.repository as repository_module
from gh_action_integration_test.git.repository import TestRepository, _setup_repository_path

# prevent pytest discovery of this class
TestRepository.__test__ = False  # type: ignore[attr-defined]


class TestSetupRepositoryPath:
    def test_creates_base_dir_if_it_does_not_exist(self, fs: FakeFilesystem) -> None:  # noqa: ARG002
        repo_path = Path("/base/repo")

        _setup_repository_path(repo_path)

        assert repo_path.parent.is_dir()
        assert repo_path.is_dir()
        assert repo_path.absolute() == Path("/base/repo")

    def test_ignores_existing_base_dir(self, fs: FakeFilesystem) -> None:
        fs.create_dir("/base")
        repo_path = Path("/base/repo")

        _setup_repository_path(repo_path)

        assert repo_path.parent.is_dir()
        assert repo_path.is_dir()
        assert repo_path.absolute() == Path("/base/repo")

    def test_repo_dir_exists(self, fs: FakeFilesystem) -> None:
        fs.create_dir("/base/repo")
        repo_path = Path("/base/repo")

        with pytest.raises(FileExistsError):
            _setup_repository_path(repo_path)

    def test_repo_dir_is_root(self, fs: FakeFilesystem) -> None:  # noqa: ARG002
        with pytest.raises(FileExistsError):
            _setup_repository_path(Path("/"))


class TestTestRepository:
    @pytest.fixture
    def mock_git(self) -> Generator[MagicMock]:
        with patch("gh_action_integration_test.git.repository.git") as mock_git:
            yield mock_git

    @pytest.fixture
    def valid_paths(self, fs: FakeFilesystem) -> tuple[Path, Path]:
        fs.create_dir("/remote")
        remote_base_path = Path("/remote")
        fs.create_dir("/local")
        local_base_path = Path("/local")
        return remote_base_path, local_base_path

    @pytest.fixture
    def valid_repository(self, valid_paths: tuple[Path, Path]) -> TestRepository:
        return TestRepository("test-repository", *valid_paths)

    @pytest.fixture
    def trunk_branch_repository(self, valid_paths: tuple[Path, Path]) -> TestRepository:
        return TestRepository("test-repository", *valid_paths, default_branch="trunk")

    def test_sets_up_remote_and_local_paths(self, mock_git: MagicMock, valid_paths: tuple[Path, Path]) -> None:
        mock_git.return_value.stdout = "trunk"

        repo = TestRepository("test0", *valid_paths)

        assert repo is not None
        assert repo.tag == "test0"
        assert repo.remote_path == valid_paths[0] / "test0"
        assert repo.local_path == valid_paths[1] / "test0"

    def test_uses_configured_default_branch(self, valid_paths: tuple[Path, Path]) -> None:
        repo = TestRepository("test1", *valid_paths, default_branch="trunk")

        assert repo.default_branch == "trunk"

    def test_uses_default_branch_if_not_configured(self, valid_paths: tuple[Path, Path]) -> None:
        repo = TestRepository("test3", *valid_paths)

        assert repo.default_branch == "main"

    def test_initialize_repo_with_default_user_email(
        self, mock_git: MagicMock, valid_repository: TestRepository
    ) -> None:
        mock_git.side_effect = [
            MagicMock(stdout="initialized repository"),
            MagicMock(stdout="cloned repository"),
        ]
        with patch("gh_action_integration_test.git.repository.set_git_config") as mock_git_config:
            valid_repository.initialize_repo()

            mock_git.assert_has_calls(
                [
                    call("init", "--bare", "-b", "main", cwd=Path("/remote/test-repository")),
                    call("clone", "/remote/test-repository", ".", cwd=Path("/local/test-repository")),
                ]
            )
            mock_git_config.assert_called_once_with(Path("/local/test-repository"), "Test User", "test@user.com")

    def test_initialize_repo_with_configured_user_email(
        self, mock_git: MagicMock, valid_repository: TestRepository
    ) -> None:
        mock_git.side_effect = [
            MagicMock(stdout="initialized repo"),
            MagicMock(stdout="cloned repo"),
        ]
        with patch("gh_action_integration_test.git.repository.set_git_config") as mock_git_config:
            valid_repository.initialize_repo("Custom User", "custom.user@mail.com")

            mock_git.assert_has_calls(
                [
                    call("init", "--bare", "-b", "main", cwd=Path("/remote/test-repository")),
                    call("clone", "/remote/test-repository", ".", cwd=Path("/local/test-repository")),
                ]
            )
            mock_git_config.assert_called_once_with(
                Path("/local/test-repository"), "Custom User", "custom.user@mail.com"
            )

    def test_initialize_repo_with_other_default_branch(
        self, mock_git: MagicMock, trunk_branch_repository: TestRepository
    ) -> None:
        mock_git.side_effect = [
            MagicMock(stdout="initialized repository"),
            MagicMock(stdout="cloned repository"),
        ]
        with patch("gh_action_integration_test.git.repository.set_git_config") as mock_git_config:
            trunk_branch_repository.initialize_repo()

            mock_git.assert_has_calls(
                [
                    call("init", "--bare", "-b", "trunk", cwd=Path("/remote/test-repository")),
                    call("clone", "/remote/test-repository", ".", cwd=Path("/local/test-repository")),
                ]
            )
            mock_git_config.assert_called_once_with(Path("/local/test-repository"), "Test User", "test@user.com")

    def test_commit_all_without_message(
        self, mock_git: MagicMock, valid_repository: TestRepository, mocker: MockerFixture
    ) -> None:

        spy_gen = mocker.spy(repository_module, "generate_secure_string")

        valid_repository.commit_all()

        mock_git.assert_has_calls(
            [
                call("add", ".", cwd=Path("/local/test-repository")),
                call("commit", "-am", spy_gen.spy_return, cwd=Path("/local/test-repository")),
            ]
        )

        spy_gen.assert_called_once()

    def test_commit_all_with_message(
        self, mock_git: MagicMock, valid_repository: TestRepository, mocker: MockerFixture
    ) -> None:
        spy_gen = mocker.spy(repository_module, "generate_secure_string")

        valid_repository.commit_all("test message")

        mock_git.assert_has_calls(
            [
                call("add", ".", cwd=Path("/local/test-repository")),
                call("commit", "-am", "test message", cwd=Path("/local/test-repository")),
            ]
        )

        spy_gen.assert_not_called()

    def test_push_with_branch_and_local_path(self, mock_git: MagicMock, valid_repository: TestRepository) -> None:
        valid_repository.push()

        mock_git.assert_called_with("push", "origin", "main", cwd=Path("/local/test-repository"))
