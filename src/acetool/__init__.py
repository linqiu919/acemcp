"""Acetool - MCP server for codebase indexing."""

from acetool.server import run

__version__ = "0.1.0"

__all__ = ["run"]


def hello() -> str:
    """Hello function for testing."""
    return "Hello from acetool!"
