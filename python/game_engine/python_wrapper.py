# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Python wrapper script that intercepts .js file execution.
This script should be assigned to Python controllers that have .js files.
"""

import bpy

# This file will be dynamically generated and injected into text blocks
# when a .js file is assigned to a Python controller

WRAPPER_CODE_TEMPLATE = """# Auto-generated wrapper for JavaScript execution
# This script intercepts .js files and executes them via Node.js

import bpy
import sys
import os

# Script name to execute (will be replaced)
SCRIPT_NAME = "{script_name}"

# Try to import the SDK's script handler
try:
    # Try multiple import paths
    try:
        from upbge_nodejs_sdk.python.game_engine.script_handler import (
            execute_controller_script,
            is_javascript_file,
        )
    except ImportError:
        # Fallback: try relative import or add to sys.path
        import sys
        import os
        # Find addon path
        addon_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        if addon_path not in sys.path:
            sys.path.insert(0, addon_path)
        from python.game_engine.script_handler import (
            execute_controller_script,
            is_javascript_file,
        )
    
    # Get the script from bpy.data.texts
    if SCRIPT_NAME in bpy.data.texts:
        script_text = bpy.data.texts[SCRIPT_NAME].as_string()
        script_name = SCRIPT_NAME
        
        # Check if it's a JavaScript file
        if is_javascript_file(script_name):
            # Execute via JavaScript runtime
            success, error = execute_controller_script(script_text, script_name)
            if not success:
                print(f"JavaScript execution error: {{error}}")
        else:
            # Regular Python script - execute normally
            exec(compile(script_text, script_name, 'exec'), globals())
    else:
        print(f"Script '{{SCRIPT_NAME}}' not found in bpy.data.texts")
        
except ImportError as e:
    print(f"UPBGE JavaScript SDK not found: {{e}}")
    print("Please install and enable the UPBGE Node.js SDK add-on")
    # Fallback: try to execute as Python
    if SCRIPT_NAME in bpy.data.texts:
        try:
            script_text = bpy.data.texts[SCRIPT_NAME].as_string()
            exec(compile(script_text, SCRIPT_NAME, 'exec'), globals())
        except Exception as py_error:
            print(f"Python execution error: {{py_error}}")
except Exception as e:
    print(f"Error in script wrapper: {{e}}")
    import traceback
    traceback.print_exc()
"""


def create_wrapper_script(script_name):
    """Create a text block with the wrapper script for a specific script."""
    # Sanitize script name for wrapper name
    safe_name = script_name.replace('.', '_').replace('-', '_')
    wrapper_name = f"__js_wrapper_{safe_name}__"
    
    # Check if wrapper already exists
    if wrapper_name in bpy.data.texts:
        return bpy.data.texts[wrapper_name]
    
    # Generate wrapper code with script name
    wrapper_code = WRAPPER_CODE_TEMPLATE.format(script_name=script_name)
    
    # Create new text block
    wrapper = bpy.data.texts.new(wrapper_name)
    wrapper.from_string(wrapper_code)
    wrapper.filepath = ""  # Internal script
    
    return wrapper


def assign_wrapper_to_controller(controller):
    """Assign the wrapper script to a controller that has a .js file."""
    if not controller or controller.type != 'PYTHON':
        return False
    
    if not controller.text:
        return False
    
    script_name = controller.text.name
    if not (script_name.endswith(('.js', '.mjs'))):
        return False
    
    # Create wrapper with reference to the original script
    wrapper = create_wrapper_script(script_name)
    
    # Store reference to original script (we'll keep it accessible)
    # The wrapper will look up the script by name from bpy.data.texts
    
    # Assign wrapper to controller
    controller.text = wrapper
    
    return True
