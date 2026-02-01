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

try:
    import bge  # type: ignore
except Exception:
    bge = None

# Script name to execute (will be replaced)
SCRIPT_NAME = "{script_name}"


def _build_context():
    \"\"\"Build rich context for the JS runtime bridge.

    Returns a dict that will be serialized to JSON and made available in JS as
    __BGE_CONTEXT__.
    \"\"\"
    ctx = {{
        "scene_name": "",
        "object_name": "",
        "position": None,
        "rotation": None,
        "scale": None,
        "parent_name": None,
        "properties": None,
        "children": None,
        "object_positions": None,
        "scenes": None,
        "keyboard": None,
        "mouse": None,
        "joystick": None,
        "engine": None,
        "controller_name": "",
        "sensors": None,
    }}

    try:
        if bge is not None:
            logic = bge.logic  # type: ignore[attr-defined]
            controller = logic.getCurrentController()
            owner = controller.owner if controller else None

            # Controller metadata
            try:
                if controller is not None:
                    ctx["controller_name"] = controller.name
            except Exception:
                pass

            # Scene / object basic info
            if owner is not None:
                ctx["object_name"] = owner.name
                try:
                    ctx["scene_name"] = owner.scene.name
                except Exception:
                    try:
                        ctx["scene_name"] = owner.scene.name
                    except Exception:
                        ctx["scene_name"] = ""
                try:
                    # worldPosition is a Vector-like, convert to plain list
                    pos = getattr(owner, "worldPosition", None)
                    if pos is not None:
                        ctx["position"] = [float(pos[0]), float(pos[1]), float(pos[2])]
                except Exception:
                    ctx["position"] = None

                # worldOrientation: Euler [x,y,z] in radians (BGE uses radians)
                try:
                    orient = getattr(owner, "worldOrientation", None)
                    if orient is not None:
                        euler = getattr(orient, "to_euler", None)
                        if euler is not None and callable(euler):
                            e = euler()
                            ctx["rotation"] = [float(e[0]), float(e[1]), float(e[2])]
                        else:
                            ctx["rotation"] = None
                    else:
                        ctx["rotation"] = None
                except Exception:
                    ctx["rotation"] = None

                # worldScale
                try:
                    scl = getattr(owner, "worldScale", None)
                    if scl is not None:
                        ctx["scale"] = [float(scl[0]), float(scl[1]), float(scl[2])]
                    else:
                        ctx["scale"] = None
                except Exception:
                    ctx["scale"] = None

                # parent name
                try:
                    parent = getattr(owner, "parent", None)
                    ctx["parent_name"] = parent.name if parent is not None else None
                except Exception:
                    ctx["parent_name"] = None

                # Object properties
                try:
                    props = {{}}
                    for key in owner.keys():
                        try:
                            props[key] = owner[key]
                        except Exception:
                            continue
                    ctx["properties"] = props
                except Exception:
                    ctx["properties"] = None

                # Children (names only)
                try:
                    children = getattr(owner, "children", None)
                    if children is not None:
                        ctx["children"] = [child.name for child in children]
                except Exception:
                    ctx["children"] = None

                # Object positions in current scene (for camera follow, etc.)
                try:
                    scene = getattr(owner, "scene", None)
                    if scene is not None:
                        obj_positions = {{}}
                        for obj in getattr(scene, "objects", []):
                            try:
                                pos = getattr(obj, "worldPosition", None)
                                if pos is not None:
                                    obj_positions[obj.name] = [float(pos[0]), float(pos[1]), float(pos[2])]
                            except Exception:
                                continue
                        ctx["object_positions"] = obj_positions
                    else:
                        ctx["object_positions"] = None
                except Exception:
                    ctx["object_positions"] = None

            # Scene list snapshot
            try:
                scenes_data = []
                try:
                    scene_list = list(logic.getSceneList())
                except Exception:
                    scene_list = []

                for sc in scene_list:
                    try:
                        scenes_data.append(
                            {{
                                "name": getattr(sc, "name", ""),
                                "objects": [obj.name for obj in getattr(sc, "objects", [])],
                            }}
                        )
                    except Exception:
                        continue

                if scenes_data:
                    ctx["scenes"] = scenes_data
            except Exception:
                ctx["scenes"] = None

            # Engine info (best-effort, may not be available in all builds)
            engine_info = {{
                "frame_rate": 0.0,
                "current_frame": 0,
                "time_since_start": 0.0,
            }}
            try:
                engine_info["frame_rate"] = float(
                    getattr(logic, "getAverageFrameRate", lambda: 0.0)()
                )
            except Exception:
                pass
            try:
                engine_info["current_frame"] = int(
                    getattr(logic, "getCurrentFrame", lambda: 0)()
                )
            except Exception:
                pass
            try:
                engine_info["time_since_start"] = float(
                    getattr(logic, "getTimeSinceStart", lambda: 0.0)()
                )
            except Exception:
                pass
            ctx["engine"] = engine_info

            # Input snapshot: keyboard, mouse, joystick
            kb_ctx = {{"pressed": [], "justPressed": [], "justReleased": []}}
            mouse_ctx = {{
                "position": [0, 0],
                "pressed": [],
                "justPressed": [],
                "justReleased": [],
                "wheelDelta": 0,
            }}
            joy_ctx = {{
                "count": 0,
                "buttonsPressed": {{}},
                "axes": {{}},
            }}

            sensors_dict = {{}}
            try:
                if controller is not None:
                    for sensor in getattr(controller, "sensors", []):
                        sname = getattr(sensor, "name", "") or type(sensor).__name__
                        positive = getattr(sensor, "positive", False)
                        stype = getattr(sensor, "type", 0)
                        sentry = {{"positive": bool(positive), "type": int(stype)}}

                        # Keyboard: use sensor.inputs only (sensor.events is deprecated in UPBGE)
                        try:
                            ACTIVE = getattr(logic, "KX_INPUT_ACTIVE", 1)
                            JUST_ACTIVATED = getattr(logic, "KX_INPUT_JUST_ACTIVATED", 2)
                            JUST_RELEASED = getattr(logic, "KX_INPUT_JUST_RELEASED", 3)
                            events_list = []
                            inputs = getattr(sensor, "inputs", None)
                            if inputs is not None:
                                for keycode, evt in inputs.items():
                                    try:
                                        if getattr(evt, "active", False):
                                            events_list.append([int(keycode), int(ACTIVE)])
                                        if getattr(evt, "activated", False):
                                            events_list.append([int(keycode), int(JUST_ACTIVATED)])
                                        if getattr(evt, "released", False):
                                            events_list.append([int(keycode), int(JUST_RELEASED)])
                                    except Exception:
                                        continue
                            if events_list:
                                sentry["events"] = events_list
                            else:
                                # Fallback: Keyboard sensor with getKeyStatus (inputs may be empty)
                                if "Keyboard" in type(sensor).__name__ or stype == 1:
                                    get_status = getattr(sensor, "getKeyStatus", None)
                                    if get_status is not None and callable(get_status):
                                        for kc in (87, 83, 65, 68, 119, 115, 97, 100):
                                            try:
                                                st = get_status(kc)
                                                if st is not None and st != 0:
                                                    events_list.append([int(kc), int(ACTIVE)])
                                            except Exception:
                                                pass
                                        if events_list:
                                            sentry["events"] = events_list
                        except Exception:
                            pass

                        # Mouse: position, pressed, wheelDelta
                        try:
                            if "Mouse" in type(sensor).__name__ or getattr(sensor, "type", 0) == 12:
                                pos = getattr(sensor, "position", None)
                                if pos is not None:
                                    sentry["position"] = [int(pos[0]), int(pos[1])]
                                but = getattr(sensor, "getButtonStatus", None)
                                if but is not None and callable(but):
                                    sentry["pressed"] = [btn for btn in (1, 2, 4) if but(btn)]
                                wheel = getattr(sensor, "wheel", None)
                                if wheel is not None:
                                    sentry["wheelDelta"] = int(wheel)
                        except Exception:
                            pass

                        # Joystick: index, buttonsPressed, axisValues
                        try:
                            if "Joystick" in type(sensor).__name__ or getattr(sensor, "type", 0) == 13:
                                sentry["index"] = getattr(sensor, "index", 0)
                                buts = getattr(sensor, "getButtonStatus", None)
                                if buts is not None and callable(buts):
                                    sentry["buttonsPressed"] = [i for i in range(32) if buts(i)]
                                ax = getattr(sensor, "axisValues", None)
                                if ax is not None:
                                    sentry["axisValues"] = [float(ax[i]) if i < len(ax) else 0.0 for i in range(4)]
                        except Exception:
                            pass

                        sensors_dict[sname] = sentry

                        # Keyboard: use sensor.inputs only for kb_ctx (sensor.events is deprecated)
                        try:
                            inputs = getattr(sensor, "inputs", None)
                            if inputs is not None:
                                for keycode, evt in inputs.items():
                                    try:
                                        if getattr(evt, "active", False):
                                            kb_ctx["pressed"].append(int(keycode))
                                        if getattr(evt, "activated", False):
                                            kb_ctx["pressed"].append(int(keycode))
                                            kb_ctx["justPressed"].append(int(keycode))
                                        if getattr(evt, "released", False):
                                            kb_ctx["justReleased"].append(int(keycode))
                                    except Exception:
                                        continue
                        except Exception:
                            pass

                        # Mouse sensor: position, buttons, wheel
                        try:
                            if "Mouse" in type(sensor).__name__ or getattr(sensor, "type", 0) == 12:
                                pos = getattr(sensor, "position", None)
                                if pos is not None:
                                    mouse_ctx["position"] = [int(pos[0]), int(pos[1])]
                                but = getattr(sensor, "getButtonStatus", None)
                                if but is not None and callable(but):
                                    for btn in (1, 2, 4):
                                        if but(btn):
                                            if btn not in mouse_ctx["pressed"]:
                                                mouse_ctx["pressed"].append(btn)
                                wheel = getattr(sensor, "wheel", None)
                                if wheel is not None:
                                    mouse_ctx["wheelDelta"] = int(wheel)
                        except Exception:
                            pass

                        # Joystick sensor
                        try:
                            if "Joystick" in type(sensor).__name__ or getattr(sensor, "type", 0) == 13:
                                joy_ctx["count"] = max(joy_ctx["count"], 1)
                                idx = str(getattr(sensor, "index", 0))
                                buts = getattr(sensor, "getButtonStatus", None)
                                if buts is not None and callable(buts):
                                    pressed_list = [i for i in range(32) if buts(i)]
                                    if pressed_list:
                                        joy_ctx["buttonsPressed"][idx] = pressed_list
                                ax = getattr(sensor, "axisValues", None)
                                if ax is not None:
                                    joy_ctx["axes"][idx] = [float(ax[i]) if i < len(ax) else 0.0 for i in range(4)]
                        except Exception:
                            pass

                ctx["sensors"] = sensors_dict
                ctx["keyboard"] = kb_ctx
                ctx["mouse"] = mouse_ctx
                ctx["joystick"] = joy_ctx
            except Exception:
                pass

    except Exception:
        pass

    return ctx


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
        print("[UPBGE-JS] Wrapper executing script:", SCRIPT_NAME)
        # Check if it's a JavaScript file
        if is_javascript_file(script_name):
            # Build context for JS runtime bridge
            ctx = _build_context()
            sens = ctx.get("sensors") or {{}}
            kb_ev = (sens.get("Keyboard") or {{}}).get("events") or []
            print("[UPBGE-JS] Context built object_name=", ctx.get("object_name"), " scene_name=", ctx.get("scene_name"), " sensors=", list(sens.keys()), " Keyboard.events_len=", len(kb_ev))
            # Execute via JavaScript runtime
            success, error = execute_controller_script(script_text, script_name, context=ctx)
            print("[UPBGE-JS] JS execution success=", success, " error=", error if error else "None")
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
    """Create or update a text block with the wrapper script for a specific script."""
    # Sanitize script name for wrapper name
    safe_name = script_name.replace('.', '_').replace('-', '_')
    wrapper_name = f"__js_wrapper_{safe_name}__"
    
    # Generate wrapper code with script name (always use latest template)
    wrapper_code = WRAPPER_CODE_TEMPLATE.format(script_name=script_name)
    
    if wrapper_name in bpy.data.texts:
        wrapper = bpy.data.texts[wrapper_name]
        wrapper.from_string(wrapper_code)
    else:
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
