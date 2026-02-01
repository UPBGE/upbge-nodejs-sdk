# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""SDK operators for installation and management."""

import os
import sys
import bpy
import subprocess
from bpy.types import Operator


class SDK_INSTALL_OT_operator(Operator):
    """Install UPBGE JavaScript SDK"""
    bl_idname = "sdk.install"
    bl_label = "Install SDK"
    bl_description = "Download and install the UPBGE JavaScript SDK"
    
    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons["upbge_nodejs_sdk"].preferences
        
        sdk_path = addon_prefs.sdk_path
        if sdk_path == "":
            self.report({'ERROR'}, "Please set SDK path in preferences first")
            return {'CANCELLED'}
        
        # For now, just create the directory structure
        # In the future, this would download from GitHub releases
        try:
            os.makedirs(sdk_path, exist_ok=True)
            os.makedirs(os.path.join(sdk_path, "python"), exist_ok=True)
            os.makedirs(os.path.join(sdk_path, "runtime"), exist_ok=True)
            os.makedirs(os.path.join(sdk_path, "lib"), exist_ok=True)
            os.makedirs(os.path.join(sdk_path, "types"), exist_ok=True)
            
            self.report({'INFO'}, f"SDK directory structure created at {sdk_path}")
            self.report({'INFO'}, "Note: Node.js need to be added manually")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create SDK directory: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class SDK_UPDATE_OT_operator(Operator):
    """Update UPBGE JavaScript SDK"""
    bl_idname = "sdk.update"
    bl_label = "Update SDK"
    bl_description = "Update to the latest SDK version"
    
    def execute(self, context):
        # For now, just report that update is not implemented
        # In the future, this would download latest from GitHub
        self.report({'INFO'}, "SDK update not yet implemented. Manual update required.")
        return {'FINISHED'}


class SDK_RESTORE_OT_operator(Operator):
    """Restore stable SDK version"""
    bl_idname = "sdk.restore"
    bl_label = "Restore Stable Version"
    bl_description = "Restore the stable SDK version"
    
    def execute(self, context):
        # For now, just report that restore is not implemented
        self.report({'INFO'}, "SDK restore not yet implemented.")
        return {'FINISHED'}


class SDK_OPEN_IN_EDITOR_OT_operator(Operator):
    """Open SDK or current project in external editor"""

    bl_idname = "sdk.open_in_editor"
    bl_label = "Open in External Editor"
    bl_description = "Open a JS script (or the SDK/project folder) in the configured external editor"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        """Just forward to execute. We decide the best target automatically."""
        return self.execute(context)

    def execute(self, context):
        prefs = context.preferences
        try:
            addon_prefs = prefs.addons["upbge_nodejs_sdk"].preferences
        except KeyError:
            self.report({'ERROR'}, "UPBGE Node.js SDK preferences not found")
            return {'CANCELLED'}

        editor_bin = getattr(addon_prefs, "code_editor_bin", "")
        if not editor_bin:
            self.report({'ERROR'}, "Configure the external editor executable in the add-on preferences first")
            return {'CANCELLED'}

        target_path = ""

        # 1) Prefer the script attached to the currently selected controller (if any)
        controller = getattr(context, "controller", None)
        if controller and controller.type == 'PYTHON':
            text = getattr(controller, "text", None)
            if text and text.filepath:
                target_path = bpy.path.abspath(text.filepath)

        # 2) If no active-controller script, pick the first JS script on the active object
        if not target_path:
            ob = context.active_object
            if ob and getattr(ob, "game", None):
                game = ob.game
                for ctrl in game.controllers:
                    if ctrl.type != 'PYTHON':
                        continue
                    text = getattr(ctrl, "text", None)
                    if text and text.filepath:
                        target_path = bpy.path.abspath(text.filepath)
                        break

        # 3) If still no target, resolve a sensible project/SDK directory
        if not target_path:
            # Prefer SDK path, else .blend directory, else addon directory
            target_dir = ""
            if getattr(addon_prefs, "sdk_path", ""):
                target_dir = addon_prefs.sdk_path
            if not target_dir or not os.path.isdir(target_dir):
                blend_path = bpy.data.filepath
                if blend_path:
                    target_dir = os.path.dirname(blend_path)
            if not target_dir or not os.path.isdir(target_dir):
                from pathlib import Path
                addon_dir = Path(__file__).resolve().parents[1]
                target_dir = str(addon_dir)

            target_path = target_dir

        try:
            cmd = [editor_bin, target_path]
            # When opening a file, cwd can still be the project/addon dir
            cwd = target_path if os.path.isdir(target_path) else os.path.dirname(target_path)
            subprocess.Popen(cmd, cwd=cwd or None)

        except FileNotFoundError as e:
            self.report({'ERROR'}, f"Failed to start external editor: {e}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error starting editor: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Opening in external editor: {target_path}")
        return {'FINISHED'}
