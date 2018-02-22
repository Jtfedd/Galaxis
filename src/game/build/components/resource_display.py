from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from panda3d.core import TransparencyAttrib

from src.core.data import Font1

class ResourceDisplay:
    def __init__(self, root):
        self.root = root.attachNewNode("ResourceDisplay")

        self.scienceImg = OnscreenImage(image="data/images/science.png",
                                        pos=(0, 0, .1),
                                        scale=0.045,
                                        parent=self.root)
        self.scienceImg.setTransparency(TransparencyAttrib.MAlpha)
        self.scienceCost = OnscreenText(scale=0.06, pos=(0.06, 0.08), fg=(1, 1, 1, 1), align=TextNode.ALeft,
                                        parent=self.root, font=Font1)

        self.creditsImg = OnscreenImage(image="data/images/currency.png",
                                        pos=(0, 0, 0),
                                        scale=0.045,
                                        parent=self.root)
        self.creditsImg.setTransparency(TransparencyAttrib.MAlpha)
        self.creditsCost = OnscreenText(scale=0.06, pos=(0.06, -.02), fg=(1, 1, 1, 1), align=TextNode.ALeft,
                                        parent=self.root, font=Font1)

        self.fuelImg = OnscreenImage(image="data/images/fuel.png",
                                     pos=(0, 0, -.1),
                                     scale=0.045,
                                     parent=self.root)
        self.fuelImg.setTransparency(TransparencyAttrib.MAlpha)
        self.fuelCost = OnscreenText(scale=0.06, pos=(0.06, -.12), fg=(1, 1, 1, 1), align=TextNode.ALeft,
                                     parent=self.root, font=Font1)

    def update(self, resources):
        self.scienceCost.setText(str(resources["science"]))
        self.creditsCost.setText(str(resources["credits"]))
        self.fuelCost.setText(str(resources["fuel"]))

    def setPos(self, x, y, z):
        self.root.setPos(x, y, z)