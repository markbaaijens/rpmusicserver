import json

class Config:
    def __init__(self):
        self.LogFileName = 'logs/rpmusicserver-api.log'
        self.LogMaxSize = 10240000
        self.LogBackupCount = 10

    def ReadSettingsFromFile(self, configDir):
        with open(configDir + '/' + 'api-settings.json') as file:
            dataAsDict = json.load(file)

        dataAsJson = json.loads(json.dumps(dataAsDict))
        self.LogFileName = dataAsJson["LogFileName"]
        self.LogMaxSize = dataAsJson["LogMaxSize"]
        self.LogBackupCount = dataAsJson["LogBackupCount"]
        return




