import json

class Config:
    def __init__(self):
        self.LogFileName = 'logs/rpmusicserver-api.log'
        self.LogMaxSize = 10240000
        self.LogBackupCount = 10

    def ReadSettingsFromFile(self, configDir):
        with open(configDir + '/' + 'api-settings.json') as file:
            data = json.load(file)

        self.LogFileName = 'xxx'
        self.LogMaxSize = 10
        self.LogBackupCount = 1
        return




