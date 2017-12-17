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


def register():
    from . import core, ui
    core.register()
    ui.register()


def unregister():
    from . import core, ui
    ui.unregister()
    core.unregister()
