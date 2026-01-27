# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Game engine integration modules."""

__all__ = (
    "controller",
    "script_handler",
    "ui",
    "python_wrapper",
)


def register():
    """Register game engine modules."""
    import sys
    import os
    import importlib.util
    
    # Get the directory where this file is located
    game_engine_dir = os.path.dirname(os.path.abspath(__file__))
    python_dir = os.path.dirname(game_engine_dir)  # Parent directory (python/)
    
    # Ensure python_dir is in sys.path for relative imports
    if python_dir not in sys.path:
        sys.path.insert(0, python_dir)
    
    # Load modules using importlib
    for module_name in ["controller", "script_handler", "ui"]:
        module_path = os.path.join(game_engine_dir, f"{module_name}.py")
        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location(f"game_engine.{module_name}", module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"game_engine.{module_name}"] = module
            spec.loader.exec_module(module)
    
    controller = sys.modules["game_engine.controller"]
    script_handler = sys.modules["game_engine.script_handler"]
    ui = sys.modules["game_engine.ui"]
    
    controller.register()
    script_handler.register()
    ui.register()


def unregister():
    """Unregister game engine modules."""
    import sys
    
    ui = sys.modules.get("ui")
    script_handler = sys.modules.get("script_handler")
    controller = sys.modules.get("controller")
    
    ui.unregister()
    script_handler.unregister()
    controller.unregister()
