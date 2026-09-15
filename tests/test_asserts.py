import re
from typing import Any

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from gh_action_integration_test.asserts import (
    assert_eq,
    assert_file_exists,
    assert_file_missing,
    assert_files_exist,
    assert_files_missing,
    assert_true,
)


class TestAssertTrue:
    def test_does_not_raise_when_condition_is_true(self) -> None:
        assert_true(True, "Must not throw")  # noqa: FBT003

    def test_raises_when_condition_is_false(self) -> None:
        with pytest.raises(AssertionError, match="Must throw"):
            assert_true(False, "Must throw")  # noqa: FBT003


class TestAssertEq:
    @staticmethod
    def equal_params() -> list[tuple[Any, Any]]:
        return [
            (1, 1),
            ("a", "a"),
            ([1, 2], [1, 2]),
            ({"key": "value"}, {"key": "value"}),
        ]

    @staticmethod
    def not_equal_params() -> list[tuple[Any, Any]]:
        return [
            (1, 2),
            ("a", "b"),
            ([1, 2], [2, 1]),
            ({"key": "value"}, {"key": "different_value"}),
        ]

    @pytest.mark.parametrize(("expected", "actual"), equal_params())
    def test_does_not_raise_when_values_are_equal(self, expected: Any, actual: Any) -> None:  # noqa: ANN401
        assert_eq(expected, actual, "Must be equal.")

    @pytest.mark.parametrize(("expected", "actual"), not_equal_params())
    def test_raises_when_values_are_not_equal(self, expected: Any, actual: Any) -> None:  # noqa: ANN401
        expected_msg = re.escape(f"Mismatch: Expected: <{expected}>, Actual: <{actual}>")
        with pytest.raises(AssertionError, match=expected_msg):
            assert_eq(expected, actual, "Mismatch:")


class TestAssertFilesExist:
    def test_assert_file_exists_fail(self, fs: FakeFilesystem) -> None:  # noqa: ARG002
        with pytest.raises(AssertionError, match="File does not exist or is not a regular file: /base/path/must_exist"):
            assert_file_exists("/base/path/must_exist")

    def test_assert_file_exists_fail_no_file(self, fs: FakeFilesystem) -> None:
        fs.create_dir("/temporary/directory")
        with pytest.raises(AssertionError, match="File does not exist or is not a regular file: /temporary/directory"):
            assert_file_exists("/temporary/directory")

    def test_assert_file_exists_success(self, fs: FakeFilesystem) -> None:
        fs.create_file("must_exist", contents="important content")
        assert_file_exists("must_exist")
        # shouldn't throw

    def test_assert_files_exist_fail_empty_list(self, fs: FakeFilesystem) -> None:  # noqa: ARG002
        with pytest.raises(AssertionError, match="Must specify at least one path"):
            assert_files_exist("/temporary/directory")

    def test_assert_files_exist_one_file_not_existing(self, fs: FakeFilesystem) -> None:
        fs.create_file("/temp/dir/file1")

        with pytest.raises(AssertionError, match="File does not exist or is not a regular file: /temp/dir/file2"):
            assert_files_exist("/temp/dir/", "file1", "file2")

    def test_assert_files_exist_no_file_exists(self, fs: FakeFilesystem) -> None:  # noqa: ARG002
        with pytest.raises(AssertionError, match="File does not exist or is not a regular file: /temp/dir/file0"):
            assert_files_exist("/temp/dir/", "file0", "file1", "file2")

    def test_assert_files_exist_success(self, fs: FakeFilesystem) -> None:
        fs.create_file("/base/file0")
        fs.create_file("/base/file1")
        fs.create_file("/base/file2")
        fs.create_file("/base/dir/file3")
        assert_files_exist("/base/", "file0", "file1", "file2", "dir/file3")


class TestAssertFilesMissing:
    def test_assert_file_missing_fail(self, fs: FakeFilesystem) -> None:
        fs.create_file("/base/path/shouldnt_exist", contents="important content")
        with pytest.raises(AssertionError, match="File does exist but shouldn't: /base/path/shouldnt_exist"):
            assert_file_missing("/base/path/shouldnt_exist")

    def test_assert_file_missing_success(self, fs: FakeFilesystem) -> None:  # noqa: ARG002
        assert_file_missing("/base/path/doesnt_exist")
        # shouldn't throw

    def test_assert_file_missing_success_no_file(self, fs: FakeFilesystem) -> None:
        fs.create_dir("is_dir")
        assert_file_missing("is_dir")
        # shouldn't throw

    def test_assert_files_missing_fail_empty_list(self, fs: FakeFilesystem) -> None:  # noqa: ARG002
        with pytest.raises(AssertionError, match="Must specify at least one path"):
            assert_files_missing("/dir/")

    def test_assert_files_missing_fail_one_file_existing(self, fs: FakeFilesystem) -> None:
        fs.create_file("/temp/dir/file2")
        with pytest.raises(AssertionError, match="File does exist but shouldn't: /temp/dir/file2"):
            assert_files_missing("/temp", "dir/file0", "dir/file1", "dir/file2")

    def test_assert_files_missing_fail_all_files_existing(self, fs: FakeFilesystem) -> None:
        fs.create_file("my/dir/test0")
        fs.create_file("my/dir/test1")
        fs.create_file("my/dir/test2")
        with pytest.raises(AssertionError, match="File does exist but shouldn't: my/dir/test0"):
            assert_files_missing("my/dir", "test0", "test1", "test2")

    def test_assert_files_missing_success_base_dir_not_existing(self, fs: FakeFilesystem) -> None:
        fs.create_dir("/base")
        assert_files_missing("/base/", "file0", "file1")
        # shouldn't throw

    def test_assert_files_missing_success_neither_file_existing(self, fs: FakeFilesystem) -> None:
        fs.create_dir("my/dir")
        assert_files_missing("my/dir", "file0", "file1", "subdir/file2")
        # shouldn't throw
