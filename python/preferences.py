# SPDX-FileCopyrightText: 2024 UPBGE Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""SDK preferences and settings."""

import os
import bpy
from bpy.props import *
from bpy.types import AddonPreferences


class SDKAddonPreferences(AddonPreferences):
    bl_idname = "upbge_nodejs_sdk"

    def sdk_path_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.sdk_path = bpy.path.reduce_dirs([bpy.path.abspath(self.sdk_path)])[0] + '/'
        # Restart SDK when path changes - import from main module
        # O nome do módulo é 'upbge_nodejs_sdk' quando instalado via ZIP
        try:
            import upbge_nodejs_sdk
            if hasattr(upbge_nodejs_sdk, 'restart_sdk'):
                upbge_nodejs_sdk.restart_sdk(context)
        except ImportError:
            # Durante desenvolvimento, o diretório pode ter nome diferente
            # Tentar encontrar o módulo do add-on através do sys.modules
            import sys
            import os
            addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            addon_dir_name = os.path.basename(addon_path).replace('-', '_').replace('.', '_')
            if addon_dir_name in sys.modules:
                module = sys.modules[addon_dir_name]
                if hasattr(module, 'restart_sdk'):
                    module.restart_sdk(context)
        except:
            pass

    skip_update: BoolProperty(name="", default=False)
    
    sdk_path: StringProperty(
        name="SDK Path",
        subtype="FILE_PATH",
        update=sdk_path_update,
        default="",
        description="Path to the add-on directory (where the SDK is installed). Should contain 'python/', 'runtime/', and 'types/' folders. Usually auto-detected when installed via ZIP."
    )

    # External editor integration
    code_editor: EnumProperty(
        name="External Editor",
        description="Editor externo para abrir projetos/scripts do SDK",
        items=[
            ('custom', "Custom", "Use a custom editor executable"),
        ],
        default='custom',
    )

    code_editor_bin: StringProperty(
        name="Editor Executable",
        subtype="FILE_PATH",
        default="",
        description="Path to external editor executable (only used when External Editor is set to Custom)",
    )

    nodejs_path: StringProperty(
        name="Node.js Path",
        subtype="FILE_PATH",
        default="",
        description="Path to Node.js executable (auto-detected from SDK)"
    )
    
    auto_update: BoolProperty(
        name="Auto Update SDK",
        default=False,
        description="Automatically update SDK when new version is available"
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="UPBGE JavaScript SDK")
        
        layout.prop(self, "sdk_path")
        
        if self.sdk_path:
            sdk_exists = os.path.exists(self.sdk_path)
            if not sdk_exists:
                layout.label(text="SDK path does not exist. Please install the SDK.", icon='ERROR')
            else:
                # Validate SDK structure
                has_python = os.path.exists(os.path.join(self.sdk_path, "python"))
                has_runtime = os.path.exists(os.path.join(self.sdk_path, "runtime"))
                
                if has_python and has_runtime:
                    layout.label(text="SDK found", icon='CHECKMARK')
                else:
                    layout.label(text="SDK path exists but missing required folders (python/, runtime/)", icon='ERROR')
                    layout.label(text="This should point to the add-on directory, not the UPBGE directory.")
        
        layout.separator()
        
        box = layout.box()
        box.label(text="External Editor")
        box.prop(self, "code_editor")
        if self.code_editor == 'custom':
            box.prop(self, "code_editor_bin")

        box = layout.box()
        box.label(text="Advanced Settings")
        box.prop(self, "auto_update")
        
        if self.nodejs_path:
            box.label(text=f"Node.js: {self.nodejs_path}")
