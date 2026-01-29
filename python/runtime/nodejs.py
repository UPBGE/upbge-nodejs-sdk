# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Node.js runtime wrapper for executing JavaScript code."""

import sys
import os
import subprocess
import platform

try:
    import bpy
except ImportError:
    bpy = None


def get_sdk_path():
    """Get the SDK path from preferences or auto-detect."""
    if bpy:
        try:
            preferences = bpy.context.preferences
            addon_prefs = preferences.addons["upbge_nodejs_sdk"].preferences
            sdk_path = addon_prefs.sdk_path
            if sdk_path:
                return sdk_path
        except:
            pass
    
    # Fallback: try to get from addon location (when installed via ZIP)
    try:
        # Go up from python/runtime/nodejs.py to the addon root
        addon_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Check if this addon directory has SDK structure
        has_sdk_structure = (
            os.path.exists(os.path.join(addon_path, "python")) and
            os.path.exists(os.path.join(addon_path, "runtime"))
        )
        
        if has_sdk_structure:
            return addon_path
    except:
        pass
    
    return ""


def get_node_path():
    """Get the path to Node.js executable from the SDK."""
    sdk_path = get_sdk_path()
    if not sdk_path:
        return None
    
    os_type = platform.system()
    
    if os_type == "Windows":
        node_path = os.path.join(sdk_path, "runtime", "windows", "node.exe")
    elif os_type == "Darwin":
        node_path = os.path.join(sdk_path, "runtime", "macos", "node-osx")
    else:  # Linux
        node_path = os.path.join(sdk_path, "runtime", "linux", "node-linux64")
    
    if os.path.exists(node_path):
        return node_path
    
    # Fallback: try system Node.js
    if os_type == "Windows":
        possible_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "nodejs", "node.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "nodejs", "node.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "nodejs", "node.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    else:
        # Try system PATH
        try:
            result = subprocess.run(["which", "node"], capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
    
    return None


class NodeJSRuntime:
    """Wrapper for executing JavaScript code using Node.js."""
    
    def __init__(self):
        self.node_path = get_node_path()
        self._interactive_context = {}  # Store for interactive console context
    
    def get_node_path(self):
        """Get the path to Node.js executable."""
        if not self.node_path:
            self.node_path = get_node_path()
        return self.node_path
    
    def execute_interactive(self, code, context_id="default", timeout=5):
        """
        Execute JavaScript code in an interactive context (for console).
        Maintains variable state between executions by accumulating all code.
        Returns (output, error_output, success)
        """
        node_path = self.get_node_path()
        if not node_path:
            return ("", "Error: Node.js not found. Please install Node.js or configure SDK path.", False)
        
        try:
            # Get or create context for this console
            if context_id not in self._interactive_context:
                self._interactive_context[context_id] = {
                    "accumulated_code": ""
                }
            
            context = self._interactive_context[context_id]
            
            # Accumulate code - this maintains variable state
            if context["accumulated_code"]:
                context["accumulated_code"] += "\n" + code
            else:
                context["accumulated_code"] = code
            
            # Escape the accumulated code for use in JavaScript string
            accumulated = context["accumulated_code"]
            escaped_code = accumulated.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r').replace('`', '\\`').replace('$', '\\$')
            
            # Execute all accumulated code together to maintain context
            wrapped_code = f"""
try {{
    // Execute accumulated code
    const result = eval('{escaped_code}');
    // Print result if it's not undefined
    if (result !== undefined) {{
        if (typeof result === 'object' && result !== null) {{
            console.log(JSON.stringify(result, null, 2));
        }} else {{
            console.log(result);
        }}
    }}
}} catch (error) {{
    console.error(error.toString());
    if (error.stack) {{
        console.error(error.stack);
    }}
    process.exit(1);
}}
"""
            
            result = subprocess.run(
                [node_path, "-e", wrapped_code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            output = result.stdout
            error_output = result.stderr
            
            if result.returncode != 0:
                if not error_output:
                    error_output = output
                # Don't clear accumulated code on error - user might want to fix it
                return (output, error_output, False)
            
            return (output, error_output, True)
            
        except FileNotFoundError:
            return ("", "Error: Node.js not found. Please install Node.js or configure SDK path.", False)
        except subprocess.TimeoutExpired:
            return ("", "Error: JavaScript execution timed out.", False)
        except Exception as e:
            return ("", f"Error executing JavaScript: {str(e)}", False)
    
    def execute(self, code, timeout=5):
        """
        Execute JavaScript code using Node.js.
        Returns (output, error_output, success)
        """
        node_path = self.get_node_path()
        if not node_path:
            return ("", "Error: Node.js not found. Please install Node.js or configure SDK path.", False)
        
        try:
            # Escape the code for use in JavaScript string
            escaped_code = code.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')
            
            wrapped_code = f"""// Try to evaluate as expression first, then as statement
try {{
    // Try to evaluate as expression
    const result = eval('(' + '{escaped_code}' + ')');
    if (result !== undefined) {{
        // Print the result if it's not undefined
        if (typeof result === 'object' && result !== null) {{
            console.log(JSON.stringify(result, null, 2));
        }} else {{
            console.log(result);
        }}
    }}
}} catch (evalError) {{
    // If eval fails, try executing as statement
    try {{
        eval('{escaped_code}');
    }} catch (stmtError) {{
        // If both fail, show the error
        console.error(stmtError.toString());
        if (stmtError.stack) {{
            console.error(stmtError.stack);
        }}
    process.exit(1);
    }}
}}"""
            
            result = subprocess.run(
                [node_path, "-e", wrapped_code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            output = result.stdout
            error_output = result.stderr
            
            if result.returncode != 0:
                if not error_output:
                    error_output = output
                return (output, error_output, False)
            
            return (output, error_output, True)
            
        except FileNotFoundError:
            return ("", "Error: Node.js not found. Please install Node.js or configure SDK path.", False)
        except subprocess.TimeoutExpired:
            return ("", "Error: JavaScript execution timed out.", False)
        except Exception as e:
            return ("", f"Error executing JavaScript: {str(e)}", False)

    def execute_with_context(self, code, context=None, timeout=10):
        """
        Execute JavaScript code using Node.js with BGE bridge context.

        The code is wrapped so that:
        - A global __BGE_CONTEXT__ object is available in JS.
        - A global `bge` object is created that queues high-level commands
          into an array.
        - At the end, the commands array is printed as a single line starting
          with the marker '___BGE_CMDS___'.

        Returns (output, error_output, success).
        """
        import json

        node_path = self.get_node_path()
        if not node_path:
            return ("", "Error: Node.js not found. Please install Node.js or configure SDK path.", False)

        # Prepare context JSON that will be injected into the JS runtime
        context = context or {}
        try:
            context_json = json.dumps(context)
        except Exception:
            context_json = "{}"

        try:
            # Escape the user code for safe embedding inside a JS function body.
            # Aqui usamos uma função IIFE para executar o código do usuário.
            # Importante: NÃO escapamos crases/backticks (`) para permitir
            # o uso de template literals normalmente.
            user_code = code.replace("\\", "\\\\")

            wrapped_code = f"""
const __BGE_CONTEXT__ = {context_json} || {{}};
let __bgeCommands = [];
function __bgeQueue(cmd) {{
    __bgeCommands.push(cmd);
}}

function __bgeQueueForObject(op, objName, extra) {{
    const ctx = __BGE_CONTEXT__ || {{}};
    const payload = Object.assign({{
        op,
        scene: ctx.scene_name || "",
        object: objName || ctx.object_name || ""
    }}, extra || {{}});
    __bgeQueue(payload);
}}

function __bgeMakeGameObject(name) {{
    const ctx = __BGE_CONTEXT__ || {{}};
    const objName = name || ctx.object_name || "";
    return {{
        name: objName,
        get position() {{
            if (ctx.object_name === objName && ctx.position && Array.isArray(ctx.position)) {{
                return ctx.position.slice();
            }}
            // Para outros objetos, retornamos um vetor neutro
            return [0, 0, 0];
        }},
        set position(v) {{
            __bgeQueueForObject("setPosition", objName, {{
                value: Array.from(v || [0, 0, 0])
            }});
        }},
        applyMovement(vec) {{
            __bgeQueueForObject("applyMovement", objName, {{
                vec: Array.from(vec || [0, 0, 0])
            }});
        }},
        getProperty(propName) {{
            const props = (ctx.properties && ctx.object_name === objName) ? ctx.properties : null;
            if (props && Object.prototype.hasOwnProperty.call(props, propName)) {{
                return props[propName];
            }}
            return null;
        }},
        setProperty(propName, value) {{
            __bgeQueueForObject("setProperty", objName, {{
                property: String(propName),
                value: value
            }});
        }},
        getParent() {{
            // Não resolvemos hierarquia completa ainda; retornar null é seguro.
            return null;
        }},
        setParent(parent) {{
            const parentName = parent && parent.name ? parent.name : null;
            __bgeQueueForObject("setParent", objName, {{
                parent: parentName
            }});
        }},
        getChildren() {{
            // Poderíamos expor via contexto no futuro; por enquanto, retornar lista vazia.
            return [];
        }},
    }};
}}

function __bgeMakeScene(name) {{
    const ctx = __BGE_CONTEXT__ || {{}};
    const sceneName = name || ctx.scene_name || "";
    return {{
        name: sceneName,
        active: true,
        objects: [],
        getObject(objName) {{
            return __bgeMakeGameObject(objName);
        }},
        addObject(object) {{
            // Poderemos futuramente enfileirar um comando específico.
        }},
        removeObject(object) {{
            // Idem acima - ainda não implementado.
        }},
    }};
}}

const bge = {{
    logic: {{
        getCurrentScene() {{
            return __bgeMakeScene();
        }},
        getSceneList() {{
            // No momento só trabalhamos com a cena atual.
            return [__bgeMakeScene()];
        }},
        getScene(name) {{
            return __bgeMakeScene(name);
        }},
        getCurrentController() {{
            const ctx = __BGE_CONTEXT__ || {{}};
            return {{
                name: ctx.controller_name || "",
                type: "PYTHON",
                active: true,
                owner: __bgeMakeGameObject()
            }};
        }},
        getCurrentObject() {{
            return __bgeMakeGameObject();
        }},
        // As funções de input ainda não estão conectadas ao engine real;
        // expomos stubs baseados em contexto para expansão futura.
        getKeyboardInput() {{
            const kb = (__BGE_CONTEXT__ && __BGE_CONTEXT__.keyboard) || {{}};
            return {{
                isPressed(key) {{
                    return Array.isArray(kb.pressed) ? kb.pressed.includes(key) : false;
                }},
                isJustPressed(key) {{
                    return Array.isArray(kb.justPressed) ? kb.justPressed.includes(key) : false;
                }},
                isJustReleased(key) {{
                    return Array.isArray(kb.justReleased) ? kb.justReleased.includes(key) : false;
                }},
            }};
        }},
        getMouseInput() {{
            const m = (__BGE_CONTEXT__ && __BGE_CONTEXT__.mouse) || {{}};
            return {{
                getPosition() {{
                    return Array.isArray(m.position) ? m.position.slice() : [0, 0];
                }},
                isPressed(button) {{
                    return Array.isArray(m.pressed) ? m.pressed.includes(button) : false;
                }},
                isJustPressed(button) {{
                    return Array.isArray(m.justPressed) ? m.justPressed.includes(button) : false;
                }},
                isJustReleased(button) {{
                    return Array.isArray(m.justReleased) ? m.justReleased.includes(button) : false;
                }},
                getWheelDelta() {{
                    return typeof m.wheelDelta === "number" ? m.wheelDelta : 0;
                }},
            }};
        }},
        getJoystickInput() {{
            const j = (__BGE_CONTEXT__ && __BGE_CONTEXT__.joystick) || {{}};
            return {{
                getJoystickCount() {{
                    return typeof j.count === "number" ? j.count : 0;
                }},
                isPressed(joystick, button) {{
                    const pressed = j.buttonsPressed || {{}};
                    const list = pressed[String(joystick)] || [];
                    return Array.isArray(list) ? list.includes(button) : false;
                }},
                getAxis(joystick, axis) {{
                    const axes = j.axes || {{}};
                    const list = axes[String(joystick)] || [];
                    if (!Array.isArray(list)) return 0;
                    return typeof list[axis] === "number" ? list[axis] : 0;
                }},
            }};
        }},
        getGameEngine() {{
            const e = (__BGE_CONTEXT__ && __BGE_CONTEXT__.engine) || {{}};
            return {{
                getFrameRate() {{
                    return typeof e.frame_rate === "number" ? e.frame_rate : 0;
                }},
                getCurrentFrame() {{
                    return typeof e.current_frame === "number" ? e.current_frame : 0;
                }},
                getTimeSinceStart() {{
                    return typeof e.time_since_start === "number" ? e.time_since_start : 0;
                }},
                endGame() {{
                    __bgeQueue({{ op: "endGame" }});
                }},
                restartGame() {{
                    __bgeQueue({{ op: "restartGame" }});
                }},
            }};
        }},
    }},
    types: {{
        Vector3(x, y, z) {{
            return {{
                x: x,
                y: y,
                z: z,
                add(other) {{
                    return bge.types.Vector3(x + other.x, y + other.y, z + other.z);
                }},
                subtract(other) {{
                    return bge.types.Vector3(x - other.x, y - other.y, z - other.z);
                }},
                multiply(scalar) {{
                    return bge.types.Vector3(x * scalar, y * scalar, z * scalar);
                }},
                length() {{
                    return Math.sqrt(x * x + y * y + z * z);
                }},
                normalize() {{
                    const len = this.length();
                    if (len === 0) return bge.types.Vector3(0, 0, 0);
                    return bge.types.Vector3(x / len, y / len, z / len);
                }},
            }};
        }},
    }},
}};
global.bge = bge;

// Execute user code in an IIFE to avoid leaking globals
(function() {{
    try {{
        (function() {{
            {user_code}
        }})();
    }} catch (e) {{
        console.error(e.toString());
        if (e.stack) {{
            console.error(e.stack);
        }}
        process.exit(1);
    }}
}})();

// After user code finishes, emit the queued commands as a single line
try {{
    // Marker used by the Python side to extract commands
    console.log("___BGE_CMDS___" + JSON.stringify(__bgeCommands));
}} catch (e) {{
    console.error("Failed to serialize BGE commands: " + e.toString());
}}
"""

            result = subprocess.run(
                [node_path, "-e", wrapped_code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            output = result.stdout
            error_output = result.stderr

            if result.returncode != 0:
                if not error_output:
                    error_output = output
                return (output, error_output, False)

            return (output, error_output, True)

        except FileNotFoundError:
            return ("", "Error: Node.js not found. Please install Node.js or configure SDK path.", False)
        except subprocess.TimeoutExpired:
            return ("", "Error: JavaScript execution timed out.", False)
        except Exception as e:
            return ("", f"Error executing JavaScript with context: {str(e)}", False)
    def execute_file(self, filepath, timeout=30):
        """
        Execute a JavaScript file using Node.js.
        Returns (output, error_output, success)
        """
        node_path = self.get_node_path()
        if not node_path:
            return ("", "Error: Node.js not found. Please install Node.js or configure SDK path.", False)
        
        if not os.path.exists(filepath):
            return ("", f"Error: File not found: {filepath}", False)
        
        try:
            result = subprocess.run(
                [node_path, filepath],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            output = result.stdout
            error_output = result.stderr
            
            if result.returncode != 0:
                if not error_output:
                    error_output = output
                return (output, error_output, False)
            
            return (output, error_output, True)
            
        except FileNotFoundError:
            return ("", "Error: Node.js not found. Please install Node.js or configure SDK path.", False)
        except subprocess.TimeoutExpired:
            return ("", "Error: JavaScript execution timed out.", False)
        except Exception as e:
            return ("", f"Error executing JavaScript file: {str(e)}", False)
