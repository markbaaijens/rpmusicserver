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
def ShowHomePage():
    try:
        machineInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetMachineInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        machineInfo = []

    try:
        versionInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetVersionInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        versionInfo = []

    return render_template(
        'home.html', 
        appTitle = 'Home - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        machineInfo = machineInfo,
        versionInfo = versionInfo)

@app.route('/transcoder', methods=['GET'])
def ShowTranscoderPage():
    try:
        transcoderInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetTranscoderInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        transcoderInfo = []

    return render_template(
        'transcoder.html', 
        appTitle = 'Transcoder - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        transcoderInfo = transcoderInfo)    

@app.route('/system', methods=['GET'])
def ShowSystemPage():
    try:
        portStatusList = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetPortStatusList').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        portStatusList = []
    
    try:
        dockerContainerList = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetDockerContainerList').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        dockerContainerList = []

    try:
        apiInfo = json.loads(requests.get(configObject.ApiRootUrl).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiInfo = []

    try:
        machineInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetMachineInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        machineInfo = []        

    return render_template(
        'system.html', 
        appTitle = 'System - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        portStatusList = portStatusList,
        apiInfo = apiInfo,
        dockerContainerList = dockerContainerList,
        machineInfo = machineInfo)   

@app.route('/resources', methods=['GET'])
def ShowResourcesPage():
    try:
        cpuInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetCpuResourceInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        cpuInfo = []

    try:
        memoryInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetMemoryResourceInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        memoryInfo = []

    try:
        diskList = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetDiskList').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        diskList = []
    
    memoryInfo['MemTotal'] = SizeHumanReadable(int(memoryInfo['MemTotal']) * 1024, '')
    memoryInfo['MemUsed'] = SizeHumanReadable(int(memoryInfo['MemUsed']) * 1024, '')    
    memoryInfo['SwapTotal'] = SizeHumanReadable(int(memoryInfo['SwapTotal']) * 1024, '')
    memoryInfo['SwapUsed'] = SizeHumanReadable(int(memoryInfo['SwapUsed']) * 1024, '')    

    return render_template(
        'resources.html', 
        appTitle = 'Resources - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        diskList = diskList,
        cpuInfo = cpuInfo,
        memoryInfo = memoryInfo)   

@app.route('/music', methods=['GET'])
def ShowMusicPage():
    try:
        machineInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetMachineInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        machineInfo = []

    try:
        musicCollectionInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetMusicCollectionInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        musicCollectionInfo = []

    try:
        lmsServerStatus = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetLmsServerStatus').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        lmsServerStatus = []        

    try:
        lmsPlayers = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetLmsPlayers').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        lmsPlayers = []                

    return render_template(
        'music.html', 
        appTitle = 'Music - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        musicCollectionInfo = musicCollectionInfo,
        lmsServerStatus = lmsServerStatus,
        lmsPlayers = lmsPlayers,
        machineInfo = machineInfo)

@app.route('/backup', methods=['GET'])
def ShowBackupPage():
    try:
        backupInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetBackupInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        backupInfo = []

    return render_template(
        'backup.html', 
        appTitle = 'Backup - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        backupInfo = backupInfo)   

@app.route('/ask-backup-server', methods=['GET'])
def AskBackupServer():
    return render_template(
        'dialog.html', 
        appTitle = 'Backup Server - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        labelText = 'Backup server?',
        proceedUrl = '/backup-server',
        backUrl = request.referrer)

@app.route('/backup-server', methods=['GET'])
def DoBackupServer():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoBackupServer').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    flash(apiMessage['Message'])

    return render_template(
        'message.html', 
        appTitle = 'Backup Server - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        backUrl = '/backup')

@app.route('/ask-kill-docker', methods=['GET'])
def AskKillDocker():
    return render_template(
        'dialog.html', 
        appTitle = 'Kill Docker - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        labelText = 'Kill docker containers?',
        proceedUrl = '/kill-docker',
        backUrl = request.referrer)

@app.route('/kill-docker', methods=['GET'])
def DoKillDocker():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoKillDocker').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    flash(apiMessage['Message'])

    return render_template(
        'message.html', 
        appTitle = 'Kill Docker - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        backUrl = '/system')

@app.route('/ask-start-docker', methods=['GET'])
def AskStartDocker():
    return render_template(
        'dialog.html', 
        appTitle = 'Start Docker - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        labelText = 'Start docker containers?',
        proceedUrl = '/start-docker',
        backUrl = request.referrer)

@app.route('/start-docker', methods=['GET'])
def DoStartDocker():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoStartDocker').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    flash(apiMessage['Message'])        

    return render_template(
        'message.html', 
        appTitle = 'Start Docker - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        backUrl = '/system')

@app.route('/ask-update-docker', methods=['GET'])
def AskUpdateDocker():
    return render_template(
        'dialog.html', 
        appTitle = 'Update Docker - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        labelText = 'Update docker containers?',
        proceedUrl = '/update-docker',
        backUrl = request.referrer)

@app.route('/update-docker', methods=['GET'])
def DoUpdateDocker():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoUpdateDocker').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    flash(apiMessage['Message'])

    return render_template(
        'message.html', 
        appTitle = 'Update Docker - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        backUrl = '/system')

@app.route('/ask-export-collection', methods=['GET'])
def AskExportCollection():
    return render_template(
        'dialog.html', 
        appTitle = 'Export Collection - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        labelText = 'Export collection?',
        proceedUrl = '/export-collection',
        backUrl = request.referrer)

@app.route('/export-collection', methods=['GET'])
def DoExportCollection():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoExportCollection').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    flash(apiMessage['Message'])        

    return render_template(
        'message.html', 
        appTitle = 'Export Collection - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        backUrl = '/music')

@app.route('/ask-transcode', methods=['GET'])
def AskTranscode():
    return render_template(
        'dialog.html', 
        appTitle = 'Transcode - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        labelText = 'Start transcoding?',
        proceedUrl = '/transcode',
        backUrl = request.referrer)

@app.route('/transcode', methods=['GET'])
def DoTranscode():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoTranscode').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    flash(apiMessage['Message'])        

    return render_template(
        'message.html', 
        appTitle = 'Transcode - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        backUrl = '/transcoder')

@app.route('/ask-update-rpms', methods=['GET'])
def AskUpdateRpms():
    return render_template(
        'dialog.html', 
        appTitle = 'Update RPMS - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        labelText = 'Update RPMS?',
        proceedUrl = '/update-rpms',
        backUrl = request.referrer)

@app.route('/update-rpms', methods=['GET'])
def DoUpdateRpms():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoUpdateRpms').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    flash('Update is in progress. Refresh this page after 1 minute.')

    return redirect('/')

@app.route('/ask-halt-server', methods=['GET'])
def AskHaltServer():
    return render_template(
        'dialog.html', 
        appTitle = 'Halt Server - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        labelText = 'Halt server?',
        proceedUrl = '/halt-server',
        backUrl = request.referrer)

@app.route('/halt-server', methods=['GET'])
def DoHaltServer():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoHaltServer').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []

    flash('Halt is in progress. In a few moments the server stops working.')

    return redirect('/')

@app.route('/ask-reboot-server', methods=['GET'])
def AskRebootServer():
    return render_template(
        'dialog.html', 
        appTitle = 'Reboot Server - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        labelText = 'Reboot server?',
        proceedUrl = '/reboot-server',
        backUrl = request.referrer)

@app.route('/reboot-server', methods=['GET'])
def DoRebootServer():
    try:
        apiMessage = json.loads(requests.post(configObject.ApiRootUrl + '/api/DoRebootServer').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiMessage = []
    
    flash('Reboot is in progress. Refresh this page after 1 minute.')

    return redirect('/')

@app.route('/logs', methods=['GET'])
def ShowLogs():
    return render_template(
        'logs.html', 
        appTitle = 'Logs - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl)   

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
        appTitle = 'API Log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'Api Log')   

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
        appTitle = 'Web Log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'Web Log')   

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
        appTitle = 'Backup Log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'Backup Log')   

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
        appTitle = 'Backup Details Log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'Backup Details Log')   

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
        appTitle = 'Transcoder Log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'Transcoder Log')   

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
        appTitle = 'Update Log - ' + configObject.AppTitle, 
        apiRootUrl = configObject.ApiRootUrl,
        logLines = logLines,
        logTitle = 'Update Log')   

@app.route('/transcoder/edit', methods=['GET', 'POST'])
def EditTranscoderSettings():
    try:
        transcoderInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetTranscoderInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        transcoderInfo = []

    defaultMusicFolder = transcoderInfo["DefaultCollectionFolder"] + '/'
    defaultMusicFolderFunctional = transcoderInfo["DefaultCollectionFolderFunctional"]

    form = EditTranscoderForm()

    try:
        transcoderSettings = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetTranscoderSettings').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        transcoderSettings = []

    if request.method == 'GET':
        form.sourceFolder.data = transcoderSettings['sourcefolder'].replace(defaultMusicFolder, '')
        form.oggFolder.data = transcoderSettings['oggfolder'].replace(defaultMusicFolder, '')
        form.oggQuality.data = transcoderSettings['oggquality']
        form.mp3Folder.data = transcoderSettings['mp3folder'].replace(defaultMusicFolder, '')
        form.mp3Bitrate.data = transcoderSettings['mp3bitrate']

    if form.cancel.data: 
        return redirect('/transcoder')

    if request.method == 'POST' and form.validate(): 
        try:
            resetToDefaults = request.form['resetToDefaults']
        except Exception as e:
            resetToDefaults = False

        newSourceFolder = defaultMusicFolder + request.form['sourceFolder'].strip()
        if not newSourceFolder.replace(defaultMusicFolder, ''):
            newSourceFolder = ''
        if resetToDefaults:
            newSourceFolder = ''            
        if newSourceFolder != transcoderSettings['sourcefolder'].strip():
            try:
                requests.post(
                    configObject.ApiRootUrl + '/api/SetTranscoderSourceFolder', 
                    json = {"Value": newSourceFolder})
                flash('Saved \'' + newSourceFolder + '\' to Source Folder')
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

        newOggFolder = defaultMusicFolder + request.form['oggFolder'].strip()
        if not newOggFolder.replace(defaultMusicFolder, ''):
            newOggFolder = ''
        if resetToDefaults:
            newOggFolder = ''                        
        if newOggFolder != transcoderSettings['oggfolder'].strip():
            try:
                requests.post(
                    configObject.ApiRootUrl + '/api/SetTranscoderOggFolder', 
                    json = {"Value": newOggFolder})
                flash('Saved \'' + newOggFolder + '\' to Ogg Folder')
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

        newOggQuality = int(request.form['oggQuality'])
        if resetToDefaults:
            newOggQuality = 0        
        if newOggQuality != int(transcoderSettings['oggquality']):
            try:
                requests.post(
                    configObject.ApiRootUrl + '/api/SetTranscoderOggQuality', 
                    json = {"Value": newOggQuality})
                flash('Saved \'' + str(newOggQuality) + '\' to Ogg Quality')
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

        newMp3Folder = defaultMusicFolder + request.form['mp3Folder'].strip()
        if not newMp3Folder.replace(defaultMusicFolder, ''):
            newMp3Folder = ''  
        if resetToDefaults:
            newMp3Folder = ''                        
        if newMp3Folder != transcoderSettings['mp3folder'].strip():
            try:
                requests.post(
                    configObject.ApiRootUrl + '/api/SetTranscoderMp3Folder', 
                    json = {"Value": newMp3Folder})
                flash('Saved \'' + newMp3Folder + '\' to Mp3 Folder')
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

        newMp3Bitrate = int(request.form['mp3Bitrate'])
        if resetToDefaults:
            newMp3Bitrate = 0
        if newMp3Bitrate != int(transcoderSettings['mp3bitrate']):
            try:
                requests.post(
                    configObject.ApiRootUrl + '/api/SetTranscoderMp3Bitrate', 
                    json = {"Value": newMp3Bitrate})
                flash('Saved \'' + str(newMp3Bitrate) + '\' to Mp3 Bitrate')
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

        return redirect('/transcoder')

    return render_template('transcoder-edit.html', 
        appTitle = 'Transcoder Settings - ' + configObject.AppTitle, 
        form = form,
        musicFolder = defaultMusicFolderFunctional)

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
        app.run(port=1080, debug=True) # auto-reload on file change, only localhost
    else:
        logger.info('Web started - production')
        app.run(host='0.0.0.0', port=80, debug=True) # public server, reachable from remote, auto-reload on file change
    logger.info('Web stopped')

