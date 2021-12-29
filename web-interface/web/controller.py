from flask import Flask, render_template, request
import requests
import json
import logging
import traceback

from globals import configObject

from converters import ConvertToTwoDecimals, ConvertBooleanToText

app = Flask(__name__)
logger = logging.getLogger()

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
def Root():
    try:
        apiInfo = json.loads(requests.get(configObject.ApiRootUrl).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiInfo = []

    try:
        versionInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetVersionInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        versionInfo = []

    return render_template(
        'home.html', 
        appTitle = configObject.AppTitle, 
        apiInfo = apiInfo,
        apiRootUrl = configObject.ApiRootUrl,
        versionInfo = versionInfo
    )
    pass

@app.route('/disks', methods=['GET'])
def ShowDisks():
    try:
        diskList = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetDiskList').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        diskList = []

    return render_template(
        'disks.html', 
        appTitle = 'Disks - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        diskList = diskList
    )    
    pass

@app.route('/api-list', methods=['GET'])
def ShowApiList():    
    try:
        apiList = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetApiList').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiList = []

    return render_template(
        'api-list.html', 
        appTitle = 'API Documentation - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        apiList = apiList
    )    
    pass

@app.route('/transcoder', methods=['GET'])
def ShowTranscoderSettings():
    try:
        transcoderSettings = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetTranscoderSettings').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        transcoderSettings = []

    return render_template(
        'transcoder.html', 
        appTitle = 'Transcoder - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        transcoderSettings = transcoderSettings
    )    
    pass

@app.route('/docker', methods=['GET'])
def ShowDocker():
    try:
        dockerContainerList = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetDockerContainerList').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        dockerContainerList = []

    return render_template(
        'docker.html', 
        appTitle = 'Docker - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        dockerContainerList = dockerContainerList
    )   
    pass     

@app.route('/machine', methods=['GET'])
def ShowMachine():
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
        appTitle = 'Machine - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        machineInfo = machineInfo,
        resourceInfo = resourceInfo
    )   
    pass     

@app.route('/commands', methods=['GET'])
def ShowCommands():
    return render_template(
        'commands.html', 
        appTitle = 'Commands - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl
    )   
    pass     

@app.route('/commands/backup-server', methods=['GET'])
def DoBackupServer():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoBackupServer').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    return render_template(
        'command.html', 
        appTitle = 'BackupServer - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        commandTitle = 'BackupServer',
        commandMessage = 'Backup is in progress...',
        showBackugLogLinks = 1)
    pass     

@app.route('/commands/update-server', methods=['GET'])
def DoUpdateServer():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoUpdateServer').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    return render_template(
        'command.html', 
        appTitle = 'UpdateServer - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        commandTitle = 'UpdateServer',
        commandMessage = 'Update is in progress... watch backup-log for details'
    )   
    pass     

@app.route('/commands/halt-server', methods=['GET'])
def DoHaltServer():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoHaltServer').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    return render_template(
        'command.html', 
        appTitle = 'HaltServer - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        commandTitle = 'HaltServer',
        commandMessage = 'Halt is in progress... in a few seconds this page will be redirected to Home and stops working',
        redirect = 1
    )   
    pass     

@app.route('/commands/reboot-server', methods=['GET'])
def DoRebootServer():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoRebootServer').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    return render_template(
        'command.html', 
        appTitle = 'RebootServer - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        commandTitle = 'RebootServer',
        commandMessage = 'Reboot is in progress... in a few seconds this page will be redirected to Home; refresh this page after 1 minute',
        redirect = 1
    )   
    pass     

@app.route('/logs', methods=['GET'])
def ShowLogs():
    return render_template(
        'logs.html', 
        appTitle = 'Logs - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl
    )   
    pass     

@app.route('/logs/api/<int:nrOfLines>', methods=['GET'])
def ShowApiLog(nrOfLines):
    try:
        logLines = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetApiLog/' + str(nrOfLines)).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        logLines = []

    return render_template(
        'loglines.html', 
        appTitle = 'API-log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'ApiLog'
    )   
    pass     

@app.route('/logs/backup/<int:nrOfLines>', methods=['GET'])
def ShowBackupLog(nrOfLines):
    try:
        logLines = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetBackupLog/' + str(nrOfLines)).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        logLines = []

    return render_template(
        'loglines.html', 
        appTitle = 'Backup-log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'BackupLog'
    )   
    pass     

@app.route('/logs/backup-details/<int:nrOfLines>', methods=['GET'])
def ShowBackupDetailsLog(nrOfLines):
    try:
        logLines = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetBackupDetailsLog/' + str(nrOfLines)).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        logLines = []

    return render_template(
        'loglines.html', 
        appTitle = 'BackupDetails-log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'BackupDetailsLog'
    )   
    pass     

@app.route('/logs/transcoder/<int:nrOfLines>', methods=['GET'])
def ShowTranscoderLog(nrOfLines):
    try:
        logLines = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetTranscoderLog/' + str(nrOfLines)).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        logLines = []

    return render_template(
        'loglines.html', 
        appTitle = 'Transcoder-log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'TranscoderLog'
    )   
    pass     

@app.route('/logs/update/<int:nrOfLines>', methods=['GET'])
def ShowUpdateLog(nrOfLines):
    try:
        logLines = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetUpdateLog/' + str(nrOfLines)).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        logLines = []

    return render_template(
        'loglines.html', 
        appTitle = 'Update-log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'UpdateLog'
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

    if configObject.Debug:
        logger.info('Web started - debug')
        app.run(port=1080, debug=True)  # auto-reload on file change, only localhost
    else:
        logger.info('Web started - production')
        app.run(host='0.0.0.0', port=80)  # public server, reachable from remote
    logger.info('Web stopped')

