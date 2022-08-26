from flask import Flask, render_template, request, redirect, flash
from flask_wtf import CSRFProtect
import requests
import json
import logging
import traceback
import os

from globals import configObject
from converters import ConvertToTwoDecimals, ConvertBooleanToText
from forms import EditTranscoderForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)  # For flask/wtf-forms
csrf = CSRFProtect() # SRSF-setup for wtf-forms
csrf.init_app(app)

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

def SizeHumanReadable(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

@app.route('/', methods=['GET'])
def Home():
    try:
        machineInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetMachineInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        machineInfo = []

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
        appTitle = 'Home - ' + configObject.AppTitle, 
        apiInfo = apiInfo,
        apiRootUrl = configObject.ApiRootUrl,
        machineInfo = machineInfo,
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

@app.route('/services', methods=['GET'])
def ShowServices():
    try:
        serviceList = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetServiceList').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        serviceList = []

    return render_template(
        'services.html', 
        appTitle = 'Services - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        serviceList = serviceList
    )   
    pass     

@app.route('/resources', methods=['GET'])
def ShowResources():
    try:
        resourceInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetResourceInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        resourceInfo = []
    
    resourceInfo['MemTotal'] = SizeHumanReadable(int(resourceInfo['MemTotal']) * 1024, '')
    resourceInfo['MemUsed'] = SizeHumanReadable(int(resourceInfo['MemUsed']) * 1024, '')    
    resourceInfo['SwapTotal'] = SizeHumanReadable(int(resourceInfo['SwapTotal']) * 1024, '')
    resourceInfo['SwapUsed'] = SizeHumanReadable(int(resourceInfo['SwapUsed']) * 1024, '')    

    return render_template(
        'resources.html', 
        appTitle = 'Resources - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        resourceInfo = resourceInfo
    )   
    pass     

@app.route('/tasks', methods=['GET'])
def ShowCommands():
    try:
        versionInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetVersionInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        versionInfo = []

    return render_template(
        'tasks.html', 
        appTitle = 'Commands - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        versionInfo = versionInfo
    )   
    pass     

@app.route('/backup-server', methods=['GET'])
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
        showBackugLogLinks = 1
    )
    pass     

@app.route('/kill-docker', methods=['GET'])
def DoKillDocker():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoKillDocker').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    return render_template(
        'command.html', 
        appTitle = 'KillDocker - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        commandTitle = 'KillDocker',
        commandMessage = 'Killing docker-containers is in progress...',
        showDockerLink = 1
    )
    pass     

@app.route('/update-server', methods=['GET'])
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
        commandMessage = 'Update is in progress... in a few seconds you will be redirected to Home; refresh that page after 1 minute',
        redirect = 1        
    )   
    pass     

@app.route('/halt-server', methods=['GET'])
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

@app.route('/reboot-server', methods=['GET'])
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
        commandMessage = 'Reboot is in progress... in a few seconds you will be redirected to Home; refresh that page after 1 minute',
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

@app.route('/logs/web/<int:nrOfLines>', methods=['GET'])
def ShowWebLog(nrOfLines):
    try:
        logLines = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetWebLog/' + str(nrOfLines)).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        logLines = []

    return render_template(
        'loglines.html', 
        appTitle = 'Web-log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'WebLog'
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

@app.route('/transcoder/edit', methods=['GET', 'POST'])
def EditTranscoderSettings():
    musicFolder = '/media/usbdata/user/Publiek/Muziek/'

    form = EditTranscoderForm()

    try:
        transcoderSettings = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetTranscoderSettings').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        transcoderSettings = []

    if request.method == 'GET':
        form.sourceFolder.data = transcoderSettings['sourcefolder'].replace(musicFolder, '')
        form.oggFolder.data = transcoderSettings['oggfolder'].replace(musicFolder, '')
        form.oggQuality.data = transcoderSettings['oggquality']
        form.mp3Folder.data = transcoderSettings['mp3folder'].replace(musicFolder, '')
        form.mp3Bitrate.data = transcoderSettings['mp3bitrate']

    if request.method == 'POST' and form.validate(): 
        newSourceFolder = musicFolder + request.form['sourceFolder'].strip()
        if not newSourceFolder.replace(musicFolder, ''):
            newSourceFolder = ''
        if newSourceFolder != transcoderSettings['sourcefolder'].strip():
            try:
                requests.post(
                    configObject.ApiRootUrl + '/api/SetTranscoderSourceFolder', 
                    json = {"Value": newSourceFolder})
                flash('Saved \'' + newSourceFolder + '\' to SourceFolder')
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

        newOggFolder = musicFolder + request.form['oggFolder'].strip()
        if not newOggFolder.replace(musicFolder, ''):
            newOggFolder = ''
        if newOggFolder != transcoderSettings['oggfolder'].strip():
            try:
                requests.post(
                    configObject.ApiRootUrl + '/api/SetTranscoderOggFolder', 
                    json = {"Value": newOggFolder})
                flash('Saved \'' + newOggFolder + '\' to OggFolder')
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

        if int(request.form['oggQuality']) != int(transcoderSettings['oggquality']):
            try:
                requests.post(
                    configObject.ApiRootUrl + '/api/SetTranscoderOggQuality', 
                    json = {"Value": int(request.form['oggQuality'])})
                flash('Saved \'' + request.form['oggQuality'] + '\' to OggQuality')
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

        newMp3Folder = musicFolder + request.form['mp3Folder'].strip()
        if not newMp3Folder.replace(musicFolder, ''):
            newMp3Folder = ''            
        if newMp3Folder != transcoderSettings['mp3folder'].strip():
            try:
                requests.post(
                    configObject.ApiRootUrl + '/api/SetTranscoderMp3Folder', 
                    json = {"Value": newMp3Folder})
                flash('Saved \'' + newMp3Folder + '\' to Mp3Folder')
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

        if int(request.form['mp3Bitrate']) != int(transcoderSettings['mp3bitrate']):
            try:
                requests.post(
                    configObject.ApiRootUrl + '/api/SetTranscoderMp3Bitrate', 
                    json = {"Value": int(request.form['mp3Bitrate'])})
                flash('Saved \'' + request.form['mp3Bitrate'] + '\' to Mp3Bitrate')
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

        return redirect('/transcoder')

    return render_template('transcoder-edit.html', 
        appTitle = 'TransCoderEdit - ' + configObject.AppTitle, 
        form = form,
        musicFolder = musicFolder)

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

