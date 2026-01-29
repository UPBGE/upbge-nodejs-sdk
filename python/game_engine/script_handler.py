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
            scene = logic.getSceneList()[scene_name]
        else:
            scene = logic.getCurrentScene()
    except Exception:
        # Fallback: try current scene only
        try:
            scene = logic.getCurrentScene()
        except Exception:
            scene = None

    if scene is None:
        return

    for cmd in commands or []:
        try:
            op = cmd.get("op")
            obj_name = cmd.get("object") or context.get("object_name")
            if not obj_name:
                continue

            obj = scene.objects.get(obj_name)
            if obj is None:
                continue

            if op == "applyMovement":
                vec = cmd.get("vec") or cmd.get("value") or [0.0, 0.0, 0.0]
                try:
                    obj.applyMovement(vec, True)
                except Exception:
                    # Fallback: manual position adjust
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
            elif op == "setProperty":
                prop_name = cmd.get("property")
                if prop_name:
                    try:
                        obj[prop_name] = cmd.get("value")
                    except Exception:
                        pass
            elif op == "setParent":
                parent_name = cmd.get("parent")
                try:
                    if parent_name:
                        parent_obj = scene.objects.get(parent_name)
                        if parent_obj is not None:
                            obj.setParent(parent_obj)
                    else:
                        obj.setParent(None)
                except Exception:
                    pass
            elif op == "setPosition":
                value = cmd.get("value")
                if value is not None and len(value) >= 3:
                    try:
                        obj.worldPosition = value
                    except Exception:
                        pass
        except Exception:
            # Não deixar um comando quebrar todos os outros
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
            commands_str = line[idx + len(marker) :]
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

    try:
        runtime = get_runtime()

        # Execute JavaScript and capture output / errors
        output, error_output, success = runtime.execute_with_context(
            script_text, context=context, timeout=10
        )

        # Extraímos e aplicamos comandos, mesmo que o script tenha retornado erro,
        # mas só se o processo Node foi bem-sucedido.
        if success:
            commands = _extract_commands(output)
            _apply_commands(commands, context)

        if not success:
            return False, error_output or "Unknown JavaScript execution error"

        return True, None

    except Exception as e:
        return False, str(e)


def register():
    """Register script execution handlers."""
    bpy.app.handlers.frame_change_pre.append(on_frame_change_pre)
    print("UPBGE JavaScript SDK: Script execution handler with JS bridge registered")


def unregister():
    """Unregister script execution handlers."""
    if on_frame_change_pre in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(on_frame_change_pre)
