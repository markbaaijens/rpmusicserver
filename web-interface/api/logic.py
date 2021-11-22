import subprocess
import requests
import json
import os
from globals import configObject
from datetime import datetime

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

def GetDiskList():
# List labels of all devices: sudo blkid -o list

    disks = []

# systemSize => df -h | grep -w / | awk '{print $2}'
# systemUsed => df -h | grep -w / | awk '{print $3}'
# systemUsedPercentage => df -h | grep -w / | awk '{print $5}'

    diskName = 'system'
    diskMountPoint = '/'
    diskDeviceName = '/dev/sda'
    diskStatus = 'online'
    diskSize = '16G'
    diskUsed = '4G'
    diskUsedPercentage = '25%'
    disks.append({
                    "DiskName": diskName,
                    "MountPoint": diskMountPoint,
                    "DeviceName": diskDeviceName,
                    "Status": diskStatus,
                    "Size": diskSize,
                    "Used": diskUsed,
                    'UsedPercentage': diskUsedPercentage
                 })

# usbDataSize => df -h | grep -w /media/usbdata | awk '{print $2}'
# usbDataUsed => df -h | grep -w /media/usbdata | awk '{print $3}'
# usbDataUsedPercentage => df -h | grep -w /media/usbdata | awk '{print $5}'

    # TODO Check if online => status = 'offline' (other properties stay empty)
    diskName = 'usbdata'
    diskMountPoint = '/media/usbdata'    
    diskDeviceName = '/dev/sdb'    
    diskStatus = 'online'
    diskSize = '2TB'
    diskUsed = '1.5TB'
    diskUsedPercentage = '75%'
    disks.append({
                    "DiskName": diskName,
                    "MountPoint": diskMountPoint,
                    "DeviceName": diskDeviceName,
                    "Status": diskStatus,
                    "Size": diskSize,
                    "Used": diskUsed,
                    'UsedPercentage': diskUsedPercentage
                 })

# usbBackupSize => df -h | grep -w /media/usbbackup | awk '{print $2}'
# usbBackupUsed => df -h | grep -w /media/usbbackup | awk '{print $3}'
# usbBackupUsedPercentage => df -h | grep -w /media/usbbackup | awk '{print $5}'

    # TODO Check if online => status = 'offline' (other properties stay empty)
    diskName = 'usbbackup'
    diskMountPoint = '/media/usbbackup'    
    diskDeviceName = '/dev/sdc'    
    diskStatus = 'online'
    diskSize = '4TB'
    diskUsed = '1.8TB'
    diskUsedPercentage = '45%'
    disks.append({
                    "DiskName": diskName,
                    "MountPoint": diskMountPoint,
                    "DeviceName": diskDeviceName,
                    "Status": diskStatus,
                    "Size": diskSize,
                    "Used": diskUsed,
                    'UsedPercentage': diskUsedPercentage
                 })

    return {'Disks': disks}

