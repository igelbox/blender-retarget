bl_info = {
    'name':     'Animation Retargeting Tools',
    'author':   'Vakhurin Sergey (igel)',
    'version':  (1, 0, 0),
    'blender': (2, 80, 0),
    'category': 'Animation',
    'location': 'Properties > Object, Properties > Bone',
    'description': 'Applies an animation from one armature to another',
    'wiki_url': 'https://github.com/igelbox/blender-retarget',
    'tracker_url': 'https://github.com/igelbox/blender-retarget/issues',
}


def register():
    from . import core, ui, ops
    core.register()
    ops.register()
    ui.register()


def unregister():
    from . import core, ui, ops
    ui.unregister()
    ops.unregister()
    core.unregister()
