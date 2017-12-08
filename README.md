# blender-retarget [![Build Status](https://travis-ci.org/igelbox/blender-retarget.svg)](https://travis-ci.org/igelbox/blender-retarget) [![Code Coverage](https://codecov.io/gh/igelbox/blender-retarget/graph/badge.svg)](https://codecov.io/gh/igelbox/blender-retarget)
Animation retargeting addon for [Blender 3D](http://www.blender.org/).

# How to use the addon
- Select the destination armature object in a 3D View area
- Go to the Object Properties panel
- Choose the source armature object in the `Select Source:` field
- Choose source bones for each bone that should be linked
- Position target bones along with source ones, to make the target armature almost the same pose as the source one
- Use the `Link rotation` and `Link location` buttons to specify which kind of animation should be copied: rotation only, translation only, or both.
- Change the current frame number to see how target bones follow to source ones

Relative positions of bones can be adjusted at any time.
To do this the respective `Link rotation` or `Link location` button should be temporarily switched off.
