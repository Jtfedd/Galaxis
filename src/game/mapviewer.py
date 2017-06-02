from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject

from skybox import *
from src.core.data import Button, BackgroundCard, Font1
from src.core.showbase import *
from src.game.pause import PauseScreen

base.setBackgroundColor(0, 0, 0)

class MapViewer(DirectObject):
    """The highest level of user interaction with the game, an overall
    view of the systems with information about each. From here the player
    can build units, or enter into a system to control it rts-style"""

    def __init__(self, game):
        self.game = game
        self.type = "MapViewer"

        self.worldIcons = []
        self.connectionIcons = []
        self.root = render.attachNewNode("mapviewer_root")
        self.root.setLightOff()

        self.cameraBase = self.root.attachNewNode("Camera base")
        self.cameraBase.setP(45)
        self.cameraBase.setZ(-10)

        self.canRotate = False
        self.lastMouseX = None
        self.lastMouseY = None
        self.clickingEnabled = True

        self.selection = None

        self.skybox = Skybox("galaxy", self.root)

        for w in game.worlds:
            self.addWorld(w)

        self.infoPanel = InfoPanel(self)
        self.pauseScreen = PauseScreen(self)

        self.traverser = CollisionTraverser()
        self.handler = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = base.camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.traverser.addCollider(self.pickerNP, self.handler)

        self.active = False
        self.activate()

    def enterSystem(self):
        self.deactivate()
        self.selection.activateMap()

    def enterBuild(self):
        self.deactivate()
        self.game.buildScreen.activate(self)

    def returnFromBuild(self):
        self.activate()

    def addWorld(self, world):
        for w in self.worldIcons:
            if (w.pos - world.pos).length() < 20:
                self.addConnection(w.pos, world.pos)
        self.worldIcons.append(MapViewerPlanet(self, world))

    def addConnection(self, pos1, pos2):
        self.connectionIcons.append(MapViewerConnection(self, pos1, pos2))

    def click(self):
        if base.mouseWatcherNode.hasMouse() and self.clickingEnabled:
            mpos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            self.traverser.traverse(render)
            if self.handler.getNumEntries() > 0:
                self.handler.sortEntries()
                pickedObj = self.handler.getEntry(0).getIntoNodePath()
                pickedObj = pickedObj.findNetTag('clicktag')
                if not pickedObj.isEmpty():
                    for w in self.worldIcons:
                        if w.hitbox == pickedObj:
                            w.toggleSelected()
                            if w.selected:
                                self.selection = w.world
                            else:
                                self.selection = None
            else:
                for w in self.worldIcons:
                    w.selected = False
                    self.selection = None
            self.infoPanel.update()

    def setRotate(self, val):
        self.canRotate = val
        if val and base.mouseWatcherNode.hasMouse():
            self.lastMouseX = base.mouseWatcherNode.getMouse().getX()
            self.lastMouseY = base.mouseWatcherNode.getMouse().getY()
        else:
            self.lastMouseX = None
            self.lastMouseY = None

    def update(self, dt):
        if not self.active:
            return

        shouldUpdatePanel = False

        for w in self.worldIcons:
            if w.update(dt):
                shouldUpdatePanel = True

        if shouldUpdatePanel:
            self.infoPanel.update()

        if self.canRotate:
            if base.mouseWatcherNode.hasMouse():
                xPos = base.mouseWatcherNode.getMouse().getX()
                yPos = base.mouseWatcherNode.getMouse().getY()
                if self.lastMouseX is not None:
                    self.cameraBase.setH(self.root, self.cameraBase.getH(self.root) + (xPos - self.lastMouseX) * -100)
                self.lastMouseX = xPos
                if self.lastMouseY is not None:
                    self.cameraBase.setP(self.root, min(max(self.cameraBase.getP(self.root) + (yPos - self.lastMouseY) * -75, 0), 50))
                self.lastMouseY = yPos
            else:
                self.lastMouseX = None
                self.lastMouseY = None

        base.camera.setPos(self.cameraBase, (0, 100, 0))
        base.camera.lookAt(self.cameraBase)

        self.skybox.update()

    def activate(self):
        self.active = True
        self.root.show()
        self.infoPanel.show()
        self.update(0)
        self.accept("mouse1", self.click)
        self.accept('mouse3', self.setRotate, [True])
        self.accept('mouse3-up', self.setRotate, [False])

    def deactivate(self):
        self.active = False
        self.root.hide()
        self.infoPanel.hide()
        self.ignoreAll()

    def pause(self):
        self.game.pause()
        self.deactivate()
        self.pauseScreen.show()

    def unpause(self):
        self.game.pause()
        self.activate()
        self.pauseScreen.hide()

    def destroy(self):
        for w in self.worldIcons:
            w.destroy()
        for c in self.connectionIcons:
            c.destroy()
        self.skybox.destroy()
        self.ignoreAll()
        self.root.removeNode()

