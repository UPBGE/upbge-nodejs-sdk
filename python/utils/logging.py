# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Centralized logging module for UPBGE Node.js SDK.
Controls debug output via environment variables.
"""

import logging
import os
import sys

# Environment variables to control logging
# UPBGE_JS_DEBUG=1        -> Enable debug logs
# UPBGE_JS_LOG_LEVEL=INFO -> Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)


def _get_log_level():
    """Get log level from environment or default."""
    # Check UPBGE_JS_LOG_LEVEL first
    level_name = os.environ.get("UPBGE_JS_LOG_LEVEL", "").upper()
    if level_name in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        return getattr(logging, level_name)

    # Check UPBGE_JS_DEBUG for backward compatibility
    if os.environ.get("UPBGE_JS_DEBUG", "").lower() in ("1", "true", "yes"):
        return logging.DEBUG

    # Default to INFO
    return logging.INFO


# Create logger for the SDK
_logger = logging.getLogger("upbge_nodejs_sdk")
_logger.setLevel(_get_log_level())

# Prevent duplicate handlers
if not _logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[UPBGE-JS] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

# Don't propagate to root logger (avoid duplicate output)
_logger.propagate = False


def debug(msg, *args):
    """Log debug message."""
    _logger.debug(msg, *args)


def info(msg, *args):
    """Log info message."""
    _logger.info(msg, *args)


def warning(msg, *args):
    """Log warning message."""
    _logger.warning(msg, *args)


def error(msg, *args):
    """Log error message."""
    _logger.error(msg, *args)


def critical(msg, *args):
    """Log critical message."""
    _logger.critical(msg, *args)


def is_debug_enabled():
    """Check if debug logging is enabled."""
    return _logger.level <= logging.DEBUG
