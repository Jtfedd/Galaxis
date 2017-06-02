from src.game.upgradeable import Upgradeable

class ControlBase:
    def __init__(self, team):
        self.team = team

        self.resources = {"science": 10000, "credits": 10000, "fuel": 10000}

        self.props = {"buildSpeed": Upgradeable("buildspeed"),
                      "buildCost": Upgradeable("buildcost"),
                      "fuelCost": Upgradeable("fuelcost"),
                      "researchSpeed": Upgradeable("researchspeed"),
                      "researchCost": Upgradeable("researchcost"),
                      "shieldStrength": Upgradeable("shieldstrength"),
                      "shotDamage": Upgradeable("shotdamage")}

        self.props["researchCost"].onUpgrade.append(self.updateResearchCosts)
        self.props["buildCost"].onUpgrade.append(self.updateBuildCosts)
        self.props["fuelCost"].onUpgrade.append(self.updateFuelCosts)
        self.props["shieldStrength"].onUpgrade.append(self.updateShieldStrength)
        self.props["shotDamage"].onUpgrade.append(self.updateShotDamage)

    def updateResearchCosts(self):
        # TODO
        print "update research costs"
        pass

    def updateBuildCosts(self):
        # TODO
        print "update build costs"
        pass

    def updateFuelCosts(self):
        # TODO
        print "update fuel costs"
        pass

    def updateShieldStrength(self):
        # TODO
        print "update shield strength"
        pass

    def updateShotDamage(self):
        # TODO
        print "update shot damage"
        pass

    def upgradeProp(self, prop):
        if self.consumeResources(self.props[prop].getUpgradeCost()):
            self.props[prop].upgrade()
            return True
        return False

    def get(self, prop):
        return self.props[prop].value()

    def addResources(self, resourceType, amount):
        self.resources[resourceType] += amount

    def addBulkResources(self, resources):
        self.resources["science"] += resources["science"]
        self.resources["credits"] += resources["credits"]
        self.resources["fuel"] += resources["fuel"]

    def hasResources(self, resources):
        return self.resources["science"] >= resources["science"] and self.resources["credits"] >= resources["credits"] and self.resources["fuel"] >= resources["fuel"]

    def consumeResources(self, resources):
        if resources is None:
            return False
        if self.resources["science"] < resources["science"] or self.resources["credits"] < resources["credits"] or self.resources["fuel"] < resources["fuel"]:
            return False
        else:
            self.resources["science"] -= resources["science"]
            self.resources["credits"] -= resources["credits"]
            self.resources["fuel"] -= resources["fuel"]
            return True