from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *

from src.core.data import Font1


class ShipSelection:
    def __init__(self, world):
        self.world = world
        self.selectedShips = []
        self.root = world.game.panels.rightPanel.attachNewNode("selection-root")
        self.uiRoot = self.root.attachNewNode("selection-ui-root")

        self.bg = OnscreenImage(image = "data/images/grey.png",
                                scale = (0.3, 1, 0.2),
                                pos = (0.3, 0, -0.2),
                                parent = self.uiRoot)
        self.bg.setTransparency(TransparencyAttrib.MAlpha)
        self.bg.setAlphaScale(0.5)

        self.title = OnscreenText(text = "",
                                  scale = 0.07,
                                  parent = self.uiRoot,
                                  align = TextNode.ALeft,
                                  pos = (0.03, -0.075),
                                  fg = (1,1,1,1),
                                  font = Font1)

        self.subTitle = OnscreenText(text = "",
                                     scale = 0.05,
                                     parent = self.uiRoot,
                                     align = TextNode.ALeft,
                                     pos = (0.03, -0.13),
                                     fg = (1,1,1,1),
                                     font = Font1)

        self.healthBar = OnscreenImage(image = "data/images/green.png",
                                       parent = self.uiRoot)
        self.missileBar = OnscreenImage(image = "data/images/yellow.png",
                                        parent = self.uiRoot)
        self.torpedoBar = OnscreenImage(image = "data/images/purple.png",
                                        parent = self.uiRoot)

        self.healthBar.hide()
        self.missileBar.hide()
        self.torpedoBar.hide()

        self.root.setX(-0.65)

        self.rebuild()
        self.hide()

    def append(self, newShip):
        if self.selectedShips.__contains__(newShip):
            return
        self.selectedShips.append(newShip)
        self.update()

    def remove(self, oldShip):
        self.selectedShips.remove(oldShip)
        self.update()

    def setZ(self, y):
        self.root.setZ(y)

    def show(self):
        self.root.show()

    def hide(self):
        self.root.hide()

    def rebuild(self):
        if len(self.selectedShips) == 0:
            self.uiRoot.hide()
            self.world.toolbar.ctrlBtn.disable()
            self.world.toolbar.moveBtn.disable()
            return
        self.uiRoot.show()
        self.world.toolbar.moveBtn.enable()
        if len(self.selectedShips) == 1:
            self.bg.setPos(Vec3(0.3, 0, -0.13))
            self.bg.setScale(Vec3(0.3, 1, 0.13))
            self.subTitle.show()
            self.title.setText(self.selectedShips[0].callsign)
            self.subTitle.setText(self.selectedShips[0].name)
            self.healthBar.show()
            self.missileBar.show()
            self.torpedoBar.show()
            if self.selectedShips[0].size <= 1:
                self.world.toolbar.ctrlBtn.enable()
            return

        self.bg.setPos(Vec3(0.3, 0, -0.075))
        self.bg.setScale(Vec3(0.3, 1, 0.075))
        self.subTitle.hide()
        self.title.setText(str(len(self.selectedShips))+" Selected")
        self.healthBar.show()
        self.missileBar.hide()
        self.torpedoBar.hide()
        self.world.toolbar.ctrlBtn.disable()

        self.update()

    def update(self):
        if len(self.selectedShips) == 0:
            return

        if len(self.selectedShips) == 1:
            shield = 1
            missile = 1
            torpedo = 1

            try:
                shield = self.selectedShips[0].health/float(self.selectedShips[0].maxHealth)
            except ZeroDivisionError:
                pass

            try:
                missile = self.selectedShips[0].missiles/float(self.selectedShips[0].maxMissiles)
            except ZeroDivisionError:
                pass

            try:
                torpedo = self.selectedShips[0].torpedos/float(self.selectedShips[0].maxTorpedos)
            except ZeroDivisionError:
                pass

            self.healthBar.setPos(Vec3(0.3 - (0.27 * (1.0-shield)), 0, -0.18))
            self.healthBar.setScale(Vec3(shield*0.27, 1, 0.005))

            self.missileBar.setPos(Vec3(0.3 - (0.27 * (1.0-missile)), 0, -0.2))
            self.missileBar.setScale(Vec3(missile*0.27, 1, 0.005))

            self.torpedoBar.setPos(Vec3(0.3 - (0.27 * (1.0-torpedo)), 0, -0.22))
            self.torpedoBar.setScale(Vec3(torpedo*0.27, 1, 0.005))

            return

        health = 0
        n = 0
        for s in self.selectedShips:
            health += self.selectedShips[0].health/float(self.selectedShips[0].maxHealth)
            n += 1
        health /= float(n)

        self.healthBar.setPos(Vec3(0.3 - (0.27 * (1.0-health)), 0, -0.12))
        self.healthBar.setScale(Vec3(health*0.27, 1, 0.005))

    def destroy(self):
        self.bg.destroy()
        self.title.destroy()
        self.subTitle.destroy()
        self.healthBar.destroy()
        self.missileBar.destroy()
        self.torpedoBar.destroy()
        self.uiRoot.removeNode()
        self.root.removeNode()

    def __getitem__(self, item):
        return self.selectedShips[item]

    def __len__(self):
        return len(self.selectedShips)

    def __contains__(self, item):
        return self.selectedShips.__contains__(item)