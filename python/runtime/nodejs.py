# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Node.js runtime wrapper for executing JavaScript code."""

import sys
import os
import subprocess

try:
    import bpy
except ImportError:
    bpy = None

# Import centralized utilities
from utils.paths import get_sdk_root, get_node_executable
from utils.logging import debug as log_debug


def get_sdk_path():
    """Get the SDK path from preferences or auto-detect.

    Deprecated: Use get_sdk_root() from utils.paths instead.
    This function is kept for backward compatibility.
    """
    try:
        context = bpy.context if bpy else None
        return get_sdk_root(context=context)
    except Exception:
        return get_sdk_root()


def get_node_path():
    """Get the path to Node.js executable from the SDK.

    Deprecated: Use get_node_executable() from utils.paths instead.
    This function is kept for backward compatibility.
    """
    return get_node_executable()


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
        log_debug("Node execute_with_context code_len=%s node_path=%s" % (len(code or ""), node_path or "NOT FOUND"))
        if not node_path:
            return ("", "Error: Node.js not found. Please install Node.js or configure SDK path.", False)

        # Load BGE bridge code
        try:
            bridge_file = os.path.join(os.path.dirname(__file__), "bge_bridge.js")
            with open(bridge_file, "r", encoding="utf-8") as f:
                bridge_code = f.read()
        except Exception as e:
            return ("", f"Error loading BGE bridge: {str(e)}", False)

        # Prepare context JSON that will be injected into the JS runtime
        context = context or {}
        try:
            context_json = json.dumps(context)
        except Exception:
            context_json = "{}"

        try:
            # Replace placeholders in bridge code
            bridge_code = bridge_code.replace("__PLACEHOLDER_CONTEXT__", context_json)

            # Wrap user code in IIFE with proper error handling
            wrapped_user_code = f"""
// Execute user code in an IIFE to avoid leaking globals
(function() {{
    try {{
        (function() {{
            {code}
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

            # Combine bridge and user code
            wrapped_code = bridge_code + "\n" + wrapped_user_code

            if self._use_worker:
                output, error_output, success = self._worker_execute(wrapped_code, timeout=timeout)
                log_debug("Node worker done success=%s output_len=%s has_marker=%s" % (
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
            log_debug("Node subprocess done returncode=%s output_len=%s has_marker=%s" % (
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
