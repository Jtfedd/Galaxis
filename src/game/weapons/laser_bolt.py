from panda3d.core import *

from src.core.showbase import *

class LaserBolt:
    def __init__(self, ship, world, pos, hpr):
        self.ship = ship
        self.world = world

        self.model = loader.loadModel('data/models/weapons/laserbolt')
        self.model.setLightOff()
        self.model.setPos(pos)
        self.model.setHpr(hpr)
        self.model.reparentTo(render)

        self.life = 0
        self.speed = 500

    def update(self, dt):
        self.model.setY(self.model, self.speed*dt)
        self.life += dt
        if self.life > 2:
            self.destroy()

    def destroy(self):
        self.model.removeNode()
        self.world.laserbolts.remove(self)