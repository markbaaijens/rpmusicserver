import subprocess
import requests
import json
import os
from globals import configObject
from datetime import datetime

def ExecuteBashCommand(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode("utf-8").strip('\n')

def GetMachineInfo():
    hostName = ExecuteBashCommand("hostname")
    ipAddress = ExecuteBashCommand("hostname -I").split()[0]
    osCodeName = ExecuteBashCommand("lsb_release -c").split()[1]
    return {'HostName': hostName, 'IpAddress': ipAddress, "OsCodeName": osCodeName}

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

def GetUpdateLog():
    line1 = 'Line 1'
    line2 = 'Line 2'    
    return { "UpdateLog": [ line1, line2] }

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
