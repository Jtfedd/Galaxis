from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from panda3d.core import TextNode
from panda3d.core import WindowProperties

from src.core.showbase import base, aspect2d

from src.core.data import Button, Font3
from src.core.util import calcRatio

from components import *

class BuildScreen(DirectObject):
    def __init__(self, game):
        self.game = game
        self.root = aspect2d.attachNewNode("BuildScreenRoot")

        # TODO Remove this stuff! It doesn't belong here! It's only for positioning the layout!
        wp = WindowProperties()
        wp.setSize(1920, 1080)
        wp.setFullscreen(True)
        base.win.requestProperties(wp)

        self.elements = []
        self.upgradeButtons = []

        self.title = OnscreenText(text="Title", parent=self.root, scale=0.3, fg=(1,1,1,1), font=Font3, align=TextNode.ALeft, pos=(-1.7, .7))
        self.resourceDisplay = ResourceDisplay(self.root)
        self.resourceDisplay.setPos(1.1, 0, .825)

        self.footer = BuildScreenFooter(self)

        self.elements.append(Button(text="Back", parent=self.root, scale=0.06, pos=(1.65, 0, -.97), align=TextNode.ARight, command=self.deactivate))

        # Horizontal lines
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(1.7, 1, 0.002), pos=(0, 0, -0.9)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(1.7, 1, 0.002), pos=(0, 0, -0.6)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(1.7, 1, 0.002), pos=(0, 0, 0.65)))

        # Vertical Lines
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(0.002, 1, 0.575), pos=(-1.65, 0, 0.025)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(0.002, 1, 0.575), pos=(-0.6, 0, 0.025)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(0.002, 1, 0.575), pos=(0.45, 0, 0.025)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(0.002, 1, 0.03), pos=(1.425, 0, -.95)))

        self.shipyardButton = None

        # Ship button placeholders
        iconSize = 0.25
        iconPadding = ((3.4/11.0) - iconSize) / 2

        for i in range(11):
            placement = i*iconSize+i*2*iconPadding - 5*(iconSize+2*iconPadding)
            self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(iconSize/2, 1, iconSize/2), pos = (placement, 0, -0.75)))

        self.active = False
        self.root.hide()
        self.returnObject = None

        if self.game.playerTeam == "blue":
            self.game.blueControlBase.initBuildScreen(self)
            self.resourceDisplay.update(self.game.blueControlBase.resources)

        self.accept(base.win.getWindowEvent(), self.updateScale)

    def addUpgradeButton(self, upgradeable, action, extraArgs):
        button = UpgradeButton(self, self.root, upgradeable, action, extraArgs)
        button.setZ(0.54-len(self.upgradeButtons)*0.115)
        self.upgradeButtons.append(button)

    def removeUpgradeButton(self, button):
        self.upgradeButtons.remove(button)
        button.destroy()
        for i in range(len(self.upgradeButtons)):
            self.upgradeButtons[i].setZ(0.54-i*0.115)

    def createShipyardButton(self, action, extraArgs):
        self.shipyardButton = ShipyardButton(self, self.root, action, extraArgs)

    def updateScale(self, win):
        self.root.setScale(min(calcRatio()/(1920.0/1080.0), 1))

    def activate(self, whoActivated):
        if self.active:
            return
        self.active = True
        self.root.show()
        self.game.messageDisplayer.hide()
        self.returnObject = whoActivated

    def deactivate(self):
        if not self.active:
            return
        self.active = False
        self.root.hide()
        self.game.messageDisplayer.show()
        self.returnObject.returnFromBuild()