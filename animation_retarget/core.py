from collections import OrderedDict
import configparser
from io import StringIO

import bpy
import mathutils


__CONFIG_PREFIX_BONE__ = 'bone:'


def mapping_to_text(target_obj):
    def put_nonempty_value(data, name, value):
        if value:
            data[name] = value

    def put_nonzero_tuple(data, name, value):
        for val in value:
            if val:
                data[name] = value
                break

    def prepare_value(value):
        value = round(value, 6)
        ivalue = int(value)
        return ivalue if ivalue == value else value

    config = configparser.ConfigParser()
    config['object'] = {
        'source': target_obj.animation_retarget.source,
    }

    for bone in target_obj.pose.bones:
        prop = bone.animation_retarget
        data = OrderedDict()
        for name in ('source', 'use_location', 'use_rotation'):
            put_nonempty_value(data, name, getattr(prop, name))
        for name in ('source_to_target_rest', 'delta_transform'):
            value = tuple(map(prepare_value, getattr(prop, name)))
            put_nonzero_tuple(data, name, value)
        if data:
            config[__CONFIG_PREFIX_BONE__ + bone.name] = data

    buffer = StringIO()
    config.write(buffer)
    return buffer.getvalue()


def text_to_mapping(text, target_obj):
    def parse_boolean(text):
        return {
            'True': True,
            'False': False,
        }[text]

    def parse_tuple(text):
        text = text.replace('(', '').replace(')', '')
        return tuple(map(float, text.split(',')))

    config = configparser.ConfigParser()
    config.read_string(text)

    source = config['object']['source']
    target_obj.animation_retarget.source = source

    for key, value in config.items():
        if not key.startswith(__CONFIG_PREFIX_BONE__):
            continue
        name = key[len(__CONFIG_PREFIX_BONE__):]
        target_bone = target_obj.pose.bones.get(name)
        if not target_bone:
            print('bone ' + name + ' is not found')
            continue
        prop = target_bone.animation_retarget
        if 'source' in value:
            prop.source = value['source']
        for name in ('use_location', 'use_rotation'):
            if name in value:
                setattr(prop, name, parse_boolean(value[name]))
        for name in ('source_to_target_rest', 'delta_transform'):
            if name in value:
                setattr(prop, name, parse_tuple(value[name]))
        prop.invalidate_cache()
    bpy.context.scene.update()


__ZERO_V16__ = (0,) * 16

def clear_mapping(target_obj):
    target_obj.animation_retarget.source = ''
    for bone in target_obj.pose.bones:
        prop = bone.animation_retarget
        prop.source = ''
        prop.use_location = prop.use_rotation = False
        prop.source_to_target_rest = prop.delta_transform = __ZERO_V16__
        prop.invalidate_cache()
    bpy.context.scene.update()


class RelativeObjectTransform(bpy.types.PropertyGroup):
    b_type = bpy.types.Object

    def _update_source(self, _context):
        if self.source:
            for bone in self.id_data.pose.bones:
                if bone.animation_retarget.source:
                    bone.animation_retarget.update_link()

    source = bpy.props.StringProperty(
        name='Source Object',
        description='An object whose animation will be used',
        update=_update_source,
    )

def _prop_to_pose_bone(obj, prop):
    for bone in obj.pose.bones:
        if bone.animation_retarget == prop:
            return bone
    return None

def _fvec16_to_matrix4(fvec):
    return mathutils.Matrix((fvec[0:4], fvec[4:8], fvec[8:12], fvec[12:16]))

__ROTATION_MODES__ = ('quaternion', 'euler', 'axis_angle')

class RelativeBoneTransform(bpy.types.PropertyGroup):
    b_type = bpy.types.PoseBone

    def _update_source(self, _context):
        if self.source:
            self.update_link()

    source = bpy.props.StringProperty(
        name='Source Bone',
        description='A bone whose animation will be used',
        update=_update_source,
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
                var = driver.variables[0] if driver.variables else driver.variables.new()
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
            var = driver.variables[0] if driver.variables else driver.variables.new()
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
        self.invalidate_cache()
        bpy.context.scene.update()

    def invalidate_cache(self):
        self.frame_cache[7] = 0

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

__CLASSES__ = (
    RelativeObjectTransform,
    RelativeBoneTransform,
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
