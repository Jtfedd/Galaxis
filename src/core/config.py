from src.core.filemgr import openFile

class __Config:
    def __init__(self):
        self.configVars = {}

        self.loadConfig()

    def loadConfig(self):
        configFile = None
        try:
            configFile = openFile('config/config.cfg', 'r')
        except IOError:
            self.genDefaultConfig()
            return

        lines = configFile.readlines()
        for line in lines:
            data = line.split(':')
            if data[0] == "musicVolume":
                self.setMusicVolume(data[1])
        configFile.close()

    def saveConfig(self):
        configFile = openFile('config/config.cfg', 'w')
        for key in self.configVars.keys():
            configFile.write(key + ":" + self.configVars[key] + "\n")
        configFile.close()

    def genDefaultConfig(self):
        print "generated default"
        self.setMusicVolume(0.25)

        self.saveConfig()

    def setMusicVolume(self, vol):
        self.configVars['musicVolume'] = str(vol)

    def getMusicVolume(self):
        return float(self.configVars['musicVolume'])

CONFIG = __Config()