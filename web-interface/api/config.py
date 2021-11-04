import json
import os.path

class Config:
    def __init__(self):
        self.ApiLogFileName = 'api.log'
        self.ApiLogMaxSize = 10240000
        self.ApiLogBackupCount = 2
        self.ApiDebug = True

    def ReadSettingsFromFile(self, configDir):
        configFile = configDir + '/' + 'settings.json'
        if os.path.isfile(configFile):
            with open(configFile) as file:
                dataAsDict = json.load(file)
            dataAsJson = json.loads(json.dumps(dataAsDict))
            try:
                self.ApiLogFileName = dataAsJson["ApiLogFileName"]
                self.ApiLogMaxSize = dataAsJson["ApiLogMaxSize"]
                self.ApiLogBackupCount = dataAsJson["ApiLogBackupCount"]
                self.ApiDebug = dataAsJson["ApiDebug"]                
            except:
                pass

        return




