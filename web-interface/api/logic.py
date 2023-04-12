import subprocess
import requests
import json
import os
from globals import configObject
from datetime import datetime
from datetime import timedelta
import math
from math import ceil
import asyncio
import urllib.request

def ExecuteBashCommand(bashCommand):
    process = subprocess.run(bashCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return process.stdout.decode("utf-8").strip('\n')

def TailFromFile(file, n):
    if n != 0:
        process = subprocess.Popen(['tail', '-n', f'{n}', file], stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(['cat', file], stdout=subprocess.PIPE)
    lines = process.stdout.readlines()
    return lines

def RevisionFileName():
    revisionFile = '/etc/rpms/revision.json'
    if not os.path.isfile(revisionFile):
        revisionFile = os.path.dirname(__file__) + '/../../revision.json'
    return revisionFile


def ConvertToFunctionalFolder(folderName):
    return folderName.replace(GetUserBaseFolder(), 'server:/')

def GetElapsedTimeHumanReadable(fromDate):
    timeElapsed = datetime.today() - fromDate

    elapsedSeconds = int(timeElapsed.total_seconds())
    elapsedMinutes = int(divmod(timeElapsed.total_seconds(), 60)[0])
    elapsedMinutesSeconds = int(divmod(timeElapsed.total_seconds(), 60)[1])    
    elapsedHours = int(divmod(timeElapsed.total_seconds(), 60 * 60)[0])
    elapsedHoursMinutes = int(divmod(timeElapsed.total_seconds(), 60 * 60)[1] / 60)
    elapsedDays = int(divmod(timeElapsed.total_seconds(), 60 * 60 * 24)[0])
    elapsedDaysHours = int(divmod(timeElapsed.total_seconds(), 60 * 60 * 24)[1] / (60 * 60))
    elapsedWeeks = int(divmod(timeElapsed.total_seconds(), 60 * 60 * 24 * 7)[0])
    elapsedWeeksDays = int(divmod(timeElapsed.total_seconds(), 60 * 60 * 24 * 7)[1] / (60 * 60 * 24))    
    elapsedMonths = int(divmod(timeElapsed.total_seconds(), 60 * 60 * 24 * 30)[0])
    elapsedMonthsDays = int(divmod(timeElapsed.total_seconds(), 60 * 60 * 24 * 30)[1] / (60 * 60 * 24))
    elapsedYears = int(divmod(timeElapsed.total_seconds(), 60 * 60 * 24 * 365)[0])
    elapsedYearsMonths = int(divmod(timeElapsed.total_seconds(), 60 * 60 * 24 * 365)[1] / (60 * 60 * 24 * 30))

    elapsedTimeAsString = ''
    if elapsedYears > 0:
        elapsedTimeAsString = str(elapsedYears) + ' year'
        if elapsedYears > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedYearsMonths > 0:
            elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedYearsMonths) + ' month'
            if elapsedYearsMonths > 1:
                elapsedTimeAsString = elapsedTimeAsString + 's'            
    elif elapsedMonths > 0:
        elapsedTimeAsString = str(elapsedMonths) + ' month'
        if elapsedMonths > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedMonthsDays > 0:
            elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedMonthsDays) + ' day'
            if elapsedMonthsDays > 1:
                elapsedTimeAsString = elapsedTimeAsString + 's'
    elif elapsedWeeks > 0:
        elapsedTimeAsString = str(elapsedWeeks) + ' week'
        if elapsedWeeks > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedWeeksDays > 0:
            elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedWeeksDays) + ' day'
            if elapsedWeeksDays > 1:
                elapsedTimeAsString = elapsedTimeAsString + 's'
    elif elapsedDays > 0:
        elapsedTimeAsString = str(elapsedDays) + ' day'
        if elapsedDays > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedDaysHours > 0:
            elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedDaysHours) + ' hour'
            if elapsedDaysHours > 1:
                elapsedTimeAsString = elapsedTimeAsString + 's'
    elif elapsedHours > 0:
        elapsedTimeAsString = str(elapsedHours) + ' hour'             
        if elapsedHours > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedHoursMinutes > 0:
            elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedHoursMinutes) + ' minute'
            if elapsedHoursMinutes > 1:
                elapsedTimeAsString = elapsedTimeAsString + 's'
    elif elapsedMinutes > 0:
        elapsedTimeAsString = str(elapsedMinutes) + ' minute'
        if elapsedMinutes > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedMinutesSeconds > 0:
            elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedMinutesSeconds) + ' second'
            if elapsedMinutesSeconds > 1:
                elapsedTimeAsString = elapsedTimeAsString + 's'
    elif elapsedSeconds > 0:
        elapsedTimeAsString = str(elapsedSeconds) + ' second'
        if elapsedSeconds > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'

    if elapsedTimeAsString != '':
        elapsedTimeAsString = elapsedTimeAsString + ' ago'
    else:
        elapsedTimeAsString = 'now'        

    return elapsedTimeAsString

