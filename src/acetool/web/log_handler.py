"""Log handler for broadcasting logs to WebSocket clients."""

import asyncio
from typing import Any

from loguru import logger

# Global handler ID to prevent duplicate handlers
_global_handler_id: int | None = None


class LogBroadcaster:
    """Broadcast logs to multiple WebSocket clients."""

    def __init__(self) -> None:
        """Initialize log broadcaster."""
        self.clients: list[asyncio.Queue] = []
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Setup loguru handler to broadcast logs."""
        global _global_handler_id  # noqa: PLW0603

        # Check if handler is already registered globally
        if _global_handler_id is not None:
            return

        def log_sink(message: Any) -> None:
            """Custom sink to broadcast log messages."""
            log_text = str(message)
            # Get the current broadcaster instance to access clients
            if _broadcaster_instance is not None:
                for client_queue in _broadcaster_instance.clients[:]:  # Use slice to avoid modification during iteration
                    try:
                        client_queue.put_nowait(log_text)
                    except asyncio.QueueFull:
                        pass
                    except Exception:
                        pass

        _global_handler_id = logger.add(log_sink, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO", filter=lambda record: record["level"].no >= 20)

    def add_client(self, queue: asyncio.Queue) -> None:
        """Add a client queue.

        Args:
            queue: Client's asyncio queue
        """
        self.clients.append(queue)

    def remove_client(self, queue: asyncio.Queue) -> None:
        """Remove a client queue.

        Args:
            queue: Client's asyncio queue
        """
        if queue in self.clients:
            self.clients.remove(queue)


_broadcaster_instance: LogBroadcaster | None = None


def get_log_broadcaster() -> LogBroadcaster:
    """Get the global log broadcaster instance.

    Returns:
        LogBroadcaster instance
    """
    global _broadcaster_instance  # noqa: PLW0603
    if _broadcaster_instance is None:
        _broadcaster_instance = LogBroadcaster()
    return _broadcaster_instance

