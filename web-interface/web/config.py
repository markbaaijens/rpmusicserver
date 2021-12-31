import json
import os.path

class Config:
    def __init__(self):
        self.AppTitle = 'RP Music Server'
        self.LogFileName = 'web.log'
        self.Debug = True    
        self.ApiRootUrl = 'http://localhost:5000'
    