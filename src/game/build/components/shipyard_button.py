from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DGG

from src.core.data import RejectButton, Font1

class ShipyardButton:
    def __init__(self, buildScreen, parent, action, extraArgs):
        extraArgs.append(self)
        self.buildScreen = buildScreen
        self.root = parent.attachNewNode("ShipyardButton")
        self.root.setPos(-0.075, 0, 0.475)
        self.button = RejectButton(image="data/images/white.png", scale=(0.5, 1, 0.105), parent=self.root, command=action, extraArgs=extraArgs)
        self.button.button.bind(DGG.ENTER, command=self.displayFooter)
        self.button.button.bind(DGG.EXIT, command=self.clearFooter)

        self.cost = {"science": 500, "credits": 7500, "fuel": 0}

        self.nameText = OnscreenText(text="Build Second Shipyard", parent=self.root, scale=0.06, pos=(0, -0.015), fg=(.1, .1, .1, 1), font=Font1)

    def displayFooter(self, arg):
        self.buildScreen.footer.setText("Construct a second shipyard, allowing two items to be build/researched at once.")
        self.buildScreen.footer.setCost(self.cost)
        self.button.setRolloverTrue(arg)

    def clearFooter(self, arg):
        self.buildScreen.footer.clear()
        self.button.setRolloverFalse(arg)

    def enable(self):
        self.button.enable()

    def disable(self):
        self.button.disable()

    def reject(self, reason):
        self.button.reject()
        self.buildScreen.footer.setText(reason, True)

    def destroy(self):
        self.button.destroy()
        self.nameText.destroy()
        self.root.removeNode()