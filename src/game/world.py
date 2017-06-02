import math
import random

from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject

from ship import *
from src.core.data import Button, Font1
from src.core.showbase import messenger
from src.core.util import calcRatio, randomSign
from src.game.shipselection import ShipSelection
from src.game.skybox import Skybox


class World(DirectObject):
    """World class, which runs in the background simulating everything
    for a particular planetary system."""
    
    def __init__(self, game, name, pos):
        self.game = game
        self.name = name
        self.pos = pos
        
        self.ships = []
        self.state = "neutral"

        self.worldRoot = render.attachNewNode("worldroot")
        self.mapRoot = render.attachNewNode("maproot")

        self.worldViewActive = False
        self.mapViewActive = False
        self.active = True

        self.worldRoot.hide()
        self.mapRoot.hide()

        self.title = Title(self.name)
        self.toolbar = Toolbar(self)
        self.toolbar.ctrlBtn.disable()
        self.toolbar.moveBtn.disable()

        self.grid = loader.loadModel("data/models/grid/grid")
        self.grid.setDepthWrite(False)
        self.grid.reparentTo(self.mapRoot)
        self.cameraMoveBase = self.grid.attachNewNode("cameraMoveBase")
        self.cursor3d = loader.loadModel("data/models/cursor_3d/cursor_3d")
        self.cursor3d.reparentTo(self.cameraMoveBase)
        self.cameraBase = self.cameraMoveBase.attachNewNode("cameraBase")
        self.cameraBase.setP(20)
        self.cameraLoc = self.cameraBase.attachNewNode("cameraLoc")
        self.cameraLoc.setPos(self.cameraBase, (0, 10, 0))
        self.cameraLoc.lookAt(self.cameraBase)

        self.grid.setLightOff()
        self.grid.setScale(10)
        self.grid.setTransparency(TransparencyAttrib.MAlpha)
        self.grid.setAlphaScale(.1)
        self.gridTS = self.grid.findTextureStage("Texture")

        self.cursor3d.setLightOff()
        self.cursor3d.setScale(.35)

        self.canRotate = False
        self.lastMouseX = None
        self.lastMouseY = None

        self.canDrag = False
        self.isDragging = False
        self.dragStartX = 0
        self.dragStartY = 0
        self.dragIndicator = DragIndicator()
        self.click = False

        self.isCentering = False
        self.centeringStartX = 0
        self.centeringStartY = 0
        self.centeringStartZ = 0
        self.centeringStartZoom = 0

        self.centerButton = Button(pos = (-0.1, 0, -0.9),
                                   scale = 0.05,
                                   minAlpha = 0.75,
                                   image = "data/buttons/center.png",
                                   parent = self.game.panels.rightPanel,
                                   command = self.center)
        self.centerButton.hide()

        self.selectedShips = ShipSelection(self)
        self.selectedShips.setZ(0.95)
        self.shouldClearSelection = False

        self.mapKeys = [0, 0, 0, 0, 0, 0]

        self.skybox = Skybox(self.name, self.worldRoot)

    def setRotate(self, val):
        self.canRotate = val
        if val and base.mouseWatcherNode.hasMouse():
            self.lastMouseX = base.mouseWatcherNode.getMouse().getX()
            self.lastMouseY = base.mouseWatcherNode.getMouse().getY()
        else:
            self.lastMouseX = None
            self.lastMouseY = None

    def onClick(self, clearSelection = True):
        self.click = True
        self.shouldClearSelection = clearSelection
        if base.mouseWatcherNode.hasMouse():
            self.dragStartX = base.mouseWatcherNode.getMouse().getX() * calcRatio()
            self.dragStartY = base.mouseWatcherNode.getMouse().getY()
            self.canDrag = True
            self.isDragging = False
            self.dragIndicator.setStart(self.dragStartX, self.dragStartY)
            self.dragIndicator.setEnd(self.dragStartX, self.dragStartY)

    def onClickUp(self):
        if not self.click:
            return
        self.click = False

        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouse().getX() * calcRatio()
            y = base.mouseWatcherNode.getMouse().getY()
            if self.isDragging:
                self.selectAll(min(self.dragStartX, x), min(self.dragStartY, y), max(self.dragStartX, x), max(self.dragStartY, y))
            else:
                self.selectFirst(x-0.05, y-0.05, x+0.05, y+0.05)

        if self.canDrag:
            self.canDrag = False
            self.isDragging = False
            self.dragIndicator.hide()

    def selectAll(self, x1, y1, x2, y2):
        if self.shouldClearSelection:
            self.clearSelection()
        for ship in self.ships:
            if ship.team == self.game.playerTeam:
                pos = map3dToAspect2d(self.mapRoot, ship.mapModel.getPos())
                if pos is not None:
                    if x1 < pos.getX() < x2 and y1 < pos.getZ() < y2:
                        self.selectShip(ship)
        self.selectedShips.rebuild()

    def selectFirst(self, x1, y1, x2, y2):
        if self.shouldClearSelection:
            self.clearSelection()
        closestShip = None
        closestDist = 0
        for ship in self.ships:
            pos = map3dToAspect2d(self.mapRoot, ship.mapModel.getPos())
            if pos is not None:
                if x1 < pos.getX() < x2 and y1 < pos.getZ() < y2:
                    if closestShip is None:
                        closestShip = ship
                        closestDist = ship.mapModel.getY(base.camera)
                    else:
                        if ship.mapModel.getY(base.camera) < closestDist:
                            closestShip = ship
                            closestDist = ship.mapModel.getY(base.camera)
        if closestShip is not None:
            if self.selectedShips.__contains__(closestShip):
                self.deselectShip(closestShip)
            else:
                self.selectShip(closestShip)
        self.selectedShips.rebuild()

    def selectAllFriendly(self):
        if len(self.selectedShips) > 0:
            self.clearSelection()
        else:
            for ship in self.ships:
                if ship.team == self.game.playerTeam:
                    self.selectShip(ship)

    def clearSelection(self):
        while len(self.selectedShips) > 0:
            self.selectedShips[0].deselect()
            self.selectedShips.remove(self.selectedShips[0])

    def deselectShip(self, ship):
        ship.deselect()
        self.selectedShips.remove(ship)
        self.selectedShips.rebuild()

    def selectShip(self, ship):
        ship.select()
        self.selectedShips.append(ship)

    def center(self):
        self.isCentering = True
        self.centeringStartX = self.grid.getX()
        self.centeringStartY = self.grid.getY()
        self.centeringStartZ = self.grid.getZ()
        self.centeringStartZoom = self.grid.getScale().getX() - 10
        taskMgr.add(self.centerTask, "center")

    def centerTask(self, task):
        timeFact = task.time
        done = False
        if timeFact > 1:
            timeFact = 1
            done = True
        timeFact *= (math.pi / 2.0)

        cos2 = math.cos(timeFact) ** 2

        x = self.grid.getX()
        y = self.grid.getY()

        self.grid.setPos(self.centeringStartX*cos2, self.centeringStartY*cos2, self.centeringStartZ*cos2)
        self.grid.setScale(10 + self.centeringStartZoom*cos2)

        texOffset = self.grid.getTexOffset(self.gridTS)
        self.grid.setTexOffset(self.gridTS, texOffset + LVecBase2(self.grid.getX() - x, self.grid.getY() - y) / self.grid.getScale().getX() * 3 / 4)

        if done:
            self.isCentering = False
            return task.done

        return task.cont

    def activateMap(self):
        self.mapRoot.show()
        self.title.show()
        self.toolbar.show()
        self.centerButton.show()
        self.selectedShips.show()
        self.mapViewActive = True
        self.active = True
        self.accept('mouse1', self.onClick)
        self.accept('mouse1-up', self.onClickUp)
        self.accept('shift-mouse1', self.onClick, [False])
        self.accept('mouse3', self.setRotate, [True])
        self.accept('mouse3-up', self.setRotate, [False])
        self.accept('a', self.setMapKey, [0, 1])
        self.accept('a-up', self.setMapKey, [0, 0])
        self.accept('d', self.setMapKey, [1, 1])
        self.accept('d-up', self.setMapKey, [1, 0])
        self.accept('s', self.setMapKey, [2, 1])
        self.accept('s-up', self.setMapKey, [2, 0])
        self.accept('w', self.setMapKey, [3, 1])
        self.accept('w-up', self.setMapKey, [3, 0])
        self.accept('e', self.setMapKey, [4, 1])
        self.accept('e-up', self.setMapKey, [4, 0])
        self.accept('q', self.setMapKey, [5, 1])
        self.accept('q-up', self.setMapKey, [5, 0])
        self.accept('wheel_up', self.zoom, [-1])
        self.accept('wheel_down', self.zoom, [1])
        self.accept('z', self.selectAllFriendly)

    def setMapKey(self, key, val):
        self.mapKeys[key] = val

    def zoom(self, scrollDir):
        self.grid.setScale(min(max(5, self.grid.getScale().getX()+scrollDir), 100))
        base.camera.setPos(self.cameraLoc.getPos(render))
        base.camera.setHpr(self.cameraLoc.getHpr(render))

    def deactivateMap(self):
        self.ignoreAll()
        self.mapViewActive = False
        self.click = False
        self.tryDeactivate()
        self.title.hide()
        self.toolbar.hide()
        self.selectedShips.hide()
        self.mapRoot.hide()
        self.centerButton.hide()
        for ship in self.ships:
            ship.syncMapModel()

    def enterBuild(self):
        self.deactivateMap()
        self.game.buildScreen.activate(self)

    def returnFromBuild(self):
        self.activateMap()

    def tryDeactivate(self):
        if self.mapViewActive or self.worldViewActive:
            return

        if len(self.ships) == 0:
            self.active = False
            return

        for i in range(1, len(self.ships)):
            if self.ships[i].team != self.ships[0].team:
                return

        self.active = False

    def activateWorld(self):
        self.worldRoot.show()
        
    def addShipNew(self, shipName, quantity = 1):
        coords = [5000 * randomSign(), random.randrange(6000)-3000, random.randrange(6000)-3000]
        random.shuffle(coords)

        x = coords[0]
        y = coords[1]
        z = coords[2]

        for i in range(quantity):
            ztmp = z
            ytmp = y
            xtmp = x
            if x == 5000 or x == -5000:
                ytmp += 2*i*100
            else:
                xtmp += 2*i*100

            tmpShip = Ship(self, self.game, shipName, (xtmp, ytmp, ztmp))
            self.ships.append(tmpShip)

        self.checkState()
        self.active = True
        self.tryDeactivate()

    def addShipMove(self, ships, side):
        pass

    def addShipDirect(self, ship):
        self.ships.append(ship)
        self.active = True
        self.tryDeactivate()

    def removeShip(self, ship):
        self.ships.remove(ship)
        self.tryDeactivate()
    
    def setState(self, state):
        messenger.send("world_state_change", [self, state, self.state])
        self.state = state
        
    def checkState(self):
        newState = self.state
        if self.state == "war":
            newState = "neutral"
        hasRed = False
        hasBlue = False
        for s in self.ships:
            if s.team == "red":
                hasRed = True
            if s.team == "blue":
                hasBlue = True
        if hasRed:
            newState = "red"
        if hasBlue:
            newState = "blue"
        if hasRed and hasBlue:
            newState = "war"
        if newState != self.state:
            self.setState(newState)
    
    def update(self, dt):
        if not self.active:
            return

        for ship in self.ships:
            ship.update(dt)

        if self.mapViewActive:
            if self.canRotate:
                if base.mouseWatcherNode.hasMouse():
                    xPos = base.mouseWatcherNode.getMouse().getX()
                    yPos = base.mouseWatcherNode.getMouse().getY()
                    if self.lastMouseX is not None:
                        self.cameraMoveBase.setH(self.mapRoot, self.cameraMoveBase.getH(self.mapRoot) + (xPos - self.lastMouseX) * -100)
                    self.lastMouseX = xPos
                    if self.lastMouseY is not None:
                        self.cameraBase.setP(self.mapRoot, min(max(self.cameraBase.getP(self.mapRoot) + (yPos - self.lastMouseY) * -75, 10), 50))
                    self.lastMouseY = yPos
                else:
                    self.lastMouseX = None
                    self.lastMouseY = None

            if self.canDrag:
                if base.mouseWatcherNode.hasMouse():
                    xPos = base.mouseWatcherNode.getMouse().getX() * calcRatio()
                    yPos = base.mouseWatcherNode.getMouse().getY()
                    if not self.isDragging:
                        if (xPos - self.dragStartX)**2 + (yPos-self.dragStartY)**2 > .001:
                            self.isDragging = True
                            self.dragIndicator.show()
                    if self.isDragging:
                        self.dragIndicator.setEnd(xPos, yPos)

            x = self.grid.getX()
            y = self.grid.getY()

            self.grid.setPos(self.cameraMoveBase, 10 * self.mapKeys[0] * dt, 10 * self.mapKeys[2] * dt, 10 * self.mapKeys[4] * dt)
            self.grid.setPos(self.cameraMoveBase, -10 * self.mapKeys[1] * dt, -10 * self.mapKeys[3] * dt, -10 * self.mapKeys[5] * dt)

            if self.grid.getX() > 5000:
                self.grid.setX(5000)
            elif self.grid.getX() < -5000:
                self.grid.setX(-5000)
            if self.grid.getY() > 5000:
                self.grid.setY(5000)
            elif self.grid.getY() < -5000:
                self.grid.setY(-5000)
            if self.grid.getZ() > 5000:
                self.grid.setZ(5000)
            elif self.grid.getZ() < -5000:
                self.grid.setZ(-5000)

            base.camera.setPos(self.cameraLoc.getPos(render))
            base.camera.setHpr(self.cameraLoc.getHpr(render))

            texOffset = self.grid.getTexOffset(self.gridTS)
            self.grid.setTexOffset(self.gridTS, texOffset+LVecBase2(self.grid.getX()-x, self.grid.getY()-y)/self.grid.getScale().getX()*3/4)

            self.selectedShips.update()

            self.skybox.update()

