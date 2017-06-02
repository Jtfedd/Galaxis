import cPickle

from direct.filter.CommonFilters import CommonFilters

from mapviewer import *
from src.core.filemgr import *
from src.core.panels import *
from src.game.build import BuildScreen
from src.game.playercontrol import PlayerControl
from world import *

class Game(DirectObject):
    """Game class, responsible for creating all the worlds and managing
    "stages" which provide gameplay and interaction for the player.
    The game and its world are always running in the background"""

    # Optional params are for creating new games
    def __init__(self, gameName, newGame=False, team="blue"):

        # TODO REMOVE UNNECESSARY INIT FROM HERE WHEN GAME IS COMBINED WITH MENU
        base.camLens.setFov(80)
        render.setShaderAuto()
        filters = CommonFilters(base.win, base.cam)
        filters.setBloom(blend=(0, 0, 0, 1), desat=0.0, intensity=2.0)
        base.win.setClearColor(Vec4(0, 0, 0, 1))
        base.disableMouse()
        # -INIT

        self.gameName = gameName
        self.worlds = []
        self.playerTeam = team

        self.blueControlBase = None
        self.redControlBase = None

        self.panels = SidePanels()

        self.paused = False

        if newGame:
            self.newGame()
        else:
            self.loadGame()

        self.mapViewer = MapViewer(self)
        self.buildScreen = BuildScreen(self)

        self.messageDisplayer = MessageDisplayer(self)

        #TODO remove this test message
        self.accept("=", self.sendMessage,
                    ['This is a test message so that I can see what it looks like when messages are displayed.'])
        self.accept("display_message", self.sendMessage)
        self.accept("world_state_change", self.announceStateChange)
        taskMgr.add(self.update, "Game Update Loop")

    def newGame(self):
        # Hard-coded list of planet names
        PLANET_NAMES = ["Nebula 1", "Nebula 2", "Nebula 3", "Nebula 5", "Nebula 6", "Nebula 4", "Nebula 1", "Nebula 2", "Nebula 3",
                        "Nebula 5", "Nebula 6", "Nebula 4", "Nebula 1", "Nebula 2", "Nebula 3", "Nebula 5", "Nebula 6",
                        "Nebula 4", "Planet 1", "Planet 2"]
        numWorlds = len(PLANET_NAMES)
        random.shuffle(PLANET_NAMES)

        # Build the galaxy!
        found = False
        MAXDIST = 40
        # Add the first planet, which everything else will be based on
        temppos = Point3(0, 0, 0)
        while not found:
            temppos = Point3(random.randrange(100) - 50, random.randrange(100) - 50, random.randrange(20) - 10)
            if (temppos - Point3(0, 0, 0)).length() < MAXDIST:
                found = True
        self.worlds.append(World(self, PLANET_NAMES.pop(), temppos))

        # Now add random planets
        while len(PLANET_NAMES) > 0:
            found = False
            while not found:
                temppos = Point3(random.randrange(100) - 50, random.randrange(100) - 50, random.randrange(20) - 10)
                if (temppos - Point3(0, 0, 0)).length() < MAXDIST:
                    closeTest = True
                    farTest = False
                    for world in self.worlds:
                        if (temppos - world.pos).length() < 15:
                            closeTest = False
                        if (temppos - world.pos).length() < 20:
                            farTest = True
                    if closeTest and farTest:
                        tempworld = World(self, PLANET_NAMES.pop(), temppos)
                        self.worlds.append(tempworld)
                        found = True

        self.worlds.sort(key=lambda x: x.pos.getX())
        for i in range(numWorlds / 2 - 3):
            self.worlds[i].setState("blue")
            for j in range(1 + random.randrange(5)):
                self.worlds[i].addShipDirect(Ship(self.worlds[i], self, "testfighterblue", (j*100, 0, -100*j), False))
        for i in range(numWorlds / 2 + 3, numWorlds):
            self.worlds[i].setState("red")
            for j in range(1 + random.randrange(5)):
                self.worlds[i].addShipDirect(Ship(self.worlds[i], self, "testfighterred", (j * 100, 0, -100*j), False))

        if self.playerTeam == "blue":
            self.blueControlBase = PlayerControl(self, "blue")

    # Save files are pickled dictionaries. Attributes that should be saved are
    #   added to the dictionary in the "saveGame" method, and can be retrieved
    #   in the "loadGame" method when the dictionary is reopened.
    def loadGame(self):
        #TODO This will be changed
        return
        loadFile = openFile("Galaxis_savedata/saved_games/" + self.gameName + ".save", "r")
        loadDict = cPickle.load(loadFile)
        loadFile.close()

        self.worlds = loadDict["Worlds"]
        self.playerTeam = loadDict["playerTeam"]

    def saveGame(self):
        #TODO This will be changed
        return
        saveDict = {"Worlds": self.worlds,
                    "playerTeam": self.playerTeam}

        saveFile = openFile("Galaxis_savedata/saved_games/" + self.gameName + ".save", "w")
        cPickle.dump(saveDict, saveFile)
        saveFile.close()

    def update(self, task):
        if self.paused:
            return task.cont

        # Max simulation step 10 fps, so a large frame drop doesn't break things
        dt = min(globalClock.getDt(), 1 / 10.0)

        for w in self.worlds:
            w.update(dt)

        if self.mapViewer:
            self.mapViewer.update(dt)

        self.messageDisplayer.update(dt)

        self.blueControlBase.update(dt)

        return task.cont

    def sendMessage(self, message):
        self.messageDisplayer.displayMessage(message)

    def announceStateChange(self, world, newState, oldState):
        if newState == "neutral":
            message = world.name + " has become neutral territory!"
        elif newState == "war":
            if oldState == self.playerTeam:
                message = "Enemy forces have invaded " + world.name + "!"
            else:
                message = "Our forces have invaded " + world.name + "!"
        elif newState == self.playerTeam:
            if oldState == "neutral":
                message = world.name + " has joined our cause!"
            else:
                message = "Our forces have conquered " + world.name + "!"
        else:
            message = "Enemy forces have conquered " + world.name + "!"

        self.sendMessage(message)

    def pause(self):
        if self.paused:
            self.paused = False
            self.messageDisplayer.show()
        else:
            self.paused = True
            self.messageDisplayer.hide()

    def destroy(self):
        self.ignoreAll()
        self.messageDisplayer.destroy()
        self.panels.destroy()
        taskMgr.remove(self.update)

