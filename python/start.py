# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""SDK startup module - registers all SDK components."""

import sys
import os
import bpy


def register(local_sdk=False):
    """Register all SDK components."""
    import sys
    import os
    
    # Get the directory where this file is located (python/)
    # This allows imports to work whether start.py is imported as a module or directly
    start_dir = os.path.dirname(os.path.abspath(__file__))
    if start_dir not in sys.path:
        sys.path.insert(0, start_dir)
    
    # Now we can use regular imports since python/ is in sys.path
    try:
        # Register console modules FIRST (they need to be in sys.modules early)
        import console
        console.register()
        print("UPBGE JavaScript SDK: Console modules registered")
    except Exception as e:
        print(f"UPBGE JavaScript SDK: Failed to register console modules: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        # Register game engine modules
        import game_engine
        game_engine.register()
        print("UPBGE JavaScript SDK: Game engine modules registered")
    except Exception as e:
        print(f"UPBGE JavaScript SDK: Failed to register game engine modules: {e}")
        import traceback
        traceback.print_exc()
    
    # Verify console modules are registered
    console_modules = ['_console_javascript', 'console_javascript']
    registered = [mod for mod in console_modules if mod in sys.modules]
    if registered:
        print(f"UPBGE JavaScript SDK: Console modules in sys.modules: {registered}")
    else:
        print("UPBGE JavaScript SDK: WARNING - Console modules not found in sys.modules")
    
    print("UPBGE JavaScript SDK registered successfully")


def unregister():
    """Unregister all SDK components."""
    # Unregister in reverse order
    try:
        if "game_engine" in sys.modules:
            game_engine = sys.modules["game_engine"]
            game_engine.unregister()
    except Exception as e:
        print(f"Failed to unregister game engine modules: {e}")
    
    try:
        if "console" in sys.modules:
            console = sys.modules["console"]
            console.unregister()
    except Exception as e:
        print(f"Failed to unregister console modules: {e}")
    
    print("UPBGE JavaScript SDK unregistered")
