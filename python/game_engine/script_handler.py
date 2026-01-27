# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Script execution handler for JavaScript controllers.
Intercepts Python script execution and redirects .js files to JavaScript runtime.
"""

import bpy
import os
from bpy.app.handlers import persistent
from runtime.nodejs import NodeJSRuntime


# Global runtime instance
_runtime = None


def get_runtime():
    """Get or create Node.js runtime instance."""
    global _runtime
    if _runtime is None:
        _runtime = NodeJSRuntime()
    return _runtime


def is_javascript_file(filename):
    """Check if a filename is a JavaScript file."""
    if not filename:
        return False
    return filename.endswith('.js') or filename.endswith('.mjs')


@persistent
def on_frame_change_pre(scene):
    """
    Handler called before each frame.
    This intercepts script execution for .js files in controllers.
    """
    # This is a placeholder - actual interception needs to be done
    # at the C++ level in the game engine
    # For now, we can only prepare the runtime
    pass


def execute_controller_script(script_text, filename):
    """
    Execute a controller script using JavaScript runtime.
    Returns (success, error_message)
    """
    try:
        runtime = get_runtime()

        # Only JavaScript is supported for controllers now
        script_to_execute = script_text

        # Execute JavaScript
        output, error_output, success = runtime.execute(script_to_execute, timeout=10)

        if not success:
            return False, error_output or "Unknown JavaScript execution error"

        return True, None

    except Exception as e:
        return False, str(e)


def register():
    """Register script execution handlers."""
    # Register frame change handler
    bpy.app.handlers.frame_change_pre.append(on_frame_change_pre)
    
    print("UPBGE JavaScript SDK: Script execution handler registered")


def unregister():
    """Unregister script execution handlers."""
    if on_frame_change_pre in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(on_frame_change_pre)