def GetMachineInfo():
    hostName = ExecuteBashCommand("hostname")
    ipAddress = ExecuteBashCommand("hostname -I").split()[0]

    urlPrefix = 'http://'
    hostUrl = urlPrefix + hostName
    if ExecuteBashCommand("nslookup " + hostName + " | grep \"server can't find\"").strip() != "":
        hostUrl = urlPrefix + ipAddress

    osDescription = ExecuteBashCommand("lsb_release -d | cut -f2")
    osBitType = ExecuteBashCommand("uname -m")
    osCodeName = ExecuteBashCommand("lsb_release -c").split()[1]
    kernelVersion = ExecuteBashCommand("uname -r")

    rpModelMemoryInGB = str(ceil(float(ExecuteBashCommand("free --mega | grep Mem: | awk '{print $2}'")) / 1024)) + ' GB'

    rpModel = '?'
    if os.path.isfile('/proc/device-tree/model'):    
        rpModel = ExecuteBashCommand("cat /proc/device-tree/model").replace('\u0000', '')
 
    # upTime => uptime -p | cut -c 4-
    process = subprocess.run(["uptime -p"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["cut -c 4-"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    upTime = process.stdout.decode("utf-8").strip('\n')

    return {"HostName": hostName,
            "HostUrl": hostUrl,
            "IpAddress": ipAddress,
            "OsCodeName": osCodeName,
            "OsDescription": osDescription,
            "OsBitType": osBitType,
            "KernelVersion": kernelVersion,
            "RpModel": rpModel,
            "RpModelMemoryInGB": rpModelMemoryInGB,
            "UpTime": upTime}

disks = []

def AppendDiskInfo(diskMountPoint):
    # diskDeviceName => mount | grep -w / | awk '{print $1}'
    process = subprocess.run(["mount"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["grep -w " + diskMountPoint], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $1}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    diskDeviceName = process.stdout.decode("utf-8").strip('\n')

    diskName = diskMountPoint.replace('/media/', '')

    diskSize = ''
    diskUsed = ''
    diskUsedPercentage = 0
    if diskDeviceName:

        # diskSize => df -h | grep -w / | awk '{print $2}'
        process = subprocess.run(["df -h"], stdout=subprocess.PIPE, shell=True)
        process = subprocess.run(["grep -w " + diskMountPoint], input=process.stdout, stdout=subprocess.PIPE, shell=True)
        process = subprocess.run(["awk '{print $2}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
        diskSize = process.stdout.decode("utf-8").strip('\n')

        # diskUsed => df -h | grep -w / | awk '{print $3}'
        process = subprocess.run(["df -h"], stdout=subprocess.PIPE, shell=True)
        process = subprocess.run(["grep -w " + diskMountPoint], input=process.stdout, stdout=subprocess.PIPE, shell=True)
        process = subprocess.run(["awk '{print $3}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
        diskUsed = process.stdout.decode("utf-8").strip('\n')

        # diskUsedPercentage => df -h | grep -w / | awk '{print $5}'
        process = subprocess.run(["df -h"], stdout=subprocess.PIPE, shell=True)
        process = subprocess.run(["grep -w " + diskMountPoint], input=process.stdout, stdout=subprocess.PIPE, shell=True)
        process = subprocess.run(["awk '{print $5}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
        diskUsedPercentage = int(process.stdout.decode("utf-8").strip('\n').replace('%', ''))

        onlineStatus = True
    else:
        onlineStatus = False

    disks.append({
                    "DiskName": diskName,
                    "MountPoint": diskMountPoint,
                    "DeviceName": diskDeviceName,
                    "IsOnline": onlineStatus,
                    "Size": diskSize,
                    "Used": diskUsed,
                    'UsedPercentage': diskUsedPercentage
                 })
    pass

def GetDiskList():
    disks.clear()
    AppendDiskInfo('/')
    AppendDiskInfo('/media/usbdata')
    AppendDiskInfo('/media/usbbackup')
    return disks

def GetServiceStatusList():
    class ServiceInfo:
        def __init__(self, portNumber, serviceName, isActive=False):
            self.PortNumber = portNumber
            self.ServiceName = serviceName
            self.IsActive = isActive

    serviceList = []
    serviceList.append(ServiceInfo(22, 'ssh'))
    serviceList.append(ServiceInfo(80, 'rpms/web'))
    serviceList.append(ServiceInfo(139, 'samba/netbios'))
    serviceList.append(ServiceInfo(5000, 'rpms/api'))
    serviceList.append(ServiceInfo(8384, 'syncthing/web'))
    serviceList.append(ServiceInfo(9002, 'lms/web'))
    serviceList.append(ServiceInfo(9091, 'transmission/web'))

    portList = ''
    for serviceInfoObject in serviceList:
        if portList != '':
            portList = portList + ','
        portList = portList + str(serviceInfoObject.PortNumber)

    nmapResult = ExecuteBashCommand('nmap localhost --open -p ' + portList)

    for serviceInfoObject in serviceList:
        if (str(serviceInfoObject.PortNumber) + '/tcp') in nmapResult:
            serviceInfoObject.IsActive = True

    serviceListResult = []
    for serviceInfoObject in serviceList:
        serviceListResult.append({"PortNumber": serviceInfoObject.PortNumber,
                                  "ServiceName": serviceInfoObject.ServiceName,
                                  "IsActive": serviceInfoObject.IsActive
                                 })

    return serviceListResult

def GetCpuResourceInfo():
    # cpuLoad1 =>  uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | cut -c 1-4
    process = subprocess.run(["uptime"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk -F'load average:' '{print $2}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    process = subprocess.run(["awk '{print $1}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["cut -c 1-4"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    cpuLoad1 = float(process.stdout.decode("utf-8").strip('\n').replace(',', '.'))

    # cpuLoad5 =>  uptime | awk -F'load average:' '{print $2}' | awk '{print $2}' | cut -c 1-4
    process = subprocess.run(["uptime"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk -F'load average:' '{print $2}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)        
    process = subprocess.run(["awk '{print $2}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["cut -c 1-4"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    cpuLoad5 = float(process.stdout.decode("utf-8").strip('\n').replace(',', '.'))

    # cpuLoad15 =>  uptime | awk -F'load average:' '{print $2}' | awk '{print $3}' | cut -c 1-4
    process = subprocess.run(["uptime"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk -F'load average:' '{print $2}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)            
    process = subprocess.run(["awk '{print $3}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    cpuLoad15 = float(process.stdout.decode("utf-8").strip('\n').replace(',', '.'))

    # cputemp
    cpuTemp = 0
    if len(ExecuteBashCommand("whereis vcgencmd").split()) > 1:
        process = subprocess.run(["vcgencmd measure_temp"], stdout=subprocess.PIPE, shell=True)
        process = subprocess.run(["cut -c 6-"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
        cpuTemp = int(float(process.stdout.decode("utf-8").strip('\n').strip("\'C")))

    return {"CpuLoad1": cpuLoad1,
            "CpuLoad5": cpuLoad5,
            "CpuLoad15": cpuLoad15,           
            "CpuTemp": cpuTemp
            }

def GetMemoryResourceInfo():
    # memTotal => free | grep 'Mem:' | awk '{print $2}'
    process = subprocess.run(["free"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["grep 'Mem:'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $2}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    memTotal = int(process.stdout.decode("utf-8").strip('\n'))

    # memUsed => free | grep 'Mem:' | awk '{print $3}'
    process = subprocess.run(["free"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["grep 'Mem:'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $3}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    memUsed = int(process.stdout.decode("utf-8").strip('\n'))

    memUsedPercentage = math.floor(memUsed/memTotal * 100)

    # swapTotal => free | grep 'Swap:' | awk '{print $2}'
    process = subprocess.run(["free"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["grep 'Swap:'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $2}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    swapTotal = int(process.stdout.decode("utf-8").strip('\n'))

    # swapUsed => free | grep 'Swap:' | awk '{print $3}'
    process = subprocess.run(["free"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["grep 'Swap:'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $3}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    swapUsed = int(process.stdout.decode("utf-8").strip('\n'))

    swapUsedPercentage = math.floor(swapUsed/swapTotal * 100)

    return {'MemTotal': memTotal,
            "MemUsed": memUsed,
            "MemUsedPercentage": memUsedPercentage,
            "SwapTotal": swapTotal,
            "SwapUsed": swapUsed,
            "SwapUsedPercentage": swapUsedPercentage
            }

def GetVersionInfo():
    revisionFile = RevisionFileName()

    currentVersion = '0.0'
    lastUpdateTimeStampAsString = ''
    if os.path.isfile(revisionFile):
        with open(revisionFile) as file:
            dataAsDict = json.load(file)
        dataAsJson = json.loads(json.dumps(dataAsDict))
        try:
            if dataAsJson["CurrentVersion"]:
                currentVersion = dataAsJson["CurrentVersion"]
        except:
            pass

        try:
            lastUpdateTimeStamp = os.path.getmtime(revisionFile)
        except:
            pass
        lastUpdateTimeStampAsString = datetime.fromtimestamp(lastUpdateTimeStamp).strftime('%Y-%m-%d %H:%M:%S')
        lastUpdateTimeStampAsString = lastUpdateTimeStampAsString + ' - ' + GetElapsedTimeHumanReadable(datetime.strptime(lastUpdateTimeStampAsString, '%Y-%m-%d %H:%M:%S'))

    updateBranchName = 'master'
    updateBranchFile = '/media/usbdata/rpms/config/update-branch.txt'
    if os.path.isfile(updateBranchFile):
        file = open(updateBranchFile, 'r')
        updateBranchName = file.read().strip('\n')

    availableVersion = '0.0'
    url = "https://raw.githubusercontent.com/markbaaijens/rpmusicserver/" + updateBranchName +  "/revision.json"
    print(url)
    with urllib.request.urlopen(url) as url:
        revisionData = json.loads(url.read().decode())
        availableVersion = revisionData['CurrentVersion']

    canUpdate = False
    availableVersionSplit = availableVersion.split('.')
    currentVersionSplit = currentVersion.split('.')    
    if int(availableVersionSplit[0]) > int(currentVersionSplit[0]):
        canUpdate = True
    else:
        if int(availableVersionSplit[0]) == int(currentVersionSplit[0]):
            if int(availableVersionSplit[1]) > int(currentVersionSplit[1]):
                canUpdate = True

    # Always update if override-branch has been given, even if versions don't match   
    isVersionOverridden = False
    if updateBranchName != 'master':
        canUpdate = True
        isVersionOverridden = True

    return {"VersionFile": revisionFile,
            "CurrentVersion": currentVersion, 
            "LastUpdateTimeStamp": lastUpdateTimeStampAsString,
            "AvailableVersion": availableVersion,
            "CanUpdate": canUpdate,
            "UpdateBranchName": updateBranchName,
            "IsVersionOverridden": isVersionOverridden}

def GetVersionList():
    revisionFile = RevisionFileName()

    dataAsJson = {}
    apiInfoFile = revisionFile
    if os.path.isfile(apiInfoFile):
        with open(apiInfoFile) as file:
            dataAsDict = json.load(file)
        dataAsJson = json.loads(json.dumps(dataAsDict))
    return dataAsJson

def GetBackupInfo():
    isBackupNotInProgress = True

    if ExecuteBashCommand("ps -ef | grep backup-server | grep -v grep").strip() != '':
        isBackupNotInProgress = False

    isBackupDiskPresent = ExecuteBashCommand("ls /dev/disk/by-label | grep usbbackup") == "usbbackup"
    canBackup = isBackupDiskPresent and isBackupNotInProgress

    lastBackup = ExecuteBashCommand("cat /media/usbdata/rpms/logs/backup.log | grep 'executing backup' | tail -n 1 | cut -c1-19")
    lastBackup = lastBackup + ' - ' + GetElapsedTimeHumanReadable(datetime.strptime(lastBackup, '%Y-%m-%d %H:%M:%S'))    

    return {"IsBackupNotInProgress": isBackupNotInProgress,
            "IsBackupDiskPresent": isBackupDiskPresent,
            "CanBackup": canBackup,
            "LastBackup": lastBackup}

def GetTranscoderInfo():
    defaultCollectionFolder = GetDefaultMusicCollectionFolder()
    defaultCollectionFolderFunctional = ConvertToFunctionalFolder(defaultCollectionFolder)

    transcoderSettings = GetTranscoderSettings()
    settingSourceFolder = transcoderSettings['sourcefolder']
    settingSourceFolderShort = settingSourceFolder.replace(defaultCollectionFolder + '/', '')
    settingOggFolder = transcoderSettings['oggfolder']
    settingOggFolderShort = settingOggFolder.replace(defaultCollectionFolder + '/', '')    
    settingOggQuality = transcoderSettings['oggquality']
    settingMp3Folder = transcoderSettings['mp3folder']
    settingMp3FolderShort = settingMp3Folder.replace(defaultCollectionFolder + '/', '')        
    settingMp3Bitrate = transcoderSettings['mp3bitrate']

    isActivated = (transcoderSettings['sourcefolder'] != '') and ((transcoderSettings['oggfolder'] != '') or (transcoderSettings['mp3folder'] != ''))

    lastTranscode = ExecuteBashCommand("cat /media/usbdata/rpms/logs/transcoder.log | grep 'End session' | tail -n 1 | cut -c1-19")
    lastTranscode = lastTranscode + ' - ' + GetElapsedTimeHumanReadable(datetime.strptime(lastTranscode, '%Y-%m-%d %H:%M:%S'))

    return {"IsActivated": isActivated,
            "LastTranscode": lastTranscode,
            "DefaultCollectionFolder": defaultCollectionFolder,
            "DefaultCollectionFolderFunctional": defaultCollectionFolderFunctional,
            "SettingSourceFolderShort": settingSourceFolderShort,
            "SettingOggFolderShort": settingOggFolderShort,
            "SettingOggQuality": settingOggQuality,
            "SettingMp3FolderShort": settingMp3FolderShort,
            "SettingMp3Bitrate": settingMp3Bitrate}            

def GetApiList():
    dataAsJson = {}
    apiInfoFile = os.path.dirname(__file__) + '/api-info.json'
    if os.path.isfile(apiInfoFile):
        with open(apiInfoFile) as file:
            dataAsDict = json.load(file)
        dataAsJson = json.loads(json.dumps(dataAsDict))
    return dataAsJson

def GetTranscoderSettings():
    dataAsJson = {}
    transcoderSettingsFile = '/media/usbdata/rpms/config/transcoder-settings.json'
    if os.path.isfile(transcoderSettingsFile):
        with open(transcoderSettingsFile) as file:
            dataAsDict = json.load(file)
        dataAsJson = json.loads(json.dumps(dataAsDict))
    return dataAsJson

def GetUserBaseFolder():
    return '/media/usbdata/user'

def GetPublicFolder():
    return 'Publiek'

def GetMusicFolder():
    return 'Muziek'    

def GetDefaultMusicCollectionFolder():
    return GetUserBaseFolder() + '/' + GetPublicFolder() + '/' + GetMusicFolder()

def GetMusicCollectionInfo():   
    transcoderSettings = GetTranscoderSettings()
    actualCollectionFolder = transcoderSettings["sourcefolder"]
    actualCollectionFolderFunctional = ConvertToFunctionalFolder(actualCollectionFolder)
    exportFile = "tree.txt"

    if actualCollectionFolder == '':
        actualCollectionFolder = defaultCollectionFolder

    lastExportTimeStampAsString = ''
    fullExportFile = actualCollectionFolder + "/" + exportFile
    if os.path.isfile(fullExportFile):
        try:
            lastExportTimeStampAsString = os.path.getmtime(fullExportFile)
        except:
            pass
        lastExportTimeStampAsString = datetime.fromtimestamp(lastExportTimeStampAsString).strftime('%Y-%m-%d %H:%M:%S')
        lastExportTimeStampAsString = lastExportTimeStampAsString + ' - ' + GetElapsedTimeHumanReadable(datetime.strptime(lastExportTimeStampAsString, '%Y-%m-%d %H:%M:%S'))    

    return {"CollectionFolder": actualCollectionFolder,
            "CollectionFolderFunctional": actualCollectionFolderFunctional,
            "ExportFile": exportFile,
            "LastExport": lastExportTimeStampAsString}

def GetLog(logFile, nrOfLines):
    logLines = []
    if os.path.isfile(logFile):
        logLinesFromFile = TailFromFile(logFile, nrOfLines)
        for logLine in logLinesFromFile:
            logLines.append(logLine.decode("utf-8").strip('\n'))
    return logLines

def GetDockerContainerList():
    dockerContainerList = []

    process = subprocess.run(["docker ps --format '{{.Names}}'"], stdout=subprocess.PIPE, shell=True)
    activeContainers = process.stdout.decode("utf-8").strip('\n')
    activeContainers = activeContainers.splitlines()

    isActive = 'lms' in activeContainers
    dockerContainerList.append({
                    "ContainerName": 'lms',
                    "IsActive": isActive
                 })    
    isActive = 'transmission' in activeContainers                 
    dockerContainerList.append({
                    "ContainerName": 'transmission',
                    "IsActive": isActive
                 })    
    isActive = 'samba' in activeContainers                 
    dockerContainerList.append({
                    "ContainerName": 'samba',
                    "IsActive": isActive
                 })    
    isActive = 'syncthing' in activeContainers                 
    dockerContainerList.append({
                    "ContainerName": 'syncthing',
                    "IsActive": isActive
                 })                    

    return dockerContainerList

def SetTranscoderSetting(settingName, newValue):
    transcoderSettingsFileName = '/media/usbdata/rpms/config/transcoder-settings.json'
    if not os.path.isfile(transcoderSettingsFileName):
        return { "Message": "File " + transcoderSettingsFileName + " does not exist"}

    with open(transcoderSettingsFileName, 'r') as jsonFile:
        data = json.load(jsonFile)
    data[settingName] = newValue
    with open(transcoderSettingsFileName, 'w') as jsonFile:
        json.dump(data, jsonFile)

    return { "Message": "Transcoder-setting ["+ settingName + "] is modified to [" + str(newValue) + "]"}

async def DoRebootServer():
    await asyncio.create_subprocess_shell("reboot-server")
    pass

async def DoBackupServer():
    await asyncio.create_subprocess_shell("backup-server")
    pass

async def DoHaltServer():
    await asyncio.create_subprocess_shell("halt-server")
    pass

async def DoKillDocker():
    await asyncio.create_subprocess_shell("kill-docker")
    pass

async def DoStartDocker():
    await asyncio.create_subprocess_shell("start-docker")
    pass

async def DoUpdateDocker():
    await asyncio.create_subprocess_shell("update-docker")
    pass

async def DoUpdateRpms():
    await asyncio.create_subprocess_shell("update-rpms")
    pass

async def DoExportCollection():
    await asyncio.create_subprocess_shell("export-collection")
    pass

async def DoTranscode():
    await asyncio.create_subprocess_shell("transcode")
    pass

def GetLmsServerInfo():
    # LMS API-reference: http://msi:9000/html/docs/cli-api.html 
    url = "http://rpms:9002/jsonrpc.js"    
    payload = "{\"method\": \"slim.request\", \"params\": [\"-\", [\"serverstatus\",\"0\",\"100\"]]}\n"
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    return(response.text)
