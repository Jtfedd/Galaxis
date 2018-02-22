from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from panda3d.core import TransparencyAttrib

from src.core.data import Button, Font1

class BuildItem:
    def __init__(self, screen, action, cancel, time, name, cost, button=None, extraArgs=[]):
        self.buildScreen = screen
        self.action = action
        self.cancelAction = cancel
        self.currentTime = 0
        self.time = time
        self.name = name
        self.cost = cost
        self.button = button
        self.args = extraArgs

        self.active = False

        self.root = self.buildScreen.root.attachNewNode("BuildItem")
        self.bg = OnscreenImage(image="data/images/white.png",
                                scale=(0.5, 1, 0.105),
                                parent=self.root)
        self.bg.setTransparency(TransparencyAttrib.MAlpha)
        self.bg.setAlphaScale(0.3)

        self.title = OnscreenText(text=self.name,
                                  scale=0.06,
                                  align=TextNode.ALeft,
                                  parent=self.root,
                                  pos=(-0.475, 0.04),
                                  font=Font1,
                                  fg=(1,1,1,1),
                                  wordwrap=13)

        self.progressBarBg = OnscreenImage(image="data/images/black.png",
                                           scale=(0.475, 1, 0.002),
                                           pos=(0, 0, -0.08),
                                           parent=self.root)
        self.progressBar = OnscreenImage(image="data/images/green.png",
                                         scale=(0, 1, 0.002),
                                         pos=(-0.475, 0, -0.08),
                                         parent=self.root)

        self.cancelButton = Button(image="data/buttons/x.png",
                                   scale=0.0425,
                                   parent=self.root,
                                   pos=(0.4075, 0, 0.0125),
                                   command=self.cancel)

    def setPos(self, x, z):
        self.root.setPos(x, 0, z)

    def update(self, dt):
        if self.active:
            self.currentTime += dt
            progressPercent = self.currentTime/float(self.time)
            self.progressBar.setScale(0.475*progressPercent, 1, 0.002)
            self.progressBar.setX(-0.475*(1-progressPercent))
        if self.currentTime > self.time:
            self.complete()

    def complete(self):
        self.destroyGui()
        self.action(self)

    def cancel(self):
        self.destroyGui()
        self.cancelAction(self)

    def destroyGui(self):
        self.bg.destroy()
        self.title.destroy()
        self.progressBarBg.destroy()
        self.progressBar.destroy()
        self.cancelButton.destroy()
        self.root.removeNode()