def GetResourceInfo():
    # memTotal => free | grep 'Mem:' | awk '{print $2}'
    process = subprocess.run(["free"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["grep 'Mem:'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $2}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    memTotal = process.stdout.decode("utf-8").strip('\n')

    # memUsed => free | grep 'Mem:' | awk '{print $3}'
    process = subprocess.run(["free"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["grep 'Mem:'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $3}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    memUsed = process.stdout.decode("utf-8").strip('\n')

    # swapTotal => free | grep 'Swap:' | awk '{print $2}'
    process = subprocess.run(["free"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["grep 'Swap:'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $2}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    swapTotal = process.stdout.decode("utf-8").strip('\n')

    # swapUsed => free | grep 'Swap:' | awk '{print $3}'
    process = subprocess.run(["free"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["grep 'Swap:'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $3}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    swapUsed = process.stdout.decode("utf-8").strip('\n')

    # upTimeInDays => uptime | awk '{print $3}'
    process = subprocess.run(["uptime"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $3}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    upTimeInDays = process.stdout.decode("utf-8").strip('\n')

    # averageLoad1 => uptime | awk '{print $10}' | cut -c 1-4
    process = subprocess.run(["uptime"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $10}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["cut -c 1-4"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    averageLoad1 = process.stdout.decode("utf-8").strip('\n')

    # averageLoad5 => uptime | awk '{print $11}' | cut -c 1-4
    process = subprocess.run(["uptime"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $11}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["cut -c 1-4"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    averageLoad5 = process.stdout.decode("utf-8").strip('\n')

    # averageLoad15 => uptime | awk '{print $12}' | cut -c 1-4
    process = subprocess.run(["uptime"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["awk '{print $12}'"], input=process.stdout, stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["cut -c 1-4"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    averageLoad15 = process.stdout.decode("utf-8").strip('\n')

    # topProcessesByCpu => ps --no-headers -eo command --sort -%cpu | head -5
    topProcessesByCpu = []
    process = subprocess.run(["ps --no-headers -eo command --sort -%cpu"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["head -5"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    lines = process.stdout.decode("utf-8").strip('\n')
    lines = lines.splitlines()
    for line in lines:
        topProcessesByCpu.append(line)

    # topProcessesByMemory => ps --no-headers -eo command --sort -%mem | head -10
    topProcessesByMemory = []
    process = subprocess.run(["ps --no-headers -eo command --sort -%mem"], stdout=subprocess.PIPE, shell=True)
    process = subprocess.run(["head -5"], input=process.stdout, stdout=subprocess.PIPE, shell=True)    
    lines = process.stdout.decode("utf-8").strip('\n')
    lines = lines.splitlines()
    for line in lines:
        topProcessesByMemory.append(line)

    return {'MemTotal': memTotal,
            "MemUsed": memUsed,
            "SwapTotal": swapTotal,
            "SwapUsed": swapUsed,
            "UpTimeInDays": upTimeInDays,
            "OverageLoad1": averageLoad1,
            "OverageLoad5": averageLoad5,
            "OverageLoad15": averageLoad15,
            "TopProcessesByCpu": topProcessesByCpu,
            "TopProcessesByMemory":topProcessesByMemory}

def GetVersionInfo():
    currentVersion = ''
    lastUpdateTimeStampAsString = ''
    if configObject.Debug:
        revisionFile = '../../revision.json'    
    else: 
        revisionFile = '/etc/rmps/revision.json'    
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

    return {'CurrentVersion': currentVersion, "LastUpdateTimeStamp": lastUpdateTimeStampAsString}

def GetApiList():
    dataAsJson = {}
    apiInfoFile = 'api-info.json'    
    if os.path.isfile(apiInfoFile):
        with open(apiInfoFile) as file:
            dataAsDict = json.load(file)
        dataAsJson = json.loads(json.dumps(dataAsDict))
    return dataAsJson

def GetLog(logFile, nrOfLines):
    logLines = []
    if os.path.isfile(logFile):
        logLinesFromFile = TailFromFile(logFile, nrOfLines)
        for logLine in logLinesFromFile:
            logLines.append(logLine.decode("utf-8").strip('\n'))
    return { "logLines": logLines }

def GetDockerContainerList():
    dockerContainerList = []
    process = subprocess.run(["docker ps --format '{{.Image}}'"], stdout=subprocess.PIPE, shell=True)
    lines = process.stdout.decode("utf-8").strip('\n')
    lines = lines.splitlines()
    for line in lines:
        dockerContainerList.append(line)
    return { "DockerContainers": dockerContainerList }

def DoRebootServer():
    subprocess.run(["reboot now"], stdout=subprocess.PIPE, shell=True)
    return { "Message": "Server is rebooting" }

def DoHaltServer():
    subprocess.run(["halt"], stdout=subprocess.PIPE, shell=True)
    return { "Message": "Server is halting" }

def DoUpdateServer():
    subprocess.run(["update-rpms"], stdout=subprocess.PIPE, shell=True)
    return { "Message": "Server is updating" }

'''
LMS API-reference: http://msi:9000/html/docs/cli-api.html

Examples:

# [player] Play
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["b8:27:eb:79:f5:47", ["play"]]}'

# [player] Pause/unpause
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["b8:27:eb:79:f5:47", ["pause"]]}'

# [player] Player status
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["b8:27:eb:79:f5:47", ["status","-"]]}'

# [player] Get title now playing
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["b8:27:eb:79:f5:47", ["playlist","title","?"]]}

# [server] Get song details (song-id from status, first in playlist); bitrate/samplesize
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["-", ["songinfo","0","100", "track_id:3903170"]]}'

# [server] Get server status; playerlist, library-statistics
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["-", ["serverstatus","0","100"]]}
'''

def GetLmsInfo():  # Sample function from generated code in Postman; may not function
    # Todo 'msi' => 'localhost'
    # Todo '9000' => '9002'    
    url = "http://msi:9000/jsonrpc.js"
    payload = "{\"method\": \"slim.request\", \"params\": [\"-\", [\"serverstatus\",\"0\",\"100\"]]}\n"
    headers = {'Content-Type': 'application/json'}

    # TODO This call does npt seem to return the result (body)
    response = requests.request("POST", url, headers=headers, data=payload)

    # TODO This call should return the resukt
#    response = json.loads(requests.get(app.config['API_ROOT_URL'] + '/books').content)

    print(response)

    return(response)
