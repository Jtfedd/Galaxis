from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from panda3d.core import TransparencyAttrib

from src.core.data import Font1

class BuildScreenFooter:
    def __init__(self, buildScreen):
        self.buildScreen = buildScreen

        self.text = OnscreenText(font=Font1, parent = buildScreen.root, scale=0.06, pos=(-1.65, -.97), fg=(1,1,1,1), align=TextNode.ALeft)

        self.scienceImg = OnscreenImage(image="data/images/science.png",
                                        pos=(0, 0, -0.95),
                                        scale=0.045,
                                        parent=buildScreen.root)
        self.scienceImg.setTransparency(TransparencyAttrib.MAlpha)
        self.scienceCost = OnscreenText(scale=0.06, pos=(0, -.97), fg=(1,1,1,1), align=TextNode.ALeft, parent=buildScreen.root, font=Font1)
        self.scienceImg.hide()
        self.scienceCost.hide()

        self.creditsImg = OnscreenImage(image="data/images/currency.png",
                                        pos=(0, 0, -0.95),
                                        scale=0.045,
                                        parent=buildScreen.root)
        self.creditsImg.setTransparency(TransparencyAttrib.MAlpha)
        self.creditsCost = OnscreenText(scale=0.06, pos=(0, -.97), fg=(1,1,1,1), align=TextNode.ALeft, parent=buildScreen.root, font=Font1)
        self.creditsImg.hide()
        self.creditsCost.hide()

        self.fuelImg = OnscreenImage(image="data/images/fuel.png",
                                     pos=(0, 0, -.95),
                                     scale=0.045,
                                     parent=buildScreen.root)
        self.fuelImg.setTransparency(TransparencyAttrib.MAlpha)
        self.fuelCost = OnscreenText(scale=0.06, pos=(0, -.97), fg=(1,1,1,1), align=TextNode.ALeft, parent=buildScreen.root, font=Font1)
        self.fuelImg.hide()
        self.fuelCost.hide()

    def setText(self, text, warning=False):
        self.text.setText(text)
        if warning:
            self.text.setColorScale(1, 0, 0, 1)
        else:
            self.text.setColorScale(1, 1, 1, 1)
        self.text.show()

    def setCost(self, resources):
        count = 0

        if resources["fuel"] > 0:
            self.fuelImg.show()
            self.fuelCost.setText(str(resources["fuel"]))
            self.fuelCost.show()

            self.fuelImg.setX(1.1)
            self.fuelCost.setX(1.16)

            count += 1

        if resources["credits"] > 0:
            self.creditsImg.show()
            self.creditsCost.setText(str(resources["credits"]))
            self.creditsCost.show()

            self.creditsImg.setX(1.1-.35*count)
            self.creditsCost.setX(1.16-.35*count)

            count += 1

        if resources["science"] > 0:
            self.scienceImg.show()
            self.scienceCost.setText(str(resources["science"]))
            self.scienceCost.show()

            self.scienceImg.setX(1.1-.35*count)
            self.scienceCost.setX(1.16-.35*count)

    def clear(self):
        self.text.hide()
        self.fuelImg.hide()
        self.fuelCost.hide()
        self.creditsImg.hide()
        self.creditsCost.hide()
        self.scienceImg.hide()
        self.scienceCost.hide()