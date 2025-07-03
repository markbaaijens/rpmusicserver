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

const_LmsApiUrl = 'http://localhost:9000/jsonrpc.js'
const_PublicFolder = 'public'
const_MusicFolder = 'music' 
const_DownloadsFolder = 'downloads' 

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

def GetHostName():
    return ExecuteBashCommand("hostname")

def ConvertToFunctionalFolder(folderName):
    hostName = GetHostName()
    functionalFolder = folderName.replace(GetUserBaseFolder(), 'smb://' + hostName)

    translationList = GetTranslations();
    publicShareName = translationList['PublicShareName'].strip()
    musicShareName = translationList['MusicShareName'].strip()
    downloadsShareName = translationList['DownloadsShareName'].strip()    

    if const_MusicFolder in functionalFolder:
        functionalFolder = functionalFolder.replace(const_MusicFolder, musicShareName)
    else: 
        if const_PublicFolder in functionalFolder:
            functionalFolder = functionalFolder.replace(const_PublicFolder, publicShareName)
        else: 
            if const_DownloadsFolder in functionalFolder:
                functionalFolder = functionalFolder.replace(const_DownloadsFolder, downloadsShareName)

    return functionalFolder

def GetElapsedTimeHumanReadable(fromDate):
    if fromDate == '':
        return ''

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
        if elapsedYears == 1:            
            if elapsedYearsMonths > 0:
                elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedYearsMonths) + ' month'
                if elapsedYearsMonths > 1:
                    elapsedTimeAsString = elapsedTimeAsString + 's'            
    elif elapsedMonths > 0:
        elapsedTimeAsString = str(elapsedMonths) + ' month'
        if elapsedMonths > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedMonths == 1:            
            if elapsedMonthsDays > 0:
                elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedMonthsDays) + ' day'
                if elapsedMonthsDays > 1:
                    elapsedTimeAsString = elapsedTimeAsString + 's'
    elif elapsedWeeks > 0:
        elapsedTimeAsString = str(elapsedWeeks) + ' week'
        if elapsedWeeks > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedWeeks == 1:            
            if elapsedWeeksDays > 0:
                elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedWeeksDays) + ' day'
                if elapsedWeeksDays > 1:
                    elapsedTimeAsString = elapsedTimeAsString + 's'
    elif elapsedDays > 0:
        elapsedTimeAsString = str(elapsedDays) + ' day'
        if elapsedDays > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedDays == 1:            
            if elapsedDaysHours > 0:
                elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedDaysHours) + ' hour'
                if elapsedDaysHours > 1:
                    elapsedTimeAsString = elapsedTimeAsString + 's'
    elif elapsedHours > 0:
        elapsedTimeAsString = str(elapsedHours) + ' hour'             
        if elapsedHours > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedHours == 1:            
            if elapsedHoursMinutes > 0:
                elapsedTimeAsString = elapsedTimeAsString + ', ' + str(elapsedHoursMinutes) + ' minute'
                if elapsedHoursMinutes > 1:
                    elapsedTimeAsString = elapsedTimeAsString + 's'
    elif elapsedMinutes > 0:
        elapsedTimeAsString = str(elapsedMinutes) + ' minute'
        if elapsedMinutes > 1:
            elapsedTimeAsString = elapsedTimeAsString + 's'
        if elapsedMinutes == 1:            
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
    hostName = GetHostName()
    ipAddress = ExecuteBashCommand("hostname -I").split()[0]

    urlPrefix = 'http://'
    hostUrl = urlPrefix + hostName
    if ExecuteBashCommand('nslookup ' + hostName + ' | grep "NXDOMAIN"').strip() != "":
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

DISK_SIZE = 2
DISK_USED = 3
DISK_USED_PERCENTAGE = 5