class MessageDisplayer:
    def __init__(self, game):
        self.messages = []
        self.maxMessages = 10

        self.root = game.panels.leftPanel.attachNewNode("MessagesRoot")

        self.game = game

    def update(self, dt):
        for m in self.messages:
            m.update(dt)

    def displayMessage(self, text):
        if len(self.messages) >= self.maxMessages:
            self.messages[0].destroy()
        tmp = OnscreenMessage(self, text, self.root)
        while tmp.size * 2 + 0.01 + self.totalLength() > 1.5:
            self.messages[0].destroy()
        for m in self.messages:
            m.moveDown(tmp.size * 2 + 0.01)
        self.messages.append(tmp)

    def totalLength(self):
        total = .01 * (len(self.messages) - 1)
        for m in self.messages:
            total += m.size * 2
        return total

    def hide(self):
        self.root.hide()

    def show(self):
        self.root.show()

    def destroy(self):
        while len(self.messages) > 0:
            self.messages[0].destroy()

class OnscreenMessage:
    def __init__(self, display, text, root):
        self.text = ""
        self.display = display

        self.time = 5.0
        self.moveDist = 0

        words = text.split(" ")
        i = 0
        lines = 1
        count = 0
        while i < len(words) - 1:
            self.text += words[i] + " "
            count += (len(words[i]) + 1)
            if count + len(words[i + 1]) + 1 > 27:
                self.text += "\n"
                lines += 1
                count = 0
            i += 1
        self.text += words[len(words) - 1]

        self.size = lines * .03

        self.root = root.attachNewNode("message")
        self.root.setTransparency(TransparencyAttrib.MAlpha)
        self.root.setPos(.35, 0, .95)
        self.root.setScale(0.75)

        self.bg = OnscreenImage(parent=self.root,
                                image="data/images/" + display.game.playerTeam + ".png",
                                scale=(0.42, 1, self.size),
                                pos=(0, 0, -self.size))
        self.bg.setAlphaScale(0.5)

        self.text = OnscreenText(parent=self.root,
                                 text=self.text,
                                 font=Font1,
                                 fg=(1, 1, 1, 1),
                                 scale=0.05,
                                 pos=(-0.39, -0.045),
                                 align=TextNode.ALeft)

    def update(self, dt):
        self.root.setAlphaScale(min(1.0, self.time))
        self.time -= dt
        if self.time < 0:
            self.destroy()

    def moveDown(self, amount):
        self.root.setZ(self.root, -amount)

    def destroy(self):
        self.root.removeNode()
        self.display.messages.remove(self)
