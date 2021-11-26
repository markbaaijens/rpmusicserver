import subprocess
import requests
import json
import os
from globals import configObject
from datetime import datetime
import math

def ExecuteBashCommand(bashCommand):
    process = subprocess.run(bashCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return process.stdout.decode("utf-8").strip('\n')

def TailFromFile(file, n):
    process = subprocess.Popen(['tail', '-n', f'{n}', file], stdout=subprocess.PIPE)    
    lines = process.stdout.readlines()
    return lines

def GetMachineInfo():
    hostName = ExecuteBashCommand("hostname")
    ipAddress = ExecuteBashCommand("hostname -I").split()[0]
    osCodeName = ExecuteBashCommand("lsb_release -c").split()[1]
    return {'HostName': hostName, 'IpAddress': ipAddress, "OsCodeName": osCodeName}

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
    diskUsedPercentage = ''
    isHealthy = None
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
        diskUsedPercentage = process.stdout.decode("utf-8").strip('\n')

        diskStatus = 'online'
    else:
        diskStatus = 'offline'

    disks.append({
                    "DiskName": diskName,
                    "MountPoint": diskMountPoint,
                    "DeviceName": diskDeviceName,
                    "Status": diskStatus,
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
    return {'Disks': disks}

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

    # upTime => uptime -p | cut -c 4-
    process = subprocess.run(["uptime -p"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["cut -c 4-"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    upTime = process.stdout.decode("utf-8").strip('\n')

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
            "UpTime": upTime,
            "OverageLoad1": averageLoad1,
            "OverageLoad5": averageLoad5,
            "OverageLoad15": averageLoad15,
            "TopProcessesByCpu": topProcessesByCpu,
            "TopProcessesByMemory":topProcessesByMemory}

def GetVersionInfo():
    revisionFile = '/etc/rpms/revision.json'
    if not os.path.isfile(revisionFile):
        revisionFile = os.path.dirname(__file__) + '/../../revision.json'

    currentVersion = ''
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

    return {"VersionFile": revisionFile,
            "CurrentVersion": currentVersion, 
            "LastUpdateTimeStamp": lastUpdateTimeStampAsString}

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
    transcoderSettingsFile = '/media/usbdata/config/transcoder-settings.json'
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
    return { "LogLines": logLines }

def GetDockerContainerList():
    dockerContainerList = []
    process = subprocess.run(["docker ps --format '{{.Image}}'"], stdout=subprocess.PIPE, shell=True)
    lines = process.stdout.decode("utf-8").strip('\n')
    lines = lines.splitlines()
    for line in lines:
        dockerContainerList.append(line)
    return { "DockerContainers": dockerContainerList }

def SetTranscoderSetting(requestData, settingName):
    if not settingName in requestData:
        return { "Message": "Invalid request-data"}
    sourceFolder = requestData[settingName]
    
    transcoderSettingsFileName = '/media/usbdata/config/transcoder-settings.json'
    if not os.path.isfile(transcoderSettingsFileName):
        return { "Message": "File " + transcoderSettingsFileName + " does not exist"}

    with open(transcoderSettingsFileName, 'r') as jsonFile:
        data = json.load(jsonFile)
    data[settingName] = sourceFolder
    with open(transcoderSettingsFileName, 'w') as jsonFile:
        json.dump(data, jsonFile)

    return { "Message": "Transcoder-setting ["+ settingName + "] is modified to [" + sourceFolder + "]"}

def DoRebootServer():
    subprocess.run(["reboot now"], stdout=subprocess.PIPE, shell=True)
    return { "Message": "Server is rebooting" }

def DoHaltServer():
    subprocess.run(["halt"], stdout=subprocess.PIPE, shell=True)
    return { "Message": "Server is halting" }

def DoUpdateServer():
    subprocess.run(["update-rpms"], stdout=subprocess.PIPE, shell=True)
    return { "Message": "Server is updating" }

def GetLmsServerInfo():
    # LMS API-reference: http://msi:9000/html/docs/cli-api.html 
    url = "http://rpms:9002/jsonrpc.js"    
    payload = "{\"method\": \"slim.request\", \"params\": [\"-\", [\"serverstatus\",\"0\",\"100\"]]}\n"
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    return(response.text)
