"""Configuration management for acetool MCP server."""

import toml
from pathlib import Path

from dynaconf import Dynaconf
from loguru import logger

# Default configuration values
DEFAULT_CONFIG = {
    "BATCH_SIZE": 10,
    "MAX_LINES_PER_BLOB": 800,
    "BASE_URL": "https://api.example.com",
    "TOKEN": "your-token-here",
    "TEXT_EXTENSIONS": [
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".go",
        ".rs",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".rb",
        ".php",
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".xml",
        ".html",
        ".css",
        ".scss",
        ".sql",
        ".sh",
        ".bash",
    ],
    "EXCLUDE_PATTERNS": [
        ".venv",
        "venv",
        ".env",
        "env",
        "node_modules",
        ".git",
        ".svn",
        ".hg",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        ".eggs",
        "*.egg-info",
        "dist",
        "build",
        ".idea",
        ".vscode",
        ".DS_Store",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "pip-log.txt",
        "pip-delete-this-directory.txt",
        ".coverage",
        "htmlcov",
        ".gradle",
        "target",
        "bin",
        "obj",
    ],
}

# User configuration and data paths
USER_CONFIG_DIR = Path.home() / ".acetool"
USER_CONFIG_FILE = USER_CONFIG_DIR / "settings.toml"
USER_DATA_DIR = USER_CONFIG_DIR / "data"


def _ensure_user_config() -> Path:
    """Ensure user configuration file exists.

    Returns:
        Path to user configuration file
    """
    if not USER_CONFIG_DIR.exists():
        USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created user config directory: {USER_CONFIG_DIR}")

    if not USER_DATA_DIR.exists():
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created user data directory: {USER_DATA_DIR}")

    if not USER_CONFIG_FILE.exists():
        with USER_CONFIG_FILE.open("w", encoding="utf-8") as f:
            toml.dump(DEFAULT_CONFIG, f)
        logger.info(f"Created default user config file: {USER_CONFIG_FILE}")

    return USER_CONFIG_FILE


# Ensure user config exists and initialize dynaconf
_ensure_user_config()

settings = Dynaconf(
    envvar_prefix="ACETOOL",
    settings_files=[str(USER_CONFIG_FILE)],
    load_dotenv=True,
    merge_enabled=True,
)


class Config:
    """MCP server configuration."""

    def __init__(self, base_url: str | None = None, token: str | None = None) -> None:
        """Initialize configuration.

        Args:
            base_url: Override BASE_URL from command line
            token: Override TOKEN from command line
        """
        self._cli_base_url = base_url
        self._cli_token = token

        self.index_storage_path: Path = USER_DATA_DIR
        self.batch_size: int = settings.get("BATCH_SIZE", DEFAULT_CONFIG["BATCH_SIZE"])
        self.max_lines_per_blob: int = settings.get("MAX_LINES_PER_BLOB", DEFAULT_CONFIG["MAX_LINES_PER_BLOB"])
        self.base_url: str = base_url or settings.get("BASE_URL", DEFAULT_CONFIG["BASE_URL"])
        self.token: str = token or settings.get("TOKEN", DEFAULT_CONFIG["TOKEN"])
        self.text_extensions: set[str] = set(settings.get("TEXT_EXTENSIONS", DEFAULT_CONFIG["TEXT_EXTENSIONS"]))
        self.exclude_patterns: list[str] = settings.get("EXCLUDE_PATTERNS", DEFAULT_CONFIG["EXCLUDE_PATTERNS"])

    def reload(self) -> None:
        """Reload configuration from user config file, respecting CLI overrides."""
        settings.reload()

        self.index_storage_path = USER_DATA_DIR
        self.batch_size = settings.get("BATCH_SIZE", DEFAULT_CONFIG["BATCH_SIZE"])
        self.max_lines_per_blob = settings.get("MAX_LINES_PER_BLOB", DEFAULT_CONFIG["MAX_LINES_PER_BLOB"])
        self.base_url = self._cli_base_url or settings.get("BASE_URL", DEFAULT_CONFIG["BASE_URL"])
        self.token = self._cli_token or settings.get("TOKEN", DEFAULT_CONFIG["TOKEN"])
        self.text_extensions = set(settings.get("TEXT_EXTENSIONS", DEFAULT_CONFIG["TEXT_EXTENSIONS"]))
        self.exclude_patterns = settings.get("EXCLUDE_PATTERNS", DEFAULT_CONFIG["EXCLUDE_PATTERNS"])

    def validate(self) -> None:
        """Validate configuration."""
        if self.batch_size <= 0:
            msg = "BATCH_SIZE must be positive"
            raise ValueError(msg)
        if self.max_lines_per_blob <= 0:
            msg = "MAX_LINES_PER_BLOB must be positive"
            raise ValueError(msg)
        if not self.base_url:
            msg = "BASE_URL must be configured"
            raise ValueError(msg)
        if not self.token:
            msg = "TOKEN must be configured"
            raise ValueError(msg)


_config_instance: Config | None = None


def get_config() -> Config:
    """Get the global config instance.

    Returns:
        Config instance
    """
    global _config_instance  # noqa: PLW0603
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def init_config(base_url: str | None = None, token: str | None = None) -> Config:
    """Initialize config with command line arguments.

    Args:
        base_url: Override BASE_URL from command line
        token: Override TOKEN from command line

    Returns:
        Config instance
    """
    global _config_instance  # noqa: PLW0603
    _config_instance = Config(base_url=base_url, token=token)
    return _config_instance


config = get_config()