class Title:
    def __init__(self, name):
        self.titleBg = OnscreenImage(image='data/images/black.png',
                                     pos=(0, 0, .95),
                                     scale=(0.4, 1, 0.05))
        self.titleBg.setTransparency(TransparencyAttrib.MAlpha)
        self.titleBg.setAlphaScale(0.5)

        self.titleText = OnscreenText(text=name,
                                      scale=0.06,
                                      fg=(1, 1, 1, 1),
                                      pos=(0, 0.935),
                                      font=Font1)

        self.hide()

    def show(self):
        self.titleBg.show()
        self.titleText.show()

    def hide(self):
        self.titleBg.hide()
        self.titleText.hide()

    def destroy(self):
        self.titleBg.destroy()
        self.titleText.destroy()

class DragIndicator:
    def __init__(self):
        self.card = OnscreenImage(image='data/images/grey.png')
        self.card.setTransparency(TransparencyAttrib.MAlpha)
        self.card.setAlphaScale(0.2)
        self.card.hide()

        self.startX = 0
        self.startY = 0
        self.endX = 0
        self.endY = 0

    def show(self):
        self.card.show()

    def hide(self):
        self.card.hide()

    def destroy(self):
        self.card.destroy()

    def setStart(self, x, y):
        self.startX = x
        self.startY = y
        self.update()

    def setEnd(self, x, y):
        self.endX = x
        self.endY = y
        self.update()

    def update(self):
        self.card.setPos((self.startX + self.endX)/2.0, 0, (self.startY + self.endY)/2.0)
        self.card.setScale((self.endX - self.startX)/2.0, 1, (self.endY - self.startY)/2.0)

