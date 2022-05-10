from unittest.mock import patch

import bpy

from animation_retarget.ui import BONE_PT_PoseBonePanel, overlay_view_3d, OBJECT_PT_ObjectPanel
from tests.utils import BaseTestCase, ContextMock, create_armature


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


class LayoutMock:
    def __init__(self, kwargs=None) -> None:
        self.calls = []
        self.kwargs = kwargs or {}

    @property
    def active(self):
        return self.kwargs.get('active', False)

    @active.setter
    def active(self, value):
        self.kwargs['active'] = value

    @property
    def enabled(self):
        return self.kwargs.get('enabled', False)

    @enabled.setter
    def enabled(self, value):
        self.kwargs['enabled'] = value

    def operator(self, *args, **kwargs):
        self.calls.append(('operator', args, kwargs))

    def prop(self, *args, **kwargs):
        self.calls.append(('prop', args, kwargs))

    def prop_search(self, *args, **kwargs):
        self.calls.append(('prop_search', args, kwargs))

    def label(self, *args, **kwargs):
        self.calls.append(('label', args, kwargs))

    def split(self, *args, **kwargs):
        layout = LayoutMock(kwargs)
        self.calls.append(('split', args, kwargs, layout.calls))
        return layout

    def column(self, *args, **kwargs):
        layout = LayoutMock(kwargs)
        self.calls.append(('column', args, kwargs, layout.calls))
        return layout

    def row(self, *args, **kwargs):
        layout = LayoutMock(kwargs)
        self.calls.append(('row', args, kwargs, layout.calls))
        return layout


class PanelMock:
    def __init__(self) -> None:
        self.layout = LayoutMock()


class TestUI(BaseTestCase):
    def test_object_panel(self):
        panel = OBJECT_PT_ObjectPanel
        self.assertFalse(panel.poll(bpy.context))

        src = create_armature('src')
        tgt = create_armature('tgt')
        self.assertTrue(panel.poll(bpy.context))

        expected_operators_row = ('row', (), {'align': True}, [
            ('operator', ('animation_retarget.auto_mapping',),
             {'icon': 'SHADERFX', 'text': 'Auto'}),
            ('operator', ('animation_retarget.copy_mapping',),
             {'icon': 'COPYDOWN', 'text': 'Copy'}),
            ('operator', ('animation_retarget.paste_mapping',),
             {'icon': 'PASTEDOWN', 'text': 'Paste'}),
            ('operator', ('animation_retarget.clear_mapping',),
             {'icon': 'X', 'text': 'Clear'})
        ])

        panel_mock = PanelMock()
        panel.draw(panel_mock, bpy.context)
        self.assertEqual(panel_mock.layout.calls, [
            expected_operators_row,
            ('prop_search',
             (tgt.animation_retarget, 'source', bpy.data, 'objects'), {}),
        ])

        panel_mock = PanelMock()
        tgt.animation_retarget.source = src.name
        prop_root = tgt.pose.bones['root'].animation_retarget
        prop_root.source = 'root'
        prop_root.use_location = True
        prop_child = tgt.pose.bones['child'].animation_retarget
        prop_child.source = 'child'
        prop_child.use_rotation = True
        prop_child.source = ''
        self.assertTrue(panel.poll(bpy.context))
        panel.draw(panel_mock, bpy.context)
        self.assertEqual(panel_mock.layout.calls, [
            expected_operators_row,
            ('prop_search',
             (tgt.animation_retarget, 'source', bpy.data, 'objects'), {}),
            ('prop', (bpy.data.objects['tgt'].animation_retarget, 'draw_links'), {
                'toggle': True}),
            ('column', (), {'align': True}, [
                ('row', (), {'align': True, 'active': True}, [
                    ('label', (), {'text': 'root'}),
                    ('prop_search', (prop_root, 'source',
                                     src.pose, 'bones'), {'text': ''}),
                    ('prop', (prop_root, 'use_rotation'), {
                        'toggle': True, 'icon': 'CON_ROTLIKE', 'text': ''}),
                    ('prop', (prop_root, 'use_location'), {
                        'toggle': True, 'icon': 'CON_LOCLIKE', 'text': ''}),
                ]),
                ('row', (), {'align': True, 'active': True}, [
                    ('label', (), {'text': 'child'}),
                    ('prop_search', (prop_child, 'source', src.pose, 'bones'), {
                        'text': ''}),
                    ('split', (), {'align': True}, [
                        ('prop', (prop_child, 'use_rotation'), {
                            'toggle': True, 'icon': 'CON_ROTLIKE', 'text': ''})
                    ]),
                    ('split', (), {'align': True, 'enabled': False}, [
                        ('prop', (prop_child, 'use_location'), {
                            'toggle': True, 'icon': 'CON_LOCLIKE', 'text': ''})
                    ])
                ])
            ]),
        ])

    @patch.object(bpy, 'context', ContextMock())
    def test_pose_bone_panel(self):
        panel = BONE_PT_PoseBonePanel
        self.assertFalse(panel.poll(bpy.context))

        src = create_armature('src')
        tgt = create_armature('tgt')
        bpy.context.active_pose_bone = tgt.pose.bones['root']
        self.assertTrue(panel.poll(bpy.context))

        panel_mock = PanelMock()
        panel.draw(panel_mock, bpy.context)
        self.assertEqual(panel_mock.layout.calls, [
            ('label', (), {
             'icon': 'INFO', 'text': 'Select the source object on the Object Properties panel'})
        ])

        panel_mock = PanelMock()
        tgt.animation_retarget.source = src.name
        prop_root = tgt.pose.bones['root'].animation_retarget
        prop_root.source = 'root'
        prop_root.use_location = True
        self.assertTrue(panel.poll(bpy.context))
        panel.draw(panel_mock, bpy.context)
        self.assertEqual(panel_mock.layout.calls, [
            ('prop_search', (prop_root, 'source', src.pose, 'bones'), {}),
            ('row', (), {'align': True}, [
                ('prop', (prop_root, 'use_rotation'), {
                 'icon': 'CON_ROTLIKE', 'toggle': True}),
                ('prop', (prop_root, 'use_location'), {
                 'icon': 'CON_LOCLIKE', 'toggle': True}),
            ]),
        ])

    @patch('gpu.shader.from_builtin', ShaderMock)
    @patch('gpu_extras.batch.batch_for_shader', BatchMock)
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
