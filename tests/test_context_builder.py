# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Tests for context_builder module.
Tests extraction and building of BGE context for JS runtime.
"""

import os
import sys
from pathlib import Path

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from unittest.mock import MagicMock, patch

import pytest
# Import context builder
from game_engine.context_builder import (_get_engine_info, _get_object_info,
                                         build_context)


class TestGetEngineInfo:
    """Tests for _get_engine_info() helper."""

    def test_get_engine_info_returns_dict(self):
        """Should return dict with engine info."""
        info = _get_engine_info()
        assert isinstance(info, dict)
        assert "frame_rate" in info
        assert "current_frame" in info
        assert "time_since_start" in info

    def test_get_engine_info_no_bge(self):
        """Should return defaults when bge not available."""
        with patch("game_engine.context_builder.bge", None):
            info = _get_engine_info()
            assert info["frame_rate"] == 0.0
            assert info["current_frame"] == 0
            assert info["time_since_start"] == 0.0

    def test_get_engine_info_with_bge(self):
        """Should extract engine info from bge when available."""
        mock_logic = MagicMock()
        mock_logic.getAverageFrameRate = MagicMock(return_value=60.0)
        mock_logic.getCurrentFrame = MagicMock(return_value=100)
        mock_logic.getTimeSinceStart = MagicMock(return_value=10.5)

        mock_bge = MagicMock()
        mock_bge.logic = mock_logic

        with patch("game_engine.context_builder.bge", mock_bge):
            info = _get_engine_info()
            assert info["frame_rate"] == 60.0
            assert info["current_frame"] == 100
            assert info["time_since_start"] == 10.5


class TestGetObjectInfo:
    """Tests for _get_object_info() helper."""

    def test_get_object_info_returns_dict(self):
        """Should return dict with object info."""
        info = _get_object_info(None)
        assert isinstance(info, dict)
        assert "position" in info
        assert "rotation" in info
        assert "scale" in info

    def test_get_object_info_none_owner(self):
        """Should return None values for None owner."""
        info = _get_object_info(None)
        assert info["position"] is None
        assert info["rotation"] is None
        assert info["scale"] is None

    def test_get_object_info_with_position(self):
        """Should extract position from owner."""
        mock_owner = MagicMock()
        mock_owner.worldPosition = [1.0, 2.0, 3.0]

        info = _get_object_info(mock_owner)
        assert info["position"] == [1.0, 2.0, 3.0]

    def test_get_object_info_with_scale(self):
        """Should extract scale from owner."""
        mock_owner = MagicMock()
        mock_owner.worldPosition = None
        mock_owner.worldOrientation = None
        mock_owner.worldScale = [0.5, 1.0, 1.5]

        info = _get_object_info(mock_owner)
        assert info["scale"] == [0.5, 1.0, 1.5]

    def test_get_object_info_with_rotation(self):
        """Should extract rotation from owner."""
        mock_euler = MagicMock()
        mock_euler.__getitem__ = MagicMock(side_effect=lambda i: [0.1, 0.2, 0.3][i])

        mock_orientation = MagicMock()
        mock_orientation.to_euler = MagicMock(return_value=mock_euler)

        mock_owner = MagicMock()
        mock_owner.worldPosition = None
        mock_owner.worldOrientation = mock_orientation
        mock_owner.worldScale = None

        info = _get_object_info(mock_owner)
        assert info["rotation"] == [0.1, 0.2, 0.3]


class TestBuildContext:
    """Tests for build_context() main function."""

    def test_build_context_returns_dict(self):
        """Should return dict with all required keys."""
        ctx = build_context()
        assert isinstance(ctx, dict)
        assert "scene_name" in ctx
        assert "object_name" in ctx
        assert "position" in ctx
        assert "rotation" in ctx
        assert "scale" in ctx
        assert "parent_name" in ctx
        assert "properties" in ctx
        assert "children" in ctx
        assert "object_positions" in ctx
        assert "scenes" in ctx
        assert "windowWidth" in ctx
        assert "windowHeight" in ctx
        assert "active_camera_name" in ctx
        assert "keyboard" in ctx
        assert "mouse" in ctx
        assert "joystick" in ctx
        assert "engine" in ctx
        assert "controller_name" in ctx
        assert "actuators" in ctx
        assert "sensors" in ctx
        assert "rayCastResults" in ctx

    def test_build_context_no_bge(self):
        """Should return empty context when bge not available."""
        with patch("game_engine.context_builder.bge", None):
            ctx = build_context()
            assert ctx["scene_name"] == ""
            assert ctx["object_name"] == ""
            assert ctx["position"] is None
            # Engine should be a dict with defaults or None
            assert ctx["engine"] is None or isinstance(ctx["engine"], dict)

    def test_build_context_keyboard_structure(self):
        """Should have keyboard context structure."""
        ctx = build_context()
        assert "keyboard" in ctx
        kb = ctx["keyboard"]
        assert isinstance(kb, dict)
        assert "pressed" in kb
        assert "justPressed" in kb
        assert "justReleased" in kb
        assert isinstance(kb["pressed"], list)

    def test_build_context_mouse_structure(self):
        """Should have mouse context structure."""
        ctx = build_context()
        assert "mouse" in ctx
        mouse = ctx["mouse"]
        assert isinstance(mouse, dict)
        assert "position" in mouse
        assert "pressed" in mouse
        assert "wheelDelta" in mouse
        assert isinstance(mouse["position"], list)
        assert len(mouse["position"]) == 2

    def test_build_context_joystick_structure(self):
        """Should have joystick context structure."""
        ctx = build_context()
        assert "joystick" in ctx
        joy = ctx["joystick"]
        assert isinstance(joy, dict)
        assert "count" in joy
        assert "buttonsPressed" in joy
        assert "axes" in joy
        assert isinstance(joy["buttonsPressed"], dict)
        assert isinstance(joy["axes"], dict)

    def test_build_context_sensors_structure(self):
        """Should have sensors context structure."""
        ctx = build_context()
        assert "sensors" in ctx
        assert isinstance(ctx["sensors"], dict)

    def test_build_context_with_owner(self):
        """Should extract object info when owner exists."""
        mock_owner = MagicMock()
        mock_owner.name = "TestObject"
        mock_owner.scene = MagicMock()
        mock_owner.scene.name = "TestScene"
        mock_owner.worldPosition = [1.0, 2.0, 3.0]
        mock_owner.worldOrientation = None
        mock_owner.worldScale = [1.0, 1.0, 1.0]
        mock_owner.parent = None
        mock_owner.keys = MagicMock(return_value=[])
        mock_owner.children = []

        mock_controller = MagicMock()
        mock_controller.owner = mock_owner
        mock_controller.name = "TestController"
        mock_controller.actuators = []
        mock_controller.sensors = []

        mock_logic = MagicMock()
        mock_logic.getCurrentController = MagicMock(return_value=mock_controller)
        mock_logic.getSceneList = MagicMock(return_value=[mock_owner.scene])
        mock_logic.getAverageFrameRate = MagicMock(return_value=60.0)
        mock_logic.getCurrentFrame = MagicMock(return_value=1)
        mock_logic.getTimeSinceStart = MagicMock(return_value=0.016)

        mock_bge = MagicMock()
        mock_bge.logic = mock_logic
        mock_bge.render = None

        with patch("game_engine.context_builder.bge", mock_bge):
            ctx = build_context()
            assert ctx["object_name"] == "TestObject"
            assert ctx["scene_name"] == "TestScene"
            assert ctx["position"] == [1.0, 2.0, 3.0]
            assert ctx["controller_name"] == "TestController"

    def test_build_context_with_properties(self):
        """Should extract object properties."""
        mock_owner = MagicMock()
        mock_owner.name = "TestObj"
        mock_owner.scene = MagicMock(name="Scene")
        mock_owner.worldPosition = None
        mock_owner.worldOrientation = None
        mock_owner.worldScale = None
        mock_owner.parent = None
        mock_owner.keys = MagicMock(return_value=["health", "ammo"])
        mock_owner.__getitem__ = MagicMock(
            side_effect=lambda k: 100 if k == "health" else 50
        )
        mock_owner.children = []

        mock_controller = MagicMock()
        mock_controller.owner = mock_owner
        mock_controller.name = "Ctrl"
        mock_controller.actuators = []
        mock_controller.sensors = []

        mock_logic = MagicMock()
        mock_logic.getCurrentController = MagicMock(return_value=mock_controller)
        mock_logic.getSceneList = MagicMock(return_value=[])
        mock_logic.getAverageFrameRate = MagicMock(return_value=60.0)
        mock_logic.getCurrentFrame = MagicMock(return_value=1)
        mock_logic.getTimeSinceStart = MagicMock(return_value=0.0)

        mock_bge = MagicMock()
        mock_bge.logic = mock_logic
        mock_bge.render = None

        with patch("game_engine.context_builder.bge", mock_bge):
            ctx = build_context()
            assert ctx["properties"] is not None
            assert "health" in ctx["properties"]
            assert ctx["properties"]["health"] == 100

    def test_build_context_exception_safety(self):
        """Should not crash on exceptions, return partial context."""
        mock_logic = MagicMock()
        mock_logic.getCurrentController = MagicMock(
            side_effect=Exception("Test exception")
        )

        mock_bge = MagicMock()
        mock_bge.logic = mock_logic

        with patch("game_engine.context_builder.bge", mock_bge):
            ctx = build_context()
            assert isinstance(ctx, dict)
            assert ctx["scene_name"] == ""
            assert ctx["object_name"] == ""


class TestContextBuilderIntegration:
    """Integration tests for context builder."""

    def test_build_context_with_full_mock_scene(self):
        """Should build complete context with full mock scene."""
        # Create mock objects
        mock_camera = MagicMock()
        mock_camera.name = "Camera"

        mock_scene = MagicMock()
        mock_scene.name = "MainScene"
        mock_scene.objects = [mock_camera]
        mock_scene.active_camera = mock_camera

        mock_owner = MagicMock()
        mock_owner.name = "Player"
        mock_owner.scene = mock_scene
        mock_owner.worldPosition = [0.0, 0.0, 0.0]
        mock_owner.worldOrientation = None
        mock_owner.worldScale = [1.0, 1.0, 1.0]
        mock_owner.parent = None
        mock_owner.keys = MagicMock(return_value=[])
        mock_owner.children = []

        mock_controller = MagicMock()
        mock_controller.owner = mock_owner
        mock_controller.name = "PlayerController"
        mock_controller.actuators = []
        mock_controller.sensors = []

        mock_logic = MagicMock()
        mock_logic.getCurrentController = MagicMock(return_value=mock_controller)
        mock_logic.getSceneList = MagicMock(return_value=[mock_scene])
        mock_logic.getAverageFrameRate = MagicMock(return_value=60.0)
        mock_logic.getCurrentFrame = MagicMock(return_value=100)
        mock_logic.getTimeSinceStart = MagicMock(return_value=1.66)

        mock_render = MagicMock()
        mock_render.getWindowWidth = MagicMock(return_value=1920)
        mock_render.getWindowHeight = MagicMock(return_value=1080)

        mock_bge = MagicMock()
        mock_bge.logic = mock_logic
        mock_bge.render = mock_render

        with patch("game_engine.context_builder.bge", mock_bge):
            ctx = build_context()
            assert ctx["object_name"] == "Player"
            assert ctx["scene_name"] == "MainScene"
            assert ctx["position"] == [0.0, 0.0, 0.0]
            assert ctx["active_camera_name"] == "Camera"
            assert ctx["windowWidth"] == 1920
            assert ctx["windowHeight"] == 1080
            assert ctx["engine"]["frame_rate"] == 60.0
            assert ctx["engine"]["current_frame"] == 100
            assert len(ctx["scenes"]) == 1
            assert ctx["scenes"][0]["name"] == "MainScene"

    def test_build_context_json_serializable(self):
        """Context should be JSON serializable."""
        import json

        # Mock bge to None so context has only basic values
        with patch("game_engine.context_builder.bge", None):
            ctx = build_context()
            try:
                json_str = json.dumps(ctx)
                assert isinstance(json_str, str)
            except TypeError as e:
                pytest.fail(f"Context not JSON serializable: {e}")