class Toolbar:
    def __init__(self, world):
        self.world = world

        self.bg = OnscreenImage(image='data/images/black.png',
                                pos=(0, 0, -.95),
                                scale=(0.8, 1, 0.05))
        self.bg.setTransparency(TransparencyAttrib.MAlpha)
        self.bg.setAlphaScale(0.7)

        self.ctrlBtn = Button(text='Control', pos=(-.65, 0, -.97), scale=0.06, command=None) # TODO
        self.buildBtn = Button(text='Build', pos=(-0.216666, 0, -.97), scale=0.06, command=self.world.enterBuild)
        self.moveBtn = Button(text='Move', pos=(.216666, 0, -.97), scale=0.06, command=None) # TODO
        self.backBtn = Button(text='Back', pos=(.65, 0, -.97), scale=0.06, command=self.backCmd)

        self.hide()

    def backCmd(self):
        self.world.deactivateMap()
        self.world.game.mapViewer.activate()

    def hide(self):
        self.bg.hide()
        self.ctrlBtn.hide()
        self.buildBtn.hide()
        self.moveBtn.hide()
        self.backBtn.hide()

    def show(self):
        self.bg.show()
        self.ctrlBtn.show()
        self.buildBtn.show()
        self.moveBtn.show()
        self.backBtn.show()

    def destroy(self):
        self.bg.destroy()
        self.ctrlBtn.destroy()
        self.buildBtn.destroy()
        self.moveBtn.destroy()
        self.backBtn.destroy()