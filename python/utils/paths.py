"""Path resolution utilities for UPBGE Node.js SDK.

Centralizes logic for:
- Detecting SDK root directory
- Resolving Node.js executable path
- Platform detection (Windows, macOS, Linux)
- Environment variable handling
"""

import os
import platform
import subprocess
from typing import Optional


def get_platform() -> str:
    """Detect current platform.

    Returns:
        "Windows", "Darwin" (macOS), or "Linux"
    """
    return platform.system()


def get_sdk_root(context=None) -> str:
    """Get SDK root path with fallback chain.

    Tries to resolve SDK path in this order:
    1. UPBGE_SDK_PATH environment variable
    2. Blender addon preferences (if bpy available)
    3. Auto-detect from addon location
    4. Return empty string if not found

    Args:
        context: Blender context (optional, for addon preferences)

    Returns:
        SDK root path or empty string if not found
    """

    # 1. Check environment variable
    sdk_path = os.getenv("UPBGE_SDK_PATH")
    if sdk_path and os.path.isdir(sdk_path):
        return sdk_path

    # 2. Try to get from Blender addon preferences
    if context is not None:
        try:
            import bpy
            preferences = bpy.context.preferences
            addon_prefs = preferences.addons.get("upbge_nodejs_sdk")
            if addon_prefs and hasattr(addon_prefs, "preferences"):
                sdk_path = getattr(addon_prefs.preferences, "sdk_path", None)
                if sdk_path and os.path.isdir(sdk_path):
                    return sdk_path
        except Exception:
            pass

    # 3. Try to auto-detect from addon location
    try:
        # Get path: python/utils/paths.py → python/utils → python → addon root
        addon_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Verify this is an SDK directory by checking for expected subdirectories
        has_sdk_structure = (
            os.path.isdir(os.path.join(addon_path, "python")) and
            os.path.isdir(os.path.join(addon_path, "runtime"))
        )

        if has_sdk_structure:
            return addon_path
    except Exception:
        pass

    # 4. Return empty if nothing found
    return ""


def get_node_executable() -> Optional[str]:
    """Get path to Node.js executable.

    Tries to locate Node.js in this order:
    1. In SDK runtime/{platform}/node.exe|node-osx|node-linux64
    2. System PATH (Windows: Program Files, macOS/Linux: which node)

    Returns:
        Path to Node.js executable or None if not found
    """
    sdk_root = get_sdk_root()

    if sdk_root:
        # Try SDK bundled Node.js
        node_path = resolve_sdk_path(sdk_root)
        if node_path and os.path.exists(node_path):
            return node_path

    # Fallback to system Node.js
    os_type = get_platform()

    if os_type == "Windows":
        return _find_node_windows()
    elif os_type == "Darwin":
        return _find_node_unix()
    else:  # Linux
        return _find_node_unix()


def resolve_sdk_path(sdk_root: str) -> Optional[str]:
    """Resolve Node.js path within SDK for current platform.

    Args:
        sdk_root: Root directory of SDK

    Returns:
        Path to Node.js executable or None if not found
    """
    if not sdk_root:
        return None

    os_type = get_platform()

    if os_type == "Windows":
        node_path = os.path.join(sdk_root, "runtime", "windows", "node.exe")
    elif os_type == "Darwin":
        node_path = os.path.join(sdk_root, "runtime", "macos", "node-osx")
    else:  # Linux
        node_path = os.path.join(sdk_root, "runtime", "linux", "node-linux64")

    if os.path.exists(node_path):
        return node_path

    return None


def _find_node_windows() -> Optional[str]:
    """Find Node.js on Windows system.

    Checks common installation paths.

    Returns:
        Path to node.exe or None if not found
    """
    possible_paths = [
        os.path.join(os.environ.get("ProgramFiles", ""), "nodejs", "node.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "nodejs", "node.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "nodejs", "node.exe"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def _find_node_unix() -> Optional[str]:
    """Find Node.js on Unix-like systems (macOS, Linux).

    Uses 'which' command to locate Node.js in PATH.

    Returns:
        Path to node executable or None if not found
    """
    try:
        result = subprocess.run(
            ["which", "node"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return None
