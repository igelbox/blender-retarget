import bpy

from .core import mapping_to_text, text_to_mapping, clear_mapping

WM = bpy.context.window_manager


class OBJECT_OT_CopyMapping(bpy.types.Operator):
    bl_idname = "animation_retarget.copy_mapping"
    bl_label = "Copy Mapping"
    bl_description = "Copy the current mapping to the clipboard"

    def execute(self, context):
        target_obj = context.active_object
        WM.clipboard = mapping_to_text(target_obj)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        target_obj = context.active_object
        if (not target_obj) or (target_obj.type not in {'ARMATURE'}):
            return False
        if not target_obj.animation_retarget.source:
            return False
        return True


class OBJECT_OT_PasteMapping(bpy.types.Operator):
    bl_idname = "animation_retarget.paste_mapping"
    bl_label = "Paste Mapping"
    bl_description = "Paste the current mapping from the clipboard"

    def execute(self, context):
        target_obj = context.active_object
        text_to_mapping(WM.clipboard, target_obj)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        target_obj = context.active_object
        if (not target_obj) or (target_obj.type not in {'ARMATURE'}):
            return False
        if not WM.clipboard:
            return False
        return True


class OBJECT_OT_ClearMapping(bpy.types.Operator):
    bl_idname = "animation_retarget.clear_mapping"
    bl_label = "Clear Mapping"
    bl_description = "Clear the current mapping"

    def execute(self, context):
        target_obj = context.active_object
        clear_mapping(target_obj)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        target_obj = context.active_object
        if (not target_obj) or (target_obj.type not in {'ARMATURE'}):
            return False
        return True


__CLASSES__ = (
    OBJECT_OT_CopyMapping,
    OBJECT_OT_PasteMapping,
    OBJECT_OT_ClearMapping,
)

def register():
    for clas in __CLASSES__:
        bpy.utils.register_class(clas)
def unregister():
    for clas in reversed(__CLASSES__):
        bpy.utils.unregister_class(clas)
