# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""UI panels and operators for JavaScript controllers in Logic Editor."""

import bpy
from bpy.types import Panel, Operator
from bpy.props import IntProperty, StringProperty


class LOGIC_OT_add_javascript_controller(Operator):
    """Add a JavaScript controller (uses Python controller internally)"""
    bl_idname = "logic.controller_add_javascript"
    bl_label = "Add JavaScript Controller"
    bl_description = "Add a JavaScript controller. Assign a .js file to it."
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        ob = context.active_object
        if not ob or not ob.game:
            self.report({'ERROR'}, "No active object with game properties")
            return {'CANCELLED'}
        
        # Add a Python controller (we'll intercept execution for .js files)
        bpy.ops.logic.controller_add(type='PYTHON')
        
        # Find the newly added controller
        game = ob.game
        if game.controllers:
            controller = game.controllers[-1]
            # Set name to indicate this is a JS controller
            controller.name = "JavaScript Controller"
            
            self.report({'INFO'}, "JavaScript controller added. Assign a .js file to it.")
        
        return {'FINISHED'}


class LOGIC_OT_setup_js_ts_controller(Operator):
    """Setup a controller to use JavaScript execution"""
    bl_idname = "logic.setup_js_ts_controller"
    bl_label = "Setup JS/TS Controller"
    bl_description = "Configure controller to execute JavaScript via wrapper"
    bl_options = {'REGISTER', 'UNDO'}
    
    controller_index: bpy.props.IntProperty(name="Controller Index", default=-1)
    
    def execute(self, context):
        import python_wrapper
        assign_wrapper_to_controller = python_wrapper.assign_wrapper_to_controller
        
        ob = context.active_object
        if not ob or not ob.game:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        game = ob.game
        if self.controller_index < 0 or self.controller_index >= len(game.controllers):
            self.report({'ERROR'}, "Invalid controller index")
            return {'CANCELLED'}
        
        controller = game.controllers[self.controller_index]
        
        if assign_wrapper_to_controller(controller):
            self.report({'INFO'}, "Controller configured for JavaScript execution")
        else:
            self.report({'WARNING'}, "Controller setup failed or not needed")
        
        return {'FINISHED'}


class LOGIC_OT_load_js_ts_from_file(Operator):
    """Assign a JavaScript script file from disk to this controller"""

    bl_idname = "logic.load_js_ts_from_file"
    bl_label = "Load JS From File"
    bl_description = "Load a .js/.mjs file from disk and assign it to this controller"
    bl_options = {'REGISTER', 'UNDO'}

    controller_name: StringProperty(name="Controller Name")
    filter_glob: StringProperty(
        default="*.js;*.mjs",
        options={'HIDDEN'},
    )
    filepath: StringProperty(
        name="File Path",
        subtype="FILE_PATH",
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        import os

        ob = context.active_object
        if not ob or not ob.game:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        if not self.filepath:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}

        game = ob.game
        idx = game.controllers.find(self.controller_name)
        if idx == -1:
            self.report({'ERROR'}, f"Controller '{self.controller_name}' not found")
            return {'CANCELLED'}

        controller = game.controllers[idx]

        # Read file contents
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                contents = f.read()
        except Exception as e:
            self.report({'ERROR'}, f"Failed to read file: {e}")
            return {'CANCELLED'}

        # Create or reuse a Text datablock with the file name
        basename = os.path.basename(self.filepath)
        text = bpy.data.texts.get(basename)
        if text is None:
            text = bpy.data.texts.new(basename)

        text.clear()
        text.write(contents)
        text.filepath = self.filepath

        controller.text = text
        self.report({'INFO'}, f"Assigned {basename} to controller '{controller.name}'")
        return {'FINISHED'}


class LOGIC_PT_javascript_controllers(Panel):
    """Panel for JavaScript controllers in Logic Editor"""
    bl_space_type = 'LOGIC_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Logic"
    bl_label = "JavaScript"
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob and ob.game
    
    def draw(self, context):
        layout = self.layout
        ob = context.active_object
        game = ob.game

        # External editor integration
        box = layout.box()
        box.label(text="External Editor", icon='URL')
        row = box.row()
        row.operator("sdk.open_in_editor", icon='FILE_FOLDER', text="Open SDK/Project in Editor")
        
        # Add controller buttons
        box = layout.box()
        box.label(text="Add Controllers:", icon='ADD')
        row = box.row()
        row.scale_y = 1.5
        row.operator("logic.controller_add_javascript", icon='SCRIPT', text="JavaScript")
        
        # List controllers (we always show Python controllers so user can attach files)
        js_controllers = []
        for controller in game.controllers:
            if controller.type == 'PYTHON':
                text_name = controller.text.name if getattr(controller, "text", None) else ""
                js_controllers.append((controller, text_name))
        
        if js_controllers:
            layout.separator()
            box = layout.box()
            box.label(text="Active Controllers:", icon='SCRIPT')
            
            for controller, text_name in js_controllers:
                row = box.row()
                row.label(text=f"{controller.name}", icon='SCRIPT')
                
                # Show script file
                # Show script info and button to load from file
                row = box.row()
                if controller.text and controller.text.filepath:
                    row.label(text=f"File: {bpy.path.basename(controller.text.filepath)}")
                elif controller.text:
                    row.label(text=f"Text: {controller.text.name}")
                else:
                    row.label(text="No script assigned")
                op_load = row.operator("logic.load_js_ts_from_file", text="Load JS File", icon='FILEBROWSER')
                op_load.controller_name = controller.name
                
                # Show file type indicator (only for JS files)
                if text_name.endswith(('.js', '.mjs')):
                    row = box.row()
                    row.label(text="JavaScript file", icon='INFO')
                    # Check if wrapper is already assigned
                    wrapper_name = f"__js_ts_wrapper_{text_name.replace('.', '_').replace('-', '_')}__"
                    if controller.text.name == wrapper_name or controller.text.name.startswith("__js_ts_wrapper_"):
                        row = box.row()
                        row.label(text="✓ Configured for JavaScript execution", icon='CHECKMARK')
                    else:
                        row = box.row()
                        op = row.operator("logic.setup_js_ts_controller", text="Setup for JavaScript")
                        op.controller_index = game.controllers.find(controller.name)
                
                box.separator()
        
        else:
            layout.separator()
            box = layout.box()
            box.label(text="No Python controllers on active object", icon='INFO')
            box.label(text="Add controllers above first")


classes = (
    LOGIC_OT_add_javascript_controller,
    LOGIC_OT_setup_js_ts_controller,
    LOGIC_OT_load_js_ts_from_file,
    LOGIC_PT_javascript_controllers,
)


def register():
    """Register UI classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    print("UPBGE JavaScript SDK: Logic Editor UI registered")


def unregister():
    """Unregister UI classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
