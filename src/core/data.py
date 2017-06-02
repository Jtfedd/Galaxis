from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from panda3d.core import TransparencyAttrib, TextNode

from src.core.showbase import *

Font1 = loader.loadFont("data/font1.otf")
Font2 = loader.loadFont("data/font4.otf")
Font2.setPixelsPerUnit(120)
Font3 = loader.loadFont("data/font2.otf")
Font3.setPixelsPerUnit(120)

class Button(DirectObject):
    def __init__(self, pos=(0, 0, 0), scale=.1, minAlpha=.5, path=None, img=None, image=None, text=None, align=TextNode.ACenter, parent=None, command=None, extraArgs=[]):
        if parent == None:
            parent = aspect2d
        self.minAlpha = minAlpha
        self.rolledover = False
        self.alpha = self.minAlpha
        if text == None:
            if image == None:
                temp = loader.loadModel(path + img)
                self.button = DirectButton(geom=(temp.find('**/' + img),
                                                 temp.find('**/' + img),
                                                 temp.find('**/' + img),
                                                 temp.find('**/' + img)),
                                           borderWidth=(0, 0),
                                           frameColor=(0, 0, 0, 0),
                                           rolloverSound=None,
                                           clickSound=None,
                                           scale=scale,
                                           command=command,
                                           extraArgs=extraArgs,
                                           parent=parent,
                                           pos=pos)
            else:
                self.button = DirectButton(image=image,
                                           borderWidth=(0, 0),
                                           frameColor=(0, 0, 0, 0),
                                           rolloverSound=None,
                                           clickSound=None,
                                           scale=scale,
                                           command=command,
                                           extraArgs=extraArgs,
                                           parent=parent,
                                           pos=pos)
                self.button.setTransparency(TransparencyAttrib.MAlpha)
        else:
            self.button = DirectButton(text=(text, text, text, text),
                                       borderWidth=(0, 0),
                                       frameColor=(0, 0, 0, 0),
                                       rolloverSound=None,
                                       clickSound=None,
                                       scale=scale,
                                       text_fg=(1, 1, 1, 1),
                                       text_font=Font1,
                                       text_align=align,
                                       command=command,
                                       extraArgs=extraArgs,
                                       parent=parent,
                                       pos=pos)
        self.button.setAlphaScale(minAlpha)

        self.button.bind(DGG.ENTER, self.setRolloverTrue)
        self.button.bind(DGG.EXIT, self.setRolloverFalse)

        self.updateTask = taskMgr.add(self.update, "button update")

    def setRolloverTrue(self, arg):
        self.rolledover = True

    def setRolloverFalse(self, arg):
        self.rolledover = False

    def update(self, task):
        if self.rolledover:
            if self.alpha < 1:
                self.alpha += 4 * globalClock.getDt()
                if self.alpha > 1:
                    self.alpha = 1
                self.button.setAlphaScale(self.alpha)
        else:
            if self.alpha > self.minAlpha:
                self.alpha -= 2 * globalClock.getDt()
                if self.alpha < self.minAlpha:
                    self.alpha = self.minAlpha
                self.button.setAlphaScale(self.alpha)

        return task.cont

    def setText(self, text):
        self.button["text"] = text
        self.button.setFrameSize()

    def hide(self):
        self.button.hide()

    def show(self):
        self.button.show()

    def disable(self):
        self.button['state'] = DGG.DISABLED

    def enable(self):
        self.button['state'] = DGG.NORMAL

    def destroy(self):
        self.button.destroy()
        taskMgr.remove(self.updateTask)
        self = None

class RejectButton(Button):
    """Same as my standard button wrapper but has a 'reject' method, which causes the button to flash red quickly three times."""
    def __init__(self, pos=(0, 0, 0), scale=.1, minAlpha=.5, path=None, img=None, image=None, text=None, align=TextNode.ACenter, parent=None, command=None, extraArgs=[]):
        Button.__init__(self, pos, scale, minAlpha, path, img, image, text, align, parent, command, extraArgs)
        self.red = OnscreenImage(image="data/images/red.png", scale=scale, pos=pos, parent=parent)
        self.red.hide()

        self.rejectTask = None

    def reject(self):
        self.end()
        self.rejectTask = taskMgr.add(self.flash, "button-reject-task")

    def flash(self, task):
        if task.time > 1.25:
            self.end()
            return task.done
        timeFact = task.time * 4
        if timeFact % 2 > 1:
            self.red.hide()
        else:
            self.red.show()
        return task.cont

    def end(self):
        if self.rejectTask is not None:
            taskMgr.remove(self.rejectTask)
            self.red.hide()
            self.rejectTask = None

    def destroy(self):
        Button.destroy(self)
        self.red.destroy()

class BackgroundCard(DirectObject):
    def __init__(self, pos, scale, color, alpha=.7, parent=aspect2d, bordered=False):
        self.bordered = bordered
        self.root = parent.attachNewNode('bordered-background')
        self.root.setPos(pos)

        self.bg = OnscreenImage(parent=self.root,
                                image='data/images/' + color + '.png',
                                scale=scale)
        self.bg.setTransparency(TransparencyAttrib.MAlpha)
        self.bg.setAlphaScale(alpha)

        if not bordered: return

        self.leftBorder = OnscreenImage(parent=self.root,
                                        image='data/images/white.png',
                                        pos=(-scale.getX(), 0, 0),
                                        scale=(0.002, 1, scale.getZ()))
        self.rightBorder = OnscreenImage(parent=self.root,
                                         image='data/images/white.png',
                                         pos=(scale.getX(), 0, 0),
                                         scale=(0.002, 1, scale.getZ()))
        self.topBorder = OnscreenImage(parent=self.root,
                                       image='data/images/white.png',
                                       pos=(0, 0, scale.getZ()),
                                       scale=(scale.getX(), 1, 0.002))
        self.bottomBorder = OnscreenImage(parent=self.root,
                                          image='data/images/white.png',
                                          pos=(0, 0, -scale.getZ()),
                                          scale=(scale.getX(), 1, 0.002))

    def destroy(self):
        self.bg.destroy()

        if self.bordered:
            self.leftBorder.destroy()
            self.rightBorder.destroy()
            self.topBorder.destroy()
            self.bottomBorder.destroy()

        self.root.removeNode()