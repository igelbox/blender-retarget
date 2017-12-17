#!/usr/bin/env python3

from os import path, walk
from zipfile import ZipFile, ZIP_DEFLATED

from animation_retarget import bl_info

with ZipFile('animation-retarget-' + ('.'.join(map(str, bl_info['version']))) + '.zip', 'w') as z:
    z.write('LICENSE', 'animation_retarget/LICENSE', compress_type=ZIP_DEFLATED)
    for root, _, files in walk('animation_retarget'):
        for file in files:
            if not file.endswith('.py'):
                continue
            z.write(path.join(root, file), compress_type=ZIP_DEFLATED)
