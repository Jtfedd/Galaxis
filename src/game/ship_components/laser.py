from panda3d.core import *

from src.core.showbase import *

from src.game.weapons import LaserBolt

class Laser:
    def __init__(self, ship, rootNode):
        self.root = rootNode
        self.ship = ship

        self.charge = 1

    def fire(self):
        if self.charge < 1: return
        self.charge = 0
        self.ship.world.laserbolts.append(LaserBolt(self.ship, self.ship.world, self.root.getPos(render), self.root.getHpr(render)))

    def update(self, dt):
        if self.charge < 1:
            self.charge += dt*3