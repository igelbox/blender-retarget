from unittest.mock import patch

import bpy

from tests.utils import BaseTestCase, create_armature, ContextMock


class TestOperations(BaseTestCase):
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
        self.assertEqual(bpy.context.window_manager.clipboard, """[object]
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
        bpy.context.window_manager.clipboard = ''
        # the clipboard is empty
        self.assertFalse(operator.poll())
        bpy.context.window_manager.clipboard = """
[object]
source=src
[bone:root]
source = root
use_rotation = True
source_to_target_rest = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
[bone:unknown]
[bone:child]
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
