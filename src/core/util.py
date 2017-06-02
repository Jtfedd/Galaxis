from panda3d.core import *
import random

from src.core.showbase import *

def calcRatio():
    return base.win.getXSize() / float(base.win.getYSize())

def randomSign():
    if random.randrange(2):
        return 1
    return -1

def map3dToAspect2d(node, point):
    """Maps the indicated 3-d point (a Point3), which is relative to
    the indicated NodePath, to the corresponding point in the aspect2d
    scene graph. Returns the corresponding Point3 in aspect2d.
    Returns None if the point is not onscreen. """

    # Convert the point to the 3-d space of the camera
    p3 = base.cam.getRelativePoint(node, point)

    # Convert it through the lens to render2d coordinates
    p2 = Point2()
    if not base.camLens.project(p3, p2):
        return None

    r2d = Point3(p2[0], 0, p2[1])

    # And then convert it to aspect2d coordinates
    a2d = aspect2d.getRelativePoint(render2d, r2d)

    return a2d

def isOnscreen(node, point):
    if map3dToAspect2d(node, point) is not None:
        return True
    return False