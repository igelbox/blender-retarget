import os
import unittest
import shutil
import sys
import tempfile

import bpy
import addon_utils


class BaseTestCase(unittest.TestCase):
    __save_test_data = '--save-test-data' in sys.argv
    __tmp_base = os.path.join(tempfile.gettempdir(), 'animation_retarget-tests')
    __tmp = __tmp_base + '/out'

    @classmethod
    def outpath(cls, path=''):
        if not os.path.exists(cls.__tmp):
            os.makedirs(cls.__tmp)
        return os.path.join(cls.__tmp, path)

    def setUp(self):
        self._reports = []
        bpy.ops.wm.read_homefile()
        addon_utils.enable('animation_retarget', default_set=True)

    def tearDown(self):
        if os.path.exists(self.__tmp):
            if self.__save_test_data:
                bpy.ops.wm.save_mainfile(filepath=os.path.join(self.__tmp, 'result.blend'))
                new_path = os.path.join(
                    self.__tmp_base,
                    self.__class__.__name__,
                    self._testMethodName
                )
                os.renames(self.__tmp, new_path)
            else:
                shutil.rmtree(self.__tmp)
        addon_utils.disable('animation_retarget')
