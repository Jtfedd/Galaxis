import sys

from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

from src.core.data import Button, Font3


class PauseScreen:
    def __init__(self, viewer):
        self.galaxy = OnscreenImage(parent=viewer.game.panels.rightPanel, image="data/images/galaxy.png", scale=(1.7777/1.5, 1, 1/1.5), pos=(-0.8, -1, -0.55))
        self.root = viewer.game.panels.leftPanel.attachNewNode("PauseScreenRoot")
        self.elements = []
        self.elements.append(OnscreenText(text = "Paused", parent = self.root, font = Font3, fg = (1,1,1,1), scale = .3, pos = (0.15, 0.6), align = TextNode.ALeft))
        self.elements.append(Button(text = "Resume", align = TextNode.ALeft, scale=0.07, parent = self.root, pos = (0.15, 0, 0.45), command = viewer.unpause))
        self.elements.append(Button(text = "Save", align = TextNode.ALeft, scale = 0.07, parent = self.root, pos = (0.15, 0, 0.35), command = None)) #TODO
        self.elements.append(Button(text = "Save and Exit to Menu", align = TextNode.ALeft, scale = 0.07, parent = self.root, pos = (0.15, 0, 0.25), command = sys.exit)) #TODO
        self.elements.append(Button(text = "Save and Exit to Desktop", align = TextNode.ALeft, scale = 0.07, parent = self.root, pos = (0.15, 0, 0.15), command = sys.exit)) #TODO

        self.hide()

    def show(self):
        self.root.show()
        self.galaxy.show()

    def hide(self):
        self.root.hide()
        self.galaxy.hide()

    def destroy(self):
        while len(self.elements) > 0:
            e = self.elements.pop()
            e.destroy()
        self.root.removeNode()