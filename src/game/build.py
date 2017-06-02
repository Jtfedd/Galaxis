from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DGG
from direct.showbase.DirectObject import DirectObject
from panda3d.core import TextNode
from panda3d.core import WindowProperties
from panda3d.core import TransparencyAttrib

from src.core.showbase import base, aspect2d

from src.core.data import Button, RejectButton, Font1, Font3
from src.core.util import calcRatio

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
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(1.7, 1, 0.002), pos=(0, 0, -0.9)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(1.7, 1, 0.002), pos=(0, 0, -0.6)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(1.7, 1, 0.002), pos=(0, 0, 0.65)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(0.002, 1, 0.575), pos=(-1.65, 0, 0.025)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(0.002, 1, 0.575), pos=(-0.6, 0, 0.025)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(0.002, 1, 0.575), pos=(0.45, 0, 0.025)))
        self.elements.append(OnscreenImage(image="data/images/white.png", parent=self.root, scale=(0.002, 1, 0.03), pos=(1.425, 0, -.95)))

        self.shipyardButton = None

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