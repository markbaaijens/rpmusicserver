import subprocess
import requests
import json
import os
from globals import configObject
from datetime import datetime
import math
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

def GetMachineInfo():
    def CheckRpModelMemoryInGB(rpModelMemoryInGB):
        if int(rpModelMemoryInGB) < 1:
            rpModelMemoryInGB = "1"
        return rpModelMemoryInGB + "GB"
        
    def GetOsBitType():
        osBitType = ExecuteBashCommand("uname -m")
        if osBitType == "armv7l":
            return osBitType + ' 32-bit'
        elif osBitType == "armv8":
            return osBitType + ' 64-bit'
        return osBitType

    def GetHostUrl():
        urlPrefix = 'http://'
        hostUrl = urlPrefix + hostName
        if ExecuteBashCommand("nslookup " + hostName + " | grep \"server can't find\"").strip() != "":
            hostUrl = urlPrefix + ipAddress
        return hostUrl

    hostName = ExecuteBashCommand("hostname")
    ipAddress = ExecuteBashCommand("hostname -I").split()[0]
    hostUrl = GetHostUrl()  # Must be behind hostName + ipAddress
    osDescription = ExecuteBashCommand("lsb_release -d | cut -f2")
    osBitType = GetOsBitType()
    osCodeName = ExecuteBashCommand("lsb_release -c").split()[1]
    rpModel = '?'
    rpModelMemoryInGB = CheckRpModelMemoryInGB(ExecuteBashCommand("free --giga | grep Mem: | awk '{print $2}'"))
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

    if os.path.isfile('/media/usbdata/rpms/logs/backup-details.log'):
        if ExecuteBashCommand("grep 'speedup is ' /media/usbdata/rpms/logs/backup-details.log").strip() == '':
            isBackupNotInProgress = False

    isBackupDiskPresent = ExecuteBashCommand("ls /dev/disk/by-label | grep usbbackup") == "usbbackup"
    canBackup = isBackupDiskPresent and isBackupNotInProgress
    lastBackup = ExecuteBashCommand("cat /media/usbdata/rpms/logs/backup.log | grep 'executing backup' | tail -n 1 | cut -c1-19")

    return {"IsBackupNotInProgress": isBackupNotInProgress,
            "IsBackupDiskPresent": isBackupDiskPresent,
            "CanBackup": canBackup,
            "LastBackup": lastBackup}

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

def GetDefaultMusicCollectionFolder():
    return '/media/usbdata/user/Publiek/Muziek'    

def GetMusicCollectionInfo():
    defaultCollectionFolder = GetDefaultMusicCollectionFolder()

    transcoderSettings = GetTranscoderSettings()
    actualCollectionFolder = transcoderSettings["sourcefolder"]
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

    return {"CollectionFolder": actualCollectionFolder,
            "DefaultCollectionFolder": defaultCollectionFolder,
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
