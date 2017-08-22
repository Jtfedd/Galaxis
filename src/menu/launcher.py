import sys
import webbrowser

from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

from splashscreen import SplashScreen
from src.core.data import Font1, Font3, Button
from src.core.showbase import *


class Launcher(DirectObject):
    def __init__(self):
        base.setFrameRateMeter(True)
        self.accept('escape', self.exit)
        self.background = OnscreenImage(image = 'data/launcher/launcherBG.png',
                                        scale = (4.0/3.0, 1, 1))
        self.titleText = OnscreenText(text = 'Galaxis',
                                      font = Font3,
                                      scale = .4,
                                      pos = (0, .6),
                                      fg = (1,1,1,1))

        self.buttons = []
        self.texts = []
        self.currentPos = .4

        self.updating = False

        self.makeButton('Play', self.play)
        self.makeButton('Update', self.update)
        self.makeButton('Website', self.website)
        self.makeButton('Exit', self.exit)

        self.footerBg = OnscreenImage(image = 'data/images/white.png',
                                      pos = (0, 0, -.83),
                                      scale = (1.25, 1, .1))
        self.footerBg.setTransparency(TransparencyAttrib.MAlpha)
        self.footerBg.setAlphaScale(.6)
        # self.footerBg.setColorScale(.7, .7, .7, .75)

        self.footerText = OnscreenText(text = '',
                                       font = Font1,
                                       pos = (0, -.85),
                                       scale = .07,
                                       fg = (.1,.1,.1,1))
        self.setFooterMessage(None)

    def makeButton(self, text, command):
        tmpBtn = Button(pos=(-.85, 0, self.currentPos + .02), scale=(.4, 1, .04), image='data/images/white.png', command = command, minAlpha = .5)

        tmpTxt = OnscreenText(text=text,
                              font=Font1,
                              pos=(-1.2, self.currentPos),
                              scale=.07,
                              fg=(.1, .1, .1, 1),
                              align=TextNode.ALeft)

        self.buttons.append(tmpBtn)
        self.texts.append(tmpTxt)
        self.currentPos -= .1

    def setFooterMessage(self, text):
        if text is None:
            self.footerBg.hide()
            self.footerText.hide()
            return

        self.footerBg.show()
        self.footerText.show()
        self.footerText.setText(text)

    def play(self):
        self.cleanup()

        wp = WindowProperties()
        wp.setFullscreen(True)
        wp.setSize(1920, 1080)
        wp.setCursorHidden(True)
        base.win.requestProperties(wp)

        SplashScreen()

    def update(self):
        #TODO: Incomplete, no implementation of updating
        if self.updating:
            self.cancelUpdate()
            return

        self.setFooterMessage('Checking for updates...')
        self.buttons[0].disable()
        self.texts[1].setText('Cancel Update')
        self.updating = True

    def cancelUpdate(self):
        #TODO: Incomplete, no implementation of updating
        self.updating = False
        self.buttons[0].enable()
        self.texts[1].setText('Update')

        self.setFooterMessage(None)

    def website(self):
        webbrowser.open('https://jtfedd.github.io/Galaxis/')

    def exit(self):
        self.cleanup()
        sys.exit()

    def cleanup(self):
        self.background.destroy()
        self.titleText.destroy()

        for t in self.texts:
            t.destroy()
        for b in self.buttons:
            b.destroy()

        self.footerBg.destroy()
        self.footerText.destroy()

        self.ignoreAll()