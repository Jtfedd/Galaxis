from direct.showbase.DirectObject import DirectObject

from src.core.showbase import *
from src.core.util import calcRatio

class SidePanels(DirectObject):
    def __init__(self):
        self.leftPanel = aspect2d.attachNewNode('ui-left-panel')
        self.rightPanel = aspect2d.attachNewNode('ui-right-panel')

        self.updatePanels(base.win)

        self.accept(base.win.getWindowEvent(), self.updatePanels)

    def updatePanels(self, win):
        ratio = calcRatio()
        self.leftPanel.setX(-ratio)
        self.rightPanel.setX(ratio)

    def destroy(self):
        self.ignoreAll()
        self.leftPanel.removeNode()
        self.rightPanel.removeNode()