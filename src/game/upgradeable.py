from src.game.gamedata import upgrades

class Upgradeable:
    def __init__(self, name):
        self.name = name

        self.value = upgrades[self.name]["startingValue"]
        self.upgradeLevel = 0
        self.onUpgrade = []

        self.upgradeNames = upgrades[self.name]["names"]
        self.upgradeDescriptions = upgrades[self.name]["descriptions"]
        self.upgradeCosts = upgrades[self.name]["costs"]
        self.upgradeValues = upgrades[self.name]["values"]

    def value(self):
        return self.value

    def getUpgradeName(self):
        if self.upgradeLevel >= 3:
            return None
        return self.upgradeNames[self.upgradeLevel]

    def getUpgradeDescription(self):
        if self.upgradeLevel >= 3:
            return None
        return self.upgradeDescriptions[self.upgradeLevel]

    def getUpgradeCost(self):
        if self.upgradeLevel >= 3:
            return None
        return self.upgradeCosts[self.upgradeLevel]

    def upgrade(self):
        self.value = self.upgradeValues[self.upgradeLevel]
        self.upgradeLevel += 1
        for function in self.onUpgrade:
            function()