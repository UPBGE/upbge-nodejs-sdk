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
            # Global ops (no object required)
            if op == "endGame":
                try:
                    logic.endGame()
                except Exception:
                    pass
                continue
            if op == "restartGame":
                try:
                    logic.restartGame()
                except Exception:
                    pass
                continue

            obj_name = cmd.get("object") or context.get("object_name")
            if not obj_name:
                continue

            obj = _scene_get_object(scene, obj_name)
            if obj is None:
                _log("[UPBGE-JS] _apply_commands: object not found obj_name=%s scene=%s" % (obj_name, scene_name or "(current)"))
                continue

            if op == "applyMovement":
                vec = cmd.get("vec") or cmd.get("value") or [0.0, 0.0, 0.0]
                _log("[UPBGE-JS] applyMovement obj=%s vec=%s" % (obj_name, vec))
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
            elif op == "setPosition":
                value = cmd.get("value")
                if value is not None and len(value) >= 3:
                    try:
                        obj.worldPosition = value
                    except Exception:
                        pass
            elif op == "setRotation":
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
            elif op == "lookAt":
                target_name = cmd.get("target")
                if target_name and target_name != obj_name:
                    target_obj = _scene_get_object(scene, target_name)
                    if target_obj is not None:
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
            elif op == "setScale":
                value = cmd.get("value")
                if value is not None and len(value) >= 3:
                    try:
                        obj.worldScale = value
                    except Exception:
                        try:
                            obj.localScale = value
                        except Exception:
                            pass
            elif op == "setProperty":
                prop_name = cmd.get("property")
                if prop_name:
                    try:
                        obj[prop_name] = cmd.get("value")
                    except Exception:
                        pass
            elif op == "setLocalPosition":
                value = cmd.get("value")
                if value is not None and len(value) >= 3:
                    try:
                        obj.localPosition = value
                    except Exception:
                        pass
            elif op == "setLocalRotation":
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
            elif op == "setParent":
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
            elif op == "sceneAddObject":
                # BGE: scene.addObject(obj, owner, time) - obj can be from any scene
                add_obj_name = cmd.get("object")
                if add_obj_name and scene:
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
                continue
            elif op == "sceneRemoveObject":
                obj_to_remove = cmd.get("object")
                if obj_to_remove and scene:
                    try:
                        robj = _scene_get_object(scene, obj_to_remove)
                        if robj is not None:
                            if hasattr(scene.objects, "unlink"):
                                scene.objects.unlink(robj)
                            elif hasattr(scene, "unlink"):
                                scene.unlink(robj)
                    except Exception:
                        pass
                continue
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
