import math

from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import *

from src.core.showbase import *
from src.menu.loading import LoadingScreen

class SplashScreen:
    def __init__(self):
        # First fade in
        self.root1 = aspect2d.attachNewNode('splash-root-1')
        self.root1.setTransparency(TransparencyAttrib.MAlpha)
        self.root1.setAlphaScale(0.0)

        # Second fade in - .5 seconds later
        self.root2 = aspect2d.attachNewNode('splash-root-2')
        self.root2.setTransparency(TransparencyAttrib.MAlpha)
        self.root2.setAlphaScale(0.0)

        self.pandaLogo = OnscreenImage(image = 'data/launcher/Panda3DLogo.png', scale = (.6, 1, .15), parent = self.root1)

        # While we're at it, let's load the loading stuff
        self.loadingText = OnscreenImage(image = 'data/launcher/loadingText.png', scale = 0, pos = (10, 0, 10))
        self.loadingArc = OnscreenImage(image = 'data/launcher/loadingArc.png', scale = 0, pos = (10, 0, 10))

        self.lastDt = 0
        self.count = 0

        taskMgr.add(self.awaitWindowLoad, 'await-window-load')

    def awaitWindowLoad(self, task):
        # Wait for the framerate to stabilize
        dt = globalClock.getDt()
        if math.fabs(dt-self.lastDt) > 0.001:
            self.count = 0
            self.lastDt = dt
            return task.cont
        else:
            self.count += 1
            self.lastDt = dt

        if self.count > 10 or task.time > 3.0:
            taskMgr.doMethodLater(1.0, self.fadeIn, 'fadeInDelay')
            taskMgr.doMethodLater(4.0, self.fadeOut, 'fadeOutDelay')
            return task.done

        return task.cont

    def fadeIn(self, task):
        self.root1.setAlphaScale(task.time * 2)
        self.root2.setAlphaScale((task.time-.5)*2)
        if task.time > 1:
            self.root1.setAlphaScale(1.0)
            self.root2.setAlphaScale(1.0)
            return task.done
        return task.cont

    def fadeOut(self, task):
        self.root1.setAlphaScale(1-task.time*2)
        self.root2.setAlphaScale(1-task.time*2)
        if task.time > .5:
            self.cleanup()
            return task.done
        return task.cont

    def cleanup(self):
        self.pandaLogo.destroy()
        self.root1.removeNode()
        self.root2.removeNode()

        LoadingScreen()

        self.loadingText.destroy()
        self.loadingArc.destroy()