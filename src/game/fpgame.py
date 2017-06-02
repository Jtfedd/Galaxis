from direct.showbase.DirectObject import DirectObject

from skybox import Skybox

class FPGame(DirectObject):
    """Creates a world based on the game and world provided,
    and places the player into the game. This is the basis for
    the standard starfighter style game. This class also serves
    as the replacement for the AI controller for the player's ship."""
    
    def __init__(self, game, world):
        self.skybox = Skybox("1")
        
        taskMgr.add(self.update, "Game update task")
        
        # Variables necessary for the ship to be controlled
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        
        self.throttle = 1
        self.fire = 0
        self.target = None
        
    def updateControl(self, dt):
        # Get user input to update the controlls, which will be accessed
        # by the ship in order to control it.
        pass
        
    def update(self, task):
        self.skybox.update()
        
        return task.cont