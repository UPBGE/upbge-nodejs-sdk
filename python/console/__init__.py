# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Console modules for JavaScript."""

__all__ = (
    "javascript"
)

import sys


def register():
    """Register console modules."""
    import sys
    import os
    import importlib.util
    
    # Get the directory where this file is located
    console_dir = os.path.dirname(os.path.abspath(__file__))
    python_dir = os.path.dirname(console_dir)  # Parent directory (python/)
    
    # Ensure python_dir is in sys.path for relative imports
    if python_dir not in sys.path:
        sys.path.insert(0, python_dir)
    
    # Load javascript module using importlib
    js_path = os.path.join(console_dir, "javascript.py")
    spec = importlib.util.spec_from_file_location("console.javascript", js_path)
    javascript = importlib.util.module_from_spec(spec)
    sys.modules["console.javascript"] = javascript
    spec.loader.exec_module(javascript)
    
    # Register console modules in sys.modules so they appear in the console language menu
    # The menu looks for modules starting with "console_" that have an "execute" function
    sys.modules['console_javascript'] = javascript
    
    # Also register with _console_ prefix for compatibility
    sys.modules['_console_javascript'] = javascript
    
    print(f"UPBGE JavaScript SDK: Registered console module: {list(sys.modules.keys()) if 'console_javascript' in sys.modules else 'FAILED'}")


def unregister():
    """Unregister console modules."""
    # Remove from sys.modules
    modules_to_remove = [
        '_console_javascript',
        'console_javascript',
    ]
    for mod_name in modules_to_remove:
        if mod_name in sys.modules:
            del sys.modules[mod_name]
