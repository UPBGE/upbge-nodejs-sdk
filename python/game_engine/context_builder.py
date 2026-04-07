# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Context builder for JavaScript runtime bridge.
Builds a rich context dict from BGE state for use in JS runtime.
"""

try:
    import bge
except ImportError:
    bge = None


def _get_engine_info():
    """Extract engine info (frame rate, current frame, time since start)."""
    if bge is None:
        return {
            "frame_rate": 0.0,
            "current_frame": 0,
            "time_since_start": 0.0,
        }

    logic = getattr(bge, "logic", None)
    if logic is None:
        return {
            "frame_rate": 0.0,
            "current_frame": 0,
            "time_since_start": 0.0,
        }

    engine_info = {
        "frame_rate": 0.0,
        "current_frame": 0,
        "time_since_start": 0.0,
    }

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

    return engine_info


def _get_object_info(owner):
    """Extract position, rotation, scale info from object."""
    info = {
        "position": None,
        "rotation": None,
        "scale": None,
    }

    if owner is None:
        return info

    # worldPosition
    try:
        pos = getattr(owner, "worldPosition", None)
        if pos is not None:
            info["position"] = [float(pos[0]), float(pos[1]), float(pos[2])]
    except Exception:
        pass

    # worldOrientation: Euler [x,y,z] in radians
    try:
        orient = getattr(owner, "worldOrientation", None)
        if orient is not None:
            euler = getattr(orient, "to_euler", None)
            if euler is not None and callable(euler):
                e = euler()
                info["rotation"] = [float(e[0]), float(e[1]), float(e[2])]
    except Exception:
        pass

    # worldScale
    try:
        scl = getattr(owner, "worldScale", None)
        if scl is not None:
            info["scale"] = [float(scl[0]), float(scl[1]), float(scl[2])]
    except Exception:
        pass

    return info


def build_context():
    """Build rich context for the JS runtime bridge.

    Returns a dict that will be serialized to JSON and made available in JS as
    __BGE_CONTEXT__.
    """
    ctx = {
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
        "windowWidth": None,
        "windowHeight": None,
        "active_camera_name": None,
        "keyboard": None,
        "mouse": None,
        "joystick": None,
        "engine": None,
        "controller_name": "",
        "actuators": None,
        "sensors": None,
        "rayCastResults": None,
    }

    try:
        if bge is None:
            return ctx

        logic = getattr(bge, "logic", None)
        if logic is None:
            return ctx

        controller = logic.getCurrentController()
        owner = controller.owner if controller else None

        # Controller metadata and actuators list
        try:
            if controller is not None:
                ctx["controller_name"] = controller.name
                ctx["actuators"] = [
                    getattr(a, "name", str(i))
                    for i, a in enumerate(getattr(controller, "actuators", []))
                ]
        except Exception:
            pass

        # Scene / object basic info
        if owner is not None:
            ctx["object_name"] = owner.name
            try:
                ctx["scene_name"] = owner.scene.name
            except Exception:
                ctx["scene_name"] = ""

            # Get position, rotation, scale
            obj_info = _get_object_info(owner)
            ctx.update(obj_info)

            # parent name
            try:
                parent = getattr(owner, "parent", None)
                ctx["parent_name"] = parent.name if parent is not None else None
            except Exception:
                ctx["parent_name"] = None

            # Object properties
            try:
                props = {}
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

            # Object positions in current scene
            try:
                scene = getattr(owner, "scene", None)
                if scene is not None:
                    obj_positions = {}
                    for obj in getattr(scene, "objects", []):
                        try:
                            pos = getattr(obj, "worldPosition", None)
                            if pos is not None:
                                obj_positions[obj.name] = [
                                    float(pos[0]),
                                    float(pos[1]),
                                    float(pos[2]),
                                ]
                        except Exception:
                            continue
                    ctx["object_positions"] = obj_positions
            except Exception:
                ctx["object_positions"] = None

        # Viewport and active camera
        try:
            try:
                render = getattr(bge, "render", None)
                if render is not None:
                    ctx["windowWidth"] = int(
                        getattr(render, "getWindowWidth", lambda: 0)()
                    )
                    ctx["windowHeight"] = int(
                        getattr(render, "getWindowHeight", lambda: 0)()
                    )
            except Exception:
                ctx["windowWidth"] = None
                ctx["windowHeight"] = None

            try:
                if owner is not None:
                    scene = getattr(owner, "scene", None)
                    if scene is not None:
                        ac = getattr(scene, "active_camera", None)
                        ctx["active_camera_name"] = (
                            ac.name if ac is not None else None
                        )
            except Exception:
                ctx["active_camera_name"] = None
        except Exception:
            pass

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
                        {
                            "name": getattr(sc, "name", ""),
                            "objects": [obj.name for obj in getattr(sc, "objects", [])],
                        }
                    )
                except Exception:
                    continue

            if scenes_data:
                ctx["scenes"] = scenes_data
        except Exception:
            ctx["scenes"] = None

        # Engine info
        ctx["engine"] = _get_engine_info()

        # Input snapshot: keyboard, mouse, joystick
        kb_ctx = {"pressed": [], "justPressed": [], "justReleased": []}
        mouse_ctx = {
            "position": [0, 0],
            "pressed": [],
            "justPressed": [],
            "justReleased": [],
            "wheelDelta": 0,
        }
        joy_ctx = {
            "count": 0,
            "buttonsPressed": {},
            "axes": {},
        }

        sensors_dict = {}
        try:
            if controller is not None:
                for sensor in getattr(controller, "sensors", []):
                    sname = getattr(sensor, "name", "") or type(sensor).__name__
                    positive = getattr(sensor, "positive", False)
                    stype = getattr(sensor, "type", 0)
                    sentry = {"positive": bool(positive), "type": int(stype)}

                    # Collision sensor: hitObjectList
                    hit_list = getattr(sensor, "hitObjectList", None)
                    if hit_list is not None:
                        try:
                            sentry["hitObjectList"] = [
                                {"name": getattr(o, "name", str(i))} for i, o in enumerate(hit_list)
                            ]
                        except Exception:
                            sentry["hitObjectList"] = []
                    elif "Collision" in type(sensor).__name__ or (
                        sname and "ollision" in sname
                    ):
                        try:
                            hit_list = getattr(sensor, "hit_object_list", None)
                            if hit_list is not None:
                                sentry["hitObjectList"] = [
                                    {"name": getattr(o, "name", str(i))} for i, o in enumerate(hit_list)
                                ]
                            else:
                                sentry["hitObjectList"] = []
                        except Exception:
                            sentry["hitObjectList"] = []

                    # Keyboard: use sensor.inputs
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
                            # Fallback: Keyboard sensor with getKeyStatus
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
                                sentry["axisValues"] = [
                                    float(ax[i]) if i < len(ax) else 0.0 for i in range(4)
                                ]
                    except Exception:
                        pass

                    sensors_dict[sname] = sentry

                    # Keyboard: use sensor.inputs for kb_ctx
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
                                joy_ctx["axes"][idx] = [
                                    float(ax[i]) if i < len(ax) else 0.0 for i in range(4)
                                ]
                    except Exception:
                        pass

            ctx["sensors"] = sensors_dict
            ctx["keyboard"] = kb_ctx
            ctx["mouse"] = mouse_ctx
            ctx["joystick"] = joy_ctx
        except Exception:
            pass

        # RayCast results from previous frame
        try:
            from upbge_nodejs_sdk.python.game_engine import script_handler

            ctx["rayCastResults"] = getattr(
                script_handler, "_get_raycast_results", lambda: {}
            )()
        except Exception:
            ctx["rayCastResults"] = {}

    except Exception:
        pass

    return ctx
