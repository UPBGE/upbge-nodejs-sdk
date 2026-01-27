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
            os.path.exists(os.path.join(addon_path, "runtime")) and
            os.path.exists(os.path.join(addon_path, "lib"))
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


def get_tsc_path():
    """Get the path to TypeScript compiler from the SDK."""
    sdk_path = get_sdk_path()
    if not sdk_path:
        return None
    
    os_type = platform.system()
    
    if os_type == "Windows":
        tsc_path = os.path.join(sdk_path, "lib", "typescript", "tsc.exe")
    else:
        tsc_path = os.path.join(sdk_path, "lib", "typescript", "tsc")
    
    if os.path.exists(tsc_path):
        return tsc_path
    
    # Fallback: try system tsc
    if os_type == "Windows":
        possible_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "nodejs", "tsc.cmd"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "nodejs", "tsc.cmd"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "nodejs", "tsc.cmd"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    else:
        # Try system PATH
        try:
            result = subprocess.run(["which", "tsc"], capture_output=True, text=True, timeout=1)
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
