from direct.showbase.DirectObject import DirectObject

from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import *

from shipdata import *
from ship_components import Laser
from src.core.showbase import *
from src.core.util import calcRatio, isOnscreen, map3dToAspect2d


class Ship(DirectObject):
    def __init__(self, world, game, name, pos, lookAtCenter = True):
        self.game = game
        self.world = world
        self.name = name
        self.isNPC = True
        self.playerView = False
        
        data = ShipData[name]
        
        self.team = data['team']
        self.type = data['type']
        self.size = data['size']

        self.health = data['maxHealth']
        self.maxHealth = data['maxHealth']

        # TODO generate callsigns
        self.callsign = "Callsign"

        self.playerCanControl = self.size == 1 and self.game.playerTeam == self.team
        
        self.model = loader.loadModel('data/models/ships/' + name + '/model')
        self.mapModel = loader.loadModel('data/models/ships/' + name + '/map')

        self.model.reparentTo(self.world.worldRoot)
        self.model.setPos(pos)
        if lookAtCenter:
            self.model.lookAt(0, 0, 0)

        self.mapModel.reparentTo(self.world.mapRoot)
        self.mapModel.setTransparency(TransparencyAttrib.MAlpha)
        self.offscreenIndicator = OnscreenImage(image="data/images/white.png", scale=0.01)
        self.offscreenIndicator.setTransparency(TransparencyAttrib.MAlpha)
        if self.team == "blue":
            self.mapModel.setColorScale(Vec4(0, 0.75, 1, 0.5))
            self.offscreenIndicator.setColorScale(Vec4(0, 0.75, 1, 0.5))
        else:
            self.mapModel.setColorScale(Vec4(1, 0, 0, 0.5))
            self.offscreenIndicator.setColorScale(Vec4(1, 0, 0, 0.5))

        self.selected = False
        self.selectIndicator = OnscreenImage(image = "data/images/select.png", scale = 0.05)
        self.selectIndicator.setTransparency(TransparencyAttrib.MAlpha)
        self.selectIndicator.hide()

        self.syncMapModel()

        # Constants defining the capability of the ship
        self.speed = data['speed']
        self.turn = data['turn']
        
        self.throttle = 0
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.useRoll = False
        self.fireLasers = False
        
        numLasers = data['numLasers']
        numTurrets = data['numTurrets']
        numTurbolasers = data['numTurboLasers']
        
        self.torpedos = data['maxTorpedos']
        self.missiles = data['maxMissiles']

        self.maxTorpedos = data['maxTorpedos']
        self.maxMissiles = data['maxMissiles']
        
        self.lasers = []
        self.turrets = []
        self.turbolasers = []

        # TODO Make this stuff work
        for i in range(numLasers):
            self.lasers.append(Laser(self, self.model.find('**/laser_'+str(i))))
        # for i in range(numTurrets):
        #     self.turrets.append(Turret(self, self.root.find('**/turretbase_'+str(i)), self.root.find('**/turretgun_'+str(i))))
        # for i in range(numTurbolasers):
        #     self.turbolasers.append(Turbolaser(self, self.root.find('**/turbolaser_'+str(i))))
            
        self.target = None
        self.whoHitMe = None
        
        self.state = ['wander']

    def setPlayerControl(self, hasPlayerControl):
        self.isNPC = not hasPlayerControl
        self.fireLasers = False

        if hasPlayerControl:
            self.model.hide()

            props = base.win.getProperties()
            base.win.movePointer(0, int(props.getXSize() / 2), int(props.getYSize() / 2))

            self.accept('mouse3', self.setUseRoll, [True])
            self.accept('mouse3-up', self.setUseRoll, [False])
            self.accept('mouse1', self.setFireLasers, [True])
            self.accept('mouse1-up', self.setFireLasers, [False])
        else:
            self.model.show()
            self.ignoreAll()

    def setPlayerViewing(self, playerViewing):
        self.playerView = playerViewing

    def setUseRoll(self, useRoll):
        self.useRoll = useRoll

    def setFireLasers(self, fire):
        self.fireLasers = fire

    def update(self, dt):
        if self.size == 1:
            self.throttle = 1

        for l in self.lasers:
            l.update(dt)

        if self.isNPC:
            self.AIUpdate()
        else:
            self.playerUpdate()
        
        self.model.setY(self.model, self.speed * self.throttle * dt)
        self.model.setH(self.model, self.turn * self.yaw * dt)
        self.model.setP(self.model, self.turn * self.pitch * dt)
        self.model.setR(self.model, self.turn * self.roll * dt)

        self.syncMapModel()

        if not self.isNPC:
            self.updateCameraPlayer()
        elif self.playerView:
            self.updateView()

    def AIUpdate(self):
        # TODO AI Logic
        pass

    def playerUpdate(self):
        if self.fireLasers:
            for l in self.lasers:
                l.fire()

        if base.mouseWatcherNode.hasMouse():
            xPos = base.mouseWatcherNode.getMouse().getX()
            yPos = base.mouseWatcherNode.getMouse().getY()

            self.pitch = yPos
            if self.useRoll:
                self.roll = xPos
                self.yaw = 0
            else:
                self.yaw = -xPos
                self.roll = 0

    def updateCameraPlayer(self):
        base.camera.setPos(self.model.getPos(render))
        base.camera.setHpr(self.model.getHpr(render))

    def updateView(self):
        pass

    def syncMapModel(self):
        self.mapModel.setPos(self.model.getPos())
        self.mapModel.setHpr(self.model.getHpr())

        if self.selected and self.world.mapViewActive:
            pos = map3dToAspect2d(self.world.mapRoot, self.mapModel.getPos())
            if pos is not None:
                self.selectIndicator.show()
                self.selectIndicator.setPos(pos)
            else:
                self.selectIndicator.hide()
        else:
            self.selectIndicator.hide()

        if not self.world.mapViewActive or isOnscreen(self.world.mapRoot, self.mapModel.getPos()):
            self.offscreenIndicator.hide()
            return

        x = self.mapModel.getX(base.camera)
        y = self.mapModel.getZ(base.camera)
        ratio = calcRatio()

        newX = 0
        newY = 0

        if x == 0:
            if y > 0:
                newY = 1
            else:
                newY = -1
        elif x > 0:
            newY = min(1, max(-1, y*ratio/x))
        else:
            newY = min(1, max(-1, -y*ratio/x))

        if newY == 1 or newY == -1:
            if y == 0:
                if x > 0:
                    newX = ratio
                else:
                    newX = -ratio
            elif y > 0:
                newX = min(ratio, max(-ratio, x/y))
            else:
                newX = min(ratio, max(-ratio, -x/y))
        else:
            if x > 0:
                newX = ratio
            else:
                newX = -ratio

        self.offscreenIndicator.setX(newX)
        self.offscreenIndicator.setZ(newY)
        self.offscreenIndicator.show()

    def select(self):
        self.offscreenIndicator.setColorScale(Vec4(1, 1, 1, 0.5))
        self.selected = True
        self.syncMapModel()

    def deselect(self):
        if self.team == "blue":
            self.offscreenIndicator.setColorScale(Vec4(0, 0.75, 1, 0.5))
        else:
            self.offscreenIndicator.setColorScale(Vec4(1, 0, 0, 0.5))
        self.selected = False
        self.syncMapModel()