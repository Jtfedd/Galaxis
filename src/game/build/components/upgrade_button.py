from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DGG
from panda3d.core import TextNode

from src.core.data import RejectButton, Font1

class UpgradeButton:
    def __init__(self, buildScreen, parent, upgradeable, action, extraArgs):
        extraArgs.append(self)
        self.buildScreen = buildScreen
        self.upgradeable = upgradeable
        self.root = parent.attachNewNode("UpgradeButton")
        self.root.setX(1.1)
        self.button = RejectButton(image="data/images/white.png", scale=(0.6, 1, 0.0575), parent=self.root, command=action, extraArgs=extraArgs)
        self.border = OnscreenImage(image="data/images/black.png", scale=(0.6, 1, 0.0092), pos=(0, 0, -0.0575), parent=self.root)
        self.button.button.bind(DGG.ENTER, command=self.displayFooter)
        self.button.button.bind(DGG.EXIT, command=self.clearFooter)

        self.nameText = OnscreenText(text=self.upgradeable.getUpgradeName(), parent=self.root, scale=0.06, pos=(-0.565, -0.015), fg=(.1,.1,.1,1), font=Font1, align=TextNode.ALeft)

    def updateText(self):
        self.nameText.setText(self.upgradeable.getUpgradeName())

    def setZ(self, z):
        self.root.setZ(z)

    def displayFooter(self, arg):
        self.buildScreen.footer.setText(self.upgradeable.getUpgradeDescription())
        self.buildScreen.footer.setCost(self.upgradeable.getUpgradeCost())
        self.button.setRolloverTrue(arg)

    def clearFooter(self, arg):
        self.buildScreen.footer.clear()
        self.button.setRolloverFalse(arg)

    def reject(self, reason):
        self.button.reject()
        self.buildScreen.footer.setText(reason, True)

    def disable(self):
        self.button.disable()

    def enable(self):
        self.button.enable()

    def destroy(self):
        self.button.destroy()
        self.border.destroy()
        self.nameText.destroy()
        self.root.removeNode()