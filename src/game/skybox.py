from panda3d.core import *

from src.core.showbase import *

class Skybox:
    def __init__(self, systemName, root):
        self.root = root
        self.name = systemName
        self.model = loader.loadModel("data/skyboxes/" + systemName + "/model")
        self.model.setLightOff()
        self.model.reparentTo(root)
        self.model.setPos(base.camera.getPos(render))
        self.model.setScale(100)
        self.model.setDepthWrite(False)
        self.model.setBin("background", 50)

        self.lights = []

        dataFile = open("data/skyboxes/" + systemName + "/data.txt", "r")
        data = dataFile.read()
        dataFile.close()
        data = data.split("\n")

        for line in data:
            lineData = line.split(":")
            if lineData[0] == "ambientLight":
                alight = AmbientLight('alight')
                alight.setColor(VBase4(float(lineData[1]), float(lineData[2]), float(lineData[3]), 1))
                alnp = root.attachNewNode(alight)
                root.setLight(alnp)
                self.lights.append(alnp)
            if lineData[0] == "directionalLight":
                dlight = DirectionalLight("dlight")
                dlight.setColor(Vec4(float(lineData[1]), float(lineData[2]), float(lineData[3]), 1))
                dlight.setSpecularColor(Vec4(float(lineData[1]), float(lineData[2]), float(lineData[3]), 1))
                dlnp = root.attachNewNode(dlight)
                dlnp.setHpr(float(lineData[4]), float(lineData[5]), 0)
                root.setLight(dlnp)
                self.lights.append(dlnp)

    def update(self):
        self.model.setPos(base.camera.getPos(render))

    def destroy(self):
        self.model.removeNode()
        for l in self.lights:
            self.root.clearLight(l)
            l.removeNode()