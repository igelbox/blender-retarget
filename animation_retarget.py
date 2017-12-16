import bpy
import mathutils

bl_info = {
    'name':     'Animation Retargeting Tools',
    'author':   'Vakhurin Sergey (igel)',
    'version':  (0, 0, 1),
    'blender':  (2, 77, 0),
    'category': 'Animation',
    'location': 'Properties > Object, Properties > Bone',
    'description': 'Applies an animation from one armature to another',
    'wiki_url': 'https://github.com/igelbox/blender-retarget',
    'tracker_url': 'https://github.com/igelbox/blender-retarget/issues',
    'warning':  'This is just a proof of concept version. \
Further versions may be not compatible with settings from this version.'
}

class RelativeObjectTransform(bpy.types.PropertyGroup):
    b_type = bpy.types.Object

    source = bpy.props.StringProperty(
        name='Source Object',
        description='An object whose animation will be used',
    )

def _prop_to_pose_bone(obj, prop):
    for bone in obj.pose.bones:
        if bone.animation_retarget == prop:
            return bone
    return None

def _fvec16_to_matrix4(fvec):
    return mathutils.Matrix((fvec[0:4], fvec[4:8], fvec[8:12], fvec[12:16]))

def _fvec9_to_matrix3(fvec):
    return mathutils.Matrix((fvec[0:3], fvec[3:6], fvec[6:9]))

__ROTATION_MODES__ = ('quaternion', 'euler', 'axis_angle')

class RelativeBoneTransform(bpy.types.PropertyGroup):
    b_type = bpy.types.PoseBone

    source = bpy.props.StringProperty(
        name='Source Bone',
        description='A bone whose animation will be used',
        update=lambda self, _: self.update_link(),
    )

    def _get_use_rotation(self):
        animation_data = self.id_data.animation_data
        if not animation_data:
            return False
        bone = _prop_to_pose_bone(self.id_data, self)
        data_path_prefix = 'pose.bones["%s"].rotation_' % (bone.name,)
        for mode in __ROTATION_MODES__:
            if animation_data.drivers.find(data_path_prefix + mode) is not None:
                return True
        return False

    def _set_use_rotation(self, value):
        bone = _prop_to_pose_bone(self.id_data, self)
        if not value:
            for mode in __ROTATION_MODES__:
                bone.driver_remove('rotation_' + mode)
            return
        self.update_link()
        for mode in __ROTATION_MODES__:
            for fcurve in bone.driver_add('rotation_' + mode):
                driver = fcurve.driver
                driver.type = 'SUM'
                var = driver.variables.new()
                tgt = var.targets[0]
                tgt.id = self.id_data
                tgt.data_path = 'pose.bones["%s"].animation_retarget.transform[%d]' % (
                    bone.name, fcurve.array_index + 3
                )

    use_rotation = bpy.props.BoolProperty(
        name='Link Rotation',
        description='Link rotation to the source bone',
        get=_get_use_rotation, set=_set_use_rotation,
    )

    def _get_use_location(self):
        animation_data = self.id_data.animation_data
        if not animation_data:
            return False
        bone = _prop_to_pose_bone(self.id_data, self)
        data_path = 'pose.bones["%s"].location' % (bone.name,)
        return animation_data.drivers.find(data_path) is not None

    def _set_use_location(self, value):
        bone = _prop_to_pose_bone(self.id_data, self)
        if not value:
            bone.driver_remove('location')
            return
        self.update_link()
        for fcurve in bone.driver_add('location'):
            driver = fcurve.driver
            driver.type = 'SUM'
            var = driver.variables.new()
            tgt = var.targets[0]
            tgt.id = self.id_data
            tgt.data_path = 'pose.bones["%s"].animation_retarget.transform[%d]' % (
                bone.name, fcurve.array_index
            )

    use_location = bpy.props.BoolProperty(
        name='Link Location',
        description='Link location to the source bone',
        get=_get_use_location, set=_set_use_location,
    )

    source_to_target_rest = bpy.props.FloatVectorProperty(
        description='-private-data-',
        size=16,
    )
    delta_transform = bpy.props.FloatVectorProperty(
        description='-private-data-',
        size=16,
    )

    def update_link(self):
        source_obj = bpy.data.objects[self.id_data.animation_retarget.source]
        source_bone = source_obj.pose.bones[self.source]
        target_obj = self.id_data
        target_bone = _prop_to_pose_bone(target_obj, self)

        source = source_obj.matrix_world * source_bone.matrix
        source_rest = source * source_bone.matrix_basis.inverted()
        target = target_obj.matrix_world * target_bone.matrix
        target_rest = target * target_bone.matrix_basis.inverted()

        source_to_target_rest = target_rest.inverted() * source_rest
        delta_transform = source.inverted() * target

        self.source_to_target_rest = (
            *source_to_target_rest.row[0],
            *source_to_target_rest.row[1],
            *source_to_target_rest.row[2],
            *source_to_target_rest.row[3]
        )
        self.delta_transform = (
            *delta_transform.row[0],
            *delta_transform.row[1],
            *delta_transform.row[2],
            *delta_transform.row[3]
        )
        self._invalidate()

    frame_cache = bpy.props.FloatVectorProperty(
        description='-private-data-',
        size=8,
    )

    def _invalidate(self):
        self.frame_cache[7] = 0
        bpy.context.scene.update()

    def _get_transform(self):
        frame = bpy.context.scene.frame_current + 1 # to workaround the default 0 value
        cache = tuple(self.frame_cache)
        if cache[7] == frame:
            return cache
        source = bpy.data.objects[self.id_data.animation_retarget.source]
        source_bone = source.pose.bones[self.source]
        target_bone = _prop_to_pose_bone(self.id_data, self)

        source_to_target_rest = _fvec16_to_matrix4(self.source_to_target_rest)
        delta_transform = _fvec16_to_matrix4(self.delta_transform)
        transform = source_to_target_rest * source_bone.matrix_basis * delta_transform

        location = transform.to_translation()
        quaternion = transform.to_quaternion()
        rotation = None
        if target_bone.rotation_mode == 'QUATERNION':
            rotation = quaternion
        elif target_bone.rotation_mode == 'AXIS_ANGLE':
            rotation = (quaternion.angle, *quaternion.axis)
        else:
            rotation = (*quaternion.to_euler(target_bone.rotation_mode), 0)

        self.frame_cache = cache = (*location, *rotation, frame)
        return cache

    transform = bpy.props.FloatVectorProperty(size=8, get=_get_transform)


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
    RelativeObjectTransform,
    RelativeBoneTransform,
    ObjectPanel,
    PoseBonePanel,
)

def register():
    for clas in __CLASSES__:
        bpy.utils.register_class(clas)
        b_type = getattr(clas, 'b_type', None)
        if b_type:
            b_type.animation_retarget = bpy.props.PointerProperty(type=clas)


def unregister():
    for clas in reversed(__CLASSES__):
        b_type = getattr(clas, 'b_type', None)
        if b_type:
            del b_type.animation_retarget
        bpy.utils.unregister_class(clas)
