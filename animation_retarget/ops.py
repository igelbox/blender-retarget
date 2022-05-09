import bpy

from .core import auto_mapping, mapping_to_text, text_to_mapping, clear_mapping
from .core import trick_blender28, need_to_trick_blender28


class OBJECT_OT_AutoMapping(bpy.types.Operator):
    bl_idname = "animation_retarget.auto_mapping"
    bl_label = "Auto Mapping"
    bl_description = "Map bones automatically"

    def execute(self, context):
        target_obj = context.active_object
        source_obj = bpy.data.objects[target_obj.animation_retarget.source]
        auto_mapping(source_obj, target_obj)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        target_obj = context.active_object
        if (not target_obj) or (target_obj.type not in {'ARMATURE'}):
            return False
        if not target_obj.animation_retarget.source:
            return False
        return True


class OBJECT_OT_CopyMapping(bpy.types.Operator):
    bl_idname = "animation_retarget.copy_mapping"
    bl_label = "Copy Mapping"
    bl_description = "Copy the current mapping to the clipboard"

    def execute(self, context):
        target_obj = context.active_object
        bpy.context.window_manager.clipboard = mapping_to_text(target_obj)
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
        text_to_mapping(bpy.context.window_manager.clipboard, target_obj)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        target_obj = context.active_object
        if (not target_obj) or (target_obj.type not in {'ARMATURE'}):
            return False
        if not bpy.context.window_manager.clipboard:
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

class OBJECT_OT_TrickBlender(bpy.types.Operator):
    bl_idname = "animation_retarget.trick_blender"
    bl_label = "Fix Refreshing"
    bl_description = "Trick Blender 2.8x 'depsgraph' to force driver variables refresh each frame"

    def execute(self, context):
        target_obj = context.active_object
        trick_blender28(target_obj)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        target_obj = context.active_object
        if (not target_obj) or (target_obj.type not in {'ARMATURE'}):
            return False

        if not target_obj.animation_retarget.source:
            return False  # No worries, we fix this on source prop update

        return need_to_trick_blender28(target_obj)


__CLASSES__ = (
    OBJECT_OT_AutoMapping,
    OBJECT_OT_CopyMapping,
    OBJECT_OT_PasteMapping,
    OBJECT_OT_ClearMapping,
    OBJECT_OT_TrickBlender,
)

def register():
    for clas in __CLASSES__:
        bpy.utils.register_class(clas)
def unregister():
    for clas in reversed(__CLASSES__):
        bpy.utils.unregister_class(clas)
