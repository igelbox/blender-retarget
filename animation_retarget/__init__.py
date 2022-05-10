bl_info = {  # pylint: disable-msg=C0103
    'name':     'Animation Retargeting Tools',
    'author':   'Vakhurin Sergei (igelbox)',
    'version':  (1, 0, 2),
    'blender': (2, 80, 0),
    'category': 'Animation',
    'location': 'Properties > Object, Properties > Bone',
    'description': 'Applies an animation from one armature to another',
    'wiki_url': 'https://github.com/igelbox/blender-retarget',
    'tracker_url': 'https://github.com/igelbox/blender-retarget/issues',
}


def register():
    from . import core, ui, ops  # pylint:disable-msg=C0415
    core.register()
    ops.register()
    ui.register()


def unregister():
    from . import core, ui, ops  # pylint:disable-msg=C0415
    ui.unregister()
    ops.unregister()
    core.unregister()
