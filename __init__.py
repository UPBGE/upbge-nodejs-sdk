# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

# UPBGE Node.js SDK
# https://github.com/UPBGE/upbge-nodejs-sdk

bl_info = {
    "name": "UPBGE Node.js SDK",
    "category": "Game Engine",
    "location": "Properties -> Render -> UPBGE Player",
    "description": "Node.js SDK for UPBGE Game Engine",
    "author": "UPBGE Contributors",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "doc_url": "https://github.com/UPBGE/upbge-nodejs-sdk/wiki",
    "tracker_url": "https://github.com/UPBGE/upbge-nodejs-sdk/issues"
}

from enum import IntEnum
import os
from pathlib import Path
import platform
import sys
import typing
from typing import Callable, Optional

import bpy
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import Operator, AddonPreferences


class SDKSource(IntEnum):
    PREFS = 0
    LOCAL = 1
    ENV_VAR = 2


# Keep the value of these globals after addon reload
if "is_running" not in locals():
    is_running = False
    last_sdk_path = ""
    last_scripts_path = ""
    sdk_source = SDKSource.PREFS

update_error_msg = ''


def get_os():
    s = platform.system()
    if s == 'Windows':
        return 'win'
    elif s == 'Darwin':
        return 'mac'
    else:
        return 'linux'


def detect_sdk_path():
    """Auto-detect the SDK path after SDK installation."""
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons["upbge_nodejs_sdk"].preferences
    if addon_prefs.sdk_path != "":
        return

    # When installed via ZIP, the add-on directory IS the SDK directory
    addon_path = os.path.dirname(os.path.abspath(__file__))
    
    # Check if this add-on directory has the SDK structure (python/, runtime/, lib/)
    has_sdk_structure = (
        os.path.exists(os.path.join(addon_path, "python")) and
        os.path.exists(os.path.join(addon_path, "runtime")) and
        os.path.exists(os.path.join(addon_path, "lib"))
    )
    
    if has_sdk_structure:
        # This is the SDK itself (installed via ZIP)
        addon_prefs.sdk_path = addon_path
        print(f"UPBGE JavaScript SDK: Auto-detected SDK path: {addon_path}")
        return
    
    # Try to detect from addon location (for development)
    possible_paths = [
        os.path.join(addon_path, "..", "bge_js_sdk"),
        os.path.join(addon_path, "bge_js_sdk"),
        os.path.join(addon_path, "..", "upbge-javascript"),  # Development path
        os.path.join(addon_path, "..", "upbge-nodejs-sdk"),  # Development path
    ]
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path) and os.path.exists(os.path.join(abs_path, "python")):
            addon_prefs.sdk_path = abs_path
            print(f"UPBGE JavaScript SDK: Auto-detected SDK path: {abs_path}")
            return


def get_fp():
    if bpy.data.filepath == '':
        return ''
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    return os.path.sep.join(s)


def same_path(path1: str, path2: str) -> bool:
    """Compare whether two paths point to the same location."""
    if os.path.exists(path1) and os.path.exists(path2):
        return os.path.samefile(path1, path2)

    p1 = os.path.realpath(os.path.normpath(os.path.normcase(path1)))
    p2 = os.path.realpath(os.path.normpath(os.path.normcase(path2)))
    return p1 == p2


def get_sdk_path(context: bpy.context) -> str:
    """Returns the absolute path of the currently set SDK.
    
    The path is read from the following sources in that priority:
        1. Environment variable 'BGE_JAVASCRIPT_SDK' (must be an absolute path)
        2. Local SDK in ./bge_js_sdk relative to the current file
        3. The SDK path specified in the add-on preferences
        4. Auto-detect: if add-on directory has SDK structure, use it
    """
    global sdk_source

    sdk_envvar = os.environ.get('BGE_JAVASCRIPT_SDK')
    if sdk_envvar is not None and os.path.isabs(sdk_envvar) and os.path.isdir(sdk_envvar) and os.path.exists(sdk_envvar):
        sdk_source = SDKSource.ENV_VAR
        return sdk_envvar

    fp = get_fp()
    if fp != '':  # blend file is saved
        local_sdk = os.path.join(fp, 'bge_js_sdk')
        if os.path.exists(local_sdk):
            sdk_source = SDKSource.LOCAL
            return local_sdk

    sdk_source = SDKSource.PREFS
    preferences = context.preferences
    addon_prefs = preferences.addons["upbge_nodejs_sdk"].preferences
    
    # If SDK path is set in preferences, use it
    if addon_prefs.sdk_path:
        return addon_prefs.sdk_path
    
    # Auto-detect: check if add-on directory itself is the SDK (when installed via ZIP)
    addon_path = os.path.dirname(os.path.abspath(__file__))
    has_sdk_structure = (
        os.path.exists(os.path.join(addon_path, "python")) and
        os.path.exists(os.path.join(addon_path, "runtime")) and
        os.path.exists(os.path.join(addon_path, "lib"))
    )
    
    if has_sdk_structure:
        # Auto-set the SDK path to the add-on directory
        addon_prefs.sdk_path = addon_path
        print(f"UPBGE JavaScript SDK: Auto-detected SDK path (add-on directory): {addon_path}")
        return addon_path
    
    return ""


