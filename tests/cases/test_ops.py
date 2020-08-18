from tests import utils

import bpy

from animation_retarget import ops


class WM:
    def __init__(self):
        self.clipboard = ''


class TestOperations(utils.BaseTestCase):
    def setUp(self):
        super().setUp()
        ops.WM = WM()

    def tearDown(self):
        ops.WM = bpy.context.window_manager
        super().tearDown()

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
        self.assertEqual(ops.WM.clipboard, """[object]
source = src

[bone:root]
source = root
use_location = True
source_to_target_rest = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
delta_transform = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)

""")

    def test_paste(self):
        operator = bpy.ops.animation_retarget.paste_mapping
        # no armature
        self.assertFalse(operator.poll())

        create_armature('src')
        tgt = create_armature('tgt')
        ops.WM.clipboard = ''
        # the clipboard is empty
        self.assertFalse(operator.poll())
        ops.WM.clipboard = """
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
        self.assertEqual(tgt.animation_retarget.source, '')
        self.assertEqual(prop.source, '')
        self.assertFalse(prop.use_location)
        self.assertFalse(prop.use_rotation)

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
