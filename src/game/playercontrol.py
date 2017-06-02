from controlbase import ControlBase
from build import BuildItem
from copy import deepcopy

class PlayerControl(ControlBase):
    def __init__(self, game, team):
        ControlBase.__init__(self, team)
        self.game = game

        self.buildScreen = None

        self.queue1 = []
        self.queue2 = []
        self.secondQueueActive = False

    def initBuildScreen(self, buildScreen):
        self.buildScreen = buildScreen

        for k in self.props.keys():
            if self.props[k].getUpgradeName() is not None:
                self.buildScreen.addUpgradeButton(self.props[k], self.startPropUpgrade, [k])

        self.buildScreen.createShipyardButton(self.startShipyardCreate, [])

    def startPropUpgrade(self, prop, button):
        if not self.hasResources(self.props[prop].getUpgradeCost()):
            button.reject("Not enough resources.")
            return
        if not self.hasBuildQueueSpace():
            button.reject("Build queue full.")
            return
        button.disable()
        self.consumeResources(self.props[prop].getUpgradeCost())
        item = BuildItem(self.buildScreen, self.completePropUpgrade, self.cancelPropUpgrade, 5, self.props[prop].getUpgradeName(), deepcopy(self.props[prop].getUpgradeCost()), button=button, extraArgs=[prop])
        self.addBuildItem(item)

    def cancelPropUpgrade(self, item):
        self.addBulkResources(item.cost)
        item.button.enable()
        self.removeBuildItem(item)

    def completePropUpgrade(self, item):
        self.props[item.args[0]].upgrade()
        item.button.enable()
        if self.props[item.args[0]].getUpgradeName() is not None:
            item.button.updateText()
        else:
            self.buildScreen.removeUpgradeButton(item.button)
            item.button.destroy()
        self.removeBuildItem(item)

    def startShipyardCreate(self, button):
        if not self.hasResources(button.cost):
            button.reject("Not enough resources.")
            return
        if not self.hasBuildQueueSpace():
            button.reject("Build queue full.")
            return
        button.disable()
        self.consumeResources(button.cost)
        item = BuildItem(self.buildScreen, self.completeShipyard, self.cancelShipyard, 10, "Create Second Shipyard", deepcopy(button.cost), button=button)
        self.addBuildItem(item)

    def cancelShipyard(self, item):
        self.addBulkResources(item.cost)
        item.button.enable()
        self.removeBuildItem(item)

    def completeShipyard(self, item):
        self.buildScreen.shipyardButton = None
        item.button.destroy()
        self.removeBuildItem(item)
        self.secondQueueActive = True
        numToMove = len(self.queue1) / 2
        for i in range(numToMove):
            item = self.queue1.pop()
            self.queue2.insert(0, item)
            for j in range(len(self.queue2)):
                self.queue2[j].setPos(-0.075, 0.475 - 0.225 * j)

    def addBuildItem(self, item):
        if self.secondQueueActive and len(self.queue2) < len(self.queue1):
            item.setPos(-0.075, 0.475-0.225*len(self.queue2))
            self.queue2.append(item)
        else:
            item.setPos(-1.125, 0.475-0.225*len(self.queue1))
            self.queue1.append(item)

    def removeBuildItem(self, item):
        for i in self.queue1:
            if i == item:
                self.queue1.remove(i)
                for j in range(len(self.queue1)):
                    self.queue1[j].setPos(-1.125, 0.475-0.225*j)
                return
        for i in self.queue2:
            if i == item:
                self.queue2.remove(i)
                for j in range(len(self.queue2)):
                    self.queue2[j].setPos(-0.075, 0.475-0.225*j)
                return

    def hasBuildQueueSpace(self):
        if self.secondQueueActive:
            return len(self.queue1) + len(self.queue2) < 10
        else:
            return len(self.queue1) < 5

    def consumeResources(self, resources):
        result = ControlBase.consumeResources(self, resources)
        if result:
            self.buildScreen.resourceDisplay.update(self.resources)
        return result

    def addResources(self, resourceType, amount):
        ControlBase.addResources(self, resourceType, amount)
        self.buildScreen.resourceDisplay.update(self.resources)

    def addBulkResources(self, resources):
        ControlBase.addBulkResources(self, resources)
        self.buildScreen.resourceDisplay.update(self.resources)

    def update(self, dt):
        if len(self.queue1) > 0:
            self.queue1[0].active = True
            self.queue1[0].update(dt)
        if self.secondQueueActive and len(self.queue2) > 0:
            self.queue2[0].active = True
            self.queue2[0].update(dt)