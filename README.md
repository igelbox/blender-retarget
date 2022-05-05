# blender-retarget
Animation retargeting addon for [Blender 3D](http://www.blender.org/).

[![Tests](https://github.com/igelbox/blender-retarget/actions/workflows/tests.yml/badge.svg)](https://github.com/igelbox/blender-retarget/actions/workflows/tests.yml)
[![Code Coverage](https://codecov.io/gh/igelbox/blender-retarget/graph/badge.svg)](https://codecov.io/gh/igelbox/blender-retarget)

# The Main Goal
The main goal is to __link/synchronize__ target armature __bones__ with a source ones in __real-time__ using some math magic.

Thus, allowing you to __use your next favorite tools__ for baking/exporting/using the result motions. For the glory of the Unix way.

# How to Install
* For Blender 2.80+ (except 2.82) - use *animation-retarget-x.x.x.zip* from the [latest release](https://github.com/igelbox/blender-retarget/releases/latest) page.
* For Blender 2.79 - the initial [animation-retarget-0.1.0.zip](https://github.com/igelbox/blender-retarget/releases/download/v0.1.0/animation-retarget-0.1.0.zip) should work fine.

_Blender 2.82 isn't supported by this addon coz there's no known trick to force `depsgraph` to refresh pose on each frame._

# How to Use
- Select the destination armature object in a 3D View area
- Go to the Object Properties panel
- Choose the source armature object in the `Select Source:` field
- Choose source bones for each bone that should be linked
- Position target bones along with source ones, to make the target armature almost the same pose as the source one
- Use the `Link rotation` and `Link location` buttons to specify which kind of animation should be copied: rotation only, translation only, or both.
- Change the current frame number to see how target bones follow to source ones

Relative positions of bones can be adjusted at any time.
To do this the respective `Link rotation` or `Link location` button should be temporarily switched off.

**TL;DR** - use the following video tutorial (text subtitles can be auto-translated by YouTube):

[![Video Tutorial](https://i.ytimg.com/vi/rPLdn0nf5Kw/hqdefault.jpg)](http://www.youtube.com/watch?v=rPLdn0nf5Kw)
