import json
import os.path

class Config:
    def __init__(self):
        self.ApiLogFileName = 'api.log'
        self.ApiLogMaxSize = 10240000
        self.ApiLogBackupCount = 1
        self.ApiDebug = True