def start_sdk(sdk_path: str):
    """Start the SDK by loading Python modules."""
    global is_running
    global last_scripts_path
    global last_sdk_path

    if sdk_path == "":
        return

    # Check if SDK path exists
    if not os.path.exists(sdk_path):
        print(f"UPBGE JavaScript SDK load error: SDK path does not exist: {sdk_path}")
        return

    python_path = os.path.join(sdk_path, "python")
    if not os.path.exists(python_path):
        # If python folder doesn't exist, use the addon's python folder
        # This allows the SDK to work even if installed as addon
        addon_path = os.path.dirname(os.path.abspath(__file__))
        python_path = os.path.join(addon_path, "python")
        if not os.path.exists(python_path):
            print("UPBGE JavaScript SDK load error: 'python' folder not found.")
            print(f"  SDK path: {sdk_path}")
            print(f"  Addon path: {addon_path}")
            print("  Please make sure the SDK is properly installed or configure SDK path in preferences.")
            return

    if python_path not in sys.path:
        sys.path.append(python_path)
    last_scripts_path = python_path

    # Import and register SDK modules
    try:
        # Import start module from SDK path
        import start
        if last_sdk_path != "":
            import importlib
            start = importlib.reload(start)
        
        use_local_sdk = (sdk_source == SDKSource.LOCAL)
        start.register(local_sdk=use_local_sdk)
        
        last_sdk_path = sdk_path
        is_running = True
        
        print(f'Running UPBGE JavaScript SDK from {sdk_path}')
    except ImportError as e:
        print(f"Failed to import SDK modules: {e}")
        print("Make sure the SDK is properly installed.")
        import traceback
        traceback.print_exc()


def stop_sdk():
    """Stop the SDK by unloading Python modules."""
    global is_running

    if not is_running:
        return

    try:
        import start
        start.unregister()
    except ImportError:
        pass

    if last_scripts_path and last_scripts_path in sys.path:
        sys.path.remove(last_scripts_path)
    is_running = False


def restart_sdk(context):
    """Restart the SDK when path changes."""
    old_sdk_source = sdk_source
    sdk_path = get_sdk_path(context)

    if sdk_path == "":
        if not is_running:
            print("UPBGE JavaScript SDK: SDK path not configured")
            print("  Please configure SDK path in add-on preferences, or")
            print("  ensure the SDK is properly installed (python/, runtime/, lib/ folders present)")
        stop_sdk()
        return

    # Only restart SDK when the path changed or it isn't running
    if not same_path(last_sdk_path, sdk_path) or sdk_source != old_sdk_source or not is_running:
        stop_sdk()
        assert not is_running
        start_sdk(sdk_path)


@persistent
def on_load_post(context):
    """Handler called after loading a blend file."""
    restart_sdk(bpy.context)


def on_register_post():
    """Handler called after addon registration."""
    try:
        detect_sdk_path()
        restart_sdk(bpy.context)
    except Exception as e:
        print(f"UPBGE JavaScript SDK: Error in on_register_post: {e}")
        import traceback
        traceback.print_exc()


def register():
    """Register the add-on."""
    try:
        from .python import preferences, operators
        
        bpy.utils.register_class(preferences.SDKAddonPreferences)
        bpy.utils.register_class(operators.SDK_INSTALL_OT_operator)
        bpy.utils.register_class(operators.SDK_UPDATE_OT_operator)
        bpy.utils.register_class(operators.SDK_RESTORE_OT_operator)
        bpy.utils.register_class(operators.SDK_OPEN_IN_EDITOR_OT_operator)
        bpy.app.handlers.load_post.append(on_load_post)

        # Hack to avoid _RestrictContext
        # Use a longer delay to ensure preferences are loaded
        bpy.app.timers.register(on_register_post, first_interval=0.1)
        
        print("UPBGE Node.js SDK: Add-on registered")
    except ImportError as e:
        print(f"UPBGE Node.js SDK: Failed to import SDK modules: {e}")
        import traceback
        traceback.print_exc()
        print("Make sure the SDK is properly installed.")


def unregister():
    """Unregister the add-on."""
    stop_sdk()
    
    try:
        from .python import preferences, operators
        
        bpy.utils.unregister_class(preferences.SDKAddonPreferences)
        bpy.utils.unregister_class(operators.SDK_INSTALL_OT_operator)
        bpy.utils.unregister_class(operators.SDK_UPDATE_OT_operator)
        bpy.utils.unregister_class(operators.SDK_RESTORE_OT_operator)
        bpy.utils.unregister_class(operators.SDK_OPEN_IN_EDITOR_OT_operator)
        bpy.app.handlers.load_post.remove(on_load_post)
    except ImportError:
        pass


if __name__ == "__main__":
    register()
