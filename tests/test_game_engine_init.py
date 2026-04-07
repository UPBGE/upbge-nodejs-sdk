# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Tests for game_engine/__init__.py register/unregister functions.
"""

import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))


class TestGameEngineInit:
    """Tests for game_engine/__init__.py module registration."""

    def test_unregister_looks_up_correct_module_names(self):
        """Unregister should look up modules with 'game_engine.' prefix."""
        # Import the function
        from game_engine import unregister

        # Create mock modules
        mock_controller = MagicMock()
        mock_script_handler = MagicMock()
        mock_ui = MagicMock()

        # Register them in sys.modules with correct names
        sys.modules["game_engine.controller"] = mock_controller
        sys.modules["game_engine.script_handler"] = mock_script_handler
        sys.modules["game_engine.ui"] = mock_ui

        try:
            # Call unregister
            unregister()

            # Verify unregister was called on each module
            mock_controller.unregister.assert_called_once()
            mock_script_handler.unregister.assert_called_once()
            mock_ui.unregister.assert_called_once()
        finally:
            # Cleanup
            sys.modules.pop("game_engine.controller", None)
            sys.modules.pop("game_engine.script_handler", None)
            sys.modules.pop("game_engine.ui", None)

    def test_unregister_handles_missing_modules(self):
        """Unregister should not crash if modules are missing."""
        from game_engine import unregister

        # Ensure modules are not registered
        sys.modules.pop("game_engine.controller", None)
        sys.modules.pop("game_engine.script_handler", None)
        sys.modules.pop("game_engine.ui", None)

        # Should not raise an exception
        try:
            unregister()
        except Exception as e:
            pytest.fail(f"unregister() raised exception: {e}")

    def test_unregister_skips_none_modules(self):
        """Unregister should skip calling unregister on None modules."""
        from game_engine import unregister

        # Register only one module
        mock_controller = MagicMock()
        sys.modules["game_engine.controller"] = mock_controller
        sys.modules.pop("game_engine.script_handler", None)
        sys.modules.pop("game_engine.ui", None)

        try:
            # Should not crash
            unregister()
            # Controller should be unregistered
            mock_controller.unregister.assert_called_once()
        finally:
            sys.modules.pop("game_engine.controller", None)

    def test_unregister_module_lookup_is_correct(self):
        """Verify module names use game_engine prefix (not bare names)."""
        from game_engine import unregister

        # Create mocks with different names to ensure correct ones are called
        mock_controller_correct = MagicMock()
        mock_controller_wrong = MagicMock()

        # Register with both names (simulating the old bug)
        sys.modules["game_engine.controller"] = mock_controller_correct
        sys.modules["controller"] = mock_controller_wrong

        try:
            unregister()
            # Only the correct one should be called
            mock_controller_correct.unregister.assert_called_once()
            # The wrong one should NOT be called
            mock_controller_wrong.unregister.assert_not_called()
        finally:
            sys.modules.pop("game_engine.controller", None)
            sys.modules.pop("controller", None)
