import math
import random

from direct.filter.FilterManager import FilterManager
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *

from src.core.config import CONFIG
from src.core.showbase import *


def weightedRandom(probStart, probEnd):
    probRandom = random.randrange(1000) / 1000.0
    distFact = probStart + (probEnd - probStart) * probRandom
    return random.randrange(int(distFact * 1000)) / 1000.0

def setupFilters():
    # Threshold (x,y,z) and brightness (w) settings
    threshold = Vec4(0.1, 0.1, 0.1, 1.0)

    # FilterManager
    manager = FilterManager(base.win, base.cam)
    tex1 = Texture()
    tex2 = Texture()
    tex3 = Texture()
    tex4 = Texture()
    finalquad = manager.renderSceneInto(colortex=tex1)
    # First step - threshold and radial blur
    interquad = manager.renderQuadInto(colortex=tex2)
    interquad.setShader(Shader.load("data/shaders/invert_threshold_r_blur.sha"))
    interquad.setShaderInput("tex1", tex1)
    interquad.setShaderInput("threshold", threshold)
    # Second step - hardcoded fast gaussian blur.
    interquad2 = manager.renderQuadInto(colortex=tex3)
    interquad2.setShader(Shader.load("data/shaders/gaussian_blur.sha"))
    interquad2.setShaderInput("tex2", tex2)
    # Third step - Make lens flare and blend it with the main scene picture
    interquad3 = manager.renderQuadInto(colortex=tex4)
    interquad3.setShader(Shader.load("data/shaders/lens_flare.sha"))
    interquad3.setShaderInput("tex1", tex1)
    interquad3.setShaderInput("tex2", tex2)
    interquad3.setShaderInput("tex3", tex3)
    # Final step - colorize
    finalquad.setShader(Shader.load("data/shaders/tint.sha"))
    finalquad.setShaderInput("tex4", tex4)
    finalquad.setShaderInput("tint", Vec3(0.0, 0.2, 1.0))

    return manager

class MenuBackground(DirectObject):
    def __init__(self):
        self.loadedModel = loader.loadModel('data/models/menu/particle')
        self.loadedModel.reparentTo(render)
        self.loadedModel.setPos(0, -100, 0)
        self.loadedModel.node().setBounds(OmniBoundingVolume())
        self.loadedModel.node().setFinal(True)

        self.musicMgr = MusicManager()

        self.pause = False

        self.isStarting = True
        self.isEnding = False
        self.done = False
        self.endStartTime = 0

        self.particleRate = 0
        self.particleTime = 0

        base.camLens.setFov(80)
        base.setBackgroundColor(0, 0, 0)
        base.camera.lookAt(0, 1, 0)
        render.setShaderAuto()
        self.filterManager = setupFilters()
        self.root = render.attachNewNode('menu-background-root')

        self.particleManager = ParticleManager(self)

        self.updateTask = None

    def start(self):
        taskMgr.doMethodLater(1, self.actuallyStart, 'startdelay')

    def actuallyStart(self, task):
        self.updateTask = taskMgr.add(self.update, 'menu-background-update')
        self.musicMgr.start()

    def end(self, newGame = False):
        if not self.isStarting:
            self.isEnding = True
        self.musicMgr.end(newGame)

    def setPause(self, val):
        self.pause = val

    def update(self, task):
        if self.pause: return task.cont

        if self.isStarting:
            if task.time < 4:
                timeFact = (task.time - 1) / 3.0
                self.particleRate = 5 + max(700 * (timeFact ** 3), 0)
                self.spawnParticles(30 - (30 * timeFact), 30)
            else:
                self.isStarting = False
                self.particleRate = 50
        elif self.isEnding:
            if self.endStartTime == 0:
                self.endStartTime = task.time
            time = task.time - self.endStartTime
            if time < 1:
                self.particleRate = 20 + 500.0 * time
                self.spawnParticles(2, 30 - (20 * time))
            else:
                self.particleRate = 0
                self.isEnding = False
                self.done = True
        else:
            self.spawnParticles(2, 30)

        self.particleTime += min(globalClock.getDt(), .1)
        self.particleManager.update(globalClock.getDt())

        if self.done and len(self.particleManager.activeParticles) == 0:
            self.destroy()
            return task.done

        return task.cont

    def spawnParticles(self, num1, num2):
        if self.done:
            return
        self.particleRate = max(1, self.particleRate)
        while self.particleTime > 1.0 / self.particleRate:
            self.particleManager.spawnParticle(num1, num2)

            self.particleTime -= 1.0 / self.particleRate

    def destroy(self):
        self.filterManager.cleanup()
        self.loadedModel.removeNode()
        self.particleManager.destroy()
        self.root.removeNode()

