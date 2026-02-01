# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""JavaScript interactive console."""

__all__ = (
    "autocomplete",
    "banner",
    "execute",
    "language_id",
)

import sys
import os
import bpy
from runtime.nodejs import NodeJSRuntime

language_id = "javascript"

# Both prompts must be the same length
PROMPT = '>>> '
PROMPT_MULTI = '... '

# Global runtime instance
_runtime = None


def get_runtime():
    """Get or create Node.js runtime instance."""
    global _runtime
    if _runtime is None:
        _runtime = NodeJSRuntime()
    return _runtime


def add_scrollback(text, text_type):
    for line in text.split("\n"):
        bpy.ops.console.scrollback_append(
            text=line,
            type=text_type,
        )


def get_console(console_id):
    """
    Helper function for console operators.
    Each console gets its own context (stored code, variables, etc.)
    
    console_id can be any hashable type
    """
    consoles = getattr(get_console, "consoles", None)
    hash_next = hash(bpy.context.window_manager)

    if consoles is None:
        consoles = get_console.consoles = {}
        get_console.consoles_namespace_hash = hash_next
    else:
        # Check if clearing the namespace is needed to avoid a memory leak
        hash_prev = getattr(get_console, "consoles_namespace_hash", 0)
        if hash_prev != hash_next:
            get_console.consoles_namespace_hash = hash_next
            consoles.clear()

    console_data = consoles.get(console_id)
    
    if console_data:
        # Return existing console data (accumulated code, etc.)
        return console_data
    else:
        # Create new console context
        # Store accumulated code and state
        console_state = {
            "accumulated_code": "",
            "is_multiline": False,
        }
        consoles[console_id] = console_state
        return console_state


def execute_javascript(code, is_multiline=False, context_id=None):
    """
    Execute JavaScript code using Node.js from SDK.
    Returns (output, error_output, success)
    """
    if is_multiline:
        # Just accumulate, don't execute yet
        return ("", "", True)
    
    runtime = get_runtime()
    # Use interactive mode to maintain context between executions
    if context_id is None:
        context_id = "default"
    return runtime.execute_interactive(code, context_id=context_id, timeout=5)


def execute(context, is_interactive):
    sc = context.space_data

    try:
        line_object = sc.history[-1]
    except:
        return {'CANCELLED'}

    console_state = get_console(hash(context.region))
    
    # Get the line to execute
    line = line_object.body
    
    # Check if this is a continuation (multiline)
    is_multiline = False
    
    # Simple multiline detection: check for unclosed brackets, braces, etc.
    if line.strip():
        # Accumulate code for multiline
        if console_state["accumulated_code"]:
            console_state["accumulated_code"] += "\n" + line
        else:
            console_state["accumulated_code"] = line
        
        # Check if line ends with certain characters that suggest continuation
        stripped = line.rstrip()
        if stripped.endswith(("{", "[", "(", ",", "&&", "||", "?", ":", "=", "+", "-", "*", "/", "%")):
            is_multiline = True
        elif stripped.endswith("\\"):
            is_multiline = True
        else:
            # Try to execute and see if it's valid
            is_multiline = False
        
        console_state["is_multiline"] = is_multiline
        
        if is_multiline:
            sc.prompt = PROMPT_MULTI
            # Insert a new blank line with indentation
            indent = line[:len(line) - len(line.lstrip())]
            if line.rstrip().endswith("{"):
                indent += "  "  # 2 spaces for JS
            bpy.ops.console.history_append(text=indent, current_character=0, remove_duplicates=True)
            sc.history[-1].current_character = len(indent)
            return {'FINISHED'}
    
    # Execute the accumulated code
    code_to_execute = console_state["accumulated_code"] if console_state["accumulated_code"] else line
    
    if not code_to_execute.strip():
        # Empty line - just execute newline
        sc.prompt = PROMPT
        bpy.ops.console.history_append(text="", current_character=0, remove_duplicates=True)
        return {'FINISHED'}
    
    # Use console region hash as context_id to maintain separate contexts per console
    context_id = f"js_console_{hash(context.region)}"
    
    # Execute JavaScript with interactive context
    output, error_output, success = execute_javascript(code_to_execute, is_multiline=False, context_id=context_id)
    
    # Clear accumulated code
    console_state["accumulated_code"] = ""
    console_state["is_multiline"] = False
    
    # Add input to scrollback
    bpy.ops.console.scrollback_append(text=sc.prompt + code_to_execute, type='INPUT')
    
    # Add output
    if output:
        add_scrollback(output, 'OUTPUT')
    if error_output:
        add_scrollback(error_output, 'ERROR')
    
    # Reset prompt
    sc.prompt = PROMPT
    
    # Insert a new blank line
    bpy.ops.console.history_append(text="", current_character=0, remove_duplicates=True)
    
    return {'FINISHED'}


def autocomplete(context):
    """
    Autocomplete for JavaScript console.
    For now, this is a placeholder - full implementation would require
    integration with language tooling if needed.
    """
    sc = context.space_data
    
    try:
        current_line = sc.history[-1]
        line = current_line.body
        cursor = current_line.current_character
        
        # Simple autocomplete: just return without changes for now
        # Full implementation would use a language server if needed
        # or analyze JavaScript AST
        
    except Exception as e:
        add_scrollback(f"Autocomplete error: {str(e)}", 'ERROR')
    
    context.area.tag_redraw()
    return {'FINISHED'}


def copy_as_script(context):
    sc = context.space_data
    lines = [
        "// JavaScript Console Script",
        "",
    ]

    for line in sc.scrollback:
        text = line.body
        type = line.type

        if type == 'INFO':  # Ignore auto-completion.
            continue
        if type == 'INPUT':
            if text.startswith(PROMPT):
                text = text[len(PROMPT):]
            elif text.startswith(PROMPT_MULTI):
                text = text[len(PROMPT_MULTI):]
        elif type == 'OUTPUT':
            text = "//~ " + text
        elif type == 'ERROR':
            text = "//! " + text

        lines.append(text)

    context.window_manager.clipboard = "\n".join(lines)

    return {'FINISHED'}


def banner(context):
    sc = context.space_data
    
    # Try to get Node.js version from SDK
    node_version = "Unknown"
    runtime = get_runtime()
    node_path = runtime.get_node_path()
    
    if node_path:
        try:
            import subprocess
            result = subprocess.run([node_path, "--version"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                node_version = result.stdout.strip()
        except:
            pass
    
    message = (
        f"JAVASCRIPT INTERACTIVE CONSOLE {node_version}",
        "",
        "Builtin Objects:        Object, Array, String, Number, Boolean, Date, Math, JSON, Promise, etc.",
        "Global Functions:       console.log(), console.error(), console.warn(), setTimeout(), setInterval(), etc.",
        "",
        "Note: This console uses Node.js from the UPBGE JavaScript SDK.",
    )
    
    if not node_path:
        message += (
            "",
            "Warning: Node.js not found. Please configure SDK path in add-on preferences.",
        )

    for line in message:
        add_scrollback(line, 'INFO')

    sc.prompt = PROMPT

    return {'FINISHED'}
