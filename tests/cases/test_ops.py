from unittest.mock import patch
from animation_retarget.ui import COLOR_LINKED, overlay_view_3d
from tests import utils

import bpy
from bpy import context

from animation_retarget import ops


class WMock:
    clipboard = ''

class ContextMock:
    base = None
    window_manager = WMock

    def __getattribute__(self, name: str):
        if name in ('window_manager', 'base'):
            return super().__getattribute__(name)
        return context.__getattribute__(name)


class ShaderMock:
    def __init__(self, *args) -> None:
        self.args = args

    def bind(self) -> None:
        pass


class BatchMock:
    def __init__(self, shader, *args) -> None:
        self.shader = shader
        self.args = args

    def draw(self, shader) -> None:
        self.shader = shader
        return self


class TestOperations(utils.BaseTestCase):
    @patch.object(bpy, 'context', ContextMock())
    def test_copy(self):
        operator = bpy.ops.animation_retarget.copy_mapping
        # no armature
        self.assertFalse(operator.poll())

        src = create_armature('src')
        tgt = create_armature('tgt')
        # no source
        self.assertFalse(operator.poll())

        tgt.animation_retarget.source = src.name
        prop = tgt.pose.bones['root'].animation_retarget
        prop.source = 'root'
        prop.use_location = True
        # all ok
        self.assertTrue(operator.poll())

        operator()
        self.assertEqual(WMock.clipboard, """[object]
source = src

[bone:root]
source = root
use_location = True
source_to_target_rest = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
delta_transform = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)

""")

    @patch.object(bpy, 'context', ContextMock())
    def test_paste(self):
        operator = bpy.ops.animation_retarget.paste_mapping
        # no armature
        self.assertFalse(operator.poll())

        create_armature('src')
        tgt = create_armature('tgt')
        WMock.clipboard = ''
        # the clipboard is empty
        self.assertFalse(operator.poll())
        WMock.clipboard = """
[object]
source=src
[bone:root]
source = root
use_rotation = True
source_to_target_rest = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
"""
        # all ok
        self.assertTrue(operator.poll())

        operator()
        self.assertEqual(tgt.animation_retarget.source, 'src')
        prop = tgt.pose.bones['root'].animation_retarget
        self.assertEqual(prop.source, 'root')
        self.assertFalse(prop.use_location)
        self.assertTrue(prop.use_rotation)

    def test_clear(self):
        operator = bpy.ops.animation_retarget.clear_mapping
        # no armature
        self.assertFalse(operator.poll())

        src = create_armature('src')
        tgt = create_armature('tgt')
        tgt.animation_retarget.source = src.name
        prop = tgt.pose.bones['root'].animation_retarget
        prop.source = 'root'
        prop.use_location = True
        prop.use_rotation = True
        # all ok
        self.assertTrue(operator.poll())

        operator()
        self.assertEqual(prop.source, '')
        self.assertFalse(prop.use_location)
        self.assertFalse(prop.use_rotation)

    def test_automap(self):
        operator = bpy.ops.animation_retarget.auto_mapping
        self.assertFalse(operator.poll(), 'no armature')

        src = create_armature('src')
        tgt = create_armature('tgt')
        self.assertFalse(operator.poll(), 'no source')
        tgt.animation_retarget.source = src.name
        self.assertTrue(operator.poll(), 'all ok')
        prop_child = tgt.pose.bones['child'].animation_retarget
        prop_child.source = 'unknown'

        operator()
        prop_root = tgt.pose.bones['root'].animation_retarget
        self.assertEqual(
            (prop_root.source, prop_root.use_location, prop_root.use_rotation),
            ('root', True, True)
        )
        self.assertEqual(
            (prop_child.source, prop_child.use_location, prop_child.use_rotation),
            ('unknown', False, False)
        )

        prop_child.source = ''
        operator()
        self.assertEqual(
            (prop_child.source, prop_child.use_location, prop_child.use_rotation),
            ('child', True, True)
        )

    def test_trick(self):
        operator = bpy.ops.animation_retarget.trick_blender
        # no armature
        self.assertFalse(operator.poll())

        src = create_armature('src')
        tgt = create_armature('tgt')
        tgt.animation_retarget.source = src.name
        prop = tgt.pose.bones['root'].animation_retarget
        prop.source = 'root'

        self.assertFalse(operator.poll())
        prop.use_location = True
        prop.use_rotation = True

        # tricked automatically
        self.assertFalse(operator.poll())


        for fcurve in tgt.animation_data.drivers:
            variables = fcurve.driver.variables
            variables.remove(variables['Just-a-Trick-to-Refresh'])
        self.assertTrue(operator.poll())

        operator()
        self.assertFalse(operator.poll())

    @patch('gpu.shader.from_builtin', ShaderMock)
    @patch('gpu_extras.batch.batch_for_shader', lambda *args: BatchMock(*args))
    @patch('bgl.glEnable', lambda _flags: None)
    def test_overlay(self):
        self.assertIsNone(overlay_view_3d())

        tgt = create_armature('tgt')
        self.assertIsNone(overlay_view_3d())
        prop = tgt.animation_retarget
        prop.draw_links = True

        create_armature('src')
        self.assertIsNone(overlay_view_3d())

        prop.source = 'src'
        self.assertIsNone(overlay_view_3d())

        prop_root = tgt.pose.bones['root'].animation_retarget
        prop_root.source = 'root'
        batch = overlay_view_3d()
        self.assertEqual(batch.args[0], 'LINES')
        self.assertEqual(len(batch.args[1]['pos']), 2)
        self.assertEqual(batch.shader.args, ('3D_FLAT_COLOR',))


def create_armature(name):
    arm = bpy.data.armatures.new(name)
    obj = bpy.data.objects.new(name, arm)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    try:
        root = arm.edit_bones.new('root')
        root.tail = (0, 0, 1)
        child = arm.edit_bones.new('child')
        child.parent = root
        child.head = root.tail
        child.tail = (0, 1, 1)
    finally:
        bpy.ops.object.mode_set(mode='OBJECT')
    return obj