class InfoPanel:
    def __init__(self, viewer):
        self.viewer = viewer
        self.world = None

        self.root = self.viewer.game.panels.rightPanel.attachNewNode('infopanel')
        self.root.setPos(-.65, 0, .95) # Top right of panel

        self.panelElements = []

        self.nameBg = OnscreenImage(image='data/images/black.png',
                                pos=(0, 0, .95),
                                scale=(0.25+len(self.viewer.game.gameName)/57.0, 1, 0.05))
        self.nameBg.setTransparency(TransparencyAttrib.MAlpha)
        self.nameBg.setAlphaScale(0.5)

        self.nameText = OnscreenText(text = "Commander "+self.viewer.game.gameName,
                                scale = 0.06,
                                fg = (1,1,1,1),
                                pos = (0, 0.935),
                                font = Font1)

        self.toolbar = Toolbar(self.viewer)
        self.update()

    def update(self):
        self.world = self.viewer.selection

        self.teardownInfoPanel()

        if self.world is not None:
            self.buildWorldInfoPanel()
            self.toolbar.enterBtn.enable()
        else:
            self.buildTeamInfoPanel()
            self.toolbar.enterBtn.disable()

    def teardownInfoPanel(self):
        for e in self.panelElements:
            e.destroy()
        self.panelElements = []

    def buildWorldInfoPanel(self):
        tmp = BackgroundCard(Point3(0.3, 0, -.8), Point3(0.3, 1, 0.8), 'grey', .2, self.root, True)

        self.panelElements.append(tmp)

        tmp = OnscreenImage(image = 'data/skyboxes/'+self.world.name+'/thumb.png',
                            parent = self.root,
                            pos = (.3, 0, -.3),
                            scale = .29)

        self.panelElements.append(tmp)

        state = self.world.state
        if state == self.viewer.game.playerTeam: state = 'Allied'
        else:
            if state == 'war': state = 'War'
            elif state == 'neutral': state = 'Neutral'
            else: state = 'Enemy'

        tmp = OnscreenText(text = self.world.name + ' - ' + state,
                           parent = self.root,
                           pos = (.3, -.65),
                           scale = .05,
                           fg = (1,1,1,1),
                           font = Font1)

        self.panelElements.append(tmp)

    def buildTeamInfoPanel(self):
        tmp = BackgroundCard(Point3(0.3, 0, -.4), Point3(0.3, 0, .4), 'grey', .2, self.root, True)

        self.panelElements.append(tmp)

        if self.viewer.game.playerTeam == 'blue': titleText = 'Blue Team'
        else: titleText = 'Red Team'

        tmp = OnscreenText(text = titleText,
                           parent = self.root,
                           pos = (.3, -.06),
                           scale = .05,
                           fg = (1,1,1,1),
                           font = Font1)

        self.panelElements.append(tmp)

        blue = 0.0
        red = 0.0
        orange = 0.0
        grey = 0.0

        for w in self.viewer.game.worlds:
            if w.state == 'blue': blue += 1.0
            elif w.state == 'red': red += 1.0
            elif w.state == 'war': orange += 1.0
            elif w.state == 'neutral': grey += 1.0

        total = blue + red + orange + grey

        b = blue/total
        r = red/total
        o = orange/total
        g = grey/total

        tmp = TeamMeasureBar(Point3(0, 0, -.09), parent = self.root, blue = b, orange = o, red = r, grey = g)

        self.panelElements.append(tmp)

    def hide(self):
        self.toolbar.hide()
        self.root.hide()
        self.nameBg.hide()
        self.nameText.hide()

    def show(self):
        self.toolbar.show()
        self.root.show()
        self.update()
        self.nameBg.show()
        self.nameText.show()

    def destroy(self):
        self.teardownInfoPanel()
        self.toolbar.destroy()
        self.nameBg.destroy()
        self.nameText.destroy()

