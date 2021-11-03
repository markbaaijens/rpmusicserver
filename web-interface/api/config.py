class Config:
    def __init__(self):
        self.LogFileName = 'logs/rpmusicserver-api.log'
        self.LogMaxSize = 10240000
        self.LogBackupCount = 10

    def ReadSettingsFromFile(self):
        self.LogFileName = 'xxx'
        self.LogMaxSize = 10
        self.LogBackupCount = 1
        return