def AppendDiskInfo(diskMountPoint):
    def DiskPropertyCommand(diskMountPoint, printNumber, allDisks):
        # B/c using the -a parameter (for all devices) hangs df if not all disks are mounted, we must use
        # this parameter with caution, so on demand.
        allDiskParameter = ''    
        if allDisks:
            allDiskParameter = '-a'
        command = "df -h " + allDiskParameter + " | grep -w " + diskMountPoint + " | awk '{print $" + str(printNumber) + "}'"
        return command

    if diskMountPoint == '/':
        diskName = 'boot'
    else: 
        diskName = diskMountPoint.replace('/media/', '')

    isDiskPresent = ExecuteBashCommand("ls /dev/disk/by-label | grep " + diskName) != ''

    diskSize = ''
    diskUsed = ''
    diskUsedPercentage = 0

    if isDiskPresent:
        diskSize = ExecuteBashCommand(DiskPropertyCommand(diskMountPoint, DISK_SIZE, False))
        if diskSize == '':
            diskSize = ExecuteBashCommand(DiskPropertyCommand(diskMountPoint, DISK_SIZE, True))

        diskUsed = ExecuteBashCommand(DiskPropertyCommand(diskMountPoint, DISK_USED, False))
        if diskUsed == '':
            diskUsed = ExecuteBashCommand(DiskPropertyCommand(diskMountPoint, DISK_USED, True))

        diskUsedPercentage = ExecuteBashCommand(DiskPropertyCommand(diskMountPoint, DISK_USED_PERCENTAGE, False))
        if diskUsedPercentage == '':
            diskUsedPercentage = ExecuteBashCommand(DiskPropertyCommand(diskMountPoint, DISK_USED_PERCENTAGE, True))
        if diskUsedPercentage != '':
            try:
                diskUsedPercentage = int(diskUsedPercentage.replace('%', ''))
            except:
                diskUsedPercentage = 0

        onlineStatus = True
    else:
        onlineStatus = False

    disks.append({
                    "DiskName": diskName,
                    "MountPoint": diskMountPoint,
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

def GetPortStatusList():
    class PortInfo:
        def __init__(self, portNumber, serviceName, serviceType='', isActive=False):
            self.PortNumber = portNumber
            self.ServiceName = serviceName
            self.ServiceType = serviceType
            self.IsActive = isActive

    portStatusList = []
    portStatusList.append(PortInfo(22, 'ssh'))
    portStatusList.append(PortInfo(80, 'rpms', 'web'))
    portStatusList.append(PortInfo(139, 'samba', 'netbios'))
    portStatusList.append(PortInfo(445, 'samba', 'microsoft-ds'))
    portStatusList.append(PortInfo(5000, 'rpms', 'api'))
    portStatusList.append(PortInfo(8384, 'syncthing', 'web'))
    portStatusList.append(PortInfo(9000, 'lms', 'web'))
    portStatusList.append(PortInfo(9090, 'lms', 'telnet'))    
    portStatusList.append(PortInfo(9091, 'transmission', 'web'))

    portList = ''
    for portStatus in portStatusList:
        if portList != '':
            portList = portList + ','
        portList = portList + str(portStatus.PortNumber)

    nmapResult = ExecuteBashCommand('nmap localhost --open -p ' + portList)

    for portStatus in portStatusList:
        if (str(portStatus.PortNumber) + '/tcp') in nmapResult:
            portStatus.IsActive = True

    portStatusListResult = []
    for portStatus in portStatusList:
        portStatusListResult.append({"PortNumber": portStatus.PortNumber,
                                     "ServiceName": portStatus.ServiceName,
                                     "ServiceType": portStatus.ServiceType,
                                     "IsActive": portStatus.IsActive
                                    })

    return portStatusListResult

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
    isBackupDiskPresent = ExecuteBashCommand("ls /dev/disk/by-label | grep usbbackup") == "usbbackup"

    isBackupRunning = False
    if ExecuteBashCommand("ps -ef | grep backup-server | grep -v grep").strip() != '':
        isBackupRunning = True  # Running

    statusMessage = 'No disk'
    if isBackupDiskPresent:
        statusMessage = 'Disk present - Idle'
        if isBackupRunning:
            statusMessage = 'Running'

    canBackup = isBackupDiskPresent and (not isBackupRunning)

    lastBackup = ExecuteBashCommand("cat /media/usbdata/rpms/logs/backup.log | grep 'executing backup' | tail -n 1 | cut -c1-19")

    try:
        lastBackup = lastBackup + ' - ' + GetElapsedTimeHumanReadable(datetime.strptime(lastBackup, '%Y-%m-%d %H:%M:%S'))  
    except:      
        lastBackup = "No backup made, yet"
    
    return {"StatusMessage": statusMessage,
            "IsBackupDiskPresent": isBackupDiskPresent,
            "IsBackupRunning": isBackupRunning,
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
    if lastTranscode != '':
        lastTranscode = lastTranscode + ' - ' + GetElapsedTimeHumanReadable(datetime.strptime(lastTranscode, '%Y-%m-%d %H:%M:%S'))

    return {"IsActivated": isActivated,
            "LastTranscode": lastTranscode,
            "DefaultCollectionFolder": defaultCollectionFolder,
            "DefaultCollectionFolderFunctional": defaultCollectionFolderFunctional,
            "SettingSourceFolder": settingSourceFolder,            
            "SettingSourceFolderShort": settingSourceFolderShort,
            "SettingOggFolder": settingOggFolder,            
            "SettingOggFolderShort": settingOggFolderShort,
            "SettingOggQuality": settingOggQuality,
            "SettingMp3Folder": settingMp3Folder,            
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

def GetTranslations():
    dataAsJson = {}
    translationsFile = '/media/usbdata/rpms/config/translations.json'
    if os.path.isfile(translationsFile):
        with open(translationsFile) as file:
            dataAsDict = json.load(file)
        dataAsJson = json.loads(json.dumps(dataAsDict))
    return dataAsJson

def GetUserBaseFolder():
    return '/media/usbdata/user'

def GetDefaultMusicCollectionFolder():
    return GetUserBaseFolder() + '/' + const_MusicFolder

def GetMusicCollectionInfo():   
    transcoderInfo = GetTranscoderInfo()
    defaultCollectionFolder = transcoderInfo["DefaultCollectionFolder"]    
    settingCollectionFolder = transcoderInfo["SettingSourceFolder"]

    collectionFolder = defaultCollectionFolder
    if settingCollectionFolder != "":
        collectionFolder = settingCollectionFolder

    collectionFolderFunctional = ConvertToFunctionalFolder(collectionFolder)

    lastExportTimeStampAsString = ''
    exportFile = "collection-artist-album-by-folder.txt"    
    fullExportFile = collectionFolder + "/" + exportFile
    if os.path.isfile(fullExportFile):
        lastExportTimeStampAsString = os.path.getmtime(fullExportFile)

    try:
        lastExportTimeStampAsString = datetime.fromtimestamp(lastExportTimeStampAsString).strftime('%Y-%m-%d %H:%M:%S')
        lastExportTimeStampAsString = lastExportTimeStampAsString + ' - ' + GetElapsedTimeHumanReadable(datetime.strptime(lastExportTimeStampAsString, '%Y-%m-%d %H:%M:%S'))    
    except:
        lastExportTimeStampAsString = "No export made, yet"
            
    return {"CollectionFolder": collectionFolder,
            "CollectionFolderFunctional": collectionFolderFunctional,
            "LastExport": lastExportTimeStampAsString}

def GetFlacHealthInfo():   
    lastCheckTimeStampAsString = ''
    isChecked = False
    fullHealthLog = '/media/usbdata/rpms/logs/flac-health-check.log'
    if os.path.isfile(fullHealthLog):
        lastCheckTimeStampAsString = os.path.getmtime(fullHealthLog)
        isChecked = True

    try:
        lastCheckTimeStampAsString = datetime.fromtimestamp(lastCheckTimeStampAsString).strftime('%Y-%m-%d %H:%M:%S')
        lastCheckTimeStampAsString = lastCheckTimeStampAsString + ' - ' + GetElapsedTimeHumanReadable(datetime.strptime(lastCheckTimeStampAsString, '%Y-%m-%d %H:%M:%S'))    
    except:
        lastCheckTimeStampAsString = "No check made, yet"

    errorCount = ExecuteBashCommand("cat /media/usbdata/rpms/logs/flac-health-check.log | grep -o ERROR -B1 | wc -l")
    warningCount = ExecuteBashCommand("cat /media/usbdata/rpms/logs/flac-health-check.log | grep -o WARNING -B1 | wc -l")
    corruptAlbumCount = ExecuteBashCommand("find /media/usbdata/user/music/flac/ -type f -name 'repair.sh' | wc -l")
            
    return {"IsChecked": isChecked,
            "LastCheck": lastCheckTimeStampAsString,
            "ErrorCount": errorCount,
            "WarningCount": warningCount,
            "CorruptAlbumCount": corruptAlbumCount}

def GetLog(logFile, nrOfLines):
    logLines = []
    if os.path.isfile(logFile):
        logLinesFromFile = TailFromFile(logFile, nrOfLines)
        for logLine in logLinesFromFile:
            logLines.append(logLine.decode("utf-8").strip('\n'))

    if len(logLines) == 0:
        logLines.append('Log is empty.')

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
    isActive = 'syncthing' in activeContainers                 
    dockerContainerList.append({
                    "ContainerName": 'syncthing',
                    "IsActive": isActive
                 })                    

    return dockerContainerList

def SetSetting(keyName, newValue, settingsFile):
    if not os.path.isfile(settingsFile):
        return { "Message": "File " + settingsFile + " does not exist"}

    with open(settingsFile, 'r') as jsonFile:
        data = json.load(jsonFile)
    data[keyName] = newValue
    with open(settingsFile, 'w') as jsonFile:
        json.dump(data, jsonFile)

    return { "Message": "Setting ["+ keyName + "] is modified to [" + str(newValue) + "]"}

def SetTranscoderSetting(keyName, newValue):
    return SetSetting(keyName, newValue, '/media/usbdata/rpms/config/transcoder-settings.json')

def SetTranslation(keyName, newValue):
    return SetSetting(keyName, newValue, '/media/usbdata/rpms/config/translations.json')

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

async def DoTranscode():
    await asyncio.create_subprocess_shell("transcode")
    pass

async def DoGenerateSambaConf():
    await asyncio.create_subprocess_shell("generate-samba-conf")
    pass

async def DoFlacHealthCheck():
    await asyncio.create_subprocess_shell("flac-health-check")
    pass

def ExportCollectionArtistAlbumByFolder(collectionFolder):
    collection = ''

    startLevel = collectionFolder.count(os.sep)
    for (dir, dirs, files) in os.walk(collectionFolder):
        dirs.sort()
        level = dir.count(os.sep) - startLevel
        dirName = dir.split(os.path.sep)[-1]
        if level > 0:
            drFileName = os.path.join(dir, 'dr14.txt')
            drValue = ''
            if os.path.isfile(drFileName):
                try:
                    drValue = os.popen('cat "' + drFileName + '" | grep "Official DR value:" | cut -c24-27 &> /dev/null').read().strip()
                    if drValue != '':
                        drValue = ' | DR' +  drValue
                except:
                    pass

            collection += (' ' * 4 * (level -1)) + dirName + drValue + '\n'

    with open(collectionFolder + '/collection-artist-album-by-folder.txt', 'w') as file:
        file.write(collection)            

    pass

def ExportCollectionArtistAlbumByTag(collectionFolder):
    collection = ''
    artists = GetLmsArtists()
    for artist in artists:
        albums = GetLmsAlbumsByArtist(artist['id'])
        collection += artist['artist'] + ' (' + str(len(albums)) + ')\n'            
        for album in albums:
            collection += (' ' * 4) + album['album'] + '\n'                

    with open(collectionFolder + '/collection-artist-album-by-tag.txt', 'w') as file:
        file.write(collection)            

    pass
        
def ExportCollectionGenreArtistAlbumByTag(collectionFolder):
    collection = ''
    genres = GetLmsGenres()
    for genre in genres:
        artists = GetLmsArtistsByGenre(genre['id'])
        collection += genre['genre'] + ' (' + str(len(artists)) + ')\n'        
        for artist in artists:
            albums = GetLmsAlbumsByGenreArtist(genre['id'], artist['id'])
            collection += (' ' * 4) + artist['artist'] + ' (' + str(len(albums)) + ')\n'            
            for album in albums:
                collection += (' ' * 4 * 2) + album['album'] + '\n'

    with open(collectionFolder + '/collection-genre-artist-album-by-tag.txt', 'w') as file:
        file.write(collection)            

    pass

def GetLmsServerStatus():
    # LMS API-reference: http://rpms:9000/html/docs/cli-api.html
    # curl "rpms:9000/jsonrpc.js" -d '{"method": "slim.request", "params": ["-", ["serverstatus","0","-1"]]}'
    url = const_LmsApiUrl
    data = '{"method": "slim.request", "params": ["-", ["serverstatus","0","-1"]]}'
    headers = {'Content-Type': 'application/json'}

    try:
        response = json.loads(requests.request("GET", url, headers=headers, data=data).content)
    except Exception as e:
        return         

    return(response['result'])

def GetLmsArtists():
    # LMS API-reference: http://rpms:9000/html/docs/cli-api.html
    # curl "rpms:9000/jsonrpc.js" -d '{"method": "slim.request", "params": ["-", ["artists","0","-1"]]}'
    url = const_LmsApiUrl
    data = '{"method": "slim.request", "params": ["-", ["artists","0","-1"]]}'
    headers = {'Content-Type': 'application/json'}

    try:
        response = json.loads(requests.request("GET", url, headers=headers, data=data).content)
    except Exception as e:
        return ''       

    return(response['result']['artists_loop'])

def GetLmsAlbumsByArtist(artist):
    # LMS API-reference: http://rpms:9000/html/docs/cli-api.html
    # curl "rpms:9000/jsonrpc.js" -d '{"method": "slim.request", "params": ["-", ["albums","0","-1","artist_id:207087"]]}'
    url = const_LmsApiUrl
    data = '{"method": "slim.request", "params": ["-", ["albums","0","-1","artist_id:' + str(artist) + '"]]}'
    headers = {'Content-Type': 'application/json'}

    try:
        response = json.loads(requests.request("GET", url, headers=headers, data=data).content)
    except Exception as e:
        return ''       

    return(response['result']['albums_loop'])

def GetLmsAlbumsByGenreArtist(genre, artist):
    # LMS API-reference: http://rpms:9000/html/docs/cli-api.html
    # curl "rpms:9000/jsonrpc.js" -d '{"method": "slim.request", "params": ["-", ["albums","0","-1","genre_id:37841","artist_id:207087"]]}'
    37841
    url = const_LmsApiUrl
    data = '{"method": "slim.request", "params": ["-", ["albums","0","-1","genre_id:' + str(genre) + '","artist_id:' + str(artist) + '"]]}'
    headers = {'Content-Type': 'application/json'}

    try:
        response = json.loads(requests.request("GET", url, headers=headers, data=data).content)
    except Exception as e:
        return ''       

    return(response['result']['albums_loop'])

def GetLmsGenres():
    # LMS API-reference: http://rpms:9000/html/docs/cli-api.html
    # curl "rpms:9000/jsonrpc.js" -d '{"method": "slim.request", "params": ["-", ["genres","0","-1"]]}'
    url = const_LmsApiUrl
    data = '{"method": "slim.request", "params": ["-", ["genres","0","-1"]]}'
    headers = {'Content-Type': 'application/json'}

    try:
        response = json.loads(requests.request("GET", url, headers=headers, data=data).content)
    except Exception as e:
        return ''               

    return(response['result']['genres_loop'])

def GetLmsArtistsByGenre(genre):
    # LMS API-reference: http://rpms:9000/html/docs/cli-api.html
    # curl "rpms:9000/jsonrpc.js" -d '{"method": "slim.request", "params": ["-", ["artists","0","-1","genre_id:37866"]]}'    
    url = const_LmsApiUrl
    data = '{"method": "slim.request", "params": ["-", ["artists","0","-1","genre_id:' + str(genre) + '"]]}'
    headers = {'Content-Type': 'application/json'}

    try:
        response = json.loads(requests.request("GET", url, headers=headers, data=data).content)
    except Exception as e:
        return ''

    return(response['result']['artists_loop'])

def GetLmsPlayers():
    def GetUpperNameFromPlayer(x):
        return (x['Name'].upper())

    # LMS API-reference: http://rpms:9000/html/docs/cli-api.html
    # curl "rpms:9000/jsonrpc.js" -d '{"method": "slim.request", "params": ["-", ["players","0","10"]]}'
    url = const_LmsApiUrl
    data = '{"method": "slim.request", "params": ["-", ["players","0","10"]]}'
    headers = {'Content-Type': 'application/json'}

    try:
        response = json.loads(requests.request("GET", url, headers=headers, data=data).content)
    except Exception as e:
        return ''

    players = []
    if response['result']['count'] > 0:
        for player in response['result']['players_loop']:
            name = player['name']
            model = player['model']
            ipAddress = player['ip'].split(':', 1)[0]
            firmWare = player['firmware']

            isWebServer = False
            if ExecuteBashCommand('nmap ' + ipAddress + ' --open -p 80 | grep 80/tcp') != '':
                isWebServer = True

            type = 'unknown'
            if model == 'squeezelite':
                type = 'pc'
                if 'PCP' in firmWare.upper():
                    type = 'pi'
            else:
                if model == 'boom':
                    type = 'sb-boom'
                elif model == 'baby':
                    type = 'sb-radio'
                elif model == 'receiver':
                    type = 'sb-receiver'
                elif model == 'fab4':
                    type = 'sb-touch'
                elif model == 'squeezebox3':
                    type = 'sb-classic'
                elif model == 'transporter':
                    type = 'sb-transporter'

            players.append({
                            "Name": name,
                            "Model": model,
                            "IpAddress": ipAddress,
                            "IsWebServer": isWebServer,
                            "FirmWare": firmWare,
                            "Type": type
                        })  
            players = sorted(players, key=GetUpperNameFromPlayer)

    return(players)