class ParticleManager:
    def __init__(self, parent):
        self.activeParticles = []
        self.inactiveParticles = []

        for i in range(260):
            self.inactiveParticles.append(Particle(self, parent.root))

    def update(self, dt):
        for p in self.activeParticles:
            p.update(dt)

    def spawnParticle(self, num1, num2):
        if len(self.inactiveParticles) == 0: return
        tmp = self.inactiveParticles.pop()
        tmp.activate(num1, num2)
        self.activeParticles.append(tmp)

    def destroy(self):
        for p in self.activeParticles: p.destroy()
        for p in self.inactiveParticles: p.destroy()

class Particle:
    def __init__(self, manager, root):
        self.manager = manager
        self.lifeTime = 0
        self.node = loader.loadModel('data/models/menu/particle')
        self.node.reparentTo(root)
        self.node.setPos(0, -10, 0)
        self.node.setScale(1, 1, 4)
        self.node.setTransparency(TransparencyAttrib.MDual)
        self.node.setAlphaScale(0.0)
        self.node.setDepthWrite(False)
        self.node.hide()

    def activate(self, num1, num2):
        self.lifeTime = 0
        angle = random.randrange(62831854) / 10000000.0
        dist = weightedRandom(num1, num2)
        x = dist * math.cos(angle)
        y = dist * math.sin(angle)
        self.node.setPos(x, 200, y)
        self.node.lookAt(0, 200, 0)
        self.node.show()

    def deactivate(self):
        self.manager.activeParticles.remove(self)
        self.manager.inactiveParticles.append(self)
        self.node.hide()

    def update(self, dt):
        self.lifeTime += dt
        self.node.setAlphaScale(min(self.lifeTime * 10, 1.0))
        self.node.setY(self.node.getY() - 500 * dt)
        if self.node.getX() + self.node.getZ() < 2:
            self.node.setY(self.node, -4 * dt)

        if self.node.getY() < -10:
            self.deactivate()

    def destroy(self):
        self.node.removeNode()

class MusicManager:
    def __init__(self):
        self.music = loader.loadMusic('data/sounds/music/Killers.wav')
        self.music.setLoop(True)

        self.newGameMusic = loader.loadMusic('data/sounds/music/Thunderbird.wav')
        self.newGameMusic.setLoop(True)

        self.outro = loader.loadSfx('data/sounds/music/outro.wav')

        self.newGame = False

    def start(self):
        taskMgr.doMethodLater(2, self.startMusic, 'musicStartDelay')

    def end(self, newGame = False):
        self.newGame = newGame
        self.outro.play()
        self.outro.setVolume(CONFIG.getMusicVolume())
        taskMgr.doMethodLater(1.5, self.endMusic, 'musicEndDelay')

    def startMusic(self, task):
        self.music.play()
        self.music.setVolume(CONFIG.getMusicVolume())

    def endMusic(self, task):
        self.music.stop()
        if self.newGame:
            self.newGameMusic.play()
            self.newGameMusic.setVolume(CONFIG.getMusicVolume())

    def endNewGameMusic(self):
        if not self.newGame: return
        taskMgr.add(self.fadeOutNewGameMusic, 'fadeOutMusic')

    def fadeOutNewGameMusic(self, task):
        vol = max(0, .25 - (task.time / 8.0))
        self.newGameMusic.setVolume(vol)
        if vol == 0:
            self.newGameMusic.stop()
            return task.done
        return task.cont