class Toolbar:
    def __init__(self, viewer):
        self.bg = OnscreenImage(image='data/images/black.png',
                                pos=(0, 0, -.95),
                                scale=(0.75, 1, 0.05))
        self.bg.setTransparency(TransparencyAttrib.MAlpha)
        self.bg.setAlphaScale(0.7)

        self.enterBtn = Button(text='Enter', pos=(-.6, 0, -.97), scale=0.06, command=viewer.enterSystem)
        self.buildBtn = Button(text='Build', pos=(0, 0, -.97), scale=0.06, command=viewer.enterBuild)
        self.pauseBtn = Button(text='Menu', pos=(.6, 0, -.97), scale=0.06, command=viewer.pause)

    def hide(self):
        self.bg.hide()
        self.enterBtn.hide()
        self.buildBtn.hide()
        self.pauseBtn.hide()

    def show(self):
        self.bg.show()
        self.enterBtn.show()
        self.buildBtn.show()
        self.pauseBtn.show()

    def destroy(self):
        self.bg.destroy()
        self.enterBtn.destroy()
        self.buildBtn.destroy()
        self.pauseBtn.destroy()

class TeamMeasureBar:
    def __init__(self, pos, parent = aspect2d, blue = 0.0, orange = 0.0, red = 0.0, grey = 0.0):
        WIDTH = .58
        OFFSET = .01
        HEIGHT = .005

        blueStart = 0
        blueEnd = blue
        blueMiddle = (blueStart + blueEnd) / 2.0
        blueScale = blueMiddle - blueStart

        orangeStart = blueEnd
        orangeEnd = orangeStart + orange
        orangeMiddle = (orangeStart + orangeEnd) / 2.0
        orangeScale = orangeMiddle - orangeStart

        redStart = orangeEnd
        redEnd = redStart + red
        redMiddle = (redStart + redEnd) / 2.0
        redScale = redMiddle - redStart

        greyStart = redEnd
        greyEnd = greyStart + grey
        greyMiddle = (greyStart + greyEnd) / 2.0
        greyScale = greyMiddle - greyStart

        self.blue = OnscreenImage(image = 'data/images/blue.png',
                                  pos = (blueMiddle * WIDTH + OFFSET, pos.getY(), pos.getZ()),
                                  scale = (blueScale * WIDTH, 1, HEIGHT),
                                  parent = parent)

        self.orange = OnscreenImage(image='data/images/orange.png',
                                    pos=(orangeMiddle * WIDTH + OFFSET, pos.getY(), pos.getZ()),
                                    scale=(orangeScale * WIDTH, 1, HEIGHT),
                                    parent=parent)

        self.red = OnscreenImage(image='data/images/red.png',
                                 pos=(redMiddle * WIDTH + OFFSET, pos.getY(), pos.getZ()),
                                 scale=(redScale * WIDTH, 1, HEIGHT),
                                 parent=parent)

        self.grey = OnscreenImage(image='data/images/grey.png',
                                  pos=(greyMiddle * WIDTH + OFFSET, pos.getY(), pos.getZ()),
                                  scale=(greyScale * WIDTH, 1, HEIGHT),
                                  parent=parent)

    def destroy(self):
        self.blue.destroy()
        self.orange.destroy()
        self.red.destroy()
        self.grey.destroy()

class MapViewerPlanet:
    def __init__(self, viewer, world):
        self.viewer = viewer
        self.world = world

        self.selected = False
        self.pos = world.pos

        self.state = self.world.state
        self.model = None
        self.updateModel()

        self.hitbox = loader.loadModel("data/models/mapviewer/collisionbox")
        self.hitbox.reparentTo(self.viewer.root)
        self.hitbox.setPos(self.pos)
        self.hitbox.setScale(2.0)
        self.hitbox.setTag('clicktag', '1')
        self.hitbox.setCollideMask(BitMask32.bit(1))

    def updateModel(self):
        self.state = self.world.state

        h = 0
        if self.model is not None:
            h = self.model.getH()
            self.model.removeNode()

        self.model = loader.loadModel("data/models/mapviewer/" + self.world.state)
        self.model.reparentTo(self.viewer.root)
        self.model.setPos(self.pos)
        self.model.setH(h)
        self.model.setScale(2.0)

    def toggleSelected(self):
        self.selected = not self.selected
        for w in self.viewer.worldIcons:
            if w != self:
                w.selected = False

    def update(self, dt):
        if self.selected:
            self.model.setH(self.model.getH() + 36 * dt)

        if self.world.state != self.state:
            self.updateModel()
            return True

        return False

    def destroy(self):
        self.model.removeNode()
        self.hitbox.removeNode()

class MapViewerConnection:
    def __init__(self, viewer, pos1, pos2):
        self.model = loader.loadModel("data/models/mapviewer/connection")
        self.model.reparentTo(viewer.root)
        self.model.setPos(pos1)
        self.model.lookAt(pos2)
        self.model.setScale(1.0, (pos1 - pos2).length(), 1.0)

    def destroy(self):
        self.model.removeNode()