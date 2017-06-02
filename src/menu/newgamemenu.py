from direct.gui.DirectGui import DirectEntry
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *

from src.core.data import Font1, Button
from src.core.showbase import *


class NewGameMenu:
    def __init__(self, mainMenu):
        self.mainMenu = mainMenu

        self.root = aspect2d.attachNewNode('newGameMenuRoot')

        self.playerName = None
        self.playerTeam = None

        self.count = 0

        self.story = []

        for i in range(3):
            storyFile = open("data/story/story_"+str(i)+".txt")

            tmpTxt = OnscreenText(text = storyFile.read(),
                                  font = Font1,
                                  fg = (1,1,1,1),
                                  pos = (-1, 0.5),
                                  scale = 0.07,
                                  align = TextNode.ALeft,
                                  parent = self.root)
            tmpTxt.hide()
            self.story.append(tmpTxt)

            storyFile.close()

        self.grad = OnscreenImage(image="data/images/gradient.png",
                                  scale=2,
                                  parent=self.root)
        self.grad.setTransparency(TransparencyAttrib.MAlpha)
        self.grad.hide()

        self.nextBNode = self.root.attachNewNode("nextB")
        self.nextB = Button(pos = (1, 0, -0.6), scale = 0.07, text = 'Next', command = self.nextScreen, parent = self.nextBNode)
        self.nextB.disable()
        self.nextBNode.hide()

        self.nameRoot = self.root.attachNewNode("nameRoot")
        self.nameBg = OnscreenImage(image = "data/images/grey.png",
                                    scale = (0.5, 1, 0.2),
                                    parent = self.nameRoot)
        self.nameBg.setTransparency(TransparencyAttrib.MAlpha)
        self.nameBg.setAlphaScale(0.1)

        self.nameTitle = OnscreenText(text = "Commander Name:",
                                      scale = 0.07,
                                      font = Font1,
                                      fg = (1,1,1,1),
                                      pos = (0, 0.1),
                                      parent = self.nameRoot)

        self.nameEntryBg = OnscreenImage(image = "data/images/black.png",
                                         scale = (0.45, 1, 0.1),
                                         parent = self.nameRoot,
                                         pos = (0, 0, -0.05))

        self.nameEntry = DirectEntry(text = "",
                                     scale = 0.07,
                                     command = self.setName,
                                     initialText = "",
                                     numLines = 1,
                                     pos = (0, 0, -.075),
                                     focus = 0,
                                     frameColor = (0,0,0,1),
                                     text_fg = (1,1,1,1),
                                     text_font = Font1,
                                     text_align = TextNode.ACenter,
                                     suppressKeys = 1,
                                     rolloverSound = None,
                                     clickSound = None,
                                     parent = self.nameRoot)

        self.nameRoot.hide()

        self.teamSelectNode = self.root.attachNewNode("teamSelect")

        self.teamSelectTitle = OnscreenText(text = "Choose your side:",
                                            font = Font1,
                                            fg = (1,1,1,1),
                                            scale = 0.07,
                                            pos = (0, 0.4),
                                            parent = self.teamSelectNode)

        self.teamBlueBtn = Button(pos = (-.5, 0, 0), scale = (0.45, 1, 0.3), minAlpha = 1, image = "data/story/blue.png", parent = self.teamSelectNode, command = self.selectBlue)
        self.teamRedBtn = Button(pos = (.5, 0, 0), scale = (0.45, 1, 0.3), minAlpha = 1, image = "data/story/red.png", parent= self.teamSelectNode, command = self.selectRed)

        self.teamSelectNode.hide()

        taskMgr.doMethodLater(3.0, self.fadeInNameEntryStart, "NameFadeInDelay")

    def fadeInNameEntryStart(self, task):
        self.nameRoot.show()
        self.nameRoot.setAlphaScale(0)
        taskMgr.add(self.fadeInNameEntry, "NameFadeInTask")

    def fadeInNameEntry(self, task):
        self.nameRoot.setAlphaScale(min(1.0, task.time))
        if task.time >= 1:
            return task.done
        return task.cont

    def fadeOutNameEntry(self, task):
        self.nameRoot.setAlphaScale(max(0, 1-task.time))
        if 1-task.time <= 0:
            self.nameRoot.hide()
            taskMgr.doMethodLater(1, self.fadeInStoryStart, "FadeInStoryDelay")
            return task.done
        return task.cont

    def setName(self, name):
        if self.playerName is None:
            taskMgr.add(self.fadeOutNameEntry, "NameFadeOutTask")
            self.playerName = name

    def fadeInStoryStart(self, task):
        if self.count < len(self.story):
            self.story[self.count].show()
            self.grad.setPos(0, 0, 1)
            self.grad.show()
            self.nextB.disable()
            self.nextBNode.setAlphaScale(0)
            self.nextBNode.show()
            taskMgr.add(self.fadeInStory, "FadeInStoryTask")
        else:
            self.teamSelectNode.show()
            taskMgr.add(self.fadeInTeamSelect, "FadeInTeamSelectTask")

    def fadeInStory(self, task):
        gradPos = max(1-(task.time*2), -3)
        nextBAlpha = min(max(0, task.time - 1), 1)

        self.grad.setPos(0,0,gradPos)
        self.nextBNode.setAlphaScale(nextBAlpha)

        if task.time > 2:
            self.nextB.enable()
            self.grad.hide()
            return task.done

        return task.cont

    def fadeOutStory(self, task):
        alpha = max(0, 1-task.time)
        self.story[self.count].setAlphaScale(alpha)
        self.nextBNode.setAlphaScale(alpha)

        if task.time > 1:
            self.story[self.count].hide()
            self.nextBNode.hide()
            self.count += 1
            return task.done

        return task.cont

    def fadeInTeamSelect(self, task):
        alpha = min(task.time, 1)

        self.teamSelectNode.setAlphaScale(alpha)

        if task.time > 1:
            return task.done
        return task.cont

    def fadeOutTeamSelect(self, task):
        alpha = max(0, 1-task.time)

        self.teamSelectNode.setAlphaScale(alpha)

        if task.time > 1:
            self.teamSelectNode.hide()
            return task.done
        return task.cont

    def nextScreen(self):
        self.nextB.disable()
        taskMgr.add(self.fadeOutStory, "FadeOutStoryTask")
        taskMgr.doMethodLater(2.0, self.fadeInStoryStart, "FadeInNextStoryDelay")

    def selectRed(self):
        self.select("red")

    def selectBlue(self):
        self.select("blue")

    def select(self, team):
        self.playerTeam = team

        taskMgr.add(self.fadeOutTeamSelect, "FadeOutTeamSelectTask")
        self.mainMenu.background.musicMgr.endNewGameMusic()

        taskMgr.doMethodLater(2.0, self.end, "endDelay")

    def end(self, task):
        self.teamSelectTitle.destroy()
        self.teamBlueBtn.destroy()
        self.teamRedBtn.destroy()
        self.teamSelectNode.removeNode()

        self.nameBg.destroy()
        self.nameEntryBg.destroy()
        self.nameTitle.destroy()
        self.nameEntry.destroy()
        self.nameRoot.removeNode()

        self.nextB.destroy()
        self.nextBNode.removeNode()

        self.grad.destroy()

        for s in self.story:
            s.destroy()

        self.root.removeNode()

        self.mainMenu.startGame(self.playerName, True, self.playerTeam)