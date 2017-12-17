import bpy
class AbstractBasePanel(bpy.types.Panel):
    bl_label = 'Animation Retargeting'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    def draw_header(self, _context):
        self.layout.label(icon='PLUGIN')

class ObjectPanel(AbstractBasePanel):
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and (obj.type == 'ARMATURE')

    def draw(self, context):
        layout = self.layout
        data = context.object.animation_retarget

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('animation_retarget.copy_mapping', icon='COPYDOWN', text='Copy')
        row.operator('animation_retarget.paste_mapping', icon='PASTEDOWN', text='Paste')
        row.operator('animation_retarget.clear_mapping', icon='X', text='Clear')

        layout.prop_search(data, 'source', bpy.data, 'objects')

        source = bpy.data.objects.get(data.source)
        if source:
            col = layout.column(align=True)
            for bone in context.object.pose.bones:
                row = col.row(align=True)
                row.label(bone.name)
                bone_data = bone.animation_retarget
                row.prop_search(bone_data, 'source', source.pose, 'bones', text='')
                alert = PoseBonePanel.draw_buttons(row, source, bone_data, hide_texts=True)
                row.active = alert or bool(bone.animation_retarget.source)


class PoseBonePanel(AbstractBasePanel):
    bl_context = 'bone'

    @classmethod
    def poll(cls, context):
        return (
            ObjectPanel.poll(context)
            and context.active_pose_bone
        )

    def draw(self, context):
        layout = self.layout
        data = context.active_pose_bone.animation_retarget

        source_object = bpy.data.objects.get(context.active_object.animation_retarget.source)
        if not source_object:
            layout.label('Select the source object on the Object Properties panel', icon='INFO')
            return

        layout.prop_search(data, 'source', source_object.pose, 'bones')
        row = layout.row(align=True)
        PoseBonePanel.draw_buttons(row, source_object, data)

    @classmethod
    def draw_buttons(cls, layout, source_object, data, hide_texts=False):
        no_source = source_object.pose.bones.get(data.source) is None

        def modified_layout(layout, use_flag):
            if no_source:
                layout = layout.split(align=True)
                if use_flag:
                    layout.alert = True
                else:
                    layout.enabled = False
            return layout

        kwargs = {}
        if hide_texts:
            kwargs['text'] = ''
        modified_layout(
            layout,
            data.use_rotation,
        ).prop(data, 'use_rotation', toggle=True, icon='MAN_ROT', **kwargs)
        modified_layout(
            layout,
            data.use_location,
        ).prop(data, 'use_location', toggle=True, icon='MAN_TRANS', **kwargs)
        return no_source and (data.use_rotation or data.use_location)


__CLASSES__ = (
    ObjectPanel,
    PoseBonePanel,
)

def register():
    for clas in __CLASSES__:
        bpy.utils.register_class(clas)
def unregister():
    for clas in reversed(__CLASSES__):
        bpy.utils.unregister_class(clas)
