from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import *

from src.menu.menu import Menu
from src.core.showbase import *


class LoadingScreen:
    def __init__(self, nextAction = 'Menu', extraArgs = []):
        self.nextAction = nextAction
        self.extraArgs = extraArgs

        self.loadingText = OnscreenImage(image = 'data/launcher/loadingText.png',
                                         scale = .7)
        self.loadingText.setTransparency(TransparencyAttrib.MAlpha)
        self.loadingText.setAlphaScale(0.0)

        self.loadingArc1 = OnscreenImage(image = 'data/launcher/loadingArc.png',
                                         scale = .7,
                                         hpr = (0, 0, 0))
        self.loadingArc1.setTransparency(TransparencyAttrib.MAlpha)
        self.loadingArc1.setAlphaScale(0.0)

        self.loadingArc2 = OnscreenImage(image='data/launcher/loadingArc.png',
                                         scale=.7,
                                         hpr=(0, 0, 90))
        self.loadingArc2.setTransparency(TransparencyAttrib.MAlpha)
        self.loadingArc2.setAlphaScale(0.0)

        self.loadingArc3 = OnscreenImage(image='data/launcher/loadingArc.png',
                                         scale=.7,
                                         hpr=(0, 0, 180))
        self.loadingArc3.setTransparency(TransparencyAttrib.MAlpha)
        self.loadingArc3.setAlphaScale(0.0)

        self.loadingArc4 = OnscreenImage(image='data/launcher/loadingArc.png',
                                         scale=.7,
                                         hpr=(0, 0, 270))
        self.loadingArc4.setTransparency(TransparencyAttrib.MAlpha)
        self.loadingArc4.setAlphaScale(0.0)

        self.completion = 0.0

        self.loadingList = []
        self.totalItems = 0
        self.currentItem = 0

        self.loadLoadingList()

        taskMgr.doMethodLater(1, self.fadeInLoading, 'loading-screen-delay')

    def loadLoadingList(self):
        loadFile = open('data/' + self.nextAction + 'LoadingList.load')
        for line in loadFile.readlines():
            self.loadingList.append(line)
        loadFile.close()

        self.totalItems = len(self.loadingList)

    def loadItems(self):
        root = render.attachNewNode('loadingTmpNode')
        root.setTransparency(TransparencyAttrib.MAlpha)
        root.setAlphaScale(0)

        images = []

        for i in self.loadingList:
            d = i.split('|')
            type = d[0]
            path = d[1].strip()
            if type == 'model':
                tmp = loader.loadModel(path)
                tmp.reparentTo(root)
                tmp.node().setBounds(OmniBoundingVolume())
                tmp.node().setFinal(True)
            elif type == 'shader':
                Shader.load(path)
            elif type == 'image':
                images.append(OnscreenImage(image = path, pos = (100, 0, 0), scale = 0))
            elif type == 'sfx':
                loader.loadSfx(path)
            elif type == 'music':
                loader.loadMusic(path)

            self.completeItem()

        root.removeNode()
        for i in images:
            i.destroy()

        self.startFadeOut()

    def fadeInLoading(self, task):
        taskMgr.add(self.fadeInLoadingTask, 'loading-screen-fadein')
        return task.done

    def fadeInLoadingTask(self, task):
        self.loadingText.setAlphaScale(task.time * 2)
        if task.time > .5:
            self.loadingText.setAlphaScale(1)
            self.loadItems()
            return task.done
        return task.cont

    def startFadeOut(self):
        self.loadingArc1.setAlphaScale(1)
        self.loadingArc2.setAlphaScale(1)
        self.loadingArc3.setAlphaScale(1)
        self.loadingArc4.setAlphaScale(1)

        taskMgr.add(self.fadeOutTask, 'loading-screen-fade-out')

    def fadeOutTask(self, task):
        self.loadingText.setAlphaScale(1 - (task.time * 2))
        self.loadingArc1.setAlphaScale(1 - (task.time * 2))
        self.loadingArc2.setAlphaScale(1 - (task.time * 2))
        self.loadingArc3.setAlphaScale(1 - (task.time * 2))
        self.loadingArc4.setAlphaScale(1 - (task.time * 2))

        if task.time > .5:
            self.cleanup()
            return task.done
        return task.cont

    def completeItem(self):
        self.currentItem += 1
        self.completion = self.currentItem / 1.0 / self.totalItems
        self.updateArcs()

    def updateArcs(self):
        self.loadingArc1.setAlphaScale(self.completion * 4)
        self.loadingArc2.setAlphaScale((self.completion - .25) * 4)
        self.loadingArc3.setAlphaScale((self.completion - .5) * 4)
        self.loadingArc4.setAlphaScale((self.completion - .75) * 4)
        base.graphicsEngine.renderFrame()

    def cleanup(self):
        self.loadingText.destroy()
        self.loadingArc1.destroy()
        self.loadingArc2.destroy()
        self.loadingArc3.destroy()
        self.loadingArc4.destroy()

        base.graphicsEngine.renderFrame()

        if self.nextAction == 'Menu':
            Menu()