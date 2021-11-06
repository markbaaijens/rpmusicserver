import json
import os.path

class Config:
    def __init__(self):
        self.LogFileName = 'api.log'
        self.LogMaxSize = 10240000
        self.LogBackupCount = 1
        self.Debug = True
