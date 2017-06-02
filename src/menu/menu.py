import math
import sys

from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

from menubackground import MenuBackground
from newgamemenu import NewGameMenu
from src.core.data import BackgroundCard
from src.core.data import Font1, Font2, Button
from src.core.panels import SidePanels
from src.core.showbase import *


class Menu(DirectObject):
    def __init__(self):
        self.background = MenuBackground()
        self.background.start()
        taskMgr.doMethodLater(10.0, self.startSpaceNotice, 'intro-delay')
        taskMgr.doMethodLater(6.0, self.enableSpace, 'enable-space-delay')

        self.spaceText = None
        self.spaceTextDone = False

        self.root = SidePanels().leftPanel
        self.root.setTransparency(TransparencyAttrib.MAlpha)
        self.root.setAlphaScale(0)

        self.gui = []

    def startSpaceNotice(self, task):
        self.spaceText = OnscreenText(text = 'Press Space',
                                      font = Font1,
                                      scale = 0.07,
                                      pos = (0, -.9),
                                      fg = (1,1,1,1))
        self.spaceText.setTransparency(TransparencyAttrib.MAlpha)
        self.spaceText.setAlphaScale(0.0)

        taskMgr.add(self.animateSpaceText, 'press-space-animate')

    def animateSpaceText(self, task):
        alphaScale = math.sin(task.time*3)
        self.spaceText.setAlphaScale(alphaScale)
        if alphaScale <= 0 and self.spaceTextDone:
            self.spaceText.destroy()
            return task.done
        return task.cont

    def enableSpace(self, task):
        self.acceptOnce('space', self.startMenu)

    def startMenu(self):
        wp = WindowProperties()
        wp.setCursorHidden(False)
        base.win.requestProperties(wp)

        taskMgr.add(self.fadeInMenu, 'menu-fade-in')
        self.mainScreen()
        self.spaceTextDone = True

    def fadeInMenu(self, task):
        self.root.setAlphaScale(task.time*2)
        if task.time >= .5:
            self.root.setAlphaScale(1.0)
            return task.done
        return task.cont

    def clearScreen(self):
        for g in self.gui:
            g.destroy()

    def makeSideCard(self):
        self.gui.append(BackgroundCard((.4, 0, 0), (0.4, 1, 1.0), 'black', parent = self.root))

    def makeTitle(self):
        self.gui.append(OnscreenText(parent = self.root,
                                     text = 'Galaxis',
                                     pos = (0.4, 0.8),
                                     scale = .15,
                                     fg = (1,1,1,1),
                                     font = Font2))
        tmp = OnscreenImage(parent = self.root,
                            image = 'data/images/white.png',
                            pos = (0.4, 0, 0.75),
                            scale = (0.3, 1, .002))
        tmp.setAlphaScale(.7)
        self.gui.append(tmp)

    def makeBackButton(self, backAction):
        self.gui.append(Button(pos = (.4, 0, -.8), scale = .07, text = 'Back', command = backAction, parent = self.root))

    def setupMenuSlide(self, backButton = False, backAction = None):
        self.clearScreen()
        self.makeSideCard()
        self.makeTitle()
        if backButton: self.makeBackButton(backAction)

    def mainScreen(self):
        self.setupMenuSlide()
        self.gui.append(Button(pos = (.4, 0, .6), scale = .07, text = 'New Game', command = self.newGame, parent = self.root))
        self.gui.append(Button(pos = (.4, 0, .45), scale = .07, text = 'Load Game', command = self.loadGame, parent = self.root))
        self.gui.append(Button(pos = (.4, 0, .3), scale = .07, text = 'Options', command = self.options, parent = self.root))
        self.gui.append(Button(pos = (.4, 0, .15), scale = .07, text = 'Credits', command = self.credits, parent = self.root))
        self.gui.append(Button(pos = (.4, 0, 0), scale = .07, text = 'Exit', command = sys.exit, parent = self.root))

    def newGame(self):
        self.clearScreen()
        self.background.end(True)
        NewGameMenu(self)

    def loadGame(self):
        self.setupMenuSlide(True, self.mainScreen)

    def credits(self):
        self.setupMenuSlide(True, self.mainScreen)

    def options(self):
        self.setupMenuSlide(True, self.mainScreen)

    def startGame(self, gameName, newGame = False, playerTeam = None):
        print gameName
        print newGame
        print playerTeam