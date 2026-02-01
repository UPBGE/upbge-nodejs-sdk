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

# Set to False to disable Node runtime flow logs
DEBUG_NODE_LOGS = True


def _node_log(msg):
    if DEBUG_NODE_LOGS:
        print("[UPBGE-JS] " + msg)


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
    
    def __init__(self, use_worker=False):
        self.node_path = get_node_path()
        self._interactive_context = {}  # Store for interactive console context
        self._use_worker = use_worker
        self._worker_process = None
        self._worker_stdin = None
        self._worker_stdout = None
        self._worker_exec_id = 0
        self._worker_bootstrap = r"""
(function(){
  const readline = require('readline');
  const rl = readline.createInterface({ input: process.stdin });
  rl.on('line', function(line) {
    try {
      const msg = JSON.parse(line);
      const id = msg.id || '';
      eval(msg.code);
      console.log('___BGE_CMDS___' + id + '\t' + JSON.stringify(typeof __bgeCommands !== 'undefined' ? __bgeCommands : []));
    } catch (e) {
      console.error(e.message || e);
      console.log('___BGE_CMDS___' + id + '\t[]');
    }
  });
})();
"""
    
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

    def _ensure_worker(self):
        """Start persistent Node worker if not running."""
        if self._worker_process is not None and self._worker_process.poll() is None:
            return True
        node_path = self.get_node_path()
        if not node_path:
            return False
        try:
            self._worker_process = subprocess.Popen(
                [node_path, "-e", self._worker_bootstrap],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            self._worker_stdin = self._worker_process.stdin
            self._worker_stdout = self._worker_process.stdout
            return True
        except Exception:
            self._worker_process = None
            self._worker_stdin = None
            self._worker_stdout = None
            return False

    def _worker_execute(self, wrapped_code, timeout=10):
        """Send code to worker and read response. Returns (output, error_output, success)."""
        if not self._ensure_worker():
            return ("", "Worker failed to start", False)
        self._worker_exec_id += 1
        req_id = str(self._worker_exec_id)
        try:
            import json as _json
            msg = {"id": req_id, "code": wrapped_code}
            line = _json.dumps(msg) + "\n"
            self._worker_stdin.write(line)
            self._worker_stdin.flush()
        except Exception as e:
            self._worker_process = None
            return ("", str(e), False)
        marker = "___BGE_CMDS___"
        output_lines = []
        end_time = __import__("time").time() + timeout
        while __import__("time").time() < end_time:
            try:
                line_out = self._worker_stdout.readline()
            except Exception:
                break
            if not line_out:
                break
            output_lines.append(line_out)
            if marker in line_out and (marker + req_id) in line_out:
                break
        output = "".join(output_lines)
        return (output, "", True)

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
        _node_log("Node execute_with_context code_len=%s node_path=%s" % (len(code or ""), node_path or "NOT FOUND"))
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
            const objPositions = ctx.object_positions || {{}};
            if (objPositions[objName] && Array.isArray(objPositions[objName])) {{
                return objPositions[objName].slice();
            }}
            if (ctx.object_name === objName && ctx.position && Array.isArray(ctx.position)) {{
                return ctx.position.slice();
            }}
            return [0, 0, 0];
        }},
        set position(v) {{
            __bgeQueueForObject("setPosition", objName, {{
                value: Array.from(v || [0, 0, 0])
            }});
        }},
        get rotation() {{
            if (ctx.object_name === objName && ctx.rotation && Array.isArray(ctx.rotation)) {{
                return ctx.rotation.slice();
            }}
            return [0, 0, 0];
        }},
        set rotation(v) {{
            __bgeQueueForObject("setRotation", objName, {{
                value: Array.from(v || [0, 0, 0])
            }});
        }},
        get scale() {{
            if (ctx.object_name === objName && ctx.scale && Array.isArray(ctx.scale)) {{
                return ctx.scale.slice();
            }}
            return [1, 1, 1];
        }},
        set scale(v) {{
            __bgeQueueForObject("setScale", objName, {{
                value: Array.from(v || [1, 1, 1])
            }});
        }},
        set localPosition(v) {{
            __bgeQueueForObject("setLocalPosition", objName, {{
                value: Array.from(v || [0, 0, 0])
            }});
        }},
        set localRotation(v) {{
            __bgeQueueForObject("setLocalRotation", objName, {{
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
            if (ctx.object_name === objName && ctx.parent_name) {{
                return __bgeMakeGameObject(ctx.parent_name);
            }}
            return null;
        }},
        setParent(parent) {{
            const parentName = parent && parent.name ? parent.name : null;
            __bgeQueueForObject("setParent", objName, {{
                parent: parentName
            }});
        }},
        getChildren() {{
            if (ctx.object_name === objName && Array.isArray(ctx.children)) {{
                return ctx.children.map(function(n) {{ return __bgeMakeGameObject(n); }});
            }}
            return [];
        }},
        lookAt(target) {{
            const targetName = target && target.name ? target.name : null;
            if (targetName) __bgeQueue({{ op: "lookAt", object: objName, target: targetName }});
        }},
    }};
}}

