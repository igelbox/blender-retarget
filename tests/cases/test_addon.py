import bpy

import animation_retarget
from tests import utils


class TestAddon(utils.BaseTestCase):
    def test_blinfo(self):
        self.assertIsNotNone(animation_retarget.bl_info)

    def test_enabled(self):
        self.assertIn('animation_retarget', bpy.context.preferences.addons)
