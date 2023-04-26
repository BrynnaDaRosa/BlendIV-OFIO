bl_info = {
    "name": "GTA IV Animation Importer",
    "version": (1, 0, 0),
    "blender": (2, 90, 0),
    "location": "File > Import",
    "description": "Buggy WIP Importer GTA IV .oad/.onim animation files.",
    "category": "Import",
}

import bpy

from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


class ImportGTA4Anim(bpy.types.Operator, ImportHelper):
    """Load a GTA IV animation"""
    bl_idname = "import_model.gta4_anim"
    bl_label = "Import GTA IV Anim"
    bl_options = {'PRESET', 'UNDO'}

    filter_glob: StringProperty(
        default="*.oad;*.onim",
        options={'HIDDEN'},
    )

    def execute(self, context):
        from .oad_import import import_oad
        from .onim_import import import_onim

        arma_ob = bpy.context.active_object
        if not arma_ob or arma_ob.type != 'ARMATURE':
            self.report({'ERROR'}, "Select armature object first!")
            return {'CANCELLED'}

        if self.filepath.lower().endswith(".oad"):
            import_oad(self.filepath, arma_ob)
        elif self.filepath.lower().endswith(".onim"):
            import_onim(self.filepath, arma_ob)
        else:
            self.report({'ERROR'}, "Unknown file type: %s" % self.filepath)

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportGTA4Anim.bl_idname, text="GTA IV Anim (.oad/.onim)")


def register():
    bpy.utils.register_class(ImportGTA4Anim)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ImportGTA4Anim)