function __bgeMakeScene(sceneNameOrData) {{
    const ctx = __BGE_CONTEXT__ || {{}};
    let sceneName = "";
    let objectNames = [];
    if (typeof sceneNameOrData === "string") {{
        sceneName = sceneNameOrData;
        const scenes = ctx.scenes || [];
        for (let i = 0; i < scenes.length; i++) {{
            if (scenes[i].name === sceneName) {{
                objectNames = Array.isArray(scenes[i].objects) ? scenes[i].objects.slice() : [];
                break;
            }}
        }}
    }} else if (sceneNameOrData && sceneNameOrData.name) {{
        sceneName = sceneNameOrData.name;
        objectNames = Array.isArray(sceneNameOrData.objects) ? sceneNameOrData.objects.slice() : [];
    }} else {{
        sceneName = ctx.scene_name || "";
        const scenes = ctx.scenes || [];
        for (let i = 0; i < scenes.length; i++) {{
            if (scenes[i].name === sceneName) {{
                objectNames = Array.isArray(scenes[i].objects) ? scenes[i].objects.slice() : [];
                break;
            }}
        }}
    }}
    const objList = objectNames.map(function(n) {{ return __bgeMakeGameObject(n); }});
    return {{
        name: sceneName,
        active: true,
        get objects() {{ return objList; }},
        getObject(objName) {{
            return __bgeMakeGameObject(objName);
        }},
        addObject(object) {{
            const oname = object && object.name ? object.name : null;
            if (oname) __bgeQueue({{ op: "sceneAddObject", scene: sceneName, object: oname }});
        }},
        removeObject(object) {{
            const oname = object && object.name ? object.name : null;
            if (oname) __bgeQueue({{ op: "sceneRemoveObject", scene: sceneName, object: oname }});
        }},
    }};
}}

const bge = {{
    logic: {{
        getCurrentScene() {{
            return __bgeMakeScene();
        }},
        getSceneList() {{
            const scenes = (__BGE_CONTEXT__ && __BGE_CONTEXT__.scenes) || [];
            return scenes.map(function(s) {{ return __bgeMakeScene(s); }});
        }},
        getScene(name) {{
            if (!name) return __bgeMakeScene();
            return __bgeMakeScene(name);
        }},
        getCurrentController() {{
            const ctx = __BGE_CONTEXT__ || {{}};
            const sensors = ctx.sensors || {{}};
            return {{
                name: ctx.controller_name || "",
                type: "PYTHON",
                active: true,
                owner: __bgeMakeGameObject(),
                get sensors() {{
                    return sensors;
                }}
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
    // Blender/UPBGE use GHOST key codes (sensor.inputs); A=23 confirmed, others guessed
    events: {{
        AKEY: 23,
        DKEY: 26,
        WKEY: 45,
        SKEY: 41,
        UPARROWKEY: 82,
        DOWNARROWKEY: 84,
        LEFTARROWKEY: 80,
        RIGHTARROWKEY: 79,
        SPACEKEY: 32,
        ACTIVE: 1,
        JUST_ACTIVATED: 2,
        JUST_RELEASED: 3,
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

// DEBUG: log context before user code runs
(function() {{
    var _ctx = __BGE_CONTEXT__ || {{}};
    var _sens = _ctx.sensors || {{}};
    var _kb = _sens.Keyboard;
    var _evLen = (_kb && _kb.events && Array.isArray(_kb.events)) ? _kb.events.length : 'n/a';
    console.log("[UPBGE-JS] DEBUG ctx.Keyboard.events.length=" + _evLen);
    if (_kb && _kb.events && _kb.events.length > 0) {{
        console.log("[UPBGE-JS] DEBUG first event key=" + _kb.events[0][0] + " status=" + _kb.events[0][1]);
    }}
}})();

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

// DEBUG: log commands count before sending
console.log("[UPBGE-JS] DEBUG __bgeCommands.length=" + (typeof __bgeCommands !== 'undefined' ? __bgeCommands.length : 'undefined'));

// After user code finishes, emit the queued commands as a single line
try {{
    // Marker used by the Python side to extract commands
    console.log("___BGE_CMDS___" + JSON.stringify(__bgeCommands));
}} catch (e) {{
    console.error("Failed to serialize BGE commands: " + e.toString());
}}
"""

            if self._use_worker:
                output, error_output, success = self._worker_execute(wrapped_code, timeout=timeout)
                _node_log("Node worker done success=%s output_len=%s has_marker=%s" % (
                    success, len(output or ""), "___BGE_CMDS___" in (output or "")))
                return (output, error_output, success)

            result = subprocess.run(
                [node_path, "-e", wrapped_code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            output = result.stdout
            error_output = result.stderr
            _node_log("Node subprocess done returncode=%s output_len=%s has_marker=%s" % (
                result.returncode, len(output or ""), "___BGE_CMDS___" in (output or "")))

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
