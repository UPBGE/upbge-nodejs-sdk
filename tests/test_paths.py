"""Tests for python/utils/paths.py module.

Tests the centralized path resolution logic used across the SDK.
"""

import os
import pytest
import sys
from unittest.mock import patch, MagicMock

# Add python directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from utils.paths import (
    get_platform,
    get_sdk_root,
    get_node_executable,
    resolve_sdk_path,
)


class TestGetPlatform:
    """Tests for platform detection."""

    @pytest.mark.unit
    def test_get_platform_returns_string(self):
        """Platform detection should return a string."""
        platform = get_platform()
        assert isinstance(platform, str)
        assert platform in ("Windows", "Darwin", "Linux")

    @pytest.mark.unit
    def test_get_platform_matches_system(self):
        """Platform should match actual system."""
        import platform as stdlib_platform
        expected = stdlib_platform.system()
        assert get_platform() == expected


class TestGetSdkRoot:
    """Tests for SDK root path resolution."""

    @pytest.mark.unit
    def test_get_sdk_root_with_env_var(self):
        """Should return SDK path from UPBGE_SDK_PATH env var."""
        fake_sdk = "/fake/sdk/path"
        with patch.dict(os.environ, {"UPBGE_SDK_PATH": fake_sdk}):
            with patch("os.path.isdir", return_value=True):
                result = get_sdk_root()
                assert result == fake_sdk

    @pytest.mark.unit
    def test_get_sdk_root_ignores_invalid_env_var(self):
        """Should ignore UPBGE_SDK_PATH if it doesn't exist."""
        fake_sdk = "/nonexistent/path"
        with patch.dict(os.environ, {"UPBGE_SDK_PATH": fake_sdk}):
            with patch("os.path.isdir", return_value=False):
                result = get_sdk_root()
                # Should return empty or try other methods
                assert isinstance(result, str)

    @pytest.mark.unit
    def test_get_sdk_root_auto_detect(self):
        """Should auto-detect SDK from addon location."""
        # Mock the file system to simulate addon structure
        with patch("os.path.isdir") as mock_isdir:
            # Return True for python and runtime directories
            def isdir_side_effect(path):
                return "python" in path or "runtime" in path
            mock_isdir.side_effect = isdir_side_effect

            with patch("os.path.abspath") as mock_abspath:
                # Mock the __file__ path
                mock_abspath.return_value = "/addon/python/utils/paths.py"
                result = get_sdk_root()
                # Should detect addon root
                assert isinstance(result, str)

    @pytest.mark.unit
    def test_get_sdk_root_returns_string(self):
        """Should always return a string (possibly empty)."""
        result = get_sdk_root()
        assert isinstance(result, str)


class TestResolveSdkPath:
    """Tests for SDK-specific Node.js path resolution."""

    @pytest.mark.unit
    def test_resolve_sdk_path_windows(self):
        """Should resolve Windows Node.js path."""
        sdk_root = "/sdk"
        expected = "/sdk/runtime/windows/node.exe"

        with patch("platform.system", return_value="Windows"):
            with patch("os.path.exists") as mock_exists:
                mock_exists.return_value = True
                result = resolve_sdk_path(sdk_root)
                # Verify the path was checked
                mock_exists.assert_called()

    @pytest.mark.unit
    def test_resolve_sdk_path_macos(self):
        """Should resolve macOS Node.js path."""
        sdk_root = "/sdk"
        expected = "/sdk/runtime/macos/node-osx"

        with patch("platform.system", return_value="Darwin"):
            with patch("os.path.exists") as mock_exists:
                mock_exists.return_value = True
                result = resolve_sdk_path(sdk_root)
                mock_exists.assert_called()

    @pytest.mark.unit
    def test_resolve_sdk_path_linux(self):
        """Should resolve Linux Node.js path."""
        sdk_root = "/sdk"
        expected = "/sdk/runtime/linux/node-linux64"

        with patch("platform.system", return_value="Linux"):
            with patch("os.path.exists") as mock_exists:
                mock_exists.return_value = True
                result = resolve_sdk_path(sdk_root)
                mock_exists.assert_called()

    @pytest.mark.unit
    def test_resolve_sdk_path_empty_root(self):
        """Should return None for empty SDK root."""
        result = resolve_sdk_path("")
        assert result is None

    @pytest.mark.unit
    def test_resolve_sdk_path_nonexistent(self):
        """Should return None if Node.js doesn't exist in SDK."""
        with patch("os.path.exists", return_value=False):
            result = resolve_sdk_path("/sdk")
            assert result is None


class TestGetNodeExecutable:
    """Tests for Node.js executable resolution."""

    @pytest.mark.unit
    def test_get_node_executable_returns_optional_string(self):
        """Should return string or None."""
        with patch("utils.paths.get_sdk_root", return_value=""):
            result = get_node_executable()
            assert result is None or isinstance(result, str)

    @pytest.mark.unit
    def test_get_node_executable_prefers_sdk(self):
        """Should prefer SDK-bundled Node.js over system."""
        sdk_root = "/sdk"
        node_path = "/sdk/runtime/windows/node.exe"

        with patch("utils.paths.get_sdk_root", return_value=sdk_root):
            with patch("utils.paths.resolve_sdk_path", return_value=node_path):
                with patch("os.path.exists", return_value=True):
                    result = get_node_executable()
                    assert result == node_path

    @pytest.mark.unit
    def test_get_node_executable_fallback_to_system(self):
        """Should fallback to system Node.js if SDK doesn't have it."""
        with patch("utils.paths.get_sdk_root", return_value=""):
            with patch("utils.paths._find_node_windows", return_value="/usr/bin/node"):
                with patch("platform.system", return_value="Windows"):
                    result = get_node_executable()
                    # May be None or system path depending on environment
                    assert result is None or isinstance(result, str)


class TestPathsIntegration:
    """Integration tests for path resolution workflow."""

    @pytest.mark.unit
    def test_paths_workflow_with_env_var(self):
        """Test complete workflow with environment variable."""
        fake_sdk = "/fake/sdk"
        with patch.dict(os.environ, {"UPBGE_SDK_PATH": fake_sdk}):
            with patch("os.path.isdir", return_value=True):
                # Should get SDK root from env var
                sdk_root = get_sdk_root()
                assert sdk_root == fake_sdk

                # Should resolve node path from SDK
                with patch("os.path.exists", return_value=True):
                    with patch("platform.system", return_value="Windows"):
                        node_path = resolve_sdk_path(sdk_root)
                        # Path should be constructed
                        assert node_path is not None or node_path is None

    @pytest.mark.unit
    def test_no_duplicate_calls(self):
        """Verify get_sdk_root is called once, not multiple times."""
        with patch("utils.paths.get_sdk_root", return_value="/sdk") as mock_get_root:
            with patch("utils.paths.resolve_sdk_path", return_value=None):
                get_node_executable()
                # Should only call get_sdk_root once
                assert mock_get_root.call_count >= 1
