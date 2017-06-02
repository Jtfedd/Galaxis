from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

from src.core.showbase import *

class SkyboxDesigner(DirectObject):
    def __init__(self):
        base.win.setClearColor(Vec4(0,0,0,1))
        base.camLens.setFov(82)
        self.skyboxName = "Planet 2"
        self.model = loader.loadModel("data/skyboxes/"+self.skyboxName+"/model")
        self.model.setLightOff()
        self.model.reparentTo(render)
        self.model.setScale(100)
        
        self.test = loader.loadModel("data/sphere")
        self.test.reparentTo(render)
        
        self.alButton = DirectButton(text = "Add Ambient Light",
                                     scale = .07,
                                     command = self.addAmbientLight,
                                     pos = (-.8, 0, -.5))
                                     
        self.dlButton = DirectButton(text = "Add Directional Light",
                                     scale = .07,
                                     command = self.addDirectionalLight,
                                     pos = (-.8, 0, -.65))
                                     
        self.addButton = DirectButton(text = "Add Data",
                                      scale = .07,
                                      command = self.addData,
                                      pos = (0, 0, -.8))
                                      
        self.clearButton = DirectButton(text = "Clear All",
                                        scale = .07,
                                        command = self.clearData,
                                        pos = (.4, 0, -.8))
                                      
        self.saveButton = DirectButton(text = "Save",
                                       scale = .07,
                                       command = self.save,
                                       pos = (.8, 0, -.8))
                                     
        self.gui = []
        self.lines = []
        self.lights = []
        
        self.currentAction = None
        self.currentColorR = 1
        self.currentColorG = 1
        self.currentColorB = 1
        self.currentX = 0
        self.currentY = 0
        self.currentZ = 0
        self.tempLight = None
        self.tempLightNP = None
                                     
    def addAmbientLight(self):
        self.destroyGui()
        self.gui.append(OnscreenImage(image = "data/images/white.png", scale = .2))
        self.gui.append(DirectSlider(scale = .5, range = (0, 1), value = self.currentColorR, pos = (0, 0, .6), command = self.updateValues))
        self.gui.append(DirectSlider(scale = .5, range = (0, 1), value = self.currentColorG, pos = (0, 0, .5), command = self.updateValues))
        self.gui.append(DirectSlider(scale = .5, range = (0, 1), value = self.currentColorB, pos = (0, 0, .4), command = self.updateValues))
        self.gui.append(OnscreenText(text = "Add Ambient Light:", scale = .07, pos = (0, .8), fg = (1,1,1,1)))
        self.tempLight = AmbientLight('alight')
        self.tempLight.setColor(VBase4(self.currentColorR, self.currentColorG, self.currentColorB, 1))
        self.tempLightNP = render.attachNewNode(self.tempLight)
        render.setLight(self.tempLightNP)
        self.currentAction = "AmbientLight"
    
    def addDirectionalLight(self):
        self.destroyGui()
        self.gui.append(OnscreenImage(image = "data/images/white.png", scale = .2, pos = (.8, 0, .5)))
        self.gui.append(DirectSlider(scale = .5, range = (0, 1), value = self.currentColorR, pos = (0, 0, .6), command = self.updateValues))
        self.gui.append(DirectSlider(scale = .5, range = (0, 1), value = self.currentColorG, pos = (0, 0, .5), command = self.updateValues))
        self.gui.append(DirectSlider(scale = .5, range = (0, 1), value = self.currentColorB, pos = (0, 0, .4), command = self.updateValues))
        self.gui.append(DirectSlider(scale = .5, range = (-1, 1), value = self.currentX, pos = (0, 0, .3), command = self.updateValues))
        self.gui.append(DirectSlider(scale = .5, range = (-1, 1), value = self.currentY, pos = (0, 0, .2), command = self.updateValues))
        self.gui.append(DirectSlider(scale = .5, range = (-1, 1), value = self.currentZ, pos = (0, 0, .1), command = self.updateValues))
        self.gui.append(OnscreenText(text = "Add Directional Light:", scale = .07, pos = (0, .8), fg = (1,1,1,1)))
        self.pointer = loader.loadModel("data/pointer")
        self.pointer.setLightOff()
        self.pointer.reparentTo(render)
        self.pointer.setPos(self.currentX*100, self.currentY*100, self.currentZ*100)
        self.tempLight = DirectionalLight("dlight")
        self.tempLight.setColor(VBase4(self.currentColorR, self.currentColorG, self.currentColorB, 1))
        self.tempLight.setSpecularColor(VBase4(self.currentColorR, self.currentColorG, self.currentColorB, 1))
        self.tempLightNP = render.attachNewNode(self.tempLight)
        self.tempLightNP.setPos(self.currentX, self.currentY, self.currentZ)
        self.tempLightNP.lookAt((0,0,0))
        render.setLight(self.tempLightNP)
        self.currentAction = "DirectionalLight"
    
    def destroyGui(self):
        while len(self.gui)>0:
            g = self.gui[0]
            g.destroy()
            self.gui.remove(g)
        if self.currentAction == "DirectionalLight":
            self.pointer.removeNode()
        if self.currentAction != "Hyperspace" and self.currentAction != None:
            render.clearLight(self.tempLightNP)
            self.tempLightNP.removeNode()
            self.tempLight = None
        self.currentAction = None
        
    def addData(self):
        if self.currentAction == "AmbientLight":
            alight = AmbientLight('alight')
            alight.setColor(VBase4(self.currentColorR, self.currentColorG, self.currentColorB, 1))
            alnp = render.attachNewNode(alight)
            render.setLight(alnp)
            self.lights.append(alnp)
            self.lines.append("ambientLight:"+str(self.currentColorR)+":"+str(self.currentColorG)+":"+str(self.currentColorB)+"\n")
        if self.currentAction == "DirectionalLight":
            dlight = DirectionalLight("dlight")
            dlight.setColor(VBase4(self.currentColorR, self.currentColorG, self.currentColorB, 1))
            dlight.setSpecularColor(VBase4(self.currentColorR, self.currentColorG, self.currentColorB, 1))
            dlnp = render.attachNewNode(dlight)
            dlnp.setPos(self.currentX, self.currentY, self.currentZ)
            dlnp.lookAt((0,0,0))
            render.setLight(dlnp)
            self.lights.append(dlnp)
            self.lines.append("directionalLight:"+str(self.currentColorR)+":"+str(self.currentColorG)+":"+str(self.currentColorB)+":"+str(self.currentX)+":"+str(self.currentY)+":"+str(self.currentZ)+"\n")
        if self.currentAction == "Hyperspace":
            for line in self.lines:
                if line[0] == "h":
                    self.lines.remove(line)
            self.lines.append("hyperspaceColor:"+str(self.currentColorR)+":"+str(self.currentColorG)+":"+str(self.currentColorB)+"\n")
        self.destroyGui()
        
    def clearData(self):
        self.lines = []
        while len(self.lights)>0:
            render.clearLight(self.lights[0])
            self.lights.remove(self.lights[0])
        
    def save(self):
        file = open("data/skyboxes/"+self.skyboxName+"/data.txt", "w")
        for line in self.lines:
            file.write(line)
        file.close()
        
    def updateValues(self):
        if self.currentAction == "AmbientLight":
            self.currentColorR = self.gui[1]["value"]
            self.currentColorG = self.gui[2]["value"]
            self.currentColorB = self.gui[3]["value"]
            self.tempLight.setColor(VBase4(self.currentColorR, self.currentColorG, self.currentColorB, 1))
            self.gui[0].setColorScale(self.currentColorR, self.currentColorG, self.currentColorB, 1)
        if self.currentAction == "DirectionalLight":
            self.currentColorR = self.gui[1]["value"]
            self.currentColorG = self.gui[2]["value"]
            self.currentColorB = self.gui[3]["value"]
            self.gui[0].setColorScale(self.currentColorR, self.currentColorG, self.currentColorB, 1)
            self.currentX = self.gui[4]["value"]
            self.currentY = self.gui[5]["value"]
            self.currentZ = self.gui[6]["value"]
            self.pointer.setPos(self.currentX*100, self.currentY*100, self.currentZ*100)
            self.pointer.lookAt((0,0,0))
            self.tempLightNP.setPos(self.currentX, self.currentY, self.currentZ)
            self.tempLightNP.lookAt((0,0,0))
            self.tempLight.setColor(VBase4(self.currentColorR, self.currentColorG, self.currentColorB, 1))
            self.tempLight.setSpecularColor(VBase4(self.currentColorR, self.currentColorG, self.currentColorB, 1))
        if self.currentAction == "Hyperspace":
            self.currentColorR = self.gui[1]["value"]
            self.currentColorG = self.gui[2]["value"]
            self.currentColorB = self.gui[3]["value"]
            self.gui[0].setShaderInput("tint", Vec3(self.currentColorR, self.currentColorG, self.currentColorB))
        
sd = SkyboxDesigner()
run()