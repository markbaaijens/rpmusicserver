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

def GetMachineInfo():
    hostName = ExecuteBashCommand("hostname")
    ipAddress = ExecuteBashCommand("hostname -I").split()[0]
    osCodeName = ExecuteBashCommand("lsb_release -c").split()[1]
    rpModel = ''
    if os.path.isfile('/proc/device-tree/model'):    
        rpModel = ExecuteBashCommand("cat /proc/device-tree/model").replace('\u0000', '')
    cpuTemp = ''
    if len(ExecuteBashCommand("whereis vcgencmd").split()) > 1:
        process = subprocess.run(["vcgencmd measure_temp"], stdout=subprocess.PIPE, shell=True)
        process = subprocess.run(["cut -c 6-"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
        cpuTemp = process.stdout.decode("utf-8").strip('\n')

    # upTime => uptime -p | cut -c 4-
    process = subprocess.run(["uptime -p"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["cut -c 4-"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    upTime = process.stdout.decode("utf-8").strip('\n')

    return {"HostName": hostName,
            "IpAddress": ipAddress,
            "OsCodeName": osCodeName,
            "RpModel": rpModel,
            "CpuTemp": cpuTemp,
            "UpTime": upTime}

disks = []
services = []

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

def AppendServiceInfo(portNumber, serviceName):
    # isOnline => nmap localhost | grep <port>/tcp'
    isOnline = False
    process = subprocess.run(["nmap localhost"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["grep " + str(portNumber) + '/tcp'], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    if process.stdout.decode("utf-8").strip('\n'):
        isOnline = True

    services.append({
                    "PortNumber": portNumber,
                    "ServiceName": serviceName,
                    "IsOnline": isOnline
                 })
    pass

def GetDiskList():
    disks.clear()
    AppendDiskInfo('/')
    AppendDiskInfo('/media/usbdata')
    AppendDiskInfo('/media/usbbackup')
    return disks

def GetServiceList():
    services.clear()
    AppendServiceInfo(22, 'SSH')
    AppendServiceInfo(80, 'RPMS/web')
    AppendServiceInfo(139, 'Samba/netbios')
    AppendServiceInfo(445, 'Samba/tcp')
    AppendServiceInfo(5000, 'RPMS/api')
    AppendServiceInfo(9002, 'LMS/web')
    AppendServiceInfo(9090, 'LMS/telnet')
    AppendServiceInfo(9091, 'Transmission')
    return services
    
def GetResourceInfo():
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

    # averageLoad1 => uptime | tail -c 17 | awk '{print $1}' | cut -c 1-4
    process = subprocess.run(["uptime"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["tail -c 17"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    process = subprocess.run(["awk '{print $1}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["cut -c 1-4"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    averageLoad1 = float(process.stdout.decode("utf-8").strip('\n').replace(',', '.'))

    # averageLoad5 => uptime | tail -c 17 | awk '{print $2}' | cut -c 1-4
    process = subprocess.run(["uptime"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["tail -c 17"], input=process.stdout, stdout=subprocess.PIPE, shell=True)        
    process = subprocess.run(["awk '{print $2}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["cut -c 1-4"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    averageLoad5 = float(process.stdout.decode("utf-8").strip('\n').replace(',', '.'))

    # averageLoad15 => uptime | tail -c 17 | awk '{print $3}'
    process = subprocess.run(["uptime"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["tail -c 17"], input=process.stdout, stdout=subprocess.PIPE, shell=True)            
    process = subprocess.run(["awk '{print $3}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    averageLoad15 = float(process.stdout.decode("utf-8").strip('\n').replace(',', '.'))

    # topProcessesByCpu => ps --no-headers -eo command --sort -%cpu | head -5
    topProcessesByCpu = []
    topProcessesByCpu.clear()
    process = subprocess.run(["ps --no-headers -eo command --sort -%cpu"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["head -5"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    lines = process.stdout.decode("utf-8").strip('\n')
    lines = lines.splitlines()
    for line in lines:
        topProcessesByCpu.append(line)

    # topProcessesByMemory => ps --no-headers -eo command --sort -%mem | head -10
    topProcessesByMemory = []
    topProcessesByMemory.clear()
    process = subprocess.run(["ps --no-headers -eo command --sort -%mem"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["head -5"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    lines = process.stdout.decode("utf-8").strip('\n')
    lines = lines.splitlines()
    for line in lines:
        topProcessesByMemory.append(line)

    return {'MemTotal': memTotal,
            "MemUsed": memUsed,
            "MemUsedPercentage": memUsedPercentage,
            "SwapTotal": swapTotal,
            "SwapUsed": swapUsed,
            "SwapUsedPercentage": swapUsedPercentage,            
            "AverageLoad1": averageLoad1,
            "AverageLoad5": averageLoad5,
            "AverageLoad15": averageLoad15,
            "TopProcessesByCpu": topProcessesByCpu,
            "TopProcessesByMemory":topProcessesByMemory}

def GetVersionInfo():
    revisionFile = '/etc/rpms/revision.json'
    if not os.path.isfile(revisionFile):
        revisionFile = os.path.dirname(__file__) + '/../../revision.json'

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
        lastUpdateTimeStampAsString = datetime.utcfromtimestamp(lastUpdateTimeStamp).strftime('%Y-%m-%d %H:%M:%S')

    availableVersion = '0.0'
    with urllib.request.urlopen("https://raw.githubusercontent.com/markbaaijens/rpmusicserver/master/revision.json") as url:
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

    updateBranchName = 'master'
    updateBranchFile = '/media/usbdata/rpms/config/update-branch.txt'
    if os.path.isfile(updateBranchFile):
        file = open(updateBranchFile, 'r')
        updateBranchName = file.read()

    # Always update if override-branch has been given, even if versions don't match        
    if updateBranchName != 'master':
        canUpdate = True

    return {"VersionFile": revisionFile,
            "CurrentVersion": currentVersion, 
            "LastUpdateTimeStamp": lastUpdateTimeStampAsString,
            "AvailableVersion": availableVersion,
            "CanUpdate": canUpdate,
            "UpdateBranchName": updateBranchName}

def GetBackupInfo():
    isBackupInProgress = False
    if os.path.isfile('/media/usbdata/rpms/logs/backup-details.log'):
        if ExecuteBashCommand("grep 'speedup is ' /media/usbdata/rpms/logs/backup-details.log").strip() == '':
            isBackupInProgress = True
    return {"IsBackupInProgress": isBackupInProgress}

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

async def DoUpdateServer():
    await asyncio.create_subprocess_shell("update-server")
    pass

def GetLmsServerInfo():
    # LMS API-reference: http://msi:9000/html/docs/cli-api.html 
    url = "http://rpms:9002/jsonrpc.js"    
    payload = "{\"method\": \"slim.request\", \"params\": [\"-\", [\"serverstatus\",\"0\",\"100\"]]}\n"
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    return(response.text)
