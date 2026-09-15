import string

from gh_action_integration_test.git.utils import generate_secure_string


def test_generate_secure_string_default_length() -> None:
    secure_string = generate_secure_string()
    assert len(secure_string) == 16, f"Expected length 16, got {len(secure_string)}"


def test_generate_secure_string_empty() -> None:
    secure_string = generate_secure_string(0)
    assert secure_string == "", f"Expected empty string, got {secure_string}"


def test_generate_secure_string_large() -> None:
    secure_string = generate_secure_string(500)
    assert len(secure_string) == 500, f"Expected length 500, got {len(secure_string)}"


def test_generate_secure_string_allowed_characters() -> None:
    secure_string = generate_secure_string()
    for char in secure_string:
        assert char in string.ascii_letters + string.digits + string.punctuation, f"Character {char} is not allowed"
