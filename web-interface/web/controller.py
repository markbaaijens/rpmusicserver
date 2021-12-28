# TODO Exception handling API-calls (based on return codes op calls) 
# TODO see: https://flask.palletsprojects.com/en/1.1.x/patterns/apierrors/
# TODO Error when service not found when doing a request

from flask import Flask, render_template, request
import requests
import json
import logging
import traceback

from globals import configObject

from converters import ConvertToTwoDecimals, ConvertBooleanToText

app = Flask(__name__)
logger = logging.getLogger()
apiInfo = []

def GetApiInfo():
    global apiInfo
    try:
        apiInfo = json.loads(requests.get(configObject.ApiRootUrl).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiInfo = []
    pass

def SetupLogger():
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler(configObject.LogFileName, 'a')
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(fileHandler)

        # By default, console logging is disabled once logger is activated; to still see console messages, 
        # a consoleHandler must be created
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(consoleHandler)
    pass

@app.route('/', methods=['GET'])
def index():
    global apiInfo

    try:
        versionInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetVersionInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        versionInfo = []

    return render_template(
        'details.html', 
        appTitle = configObject.AppTitle, 
        apiInfo = apiInfo,
        apiRootUrl = configObject.ApiRootUrl,
        versionInfo = versionInfo
    )
    pass

@app.route('/disks', methods=['GET'])
def ShowDisks():
    global apiInfo

    try:
        diskList = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetDiskList').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        diskList = []

    return render_template(
        'disks.html', 
        appTitle = configObject.AppTitle, 
        apiInfo = apiInfo,
        apiRootUrl = configObject.ApiRootUrl,
        diskList = diskList
    )    
    pass

@app.route('/docker', methods=['GET'])
def ShowDocker():
    global apiInfo

    try:
        dockerContainerList = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetDockerContainerList').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        dockerContainerList = []

    return render_template(
        'docker.html', 
        appTitle = configObject.AppTitle, 
        apiInfo = apiInfo,
        apiRootUrl = configObject.ApiRootUrl,
        dockerContainerList = dockerContainerList
    )   
    pass     

@app.route('/machine', methods=['GET'])
def ShowMachine():
    global apiInfo

    try:
        machineInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetMachineInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        machineInfo = []

    try:
        resourceInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetResourceInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        resourceInfo = []

    return render_template(
        'machine.html', 
        appTitle = configObject.AppTitle, 
        apiInfo = apiInfo,
        apiRootUrl = configObject.ApiRootUrl,
        machineInfo = machineInfo,
        resourceInfo = resourceInfo
    )   
    pass     

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Controller for RP Music Server Web')
    parser.add_argument('--logfile', type=str,  help="file where log is stored", nargs=1) 
    parser.add_argument('-p', '--production', help="start a production server", action="store_true")        

    args = parser.parse_args()

    configObject.Debug = not args.production

    if (args.logfile != None) and (args.logfile[0] != ''):
        configObject.LogFileName = args.logfile[0]

    SetupLogger()       
    logger.info('Log to: ' + configObject.LogFileName)
    GetApiInfo()

    if configObject.Debug:
        logger.info('Web started - debug')
        app.run(port=1080, debug=True)  # auto-reload on file change, only localhost
    else:
        logger.info('Web started - production')
        app.run(host='0.0.0.0', port=80)  # public server, reachable from remote
    logger.info('Web stopped')

