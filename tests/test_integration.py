# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Integration tests for UPBGE Node.js SDK.
Tests interactions between modules and realistic scenarios.
"""

import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))


class TestPathsAndContextIntegration:
    """Integration tests between paths and context modules."""

    def test_context_builder_with_sdk_path(self):
        """Context builder should work with SDK paths from utils.paths."""
        from utils.paths import get_sdk_root
        from game_engine.context_builder import build_context

        # Get SDK path
        sdk_path = get_sdk_root()

        # Build context (should not crash)
        ctx = build_context()
        assert isinstance(ctx, dict)
        assert "engine" in ctx

    def test_logging_integration_with_modules(self):
        """Logging should be usable from multiple modules."""
        from utils.logging import debug, info, warning
        from utils.paths import get_platform

        # Should be able to log from different modules
        debug(f"Platform: {get_platform()}")
        info("Context building test")
        warning("Integration test running")


class TestContextBuilderWithMocks:
    """Additional integration tests for context builder with realistic mocks."""

    def test_build_context_with_keyboard_sensor(self):
        """Context should properly extract keyboard sensor data."""
        mock_kb_sensor = MagicMock()
        mock_kb_sensor.name = "KeyboardSensor"
        mock_kb_sensor.type = 1

        mock_event_key_1 = MagicMock()
        mock_event_key_1.active = True
        mock_event_key_1.activated = False
        mock_event_key_1.released = False

        mock_event_key_2 = MagicMock()
        mock_event_key_2.active = False
        mock_event_key_2.activated = True
        mock_event_key_2.released = False

        mock_kb_sensor.inputs = {87: mock_event_key_1, 83: mock_event_key_2}
        mock_kb_sensor.positive = True

        mock_controller = MagicMock()
        mock_controller.name = "Controller"
        mock_controller.sensors = [mock_kb_sensor]
        mock_controller.actuators = []
        mock_controller.owner = None

        mock_logic = MagicMock()
        mock_logic.getCurrentController = MagicMock(return_value=mock_controller)
        mock_logic.getSceneList = MagicMock(return_value=[])
        mock_logic.getAverageFrameRate = MagicMock(return_value=60.0)
        mock_logic.getCurrentFrame = MagicMock(return_value=1)
        mock_logic.getTimeSinceStart = MagicMock(return_value=0.016)
        mock_logic.KX_INPUT_ACTIVE = 1
        mock_logic.KX_INPUT_JUST_ACTIVATED = 2
        mock_logic.KX_INPUT_JUST_RELEASED = 3

        mock_bge = MagicMock()
        mock_bge.logic = mock_logic
        mock_bge.render = None

        from game_engine.context_builder import build_context

        with patch("game_engine.context_builder.bge", mock_bge):
            ctx = build_context()

            # Verify keyboard data was extracted
            assert ctx["keyboard"] is not None
            # Should have pressed keys
            assert len(ctx["keyboard"]["pressed"]) > 0
            assert len(ctx["keyboard"]["justPressed"]) > 0

    def test_build_context_with_collision_sensor(self):
        """Context should handle collision sensor data."""
        mock_hit_obj_1 = MagicMock()
        mock_hit_obj_1.name = "Wall"

        mock_hit_obj_2 = MagicMock()
        mock_hit_obj_2.name = "Floor"

        mock_collision_sensor = MagicMock()
        mock_collision_sensor.name = "CollisionSensor"
        mock_collision_sensor.type = 0
        mock_collision_sensor.positive = True
        mock_collision_sensor.hitObjectList = [mock_hit_obj_1, mock_hit_obj_2]

        mock_controller = MagicMock()
        mock_controller.name = "Ctrl"
        mock_controller.sensors = [mock_collision_sensor]
        mock_controller.actuators = []
        mock_controller.owner = None

        mock_logic = MagicMock()
        mock_logic.getCurrentController = MagicMock(return_value=mock_controller)
        mock_logic.getSceneList = MagicMock(return_value=[])
        mock_logic.getAverageFrameRate = MagicMock(return_value=60.0)
        mock_logic.getCurrentFrame = MagicMock(return_value=1)
        mock_logic.getTimeSinceStart = MagicMock(return_value=0.016)

        mock_bge = MagicMock()
        mock_bge.logic = mock_logic
        mock_bge.render = None

        from game_engine.context_builder import build_context

        with patch("game_engine.context_builder.bge", mock_bge):
            ctx = build_context()

            # Verify collision data was extracted
            assert ctx["sensors"] is not None
            assert "CollisionSensor" in ctx["sensors"]
            sensor_data = ctx["sensors"]["CollisionSensor"]
            assert "hitObjectList" in sensor_data
            assert len(sensor_data["hitObjectList"]) == 2
            assert sensor_data["hitObjectList"][0]["name"] == "Wall"
            assert sensor_data["hitObjectList"][1]["name"] == "Floor"

    def test_build_context_with_joystick_sensor(self):
        """Context should handle joystick sensor data."""
        mock_joy_sensor = MagicMock()
        mock_joy_sensor.name = "JoystickSensor"
        mock_joy_sensor.type = 13
        mock_joy_sensor.index = 0
        mock_joy_sensor.positive = True

        # Mock joystick button status
        def mock_button_status(btn_id):
            return btn_id in [0, 1]  # Buttons 0 and 1 pressed

        mock_joy_sensor.getButtonStatus = MagicMock(side_effect=mock_button_status)
        mock_joy_sensor.axisValues = [0.5, -0.5, 0.0, 0.0]

        mock_controller = MagicMock()
        mock_controller.name = "Ctrl"
        mock_controller.sensors = [mock_joy_sensor]
        mock_controller.actuators = []
        mock_controller.owner = None

        mock_logic = MagicMock()
        mock_logic.getCurrentController = MagicMock(return_value=mock_controller)
        mock_logic.getSceneList = MagicMock(return_value=[])
        mock_logic.getAverageFrameRate = MagicMock(return_value=60.0)
        mock_logic.getCurrentFrame = MagicMock(return_value=1)
        mock_logic.getTimeSinceStart = MagicMock(return_value=0.016)

        mock_bge = MagicMock()
        mock_bge.logic = mock_logic
        mock_bge.render = None

        from game_engine.context_builder import build_context

        with patch("game_engine.context_builder.bge", mock_bge):
            ctx = build_context()

            # Verify joystick data was extracted
            assert ctx["joystick"] is not None
            assert ctx["joystick"]["count"] > 0
            assert "0" in ctx["joystick"]["buttonsPressed"]
            assert 0 in ctx["joystick"]["buttonsPressed"]["0"]
            assert 1 in ctx["joystick"]["buttonsPressed"]["0"]


class TestRuntimeIntegration:
    """Integration tests for runtime modules."""

    def test_nodejs_runtime_initialization(self):
        """NodeJS runtime should initialize properly."""
        from runtime.nodejs import NodeJSRuntime

        runtime = NodeJSRuntime(use_worker=False)
        assert runtime is not None
        assert hasattr(runtime, "execute")
        assert hasattr(runtime, "execute_with_context")
        assert hasattr(runtime, "execute_interactive")

    def test_nodejs_runtime_with_context(self):
        """NodeJS runtime should accept context parameter."""
        from runtime.nodejs import NodeJSRuntime
        from game_engine.context_builder import build_context

        runtime = NodeJSRuntime(use_worker=False)

        # Build a context without bge (to ensure JSON serializability)
        with patch("game_engine.context_builder.bge", None):
            ctx = build_context()

        # Should have all required fields
        assert ctx is not None
        assert isinstance(ctx, dict)

        # Context should be JSON serializable (for passing to JS)
        import json

        try:
            json_str = json.dumps(ctx)
            assert isinstance(json_str, str)
        except TypeError:
            pytest.fail("Context not JSON serializable")


class TestCommandHandling:
    """Integration tests for command handling."""

    def test_script_handler_command_flow(self):
        """Commands should flow through the handler properly."""
        from game_engine.script_handler import _extract_commands

        # Test command extraction
        output_with_commands = """
        Some debug output
        ___BGE_CMDS___[{"op": "set_position", "oid": "Cube", "vec": [1, 2, 3]}]
        """

        commands = _extract_commands(output_with_commands)
        assert len(commands) == 1
        assert commands[0]["op"] == "set_position"
        assert commands[0]["oid"] == "Cube"


class TestModuleImports:
    """Integration tests for module imports."""

    def test_all_utils_modules_importable(self):
        """All utils modules should be importable."""
        import utils
        from utils import get_sdk_root, get_platform, debug, info

        assert callable(get_sdk_root)
        assert callable(get_platform)
        assert callable(debug)
        assert callable(info)

    def test_game_engine_modules_importable(self):
        """Game engine modules should be importable."""
        from game_engine import script_handler, context_builder

        assert hasattr(script_handler, "_extract_commands")
        assert hasattr(context_builder, "build_context")

    def test_runtime_modules_importable(self):
        """Runtime modules should be importable."""
        from runtime.nodejs import NodeJSRuntime

        assert NodeJSRuntime is not None


class TestErrorHandling:
    """Integration tests for error handling."""

    def test_context_builder_with_missing_bge(self):
        """Context builder should handle missing bge gracefully."""
        from game_engine.context_builder import build_context

        with patch("game_engine.context_builder.bge", None):
            ctx = build_context()
            # Should return a valid context even without bge
            assert isinstance(ctx, dict)
            assert ctx["object_name"] == ""

    def test_paths_with_invalid_sdk_path(self):
        """Path functions should handle invalid paths."""
        from utils.paths import resolve_sdk_path

        result = resolve_sdk_path("/nonexistent/path")
        # Should return something (might be None or a path)
        assert result is None or isinstance(result, (str, type(None)))

    def test_logging_with_exceptions(self):
        """Logging should not crash on exceptions."""
        from utils import logging as log_utils

        # Should not raise even with problematic args
        try:
            log_utils.debug("Test %s %s", "arg1")  # Missing arg
        except TypeError:
            # This is OK - logging will handle it
            pass

        # Should be callable normally
        log_utils.debug("Test message")


class TestPerformance:
    """Performance-related integration tests."""

    def test_context_builder_performance(self):
        """Context builder should be reasonably fast."""
        import time
        from game_engine.context_builder import build_context

        start = time.perf_counter()
        for _ in range(100):
            build_context()
        elapsed = time.perf_counter() - start

        # Should complete 100 iterations in < 1 second
        # (This is a sanity check, not a strict performance requirement)
        assert (
            elapsed < 1.0
        ), f"Context building too slow: {elapsed}s for 100 iterations"

    def test_path_resolution_performance(self):
        """Path resolution should be reasonably fast."""
        import time
        from utils.paths import get_sdk_root, get_platform

        start = time.perf_counter()
        for _ in range(1000):
            get_platform()
            get_sdk_root()
        elapsed = time.perf_counter() - start

        # Should complete 2000 calls in < 1 second
        assert elapsed < 1.0, f"Path resolution too slow: {elapsed}s for 2000 calls"
