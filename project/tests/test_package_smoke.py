"""Smoke tests that verify the package is importable."""

from bpe_token_automata import __version__


def test_package_imports() -> None:
    """The installed package must import without error."""
    assert isinstance(__version__, str)
    assert __version__ == "0.1.0"
