# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Script execution handler for JavaScript controllers.

Versão com ponte JS → Python baseada em comandos em lote:
- O código JavaScript roda em um processo Node.js separado.
- As chamadas à API `bge` no JS não falam diretamente com o engine.
- Em vez disso, o runtime JS acumula comandos em um array e os imprime
  como JSON em uma linha especial no stdout (`___BGE_CMDS___[...]`).
- Este módulo lê esses comandos e os aplica usando a API real do BGE.
"""

import bpy
from bpy.app.handlers import persistent

try:
    import bge  # type: ignore
except Exception:  # Em alguns contextos pode não existir (fora do game engine)
    bge = None

from runtime.nodejs import NodeJSRuntime

# Set to False to disable bridge flow logs
DEBUG_BRIDGE_LOGS = True

# RayCast results from previous frame: key = object_name, value = { "object", "point", "normal" }
_raycast_results = {}

# Vehicle constraints by chassis object name (for applyEngineForce, setSteeringValue, etc.)
_vehicle_constraints = {}


def _log(msg):
    """Log bridge flow (enable/disable via DEBUG_BRIDGE_LOGS)."""
    if DEBUG_BRIDGE_LOGS:
        print(msg)


# Global runtime instance
_runtime = None


def get_runtime():
    """Get or create Node.js runtime instance."""
    global _runtime
    if _runtime is None:
        use_worker = False
        try:
            prefs = bpy.context.preferences.addons.get("upbge_nodejs_sdk")
            if prefs and hasattr(prefs, "preferences") and getattr(prefs.preferences, "use_persistent_worker", False):
                use_worker = True
        except Exception:
            pass
        _runtime = NodeJSRuntime(use_worker=use_worker)
    return _runtime


def is_javascript_file(filename):
    """Check if a filename is a JavaScript file."""
    if not filename:
        return False
    return filename.endswith('.js') or filename.endswith('.mjs')


def _scene_get_object(scene, obj_name):
    """Get game object by name from scene. Works with .get() or [] access (UPBGE)."""
    if scene is None or not obj_name:
        return None
    try:
        objs = scene.objects
        if hasattr(objs, "get"):
            return objs.get(obj_name)
        return objs[obj_name]
    except (KeyError, TypeError, IndexError):
        try:
            objs = getattr(scene, "objects", None)
            if objs is not None:
                for o in objs:
                    if getattr(o, "name", None) == obj_name:
                        return o
        except Exception:
            pass
    return None


def _get_raycast_results():
    """Return copy of rayCast results for context (read by wrapper)."""
    global _raycast_results
    try:
        return dict(_raycast_results)
    except Exception:
        return {}


# Command handler functions
def _handle_end_game(cmd, context, scene, obj, logic):
    """Handle endGame command."""
    try:
        logic.endGame()
    except Exception:
        pass


def _handle_restart_game(cmd, context, scene, obj, logic):
    """Handle restartGame command."""
    try:
        logic.restartGame()
    except Exception:
        pass


def _handle_set_gravity(cmd, context, scene, obj, logic):
    """Handle setGravity command."""
    vec = cmd.get("vec") or cmd.get("value") or [0, 0, -9.81]
    if len(vec) >= 3:
        try:
            constraints = getattr(bge, "constraints", None)
            if constraints is not None and hasattr(constraints, "setGravity"):
                constraints.setGravity(float(vec[0]), float(vec[1]), float(vec[2]))
        except Exception:
            pass


def _handle_activate(cmd, context, scene, obj, logic):
    """Handle activate command for actuators."""
    act_name = cmd.get("actuator")
    if not act_name or not isinstance(act_name, str):
        return

    try:
        ctrl_name = context.get("controller_name")
        if not ctrl_name:
            return

        ctrls = getattr(obj, "controllers", None)
        if ctrls is None:
            return

        ctrl = ctrls.get(ctrl_name) if hasattr(ctrls, "get") else None
        if ctrl is None and hasattr(ctrls, "__getitem__"):
            try:
                ctrl = ctrls[ctrl_name]
            except (KeyError, TypeError):
                pass

        if ctrl is None:
            return

        actuators = getattr(ctrl, "actuators", None)
        if actuators is None:
            return

        act = actuators.get(act_name) if hasattr(actuators, "get") else None
        if act is None and hasattr(actuators, "__getitem__"):
            try:
                act = actuators[act_name]
            except (KeyError, TypeError):
                pass

        if act is not None:
            ctrl.activate(act)
    except Exception:
        pass


def _handle_deactivate(cmd, context, scene, obj, logic):
    """Handle deactivate command for actuators."""
    act_name = cmd.get("actuator")
    if not act_name or not isinstance(act_name, str):
        return

    try:
        ctrl_name = context.get("controller_name")
        if not ctrl_name:
            return

        ctrls = getattr(obj, "controllers", None)
        if ctrls is None:
            return

        ctrl = ctrls.get(ctrl_name) if hasattr(ctrls, "get") else None
        if ctrl is None and hasattr(ctrls, "__getitem__"):
            try:
                ctrl = ctrls[ctrl_name]
            except (KeyError, TypeError):
                pass

        if ctrl is None:
            return

        actuators = getattr(ctrl, "actuators", None)
        if actuators is None:
            return

        act = actuators.get(act_name) if hasattr(actuators, "get") else None
        if act is None and hasattr(actuators, "__getitem__"):
            try:
                act = actuators[act_name]
            except (KeyError, TypeError):
                pass

        if act is not None:
            ctrl.deactivate(act)
    except Exception:
        pass


def _handle_raycast(cmd, context, scene, obj, logic):
    """Handle rayCast command."""
    to_vec = cmd.get("to")
    if not to_vec or len(to_vec) < 3 or obj is None:
        return

    try:
        from_vec = cmd.get("from")
        dist = float(cmd.get("dist", 0))
        prop = str(cmd.get("prop") or "")
        face = bool(cmd.get("face", False))
        xray = bool(cmd.get("xray", False))
        mask = int(cmd.get("mask", 0xFFFF))
        to_v = (float(to_vec[0]), float(to_vec[1]), float(to_vec[2]))
        from_v = (float(from_vec[0]), float(from_vec[1]), float(from_vec[2])) if from_vec and len(from_vec) >= 3 else None
        hit = obj.rayCast(to_v, from_v, dist, prop, 1 if face else 0, 1 if xray else 0, 0, mask)
        if hit and len(hit) >= 3:
            hit_obj, hit_point, hit_normal = hit[0], hit[1], hit[2]
            _raycast_results[obj.name] = {
                "object": hit_obj.name if hit_obj is not None else None,
                "point": list(hit_point) if hit_point is not None else None,
                "normal": list(hit_normal) if hit_normal is not None else None,
            }
        else:
            _raycast_results[obj.name] = {"object": None, "point": None, "normal": None}
    except Exception:
        _raycast_results[obj.name] = {"object": None, "point": None, "normal": None}


def _handle_raycast_to(cmd, context, scene, obj, logic):
    """Handle rayCastTo command."""
    target = cmd.get("target")
    if obj is None:
        return

    try:
        dist = float(cmd.get("dist", 0))
        prop = str(cmd.get("prop") or "")
        if isinstance(target, list) and len(target) >= 3:
            to_point = (float(target[0]), float(target[1]), float(target[2]))
            hit_obj = obj.rayCastTo(to_point, dist, prop)
        elif isinstance(target, str):
            tgt = _scene_get_object(scene, target)
            hit_obj = obj.rayCastTo(tgt, dist, prop) if tgt is not None else None
        else:
            hit_obj = None
        _raycast_results[obj.name] = {
            "object": hit_obj.name if hit_obj is not None else None,
            "point": None,
            "normal": None,
        }
    except Exception:
        _raycast_results[obj.name] = {"object": None, "point": None, "normal": None}


def _handle_create_vehicle(cmd, context, scene, obj, logic):
    """Handle createVehicle command."""
    obj_name = obj.name if obj else None
    if obj is None or scene is None or obj_name in _vehicle_constraints:
        return

    try:
        constraints = getattr(bge, "constraints", None)
        if constraints is not None and hasattr(constraints, "createVehicle"):
            physics_id = getattr(obj, "getPhysicsId", lambda: 0)()
            if physics_id:
                vehicle = constraints.createVehicle(physics_id)
                _vehicle_constraints[obj_name] = vehicle
    except Exception:
        pass


def _handle_vehicle_apply_engine_force(cmd, context, scene, obj, logic):
    """Handle vehicleApplyEngineForce command."""
    chassis_name = cmd.get("object") or (obj.name if obj else None)
    if not chassis_name:
        return

    try:
        wheel_index = int(cmd.get("wheelIndex", 0))
        force = float(cmd.get("force", 0))
        vehicle = _vehicle_constraints.get(chassis_name)
        if vehicle is not None and hasattr(vehicle, "applyEngineForce"):
            vehicle.applyEngineForce(force, wheel_index)
    except Exception:
        pass


def _handle_vehicle_set_steering_value(cmd, context, scene, obj, logic):
    """Handle vehicleSetSteeringValue command."""
    chassis_name = cmd.get("object") or (obj.name if obj else None)
    if not chassis_name:
        return

    try:
        wheel_index = int(cmd.get("wheelIndex", 0))
        value = float(cmd.get("value", 0))
        vehicle = _vehicle_constraints.get(chassis_name)
        if vehicle is not None and hasattr(vehicle, "setSteeringValue"):
            vehicle.setSteeringValue(value, wheel_index)
    except Exception:
        pass


def _handle_vehicle_add_wheel(cmd, context, scene, obj, logic):
    """Handle vehicleAddWheel command."""
    chassis_name = cmd.get("object") or (obj.name if obj else None)
    wheel_name = cmd.get("wheel")
    if not chassis_name or not wheel_name or scene is None:
        return

    try:
        wheel_obj = _scene_get_object(scene, wheel_name)
        attach_pos = cmd.get("attachPos") or cmd.get("connectionPoint") or [0, 0, 0]
        down_dir = cmd.get("downDir") or [0, 0, -1]
        axle_dir = cmd.get("axleDir") or [0, 1, 0]
        rest_len = float(cmd.get("suspensionRestLength", 0.5))
        radius = float(cmd.get("wheelRadius", 0.4))
        has_steering = bool(cmd.get("hasSteering", False))
        vehicle = _vehicle_constraints.get(chassis_name)
        if vehicle is not None and wheel_obj is not None and hasattr(vehicle, "addWheel"):
            vehicle.addWheel(
                wheel_obj,
                (float(attach_pos[0]), float(attach_pos[1]), float(attach_pos[2])),
                (float(down_dir[0]), float(down_dir[1]), float(down_dir[2])),
                (float(axle_dir[0]), float(axle_dir[1]), float(axle_dir[2])),
                rest_len,
                radius,
                has_steering,
            )
    except Exception:
        pass


def _handle_vehicle_apply_braking(cmd, context, scene, obj, logic):
    """Handle vehicleApplyBraking command."""
    chassis_name = cmd.get("object") or (obj.name if obj else None)
    if not chassis_name:
        return

    try:
        wheel_index = int(cmd.get("wheelIndex", 0))
        force = float(cmd.get("force", 0))
        vehicle = _vehicle_constraints.get(chassis_name)
        if vehicle is not None and hasattr(vehicle, "applyBraking"):
            vehicle.applyBraking(force, wheel_index)
    except Exception:
        pass


def _handle_character_jump(cmd, context, scene, obj, logic):
    """Handle characterJump command."""
    if obj is None:
        return

    try:
        constraints = getattr(bge, "constraints", None)
        if constraints is not None and hasattr(constraints, "getCharacter"):
            char = constraints.getCharacter(obj)
            if char is not None and hasattr(char, "jump"):
                char.jump()
    except Exception:
        pass


def _handle_character_walk_direction(cmd, context, scene, obj, logic):
    """Handle characterWalkDirection command."""
    vec = cmd.get("vec") or cmd.get("value") or [0, 0, 0]
    if obj is None or len(vec) < 3:
        return

    try:
        constraints = getattr(bge, "constraints", None)
        if constraints is not None and hasattr(constraints, "getCharacter"):
            char = constraints.getCharacter(obj)
            if char is not None and hasattr(char, "walkDirection"):
                char.walkDirection = (float(vec[0]), float(vec[1]), float(vec[2]))
    except Exception:
        pass


def _handle_character_set_velocity(cmd, context, scene, obj, logic):
    """Handle characterSetVelocity command."""
    vec = cmd.get("vec") or cmd.get("value") or [0, 0, 0]
    if obj is None or len(vec) < 3:
        return

    try:
        time_val = float(cmd.get("time", 0.2))
        local = bool(cmd.get("local", False))
        constraints = getattr(bge, "constraints", None)
        if constraints is not None and hasattr(constraints, "getCharacter"):
            char = constraints.getCharacter(obj)
            if char is not None and hasattr(char, "setVelocity"):
                char.setVelocity((float(vec[0]), float(vec[1]), float(vec[2])), time_val, local)
    except Exception:
        pass


def _handle_apply_movement(cmd, context, scene, obj, logic):
    """Handle applyMovement command."""
    if obj is None:
        return

    vec = cmd.get("vec") or cmd.get("value") or [0.0, 0.0, 0.0]
    _log("[UPBGE-JS] applyMovement obj=%s vec=%s" % (obj.name, vec))
    try:
        obj.applyMovement(vec, True)
    except Exception:
        try:
            obj.worldPosition = [
                obj.worldPosition[0] + vec[0],
                obj.worldPosition[1] + vec[1],
                obj.worldPosition[2] + vec[2],
            ]
        except Exception:
            pass


def _handle_set_position(cmd, context, scene, obj, logic):
    """Handle setPosition command."""
    if obj is None:
        return

    value = cmd.get("value")
    if value is not None and len(value) >= 3:
        try:
            obj.worldPosition = value
        except Exception:
            pass


def _handle_set_rotation(cmd, context, scene, obj, logic):
    """Handle setRotation command."""
    if obj is None:
        return

    value = cmd.get("value")
    if value is not None and len(value) >= 3:
        try:
            from mathutils import Euler
            obj.worldOrientation = Euler(value).to_matrix()
        except Exception:
            try:
                obj.worldOrientation = value
            except Exception:
                pass


def _handle_look_at(cmd, context, scene, obj, logic):
    """Handle lookAt command."""
    if obj is None:
        return

    target_name = cmd.get("target")
    if not target_name or target_name == obj.name:
        return

    target_obj = _scene_get_object(scene, target_name)
    if target_obj is None:
        return

    try:
        import mathutils
        cam_pos = obj.worldPosition
        tgt_pos = target_obj.worldPosition
        direction = mathutils.Vector(
            (tgt_pos[0] - cam_pos[0], tgt_pos[1] - cam_pos[1], tgt_pos[2] - cam_pos[2])
        )
        if direction.length_squared > 1e-6:
            direction.normalize()
            align = getattr(obj, "alignAxisToVect", None)
            if align is not None and callable(align):
                align(-direction, 1, 1.0)
            else:
                up = mathutils.Vector((0, 0, 1))
                right = direction.cross(up)
                if right.length_squared > 1e-6:
                    right.normalize()
                    up = right.cross(direction)
                    m = mathutils.Matrix((right, -direction, up)).transposed()
                    obj.worldOrientation = m
    except Exception:
        pass


def _handle_set_scale(cmd, context, scene, obj, logic):
    """Handle setScale command."""
    if obj is None:
        return

    value = cmd.get("value")
    if value is not None and len(value) >= 3:
        try:
            obj.worldScale = value
        except Exception:
            try:
                obj.localScale = value
            except Exception:
                pass


def _handle_set_property(cmd, context, scene, obj, logic):
    """Handle setProperty command."""
    if obj is None:
        return

    prop_name = cmd.get("property")
    if prop_name:
        try:
            obj[prop_name] = cmd.get("value")
        except Exception:
            pass


def _handle_set_local_position(cmd, context, scene, obj, logic):
    """Handle setLocalPosition command."""
    if obj is None:
        return

    value = cmd.get("value")
    if value is not None and len(value) >= 3:
        try:
            obj.localPosition = value
        except Exception:
            pass


def _handle_set_local_rotation(cmd, context, scene, obj, logic):
    """Handle setLocalRotation command."""
    if obj is None:
        return

    value = cmd.get("value")
    if value is not None and len(value) >= 3:
        try:
            from mathutils import Euler
            obj.localOrientation = Euler(value).to_matrix()
        except Exception:
            try:
                obj.localOrientation = value
            except Exception:
                pass


def _handle_set_parent(cmd, context, scene, obj, logic):
    """Handle setParent command."""
    if obj is None:
        return

    parent_name = cmd.get("parent")
    try:
        if parent_name:
            parent_obj = _scene_get_object(scene, parent_name)
            if parent_obj is not None:
                obj.setParent(parent_obj)
        else:
            obj.setParent(None)
    except Exception:
        pass


def _handle_scene_add_object(cmd, context, scene, obj, logic):
    """Handle sceneAddObject command."""
    if scene is None:
        return

    add_obj_name = cmd.get("object")
    if not add_obj_name:
        return

    try:
        add_obj = _scene_get_object(scene, add_obj_name)
        if add_obj is None:
            for s in logic.getSceneList():
                add_obj = _scene_get_object(s, add_obj_name)
                if add_obj is not None:
                    break
        if add_obj is not None:
            owner = context.get("object_name")
            owner_obj = _scene_get_object(scene, owner) if owner else None
            if hasattr(scene, "addObject") and owner_obj:
                scene.addObject(add_obj, owner_obj, 0)
    except Exception:
        pass


def _handle_scene_remove_object(cmd, context, scene, obj, logic):
    """Handle sceneRemoveObject command."""
    if scene is None:
        return

    obj_to_remove = cmd.get("object")
    if not obj_to_remove:
        return

    try:
        robj = _scene_get_object(scene, obj_to_remove)
        if robj is not None:
            if hasattr(scene.objects, "unlink"):
                scene.objects.unlink(robj)
            elif hasattr(scene, "unlink"):
                scene.unlink(robj)
    except Exception:
        pass


def _handle_set_viewport(cmd, context, scene, obj, logic):
    """Handle setViewport command."""
    if obj is None:
        return

    left = cmd.get("left")
    bottom = cmd.get("bottom")
    right = cmd.get("right")
    top = cmd.get("top")
    if left is None or bottom is None or right is None or top is None:
        return

    try:
        if hasattr(obj, "setViewport"):
            obj.setViewport(int(left), int(bottom), int(right), int(top))
    except Exception:
        pass


def _handle_set_active_camera(cmd, context, scene, obj, logic):
    """Handle setActiveCamera command."""
    if obj is None or scene is None:
        return

    tgt_scene = scene
    cmd_scene = cmd.get("scene")
    if cmd_scene and isinstance(cmd_scene, str):
        try:
            scene_list = logic.getSceneList()
            if hasattr(scene_list, "get"):
                tgt_scene = scene_list.get(cmd_scene)
            else:
                for s in scene_list:
                    if getattr(s, "name", None) == cmd_scene:
                        tgt_scene = s
                        break
        except Exception:
            pass

    if tgt_scene is not None and hasattr(tgt_scene, "active_camera"):
        try:
            tgt_scene.active_camera = obj
        except Exception:
            pass


# Command handler dispatch table
_COMMAND_HANDLERS = {
    "endGame": _handle_end_game,
    "restartGame": _handle_restart_game,
    "setGravity": _handle_set_gravity,
    "activate": _handle_activate,
    "deactivate": _handle_deactivate,
    "rayCast": _handle_raycast,
    "rayCastTo": _handle_raycast_to,
    "createVehicle": _handle_create_vehicle,
    "vehicleApplyEngineForce": _handle_vehicle_apply_engine_force,
    "vehicleSetSteeringValue": _handle_vehicle_set_steering_value,
    "vehicleAddWheel": _handle_vehicle_add_wheel,
    "vehicleApplyBraking": _handle_vehicle_apply_braking,
    "characterJump": _handle_character_jump,
    "characterWalkDirection": _handle_character_walk_direction,
    "characterSetVelocity": _handle_character_set_velocity,
    "applyMovement": _handle_apply_movement,
    "setPosition": _handle_set_position,
    "setRotation": _handle_set_rotation,
    "lookAt": _handle_look_at,
    "setScale": _handle_set_scale,
    "setProperty": _handle_set_property,
    "setLocalPosition": _handle_set_local_position,
    "setLocalRotation": _handle_set_local_rotation,
    "setParent": _handle_set_parent,
    "sceneAddObject": _handle_scene_add_object,
    "sceneRemoveObject": _handle_scene_remove_object,
    "setViewport": _handle_set_viewport,
    "setActiveCamera": _handle_set_active_camera,
}


def _apply_commands(commands, context):
    """Apply a list of high-level commands to the BGE using Python API.

    Each command is expected to be a dict with:
        {
            "op": "applyMovement" | "setPosition",
            "object": "<object_name>",
            "scene": "<scene_name>",
            "value" | "vec": [x, y, z]
        }
    """
    if bge is None:
        # Running outside game engine – nothing to apply
        return

    scene_name = context.get("scene_name") or ""
    scene = None

    try:
        logic = bge.logic  # type: ignore[attr-defined]
    except Exception:
        return

    try:
        if scene_name:
            scene_list = logic.getSceneList()
            if hasattr(scene_list, "get"):
                scene = scene_list.get(scene_name)
            else:
                scene = None
                for s in scene_list:
                    if getattr(s, "name", None) == scene_name:
                        scene = s
                        break
        else:
            scene = logic.getCurrentScene()
    except Exception:
        try:
            scene = logic.getCurrentScene()
        except Exception:
            scene = None

    if scene is None:
        _log("[UPBGE-JS] _apply_commands: no scene, skip")
        return

    _log("[UPBGE-JS] _apply_commands scene=%s object_name=%s num_commands=%s" % (
        scene_name or "(current)", context.get("object_name"), len(commands or [])))

    for cmd in commands or []:
        try:
            op = cmd.get("op")

            # Global ops (endGame, restartGame, setGravity) - no object needed
            if op in ("endGame", "restartGame", "setGravity"):
                if op in _COMMAND_HANDLERS:
                    _COMMAND_HANDLERS[op](cmd, context, scene, None, logic)
                continue

            # Object-specific ops
            obj_name = cmd.get("object") or context.get("object_name")
            if not obj_name:
                continue

            obj = _scene_get_object(scene, obj_name)
            if obj is None:
                _log("[UPBGE-JS] _apply_commands: object not found obj_name=%s scene=%s" % (obj_name, scene_name or "(current)"))
                continue

            # Dispatch to handler
            if op in _COMMAND_HANDLERS:
                _COMMAND_HANDLERS[op](cmd, context, scene, obj, logic)

        except Exception:
            continue


def _extract_commands(output):
    """Extract JSON commands from Node.js stdout.

    Espera uma linha contendo o prefixo '___BGE_CMDS___'.
    Exemplo:
        ... logs do usuário ...
        ___BGE_CMDS___[{"op": "applyMovement", "object": "Player", "vec": [0,0,0.1]}]
    """
    if not output:
        return []

    marker = "___BGE_CMDS___"
    commands_str = ""
    for line in output.splitlines():
        if marker in line:
            idx = line.find(marker)
            rest = line[idx + len(marker) :].strip()
            # Worker format: id\tjson; legacy format: json
            if "\t" in rest:
                rest = rest.split("\t", 1)[1]
            commands_str = rest
            break

    if not commands_str:
        return []

    import json

    try:
        data = json.loads(commands_str)
        if isinstance(data, list):
            return data
    except Exception:
        return []

    return []


@persistent
def on_frame_change_pre(scene):
    """
    Handler chamado antes de cada frame.

    Mantido apenas para futura expansão; hoje não faz nada.
    """
    return None


def execute_controller_script(script_text, filename, context=None):
    """
    Execute a controller script using JavaScript runtime with BGE command bridge.

    Args:
        script_text: JavaScript source code from the Text datablock.
        filename: Logical filename (used for logging only).
        context: dict with at least:
            {
                "scene_name": str,
                "object_name": str,
            }

    Returns:
        (success: bool, error_message: Optional[str])
    """
    context = context or {}
    _log("[UPBGE-JS] execute_controller_script called script=%s" % (filename,))

    try:
        runtime = get_runtime()

        # Execute JavaScript and capture output / errors
        output, error_output, success = runtime.execute_with_context(
            script_text, context=context, timeout=10
        )
        _log("[UPBGE-JS] Node run success=%s output_len=%s stderr_len=%s" % (success, len(output or ""), len(error_output or "")))

        # Extraímos e aplicamos comandos, mesmo que o script tenha retornado erro,
        # mas só se o processo Node foi bem-sucedido.
        if success:
            commands = _extract_commands(output)
            _log("[UPBGE-JS] Extracted %s commands" % (len(commands),))
            if commands:
                _log("[UPBGE-JS] Commands: %s" % (commands[:3] if len(commands) > 3 else commands,))
            elif output and "___BGE_CMDS___" in output:
                # Node sent marker but 0 commands: show JS debug lines from stdout
                for line in (output or "").splitlines():
                    if "[UPBGE-JS] DEBUG" in line:
                        _log(line.strip())
                    if "___BGE_CMDS___" in line:
                        _log("[UPBGE-JS] Node sent (no commands): %s" % (line.strip()[:80],))
                        break
            _apply_commands(commands, context)

        if not success:
            return False, error_output or "Unknown JavaScript execution error"

        return True, None

    except Exception as e:
        _log("[UPBGE-JS] execute_controller_script exception: %s" % (e,))
        return False, str(e)


def register():
    """Register script execution handlers."""
    bpy.app.handlers.frame_change_pre.append(on_frame_change_pre)
    print("UPBGE JavaScript SDK: Script execution handler with JS bridge registered")


def unregister():
    """Unregister script execution handlers."""
    if on_frame_change_pre in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(on_frame_change_pre)
