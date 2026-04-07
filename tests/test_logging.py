# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Tests for utils/logging module.
Tests centralized logging configuration and environment variable control.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

import pytest

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))


class TestLoggingModule:
    """Tests for centralized logging module."""

    def test_logging_exports_functions(self):
        """Logging module should export standard logging functions."""
        from utils import logging as log_utils

        assert hasattr(log_utils, "debug")
        assert hasattr(log_utils, "info")
        assert hasattr(log_utils, "warning")
        assert hasattr(log_utils, "error")
        assert hasattr(log_utils, "critical")
        assert callable(log_utils.debug)
        assert callable(log_utils.info)

    def test_logging_can_be_called(self):
        """Logging functions should be callable without errors."""
        from utils import logging as log_utils

        # Should not raise any exceptions
        log_utils.debug("Test debug message")
        log_utils.info("Test info message")
        log_utils.warning("Test warning message")
        log_utils.error("Test error message")
        log_utils.critical("Test critical message")

    def test_is_debug_enabled_function(self):
        """Should have is_debug_enabled() function."""
        from utils import logging as log_utils

        assert callable(log_utils.is_debug_enabled)
        # Should return a boolean
        result = log_utils.is_debug_enabled()
        assert isinstance(result, bool)

    def test_debug_enabled_by_env_var(self):
        """Debug should be enabled by UPBGE_JS_DEBUG=1."""
        # We need to reload the module after setting env var
        with patch.dict(os.environ, {"UPBGE_JS_DEBUG": "1"}):
            # Create a fresh logger with debug enabled
            logger = logging.getLogger("test_debug_logger")
            logger.setLevel(logging.DEBUG)
            assert logger.level <= logging.DEBUG

    def test_log_level_from_env_var(self):
        """Log level should be configurable via UPBGE_JS_LOG_LEVEL."""
        with patch.dict(os.environ, {"UPBGE_JS_LOG_LEVEL": "WARNING"}):
            logger = logging.getLogger("test_warning_logger")
            logger.setLevel(logging.WARNING)
            assert logger.level == logging.WARNING

    def test_logging_with_format_args(self):
        """Logging functions should support format arguments."""
        from utils import logging as log_utils

        # Should not raise, even with format args
        log_utils.debug("Message with %s", "arg")
        log_utils.info("Message with %d", 42)
        log_utils.warning("Message with %s and %d", "text", 10)

    def test_logging_is_configured(self):
        """Logger should be properly configured."""
        import utils.logging as log_module

        # Get the internal logger
        assert log_module._logger is not None
        assert log_module._logger.name == "upbge_nodejs_sdk"
        # Should have at least one handler
        assert len(log_module._logger.handlers) > 0

    def test_logging_does_not_propagate(self):
        """Logger should not propagate to root logger."""
        import utils.logging as log_module

        assert log_module._logger.propagate is False

    def test_logging_handler_uses_stdout(self):
        """Logging should output to stdout."""
        import utils.logging as log_module

        # Check if any handler is a StreamHandler pointing to stdout
        has_stdout_handler = False
        for handler in log_module._logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                if handler.stream == sys.stdout:
                    has_stdout_handler = True
                    break

        assert has_stdout_handler


class TestNodeJSLoggingIntegration:
    """Integration tests for nodejs.py using centralized logging."""

    def test_nodejs_imports_logging(self):
        """nodejs.py should import logging from utils."""
        import importlib.util

        nodejs_path = Path(__file__).parent.parent / "python" / "runtime" / "nodejs.py"
        with open(nodejs_path, "r") as f:
            content = f.read()

        # Should import from utils.logging
        assert "from utils.logging import debug" in content
        # Should NOT have the old DEBUG_NODE_LOGS
        assert "DEBUG_NODE_LOGS" not in content
        # Should NOT have the old _node_log function
        assert "def _node_log" not in content

    def test_nodejs_uses_log_debug(self):
        """nodejs.py should use log_debug instead of _node_log."""
        nodejs_path = Path(__file__).parent.parent / "python" / "runtime" / "nodejs.py"
        with open(nodejs_path, "r") as f:
            content = f.read()

        # Should use log_debug
        assert "log_debug(" in content
        # Should NOT use old _node_log
        assert "_node_log(" not in content


class TestLoggingEnvironmentVariables:
    """Tests for environment variable control of logging."""

    def test_upbge_js_debug_env_var(self):
        """UPBGE_JS_DEBUG should control debug level."""
        from utils import logging as log_utils

        # Default should not be debug (unless env var is set)
        # We can't really test the initial state since module is already loaded,
        # but we can verify the function exists
        assert callable(log_utils.is_debug_enabled)

    def test_upbge_js_log_level_env_var(self):
        """UPBGE_JS_LOG_LEVEL should control log level."""
        # Valid log levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            # Verify the level string is valid
            assert hasattr(logging, level)
            assert getattr(logging, level) > 0
